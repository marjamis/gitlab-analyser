from typing import List


class User:
    def __init__(self, id: str, username: str, public_email: str, state: str) -> None:
        self.id = id
        self.username = username
        self.public_email = public_email
        self.state = state


class PipelineSchedule:
    def __init__(self, id: str, description: str, active: bool, next_run_at: str, owner: User) -> None:
        self.id = id
        self.description = description
        self.active = active
        self.next_run_at = next_run_at
        self.owner = owner


class Commit:
    def __init__(self, title: str, authored_date: str, author_name: str) -> None:
        self.title = title
        self.authored_date = authored_date
        self.author_name = author_name


class Branch:
    def __init__(self, name: str) -> None:
        self.name = name
        self.last_commit = None

    def set_last_commit(self, last_commit: Commit) -> None:
        self.last_commit = last_commit

    def get_last_commit(self) -> Commit:
        return self.last_commit


class Project:
    def __init__(
        self, id: str, name: str, full_path: str, description, primary_branch: str
    ) -> None:
        self.id = id
        self.name = name
        self.full_path = full_path
        self.description = description
        self.primary_branch = primary_branch
        self.branches = []
        self.pipeline_schedules = []

    def add_branch(self, branch: Branch) -> None:
        self.branches.append(branch)

    def add_pipeline_schedule(self, pipeline_schedule: PipelineSchedule) -> None:
        self.pipeline_schedules.append(pipeline_schedule)

    def get_branches(self) -> List[Branch]:
        return self.branches

    def get_pipeline_schedules(self) -> List[PipelineSchedule]:
        return self.pipeline_schedules


class Group:
    def __init__(
        self, id: str, name: str, full_name: str, full_path: str, description: str
    ) -> None:
        self.id = id
        self.name = name
        self.full_name = full_name
        self.full_path = full_path
        self.description = description
        self.projects = []

    def add_project(self, project: Project) -> None:
        self.projects.append(project)

    def get_projects(self) -> List[Project]:
        return self.projects
