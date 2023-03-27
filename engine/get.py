from engine.configuration import Branch, Commit, Group, Project, PipelineSchedule, User
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import pickle
import os
from typing import List

# TODO Improve opening off these, such as with a context manager and proper error checking
groups_gq = gql(open("queries/groups.gql", "r").read())
projects_gq = gql(open("queries/projects.gql", "r").read())
branches_gq = gql(open("queries/branch.gql", "r").read())


def create_gitlab_client() -> Client:
    transport = AIOHTTPTransport(
        url=os.getenv("GITLAB_SERVER"),
        headers={
            "PRIVATE-TOKEN": os.getenv("GITLAB_TOKEN"),
        },
    )

    return Client(transport=transport, fetch_schema_from_transport=True)


def get_groups(client: Client) -> List[Group]:
    groups = []

    groups_result = client.execute(
        groups_gq,
        variable_values={},
    )

    for group in groups_result["groups"]["nodes"]:
        new_group = Group(
            id=group["id"],
            name=group["name"],
            full_name=group["fullName"],
            full_path=group["fullPath"],
            description=group["description"],
        )

        for project in group["projects"]["nodes"]:
            new_project = Project(
                id=project["id"],
                name=project["name"],
                full_path=project["fullPath"],
                description=project["description"],
                primary_branch=project["repository"]["rootRef"],
            )

            new_group.add_project(new_project)

        groups.append(new_group)

    return groups


def get_branch_details(client: Client, project: Project, branch_name: str) -> Branch:
    new_branch = Branch(name=branch_name)

    last_commit_result = client.execute(
        branches_gq,
        variable_values={
            "project": f"{project.full_path}",
            "branch": branch_name,
        },
    )

    try:
        ref = last_commit_result["project"]["repository"]["tree"]["lastCommit"]
        new_branch.set_last_commit(
            Commit(
                title=ref["title"],
                authored_date=ref["authoredDate"],
                author_name=ref["authorName"],
            )
        )
    except TypeError as te:
        print(f"There is a TypeError of: {te}")

    return new_branch


def get_pipeline_schedule_details(pipeline_schedule) -> PipelineSchedule:
    node = pipeline_schedule["node"]
    owner = pipeline_schedule["node"]["owner"]
    return PipelineSchedule(
        id=node["id"],
        description=node["description"],
        active=node["active"],
        next_run_at=node["nextRunAt"],
        owner=User(
                id=owner["id"],
                username=owner["username"],
                public_email=owner["publicEmail"],
                state=owner["state"],
            )
        )


def get_branches(client: Client, groups: List[Group]) -> List[Group]:
    for group in groups:
        for project in group.projects:
            branches_list_result = client.execute(
                projects_gq,
                variable_values={
                    "fullPath": f"{project.full_path}",
                },
            )

            for branch_name in branches_list_result["project"]["repository"]["branchNames"]:
                project.add_branch(get_branch_details(client, project, branch_name))

            for pipeline_schedule in branches_list_result["project"]["pipelineSchedules"]["edges"]:
                project.add_pipeline_schedule(get_pipeline_schedule_details(pipeline_schedule))

    return groups


def pickle_and_save(output_pickle_filename: str, groups: List[Group]) -> None:
    file = open(output_pickle_filename, "wb")
    pickle.dump(groups, file)


def get_data(output_pickle_filename: str) -> None:
    client = create_gitlab_client()

    groups = get_groups(client)
    groups = get_branches(client, groups)

    pickle_and_save(output_pickle_filename, groups)
