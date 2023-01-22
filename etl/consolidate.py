import os
import re
import sys
from datetime import datetime

import pandas as pd
import psycopg2

from id_generator import PersonId

# Use sets for md5 hash values of already inserted rows in hubs, satellites and links
hub_title_cache = set()
hub_detail_cache = set()
hub_programm_cache = set()
hub_contact_author_cache = set()
hub_departement_cache = set()
hub_course_cache = set()
sat_thesis_cache = set()
sat_detail_cache = set()
sat_person_cache = set()
lnk_thesis_details_cache = set()
lnk_thesis_degree_programm_cache = set()
lnk_thesis_contact_cache = set()
lnk_detail_author_cache = set()
lnk_detail_departement_cache = set()
lnk_detail_course_cache = set()


def extract_departements(html_table_rows):
    # Search every html table row for "Abteilungen"
    for row in html_table_rows:
        # Check if no departement is given in the row
        found_no_departement = re.findall("<td><strong>Abteilungen</strong></td>.*(Keinen Abteilungen zugewiesen).*",
                                          row, re.DOTALL)
        if found_no_departement:
            # print('Found empty departement list in HTML Rows: {}.'.format(found_no_departement))
            return None

        # Check if departements are given in the row (search the list in the HTML)
        found_department_list = re.findall("<td><strong>Abteilungen</strong></td>.*?(<li>.*?)</ul>", row, re.DOTALL)
        if len(found_department_list) == 1:
            found_departements = re.findall("<li>(.*?)</li>", found_department_list[0], re.DOTALL)
            # Return the found departements seperated by "|"
            return "|".join(found_departements)

    print('ERROR: Departement list not present in HTML Rows! Exiting.')
    sys.exit()


def extract_assigned_courses(html_table_rows):
    # Search every html table row for "Zugeordnete Veranstaltungen"
    for row in html_table_rows:
        # Check if no assigned course is given in the row
        found_no_courses = re.findall(
            "<td><strong>Zugeordnete Veranstaltungen</strong></td>.*(Keine Veranstaltungen zugewiesen).*", row,
            re.DOTALL)
        if found_no_courses:
            # print('Found empty assigned courses list in HTML Rows: {}.'.format(found_no_courses))
            return None

        # Check if assigned courses are given in the row (search the list in the HTML)
        found_course_list = re.findall("<td><strong>Zugeordnete Veranstaltungen</strong></td>.*?(<li>.*?)</ul>", row,
                                       re.DOTALL)
        if len(found_course_list) == 1:
            found_courses = re.findall("<a.*?>\\s*(.*?)\\s*</a>", found_course_list[0], re.DOTALL)

            # As last step replace special HTML entities (e.g. &quot; or &#039;)
            courses = [course.replace("&quot;", "\"") for course in found_courses]
            courses = [course.replace("&#039;", "'") for course in courses]

            # Return the found courses seperated by "|"
            return "|".join(courses)

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


def md5(business_key):
    # Hashes the Business Key column(s) with MD5
    import hashlib
    return hashlib.md5(business_key.encode()).hexdigest()


def md5_columns(*columns):
    # Hashes the descriptive column(s) with MD5
    import hashlib
    concat_columns = ''.join(value for value in columns)
    return hashlib.md5(concat_columns.encode()).hexdigest()


def generate_person_id():
    return str(PersonId().id)


def insert_into_db(sql_command, *parameters):
    conn = None
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="thesis",
            user="thesis_user",
            password="aB2Ck91mN0LeA")

        # create a cursor
        cursor = conn.cursor()
        cursor.execute(sql_command, *parameters)
        conn.commit()

        # close the communication with the PostgreSQL
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error accessing database: {}".format(error))
    finally:
        if conn is not None:
            conn.close()


def load_data_into_db(thesis_df, load_date):
    for thesis in thesis_df.itertuples(index=False):

        # Insert the thesis (hub_thesis)
        thesis_title = str(thesis[0])
        if md5(thesis_title) not in hub_title_cache:
            insert_into_db("INSERT INTO hub_thesis VALUES (%s, %s, %s, %s);",
                           (md5(thesis_title), thesis_title, load_date, 'DigiDigger'))
            hub_title_cache.add(md5(thesis_title))

        # Insert the thesis satellite (sat_thesis)
        thesis_type = str(thesis[1])
        thesis_work_type = str(thesis[3])
        thesis_status = str(thesis[5])
        thesis_created = str(thesis[6])
        thesis_id = str(thesis[7])
        hash_diff = md5_columns(thesis_type, thesis_work_type, thesis_status, thesis_created, thesis_id)
        if hash_diff not in sat_thesis_cache:
            insert_into_db("INSERT INTO sat_thesis VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
                           (md5(thesis_title), load_date, hash_diff, 'DigiDigger', thesis_type, thesis_work_type,
                            thesis_status, thesis_created, thesis_id))
            sat_thesis_cache.add(hash_diff)

        # Insert the thesis detail (hub_detail)
        thesis_detail = str(thesis[7])
        if md5(thesis_detail) not in hub_detail_cache:
            insert_into_db("INSERT INTO hub_detail VALUES (%s, %s, %s, %s);",
                           (md5(thesis_detail), thesis_detail, load_date, 'DigiDigger'))
            hub_detail_cache.add(md5(thesis_detail))

        # Insert the thesis detail satellite (sat_details)
        thesis_description = str(thesis[9])
        thesis_institution = str(thesis[10])
        thesis_problem = str(thesis[12])
        thesis_requirement = str(thesis[13])
        thesis_url = str(thesis[8])
        hash_diff = md5_columns(thesis_description, thesis_institution, thesis_problem, thesis_requirement, thesis_url)
        if hash_diff not in sat_detail_cache:
            insert_into_db("INSERT INTO sat_details VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
                           (md5(thesis_detail), load_date, hash_diff, 'DigiDigger', thesis_description,
                            thesis_institution, thesis_problem, thesis_requirement, thesis_url))
            sat_detail_cache.add(hash_diff)

        # Insert the thesis detail link (lnk_thesis_details)
        thesis_details_key = md5_columns(thesis_title, thesis_id)
        if thesis_details_key not in lnk_thesis_details_cache:
            hub_thesis_key = md5(thesis_title)
            hub_details_key = md5(thesis_id)
            insert_into_db("INSERT INTO lnk_thesis_details VALUES (%s, %s, %s, %s, %s);",
                          (thesis_details_key, hub_thesis_key, hub_details_key, load_date, 'DigiDigger'))
            lnk_thesis_details_cache.add(thesis_details_key)

        # Insert the degree programmes (hub_degree_programm)
        thesis_programmes = str(thesis[2]).split('|')
        for thesis_programm in thesis_programmes:
            if md5(thesis_programm) not in hub_programm_cache:
                insert_into_db("INSERT INTO hub_degree_programm VALUES (%s, %s, %s, %s);",
                               (md5(thesis_programm), thesis_programm, load_date, 'DigiDigger'))
                hub_programm_cache.add(md5(thesis_programm))

            # Insert the thesis degree programm link (lnk_thesis_degree_programm)
            detail_course_key = md5_columns(thesis_title, thesis_programm)
            if detail_course_key not in lnk_detail_course_cache:
                hub_thesis_key = md5(thesis_title)
                hub_degree_key = md5(thesis_programm)
                insert_into_db("INSERT INTO lnk_thesis_degree_programm VALUES (%s, %s, %s, %s, %s);",
                            (detail_course_key, hub_thesis_key, hub_degree_key, load_date, 'DigiDigger'))
                lnk_detail_course_cache.add(detail_course_key)

        # Insert the contact persons (hub_person)
        thesis_contacts = str(thesis[4]).split('|')
        for thesis_contact in thesis_contacts:
            # Check if the contact persons name is not yet in the database
            person_id = generate_person_id()
            if md5(thesis_contact) not in hub_contact_author_cache:
                insert_into_db("INSERT INTO hub_person VALUES (%s, %s, %s, %s);",
                    (md5(person_id), person_id, load_date, 'DigiDigger'))
                hub_contact_author_cache.add(md5(person_id))

            # Insert the thesis contact link (lnk_thesis_contact)
            thesis_contact_key = md5_columns(thesis_title, person_id)
            if thesis_contact_key not in lnk_thesis_contact_cache:
                hub_thesis_key = md5(thesis_title)
                hub_person_key = md5(person_id)
                insert_into_db("INSERT INTO lnk_thesis_contact VALUES (%s, %s, %s, %s, %s);",
                               (thesis_contact_key, hub_thesis_key, hub_person_key, load_date, 'DigiDigger'))
                lnk_thesis_contact_cache.add(thesis_contact_key)

        # Insert the author (hub_person)
        thesis_author = str(thesis[11])
        # Check if the authors name is not yet in the database
        person_id = generate_person_id()
        if md5(thesis_author) not in hub_contact_author_cache:
            insert_into_db("INSERT INTO hub_person VALUES (%s, %s, %s, %s);",
                           (md5(thesis_author), person_id, load_date, 'DigiDigger'))
            hub_contact_author_cache.add(md5(thesis_author))

        # Insert the detail author link (lnk_detail_author)
        detail_author_key = md5_columns(thesis_id, person_id)
        if detail_author_key not in lnk_detail_author_cache:
            hub_details_key = md5(thesis_id)
            hub_person_key = md5(person_id)
            insert_into_db("INSERT INTO lnk_detail_author VALUES (%s, %s, %s, %s, %s);",
                           (detail_author_key, hub_details_key, hub_person_key, load_date, 'DigiDigger'))
            lnk_detail_author_cache.add(detail_author_key)

        # Insert the person satellite (sat_person)
        thesis_author = str(thesis[4])
        hash_diff = md5(thesis_author)
        if hash_diff not in sat_person_cache:
            insert_into_db("INSERT INTO sat_person VALUES (%s, %s, %s, %s, %s);",
                           (md5(thesis_author), load_date, hash_diff, 'DigiDigger', thesis_author))
            sat_person_cache.add(hash_diff)
        thesis_contacts = str(thesis[11])
        for thesis_contact in thesis_contacts:
            hash_diff = md5(thesis_contact)
            if hash_diff not in sat_person_cache:
                insert_into_db("INSERT INTO sat_person VALUES (%s, %s, %s, %s, %s);",
                               (md5(thesis_contact), load_date, hash_diff, 'DigiDigger', thesis_contact))
                sat_person_cache.add(hash_diff)

        # Insert the departements (hub_departement)
        thesis_departements = str(thesis[14]).split('|')
        for thesis_departement in thesis_departements:
            if md5(thesis_departement) not in hub_departement_cache and thesis_departement != "None":
                insert_into_db("INSERT INTO hub_departement VALUES (%s, %s, %s, %s);",
                               (md5(thesis_departement), thesis_departement, load_date, 'DigiDigger'))
                hub_departement_cache.add(md5(thesis_departement))

            # Insert the detail departement link (lnk_detail_departement)
            detail_departement_key = md5_columns(thesis_id, thesis_departement)
            if detail_departement_key not in lnk_detail_departement_cache:
                hub_details_key = md5(thesis_id)
                hub_departement_key = md5(thesis_departement)
                insert_into_db("INSERT INTO lnk_detail_departement VALUES (%s, %s, %s, %s, %s);",
                               (detail_departement_key, hub_details_key, hub_departement_key, load_date, 'DigiDigger'))
                lnk_detail_departement_cache.add(detail_departement_key)

        # Insert the assigned courses (hub_course)
        thesis_courses = str(thesis[15]).split('|')
        for thesis_course in thesis_courses:
            if md5(thesis_course) not in hub_course_cache and thesis_course != "None":
                insert_into_db("INSERT INTO hub_course VALUES (%s, %s, %s, %s);",
                               (md5(thesis_course), thesis_course, load_date, 'DigiDigger'))
                hub_course_cache.add(md5(thesis_course))

            # Insert the detail course link (lnk_detail_course)
            detail_course_key = md5_columns(thesis_id, thesis_course)
            if detail_course_key not in lnk_detail_course_cache:
                hub_details_key = md5(thesis_id)
                hub_course_key = md5(thesis_course)
                insert_into_db("INSERT INTO lnk_detail_course VALUES (%s, %s, %s, %s, %s);",
                               (detail_course_key, hub_details_key, hub_course_key, load_date, 'DigiDigger'))
                lnk_detail_course_cache.add(detail_course_key)


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
            df = pd.DataFrame(
                {"topic_id": [topic_id], "departements": [departements], "assigned_courses": [assigned_courses]})
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
    print("Topics found: db-topics: {}, db-topics-additional: {}, HTML Detail Export: {} -> Merged: {}"
          .format(len(topic_df.index), len(topic_detail_df.index), len(html_details_df.index), len(merged_df.index)))
    if not (len(topic_df.index) == len(topic_detail_df.index) == len(html_details_df.index) == len(merged_df.index)):
        print("Error: Number of topics in consolidation Dataframes differ!")
        sys.exit()

    # Change the German Dataframe column names to English language
    merged_df.rename(columns={'titel': 'title',
                              'abschlussarbeitstyp': 'type_of_thesis',
                              'studiengaenge': 'degree_programmes',
                              'art_der_arbeit': 'type_of_work',
                              'ansprechpartner': 'contact_person',
                              'status': 'status',
                              'erstellt': 'created',
                              'beschreibung': 'description',
                              'heimateinrichtung': 'home_institution',
                              'autor': 'author',
                              'aufgabenstellung': 'problem_statement',
                              'voraussetzung': 'requirement'},
                     inplace=True, errors='raise')
    merged_df.to_csv('merged_out.csv', index=False, encoding='utf-8', sep=';')

    # After merging insert the data into the database with the load date (date of export dir)
    export_date = "{}-{}-{}".format(export_dir[:4], export_dir[4:6], export_dir[6:8])
    load_data_into_db(merged_df, export_date)

    sys.exit()

print("Import and consolidation of the data set finished.")
