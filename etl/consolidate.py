import os
import re
import sys

import pandas as pd


def extract_departements(html_table_rows):
    extraction_succeeded = False

    # Search every html table row for "Abteilungen"
    for row in html_table_rows:
        # Check if no departement is given in the row
        found_no_departement = re.findall("<td><strong>Abteilungen</strong></td>.*(Keinen Abteilungen zugewiesen).*", row, re.DOTALL)
        if found_no_departement:
            print('Found empty departement list in HTML Rows: {}.'.format(found_no_departement))
            extraction_succeeded = True
            return None

        # Check if departements are given in the row (search the list in the HTML)
        found_department_list = re.findall("<td><strong>Abteilungen</strong></td>.*?(<li>.*?)</ul>", row, re.DOTALL)
        if len(found_department_list) == 1:
            found_departements = re.findall("<li>(.*?)</li>", found_department_list[0], re.DOTALL)
            print('Found the departement(s) in HTML Rows: {}.'.format(found_departements))
            extraction_succeeded = True
            return found_departements

    if not extraction_succeeded:
        print('ERROR: Departement list not present in HTML Rows!')
        return None


def extract_assigned_courses(html_table_rows):
    extraction_succeeded = False

    # Search every html table row for "Zugeordnete Veranstaltungen"
    for row in html_table_rows:
        # Check if no assigned course is given in the row
        found_no_courses = re.findall("<td><strong>Zugeordnete Veranstaltungen</strong></td>.*(Keine Veranstaltungen zugewiesen).*", row, re.DOTALL)
        if found_no_courses:
            print('Found empty departement list in HTML Rows: {}.'.format(found_no_courses))
            extraction_succeeded = True
            return None

        # Check if assigned courses are given in the row (search the list in the HTML)
        found_course_list = re.findall("<td><strong>Zugeordnete Veranstaltungen</strong></td>.*?(<li>.*?)</ul>", row, re.DOTALL)
        if len(found_course_list) == 1:
            found_courses = re.findall("<a.*?>\\s*(.*?)\\s*</a>", found_course_list[0], re.DOTALL)

            # Replace special HTML entities (e.g. &quot;)
            courses = [course.replace("&quot;", "\"") for course in found_courses]
            print('Found the ({}) Assigned Courses(s) in HTML Rows: {}.'.format(len(courses), courses))
            extraction_succeeded = True
            return courses

    if not extraction_succeeded:
        print('ERROR: Assigned Courses list not present in HTML Rows!')
        return None


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
            departements = extract_departements(tr_contents)
            assigned_courses = extract_assigned_courses(tr_contents)

    print("Found {} HTML Detail Exports in the folder {}".format(len(html_detail_filename_set), html_detail_path))
