import pickle
import os
from typing import List, Dict, Any

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

from engine.configuration import Branch, Commit, Group, Project, PipelineSchedule, User

# TODO Improve opening off these, such as with a context manager and proper error checking
groups_and_projects_query = gql(open("queries/groups_and_projects.gql", "r").read())
project_details_query = gql(open("queries/project_details.gql", "r").read())
branch_details_query = gql(open("queries/branch_details.gql", "r").read())


def create_gitlab_client() -> Client:
    transport = AIOHTTPTransport(
        url=os.getenv("GITLAB_SERVER"),
        headers={
            "PRIVATE-TOKEN": os.getenv("GITLAB_TOKEN"),
        },
    )

    return Client(transport=transport, fetch_schema_from_transport=True)


def make_query(client: Client, query: gql, variables: dict = None) -> Dict[str, Any]:
    return client.execute(
        query,
        variable_values=variables,
    )


def create_groups_and_projects(groups_result: Dict[str, Any]) -> List[Group]:
    groups = []

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


def create_branch(branch_name: str) -> Branch:
    return Branch(name=branch_name)


def create_branch_details(branch: Branch, branch_details: Dict[str, Any]):
    try:
        ref = branch_details["project"]["repository"]["tree"]["lastCommit"]
        branch.set_last_commit(
            Commit(
                title=ref["title"],
                authored_date=ref["authoredDate"],
                author_name=ref["authorName"],
            )
        )
    except TypeError as type_error:
        print(f"There is a TypeError of: {type_error}")


def create_pipeline_schedule(pipeline_schedule: Dict[str, Any]) -> PipelineSchedule:
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
        ),
    )


def create_project_details(project: Project, project_details: Dict[str, Any]) -> None:
    for branch_name in project_details["project"]["repository"]["branchNames"]:
        project.add_branch(create_branch(branch_name))

    for pipeline_schedule in project_details["project"]["pipelineSchedules"]["edges"]:
        project.add_pipeline_schedule(create_pipeline_schedule(pipeline_schedule))


def pickle_and_save(output_pickle_filename: str, groups: List[Group]) -> None:
    file = open(output_pickle_filename, "wb")
    pickle.dump(groups, file)


# TODO this shouldnt be needed by for some reason is
def get_value(results: Dict[str, Any], key: str) -> Any:
    return results["groups"]["pageInfo"][key]


def get_data(output_pickle_filename: str) -> None:
    client = create_gitlab_client()

    # TODO deal with pagination in each query and make it more seamless than here
    groups = []
    has_next_page = True
    after = ""
    while has_next_page:
        results = make_query(
            client,
            groups_and_projects_query,
            variables={
                # Temporary to test pagination
                # "numOfResults": 1,
                "after": after,
            },
        )
        groups += create_groups_and_projects(results)
        if get_value(results, "hasNextPage"):
            after = get_value(results, "endCursor")
        else:
            has_next_page = False

    for group in groups:
        for project in group.projects:
            project_details = make_query(
                client,
                project_details_query,
                variables={
                    "projectFullPath": f"{project.full_path}",
                },
            )

            create_project_details(project, project_details)

    for group in groups:
        for project in group.projects:
            for branch in project.get_branches():
                branch_details = make_query(
                    client,
                    branch_details_query,
                    variables={
                        "projectFullPath": f"{project.full_path}",
                        "branchName": branch.name,
                    },
                )

                create_branch_details(branch, branch_details)

    pickle_and_save(output_pickle_filename, groups)
