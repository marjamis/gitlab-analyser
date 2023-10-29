"""
Processes the provided files and generates CSV outputs.
"""

import pickle
import csv
import os

from typing import List

from engine.types import Data


def get_csv_rows_projects(data: Data) -> List[List[str]]:
    """
    Generates the CSV rows for projects across all the provided GitLab groups.
    """

    project_details = [
        [
            "Group Name",
            "Project Name",
            "Primary Branch Name",
        ]
    ]

    for group in data.groups.nodes:
        for project in group.projects.nodes:
            project_details.append(
                [
                    group.name,
                    project.name,
                    project.repository.rootRef,
                ]
            )

    return project_details


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

    for group in data.groups.nodes:
        for project in group.projects.nodes:
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

    for group in data.groups.nodes:
        for project in group.projects.nodes:
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
                        str(pipeline_schedule.owner.publicEmail),
                        pipeline_schedule.owner.state,
                    ]
                )

    return pipeline_schedule_details


def create_csv_outputs(
    input_pickle_file: str,
    output_directory: str,
) -> None:
    """
    Creates CSV outputs from the supplied pickled data.
    """

    try:
        file = open(input_pickle_file, "rb")
        groups = pickle.load(file)

        outputs = [
            ("branches.csv", get_csv_rows_branches),
            ("schedules.csv", get_csv_rows_pipeline_schedules),
            ("projects.csv", get_csv_rows_projects),
        ]

        for output in outputs:
            print(f"Saving csv for: {output[0]}")
            with open(os.path.join(output_directory, output[0]), "w", encoding="utf-8") as csv_file:
                csv_writer = csv.writer(csv_file)

                for row in output[1](groups):
                    csv_writer.writerow(row)

    except Exception as e:
        print(f"There has been an exception of: {e}")
