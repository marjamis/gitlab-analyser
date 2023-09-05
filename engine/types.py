"""
Types for GitLab items.
"""

from typing import List


class User:
    """
    Type for a GitLab User.
    """

    def __init__(self, user_id: str, username: str, public_email: str, state: str) -> None:
        self.id = user_id
        self.username = username
        self.public_email = public_email
        self.state = state


class PipelineSchedule:
    """
    Type for a GitLab Pipeline Schedule.
    """

    def __init__(
        self, pipeline_schedule_id: str, description: str, active: bool, next_run_at: str, owner: User
    ) -> None:
        self.id = pipeline_schedule_id
        self.description = description
        self.active = active
        self.next_run_at = next_run_at
        self.owner = owner


class Commit:
    """
    Type for a GitLab Commit.
    """

    def __init__(self, title: str, authored_date: str, author_name: str) -> None:
        self.title = title
        self.authored_date = authored_date
        self.author_name = author_name


class Branch:
    """
    Type for a GitLab Branch.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.last_commit = None

    def set_last_commit(self, last_commit: Commit) -> None:
        """
        Sets the last commit of a branch.
        """

        self.last_commit = last_commit

    def get_last_commit(self) -> Commit | None:
        """
        Gets the last commit of a branch.
        """

        return self.last_commit


class Project:
    """
    Type for a GitLab Project.
    """

    def __init__(self, project_id: str, name: str, full_path: str, description, primary_branch: str) -> None:
        self.id = project_id
        self.name = name
        self.full_path = full_path
        self.description = description
        self.primary_branch = primary_branch
        self.branches = []
        self.pipeline_schedules = []

    def add_branch(self, branch: Branch) -> None:
        """
        Adds a branch for a project.
        """

        self.branches.append(branch)

    def add_pipeline_schedule(self, pipeline_schedule: PipelineSchedule) -> None:
        """
        Adds a pipeline schedule for a project.
        """

        self.pipeline_schedules.append(pipeline_schedule)

    def get_branches(self) -> List[Branch]:
        """
        Gets the branches of a project.
        """

        return self.branches

    def get_pipeline_schedules(self) -> List[PipelineSchedule]:
        """
        Gets the pipeline schedules of a project.
        """

        return self.pipeline_schedules


class Group:
    """
    Type for a GitLab Project Group.
    """

    def __init__(self, group_id: str, name: str, full_name: str, full_path: str, description: str) -> None:
        self.id = group_id
        self.name = name
        self.full_name = full_name
        self.full_path = full_path
        self.description = description
        self.projects = []

    def add_project(self, project: Project) -> None:
        """
        Adds a project to a group.
        """

        self.projects.append(project)

    def get_projects(self) -> List[Project]:
        """
        Gets the projects of a group.
        """

        return self.projects
