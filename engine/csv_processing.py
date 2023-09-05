"""
Processes the provided files and generates CSV outputs.
"""

import pickle
import csv

from typing import List

from engine.types import Data


def get_csv_rows_branches(data: Data) -> List[List[str]]:
    """
    Generates the CSV rows for branches across all the provided GitLab groups.
    """

    branch_details = [
        [
            "Group Name",
            "Project Name",
            "Branch Name",
            "Last Commit Title",
            "Last Commit Authored Date",
            "Last Commit Author",
        ]
    ]

    for group in data.groups:
        for project in group.group_projects:
            for branch in project.branches:
                branch_details.append(
                    [
                        group.name,
                        project.name,
                        branch.name,
                        branch.lastCommit.title,
                        branch.lastCommit.authoredDate,
                        branch.lastCommit.authorName,
                    ]
                )

    return branch_details


def get_csv_rows_pipeline_schedules(data: Data) -> List[List[str]]:
    """
    Generates the CSV rows for pipeline schedules across all the provided GitLab groups.
    """

    pipeline_schedule_details = [
        [
            "Group Name",
            "Project Name",
            "Pipeline Schedule Id",
            "Pipeline Schedule Description",
            "Pipeline Schedule Is Active?",
            "Pipeline Schedule Next Run At",
            "Pipeline Schedule Owner Id",
            "Pipeline Schedule Owner Username",
            "Pipeline Schedule Owner Public Email",
            "Pipeline Schedule Owner State",
        ]
    ]

    for group in data.groups:
        for project in group.group_projects:
            for pipeline_schedule in project.pipelineSchedules:
                pipeline_schedule_details.append(
                    [
                        group.name,
                        project.name,
                        pipeline_schedule.id,
                        pipeline_schedule.description,
                        str(pipeline_schedule.active),
                        pipeline_schedule.nextRunAt,
                        pipeline_schedule.owner.id,
                        pipeline_schedule.owner.username,
                        pipeline_schedule.owner.publicEmail,
                        pipeline_schedule.owner.state,
                    ]
                )

    return pipeline_schedule_details


def create_csv_outputs(
    input_pickle_file: str, branches_csv: str | None = None, pipeline_schedules_csv: str | None = None
) -> None:
    """
    Creates CSV outputs from the supplied file/s.
    """

    try:
        file = open(input_pickle_file, "rb")
        groups = pickle.load(file)

        if branches_csv is not None:
            with open(branches_csv, "w") as csv_file:
                csv_writer = csv.writer(csv_file)

                for row in get_csv_rows_branches(groups):
                    csv_writer.writerow(row)

        if pipeline_schedules_csv is not None:
            with open(pipeline_schedules_csv, "w") as csv_file:
                csv_writer = csv.writer(csv_file)

                for row in get_csv_rows_pipeline_schedules(groups):
                    csv_writer.writerow(row)

    except Exception as e:
        print(f"There has been an exception of: {e}")
