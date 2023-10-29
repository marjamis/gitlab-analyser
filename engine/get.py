"""
Gets data from GitLab and produces objects with the data.
"""

import pickle
import os
from typing import Dict, Any

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

from engine.types import Branch, Commit, Group, Data, Project, PipelineSchedule

# TODO Improve opening off these, such as with a context manager and proper error checking
groups_and_projects_query = open("queries/groups_and_projects.gql", "r").read()
project_details_query = open("queries/project_details.gql", "r").read()
branch_details_query = open("queries/branch_details.gql", "r").read()


def create_gitlab_client() -> Client:
    """
    Creates a GitLab GraphQL Client.
    """

    url = os.getenv("GITLAB_GRAPHQL_ENDPOINT")
    if url is None:
        raise Exception("GITLAB_GRAPHQL_ENDPOINT environment variable not specified")
    token = os.getenv("GITLAB_TOKEN")
    if token is None:
        raise Exception("GITLAB_TOKEN environment variable not specified")

    transport = AIOHTTPTransport(
        url=url,
        headers={
            "PRIVATE-TOKEN": token,
        },
    )

    return Client(transport=transport, fetch_schema_from_transport=True)


def make_query(client: Client, query: str, variables: dict | None = None) -> Dict[str, Any]:
    """
    Wrapper to make a GitLab GraphQL query.
    """

    return client.execute(
        gql(query),
        variable_values=variables,
    )


def pickle_and_save(output_pickle_filename: str, groups: Data) -> None:
    """
    Pickles the list of GitLab groups and saves the pickle locally.
    """

    file = open(output_pickle_filename, "wb")
    pickle.dump(groups, file)


def get_value(results: Dict[str, Any], key: str) -> Any:
    """
    Returns the value of key under the groups -> pageInfo keys

    TODO this shouldn't be needed by for some reason is
    """
    return results["groups"]["pageInfo"][key]


def get_groups_and_projects(client: Client, data: Data):
    """Gets the groups and project details.

    Args:
        client (Client): The GitLab client
        data (Data): The data structure that stores all the found GitLab information
    """
    # TODO deal with pagination in each query and make it more seamless than here
    has_next_page = True
    after = ""
    while has_next_page:
        results = make_query(
            client,
            groups_and_projects_query,
            variables={
                "after": after,
            },
        )

        data.groups.nodes += Data(**results).groups.nodes

        if get_value(results, "hasNextPage"):
            after = get_value(results, "endCursor")
        else:
            has_next_page = False


def get_additional_project_details(client: Client, data: Data):
    """Gets additional project details.

    Args:
        client (Client): The GitLab client
        data (Data): The data structure that stores all the found GitLab information
    """
    for group in data.groups.nodes:
        for project in group.projects.nodes:
            project_details = make_query(
                client,
                project_details_query,
                variables={
                    "projectFullPath": f"{project.fullPath}",
                },
            )

            for branch in project_details["project"]["repository"]["branchNames"]:
                project.branches.append(Branch(name=branch))

            for schedule in project_details["project"]["pipelineSchedules"]["edges"]:
                project.pipelineSchedules.append(PipelineSchedule(**schedule["node"]))


def get_additional_branch_details(client: Client, data: Data):
    """Gets additional branch details.

    Args:
        client (Client): The GitLab client
        data (Data): The data structure that stores all the found GitLab information
    """
    for group in data.groups.nodes:
        for project in group.projects.nodes:
            for branch in project.branches:
                branch_details = make_query(
                    client,
                    branch_details_query,
                    variables={
                        "projectFullPath": f"{project.fullPath}",
                        "branchName": branch.name,
                    },
                )

                branch.lastCommit = Commit(**branch_details["project"]["repository"]["tree"]["lastCommit"])


def workflow(output_pickle_filename: str) -> None:
    """
    Workflow for all the relevant calls to connect to the server and save out the data.
    """

    client = create_gitlab_client()
    data = Data()

    # Collect the required data
    get_groups_and_projects(client=client, data=data)
    get_additional_project_details(client=client, data=data)
    get_additional_branch_details(client=client, data=data)

    pickle_and_save(output_pickle_filename, data)
