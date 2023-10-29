"""
Gets data from GitLab and produces objects with the data.
"""

import pickle
import os
from typing import Dict, Any, Tuple

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

from engine.types import Branch, Commit, Data, PipelineSchedule

groups_and_projects_query = open("queries/groups_and_projects.gql", "r", encoding="utf-8").read()
project_details_query = open("queries/project_details.gql", "r", encoding="utf-8").read()
branch_details_query = open("queries/branch_details.gql", "r", encoding="utf-8").read()


class MissingEnvironmentVariable(Exception):
    def __init__(self, *args):
        super().__init__(args)


def create_gitlab_client() -> Client:
    """
    Creates a GitLab GraphQL Client.
    """

    url = os.getenv("GITLAB_GRAPHQL_ENDPOINT")
    if url is None:
        raise MissingEnvironmentVariable("GITLAB_GRAPHQL_ENDPOINT environment variable not specified")
    token = os.getenv("GITLAB_TOKEN")
    if token is None:
        raise MissingEnvironmentVariable("GITLAB_TOKEN environment variable not specified")

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


def pager(results: Dict[str, Any], query_type: str) -> Tuple[bool, str]:
    """A pager for the GitLab GraphQL queries. returns if there is another page, and if so what the continuation token
    is.

    Args:
        results (Dict[str, Any]): The data dictionary returned by the graphql client
        query_type (str): The type of graphql query that is being made

    Returns:
        Tuple[bool, str]: _description_
    """
    try:
        page_info = results[query_type]["pageInfo"]
    except KeyError:
        return (False, "")

    has_next_page = False
    after = ""

    if page_info.get("hasNextPage"):
        after = page_info.get("endCursor")
        has_next_page = True

    return (has_next_page, after)


def pickle_and_save(output_pickle_filename: str, groups: Data) -> None:
    """
    Pickles the list of GitLab groups and saves the pickle locally.
    """

    file = open(output_pickle_filename, "wb")
    pickle.dump(groups, file)


def get_groups_and_projects(client: Client, data: Data):
    """Gets the groups and project details.

    Args:
        client (Client): The GitLab client
        data (Data): The data structure that stores all the found GitLab information
    """
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

        has_next_page, after = pager(results, "groups")


def get_additional_project_details(client: Client, data: Data):
    """Gets additional project details.

    Args:
        client (Client): The GitLab client
        data (Data): The data structure that stores all the found GitLab information
    """
    for group in data.groups.nodes:
        for project in group.projects.nodes:
            has_next_page = True
            after = ""
            while has_next_page:
                project_details = make_query(
                    client,
                    project_details_query,
                    variables={
                        "projectFullPath": f"{project.fullPath}",
                        "after": after,
                    },
                )

                for branch in project_details["project"]["repository"]["branchNames"]:
                    project.branches.append(Branch(name=branch))

                for schedule in project_details["project"]["pipelineSchedules"]["edges"]:
                    project.pipelineSchedules.append(PipelineSchedule(**schedule["node"]))

                has_next_page, after = pager(project_details, "project")


def get_additional_branch_details(client: Client, data: Data):
    """Gets additional branch details.

    Args:
        client (Client): The GitLab client
        data (Data): The data structure that stores all the found GitLab information
    """
    for group in data.groups.nodes:
        for project in group.projects.nodes:
            for branch in project.branches:
                has_next_page = True
                after = ""
                while has_next_page:
                    branch_details = make_query(
                        client,
                        branch_details_query,
                        variables={
                            "projectFullPath": f"{project.fullPath}",
                            "branchName": branch.name,
                            "after": after,
                        },
                    )

                    branch.lastCommit = Commit(**branch_details["project"]["repository"]["tree"]["lastCommit"])

                    has_next_page, after = pager(branch_details, "project")


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
