import os
import re
import sys

import pandas as pd


def extract_departements(html_content):
    return "Very Large Business Applications"


def extract_assigned_courses(html_content):
    return ["Master Informatik", "Fach-Bachelor Wirtschaftsinformatik", "Master Wirtschaftsinformatik"]


data_set_path = "../data-uol-thesis-topics"
db_topics_filename = "db-topics.csv"
db_topics_add_filename = "db-topics-additional.csv"
export_dir_set = set()

print('Starting the import and consolidation of the data set ({}).'.format(data_set_path))
for dirname in os.listdir(data_set_path):
    export_dir_set.add(dirname)

export_dir_set = sorted(export_dir_set)

for export_dir in export_dir_set:
    # Exclude hidden/ system folders
    if export_dir.startswith('.'):
        continue

    print('Iterating over export folder: {}'.format(export_dir))
    db_topics_path = "/".join([data_set_path, export_dir, db_topics_filename])
    db_topics_detail_path = "/".join([data_set_path, export_dir, db_topics_add_filename])

    # Load data from db-topics.csv (see README.md: Step 1)
    try:
        topic_df = pd.read_csv(db_topics_path, sep=";")
    except FileNotFoundError:
        print("The file {} does not exist.".format(db_topics_path))
    except Exception as e:
        print("An error occurred opening the file {}:".format(db_topics_path), e)
        sys.exit()

    # Load data from db-topics-additional.csv (see README.md: Step 1 )
    try:
        topic_detail_df = pd.read_csv(db_topics_detail_path, sep=";")
    except FileNotFoundError:
        print("The file {} does not exist.".format(db_topics_detail_path))
    except Exception as e:
        print("An error occurred opening the file {}:".format(db_topics_detail_path), e)
        sys.exit()

    # Load data from the Thesis Details HTML exports (see README.md: Step 1. E.g. additional/...20210924...html)
    html_detail_path = "/".join([data_set_path, export_dir, "additional"])
    html_detail_filename_set = set()
    for filename in os.listdir(html_detail_path):
        html_detail_filename_set.add(filename)

        # Search <tr>-tags in HTMl Export as two of them contain the needed data fields (Departements, Assigned courses)
        html_detail_file_path = "/".join([html_detail_path, filename])
        with open(html_detail_file_path, "r") as file:
            html = file.read()

            # Use regular expression to find the <tr> tags
            tr_contents = re.findall("<tr>(.*?)</tr>", html, re.DOTALL)

            # The HTML Export contains 14 data fields
            if len(tr_contents) != 14:
                print("14 <tr> tags expected in {}, found: {}".format(filename, len(tr_contents)))

            # <tr> tag 11 is Departements, <tr> tag 12 is Assigned Courses
            departements = extract_departements(tr_contents[10])
            assigned_courses = extract_assigned_courses(tr_contents[11])

    print("Found {} HTML Detail Exports in the folder {}".format(len(html_detail_filename_set), html_detail_path))
