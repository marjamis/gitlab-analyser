from engine.configuration import Branch, Commit, Group, Project
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import pickle
import os


def get_data(output_pickle_filename):
    groups = []

    transport = AIOHTTPTransport(
        url=os.getenv("GITLAB_SERVER"),
        headers={
            "PRIVATE-TOKEN": os.getenv("GITLAB_TOKEN"),
        },
    )

    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Improve opening of while, such as with a context manager
    groups_gq = gql(open("queries/groups.gql", "r").read())
    projects_gq = gql(open("queries/projects.gql", "r").read())
    branches_gq = gql(open("queries/branch.gql", "r").read())

    groups_result = client.execute(
        groups_gq,
        variable_values={},
    )

    for group in groups_result["groups"]["nodes"]:
        print(group["name"])
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

    for group in groups:
        for project in group.projects:
            branches_list_result = client.execute(
                projects_gq,
                variable_values={
                    "fullPath": f"{project.full_path}",
                },
            )

            print(f"{project.full_path}")
            print(branches_list_result)

            # TODO design in such a way that if things don't exists its OK to ocntinue
            for branch_name in branches_list_result["project"]["repository"][
                "branchNames"
            ]:
                new_branch = Branch(name=branch_name)

                last_commit_result = client.execute(
                    branches_gq,
                    variable_values={
                        "project": f"{project.full_path}",
                        "branch": branch_name,
                    },
                )
                print(project.full_path)
                print(last_commit_result)
                try:
                    ref = last_commit_result["project"]["repository"]["tree"][
                        "lastCommit"
                    ]
                    print(ref)
                    new_branch.set_last_commit(
                        Commit(
                            title=ref["title"],
                            authored_date=ref["authoredDate"],
                            author_name=ref["authorName"],
                        )
                    )
                except TypeError:
                    print("Likely a NoneType found")

                project.add_branch(new_branch)

    file = open(output_pickle_filename, "wb")
    pickle.dump(groups, file)

    print(groups)
