"""Types for GitLab items."""

from typing import List
from pydantic import BaseModel


class User(BaseModel):
    """GitLab User."""

    id: str
    username: str
    publicEmail: str | None = ""
    state: str


class PipelineSchedule(BaseModel):
    """GitLab Pipeline Schedule."""

    id: str
    description: str
    active: bool
    nextRunAt: str
    owner: User


class Commit(BaseModel):
    """GitLab Commit."""

    title: str
    authoredDate: str
    authorName: str


class Branch(BaseModel):
    """GitLab Branch."""

    name: str
    lastCommit: Commit = Commit(title="", authoredDate="", authorName="")


class RepositoryDetails(BaseModel):
    """Repository details"""

    rootRef: str


class Project(BaseModel):
    """GitLab Project."""

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
    """GitLab Projects."""

    nodes: List[Project] = []


class Group(BaseModel):
    """GitLab Project Group."""

    id: str
    name: str
    fullName: str
    fullPath: str
    description: str
    projects: Projects = Projects()


class Groups(BaseModel):
    """GitLab Groups"""

    nodes: List[Group] = []


class Data(BaseModel):
    """List of GitLab Project Groups."""

    groups: Groups = Groups()
