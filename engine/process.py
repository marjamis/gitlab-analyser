from engine.configuration import Branch, Commit, Group, Project
import pickle
import os
import csv


def get_csv_rows(groups) -> None:
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

    for group in groups:
        for project in group.get_projects():
            for branch in project.get_branches():
                last_commit = branch.get_last_commit()
                branch_details.append(
                    [
                        group.name,
                        project.name,
                        branch.name,
                        last_commit.title,
                        last_commit.authored_date,
                        last_commit.author_name,
                    ]
                )

    return branch_details


def create_csv_output(input_pickle_file: str, output_csv_filename: str):
    try:
        file = open(input_pickle_file, "rb")
        groups = pickle.load(file)

        with open(output_csv_filename, "w") as csv_file:
            csv_writer = csv.writer(csv_file)

            for row in get_csv_rows(groups):
                csv_writer.writerow(row)

    except Exception as e:
        print(f"There has been an exception of: {e}")
