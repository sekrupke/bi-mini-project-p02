import os
import re
import sys
from datetime import datetime

import pandas as pd


def extract_departements(html_table_rows):
    # Search every html table row for "Abteilungen"
    for row in html_table_rows:
        # Check if no departement is given in the row
        found_no_departement = re.findall("<td><strong>Abteilungen</strong></td>.*(Keinen Abteilungen zugewiesen).*", row, re.DOTALL)
        if found_no_departement:
            # print('Found empty departement list in HTML Rows: {}.'.format(found_no_departement))
            return None

        # Check if departements are given in the row (search the list in the HTML)
        found_department_list = re.findall("<td><strong>Abteilungen</strong></td>.*?(<li>.*?)</ul>", row, re.DOTALL)
        if len(found_department_list) == 1:
            found_departements = re.findall("<li>(.*?)</li>", found_department_list[0], re.DOTALL)
            # print('Found the departement(s) in HTML Rows: {}.'.format(found_departements))
            return found_departements

    print('ERROR: Departement list not present in HTML Rows! Exiting.')
    sys.exit()


def extract_assigned_courses(html_table_rows):
    # Search every html table row for "Zugeordnete Veranstaltungen"
    for row in html_table_rows:
        # Check if no assigned course is given in the row
        found_no_courses = re.findall("<td><strong>Zugeordnete Veranstaltungen</strong></td>.*(Keine Veranstaltungen zugewiesen).*", row, re.DOTALL)
        if found_no_courses:
            # print('Found empty assigned courses list in HTML Rows: {}.'.format(found_no_courses))
            return None

        # Check if assigned courses are given in the row (search the list in the HTML)
        found_course_list = re.findall("<td><strong>Zugeordnete Veranstaltungen</strong></td>.*?(<li>.*?)</ul>", row, re.DOTALL)
        if len(found_course_list) == 1:
            found_courses = re.findall("<a.*?>\\s*(.*?)\\s*</a>", found_course_list[0], re.DOTALL)

            # As last step replace special HTML entities (e.g. &quot; or &#039;)
            courses = [course.replace("&quot;", "\"") for course in found_courses]
            courses = [course.replace("&#039;", "'") for course in courses]
            # print('Found the ({}) Assigned Course(s) in HTML Rows: {}.'.format(len(courses), courses))
            return courses

    print('ERROR: Departement list not present in HTML Rows! Exiting.')
    sys.exit()


def clean_contact(contact):
    # As multiple contact persons are seperated with 3 new lines and several whitespaces spaces a Regex is used
    # "Person A\n\n\n           Person B" -> "Person A|Person B"
    return re.sub("\\n{3}\\s+ ", "|", str(contact))


def split_degree_programmes(degree_programmes):
    # The degree programmes must be split because they are not seperated properly and contain irrelevant information
    # "Zugeordnete StudiengängeMaster WirtschaftsinformatikFach-Bachelor InformatikFach-Bachelor Wirtschaftsinformatik"
    # Result: "Master Wirtschaftsinformatik|Fach-Bachelor Informatik|Fach-Bachelor Wirtschaftsinformatik"
    programmes = str(degree_programmes).removeprefix("Zugeordnete Studiengänge")
    programmes = programmes.replace("Fach-Bachelor", "|Fach-Bachelor")
    programmes = programmes.replace("Master", "|Master")
    programmes = programmes.replace("Zwei-Fächer", "|Zwei-Fächer")
    programmes = programmes.removeprefix("|")
    return programmes


def convert_german_date(date):
    # Converts the German date to English date (25.02.2012 -> 2012-02-25)
    created_date = datetime.strptime(str(date), '%d.%m.%Y')
    return datetime.strftime(created_date, '%Y-%m-%d')


data_set_path = "../data-uol-thesis-topics"
db_topics_filename = "db-topics.csv"
db_topics_add_filename = "db-topics-additional.csv"
export_dir_set = set()

print('Starting the import and consolidation of the data set ({}).'.format(data_set_path))
for dirname in os.listdir(data_set_path):
    export_dir_set.add(dirname)

export_dir_set = sorted(export_dir_set)

# Iterate over every export folder in the data set directory
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
        print("Error: The file {} does not exist.".format(db_topics_path))
        sys.exit()
    except Exception as e:
        print("An error occurred opening the file {}:".format(db_topics_path), e)
        sys.exit()

    # Load data from db-topics-additional.csv (see README.md: Step 1 )
    try:
        topic_detail_df = pd.read_csv(db_topics_detail_path, sep=";")
    except FileNotFoundError:
        print("Error: The file {} does not exist.".format(db_topics_detail_path))
        sys.exit()
    except Exception as e:
        print("An error occurred opening the file {}:".format(db_topics_detail_path), e)
        sys.exit()

    # Load data from the Thesis Details HTML exports (see README.md: Step 1. E.g. additional/...20210924...html)
    html_detail_path = "/".join([data_set_path, export_dir, "additional"])
    html_detail_filename_set = set()
    html_details_df = pd.DataFrame(columns=['topic_id', 'departements', 'assigned_courses'])
    for filename in os.listdir(html_detail_path):
        html_detail_filename_set.add(filename)

        # Search <tr>-tags in HTMl Export as two of them contain the needed data fields (Departements, Assigned courses)
        html_detail_file_path = "/".join([html_detail_path, filename])
        with open(html_detail_file_path, "r") as file:
            html = file.read()

            # Use regular expression to find the <tr> tags
            tr_contents = re.findall("<tr>(.*?)</tr>", html, re.DOTALL)

            # Extract the Departements and Assigned Courses from <tr> tags
            departements = extract_departements(tr_contents)
            assigned_courses = extract_assigned_courses(tr_contents)

            # Extract the topic_id of the Detail HTML export (in the filename)
            split_path = filename.split("_")
            topic_id = None
            if len(split_path) == 2:
                topic_id = split_path[0]
            else:
                print("Error: No topic_id in Detail HTML export filename found: {}".format(filename))
                sys.exit()

            # Add the topic_id, Departements and Assigned Courses to the Dataframe
            df = pd.DataFrame({"topic_id": [topic_id], "departements": [departements], "assigned_courses": [assigned_courses]})
            html_details_df = pd.concat([html_details_df, df], ignore_index=True)

    # Consolidate the three data sources (db-topics, db-topics-additional, HTML-Export) from the export_dir
    # Remove unnecessary columns from Dataframes db-topics and db-topics-additional
    topic_df.drop('action', axis=1, inplace=True)
    topic_detail_df.drop('titel', axis=1, inplace=True)
    topic_detail_df.drop('art_der_arbeit', axis=1, inplace=True)
    topic_detail_df.drop('abschlussarbeitstyp', axis=1, inplace=True)
    topic_detail_df.drop('status', axis=1, inplace=True)
    topic_detail_df.drop('erstellt', axis=1, inplace=True)

    # Transformations in the Dataframes
    # Cleanup and split Contact person (there could be multiple)
    topic_df['ansprechpartner'] = topic_df['ansprechpartner'].apply(lambda x: clean_contact(x))
    # Split Degree Programmes
    topic_df['studiengaenge'] = topic_df['studiengaenge'].apply(lambda x: split_degree_programmes(x))
    # Convert Created Date to English date format
    topic_df['erstellt'] = topic_df['erstellt'].apply(lambda x: convert_german_date(x))

    # Merge the Dataframes topic_df and topic_detail_df on the topic_id
    topic_detail_merged_df = pd.merge(topic_df, topic_detail_df, how='inner', on='topic_id')
    # Merge the resulting Dataframe with the html_details_df
    merged_df = pd.merge(topic_detail_merged_df, html_details_df, how='inner', on='topic_id')

    # Check if the merge was successful
    #topic_df.to_csv('topic_out.csv', index=False, encoding='utf-8', sep=';')
    #topic_detail_df.to_csv('topic_detail_out.csv', index=False, encoding='utf-8', sep=';')
    #html_details_df.to_csv('html_details_out.csv', index=False, encoding='utf-8', sep=';')
    #merged_df.to_csv('merged_out.csv', index=False, encoding='utf-8', sep=';')
    print("Topics found: db-topics: {}, db-topics-additional: {}, HTML Detail Export: {} -> Merged: {}"
          .format(len(topic_df.index), len(topic_detail_df.index), len(html_details_df.index), len(merged_df.index)))
    if not (len(topic_df.index) == len(topic_detail_df.index) == len(html_details_df.index) == len(merged_df.index)):
        print("Error: Number of topics in consolidation Dataframes differ!")
        sys.exit()

    #sys.exit()

print("Import and consolidation of the data set finished.")
