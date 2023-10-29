"""
Types for GitLab items.
"""

from typing import List
from pydantic import BaseModel


class User(BaseModel):
    """
    Type for a GitLab User.
    """

    id: str
    username: str
    publicEmail: str | None = ""
    state: str


class PipelineSchedule(BaseModel):
    """
    Type for a GitLab Pipeline Schedule.
    """

    id: str
    description: str
    active: bool
    nextRunAt: str
    owner: User


class Commit(BaseModel):
    """
    Type for a GitLab Commit.
    """

    title: str
    authoredDate: str
    authorName: str


class Branch(BaseModel):
    """
    Type for a GitLab Branch.
    """

    name: str
    lastCommit: Commit = Commit(title="", authoredDate="", authorName="")


class RepositoryDetails(BaseModel):
    rootRef: str


class Project(BaseModel):
    """
    Type for a GitLab Project.
    """

    id: str
    name: str
    description: str | None = ""
    fullPath: str
    repository: RepositoryDetails
    # TODO computed branch that points to this for primary_branch?

    # Custom components
    branches: List[Branch] = []
    pipelineSchedules: List[PipelineSchedule] = []


class Projects(BaseModel):
    nodes: List[Project] = []


class Group(BaseModel):
    """
    Type for a GitLab Project Group.
    """

    id: str
    name: str
    fullName: str
    fullPath: str
    description: str
    projects: Projects = Projects()


class Groups(BaseModel):
    nodes: List[Group] = []


class Data(BaseModel):
    """
    Type for a list of GitLab Project Groups.
    """

    groups: Groups = Groups()
