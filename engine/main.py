from configuration import Branch, Commit, Group, Project
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import pickle
import os

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
    variable_values={
        "numOfResults": 2,
    },
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
                "fullPath": f"{group.full_path}/{project.name}",
            },
        )

        print(f"{group.full_path}/{project.name}")
        print(branches_list_result)

        # TODO design in such a way that if things don't exists its OK to ocntinue
        for branch_name in branches_list_result["project"]["repository"]["branchNames"]:
            new_branch = Branch(name=branch_name)

            last_commit_result = client.execute(
                branches_gq,
                variable_values={
                    "project": f"{group.full_path}/{project.name}",
                    "branch": branch_name,
                },
            )
            print(project.name)
            print(last_commit_result)
            try:
                ref = last_commit_result["project"]["repository"]["tree"]["lastCommit"]
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


file = open("./data/data.pickle", "wb")
pickle.dump(groups, file)

print(groups)


file = open("./data/data.pickle", "rb")
groups = pickle.load(file)

print(groups)
for group in groups:
    print(f"{group.id} | {group.name} | {group.full_path} | {group.description}")
    for project in group.projects:
        print(f"\t\t{project.id} | {project.name} | {project.description}")
        for branch in project.branches:
            print(
                f"\t\t\t\t{branch.name} | {branch.last_commit.title} | {branch.last_commit.authored_date} | {branch.last_commit.author_name}"
            )
