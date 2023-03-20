from engine.configuration import Branch, Commit, Group, Project
import pickle
import os
import csv


def create_csv_output(input_pickle_file: str, output_csv_filename: str):
    try:
        file = open(input_pickle_file, "rb")
        groups = pickle.load(file)

        with open(output_csv_filename, "w") as csvfile:
            csv_writer = csv.writer(csvfile)

            for group in groups:
                for row in group.get_branch_details_csv_array():
                    csv_writer.writerow(row)
    except Exception as e:
        print(f"There has been an exception of: {e}")
