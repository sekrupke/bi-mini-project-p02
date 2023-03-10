import os
import re
import sys
from datetime import datetime

import pandas as pd
import psycopg2

from id_generator import PersonId

# Database connection parameters
LOCALHOST = "localhost"
PORT = "5432"
DATABASE = "thesis"
USER = "thesis_user"
PASSWORD = "aB2Ck91mN0LeA"


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
    # "Zugeordnete Studieng??ngeMaster WirtschaftsinformatikFach-Bachelor InformatikFach-Bachelor Wirtschaftsinformatik"
    # Result: "Master Wirtschaftsinformatik|Fach-Bachelor Informatik|Fach-Bachelor Wirtschaftsinformatik"
    programmes = str(degree_programmes).removeprefix("Zugeordnete Studieng??nge")
    programmes = programmes.replace("Fach-Bachelor", "|Fach-Bachelor")
    programmes = programmes.replace("Master", "|Master")
    programmes = programmes.replace("Zwei-F??cher", "|Zwei-F??cher")
    programmes = programmes.replace("Staatsexamen", "|Staatsexamen")
    programmes = programmes.replace("Betriebswirtschaftslehre (berufsbegleitend)",
                                    "|Betriebswirtschaftslehre (berufsbegleitend)")
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
    # Generate new person id
    return str(PersonId().id)


def transform_removal_date(date, latest_export_date):
    # Return the date when it does not match latest_export_date, else None (no date)
    if date != latest_export_date:
        return date
    else:
        return None


def add_removal_date(thesis_df):
    # Calculate the latest export date (overall max export date over all thesis data)
    latest_date = thesis_df['export_date'].max()

    # Group all thesis by title and find the highest (latest) export date for each grouped thesis
    thesis_date_df = thesis_df.groupby('title', as_index=False)['export_date'].max()

    # Use the latest export date of a thesis as removal date when it is not the overall max export date
    thesis_date_df['removed'] = thesis_date_df['export_date'].apply(lambda d: transform_removal_date(d, latest_date))

    # Merge the thesis_df with the determined removed date from the thesis_date_df, before drop column "export_date"
    thesis_date_df.drop('export_date', axis=1, inplace=True)
    thesis_df = pd.merge(thesis_df, thesis_date_df, how='inner', on='title')

    return thesis_df


def insert_into_db(sql_command, *parameters):
    conn = None
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(host=LOCALHOST, port=PORT, database=DATABASE, user=USER, password=PASSWORD)

        # Create a cursor
        cursor = conn.cursor()
        cursor.execute(sql_command, *parameters)
        conn.commit()

        # Close the communication with PostgreSQL database
        cursor.close()
    except psycopg2.DatabaseError as error:
        # Special exception handling for duplicate key entries
        if error.pgcode == '23505':
            print("Warning: Duplicate key value, consider checking dataset: {}".format(error))
        else:
            print("Error accessing PostgreSQL database: {}".format(error))
    except Exception as error:
        print("Error inserting data in the database: {}".format(error))
    finally:
        if conn is not None:
            conn.close()


def load_data_into_db(thesis_df):
    # Variables for calculation of database import progress
    number_of_thesis = len(thesis_df)
    imported_thesis = 0

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

    # Dictionary for storing the generated person_id for contact names/ author names
    person_id_dict = dict()

    for thesis in thesis_df.itertuples(index=False):

        # Read all needed values from the Dataframe
        thesis_title = str(thesis.title)
        thesis_type = str(thesis.type_of_thesis)
        thesis_programmes = str(thesis.degree_programmes).split('|')
        thesis_work_type = str(thesis.type_of_work)
        thesis_contacts = str(thesis.contact_person).split('|')
        thesis_status = str(thesis.status)
        thesis_created = str(thesis.created)
        thesis_id = str(thesis.topic_id)
        thesis_url = str(thesis.url_topic_details)
        thesis_description = str(thesis.description)
        thesis_institution = str(thesis.home_institution)
        thesis_author = str(thesis.author)
        thesis_problem = str(thesis.problem_statement)
        thesis_requirement = str(thesis.requirement)
        thesis_departements = str(thesis.departements).split('|')
        thesis_courses = str(thesis.assigned_courses).split('|')
        thesis_removed = thesis.removed
        load_date = str(thesis.export_date)

        # Insert the thesis (hub_thesis)
        if md5(thesis_title) not in hub_title_cache:
            insert_into_db("INSERT INTO hub_thesis VALUES (%s, %s, %s, %s);",
                           (md5(thesis_title), thesis_title, load_date, 'DigiDigger'))
            hub_title_cache.add(md5(thesis_title))

        # Insert the thesis satellite (sat_thesis)
        hash_diff = md5_columns(thesis_type, thesis_work_type, thesis_status, thesis_created, thesis_id)
        if hash_diff not in sat_thesis_cache:
            insert_into_db("INSERT INTO sat_thesis VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                           (md5(thesis_title), load_date, hash_diff, 'DigiDigger', thesis_type, thesis_work_type,
                            thesis_status, thesis_created, thesis_removed, thesis_id))
            sat_thesis_cache.add(hash_diff)

        # Insert the thesis detail (hub_detail)
        if md5(thesis_id) not in hub_detail_cache:
            insert_into_db("INSERT INTO hub_detail VALUES (%s, %s, %s, %s);",
                           (md5(thesis_id), thesis_id, load_date, 'DigiDigger'))
            hub_detail_cache.add(md5(thesis_id))

        # Insert the thesis detail satellite (sat_details)
        hash_diff = md5_columns(thesis_description, thesis_institution, thesis_problem, thesis_requirement, thesis_url)
        if hash_diff not in sat_detail_cache:
            insert_into_db("INSERT INTO sat_details VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
                           (md5(thesis_id), load_date, hash_diff, 'DigiDigger', thesis_description,
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
        for thesis_programm in thesis_programmes:
            if md5(thesis_programm) not in hub_programm_cache:
                insert_into_db("INSERT INTO hub_degree_programm VALUES (%s, %s, %s, %s);",
                               (md5(thesis_programm), thesis_programm, load_date, 'DigiDigger'))
                hub_programm_cache.add(md5(thesis_programm))

            # Insert the thesis degree programm link (lnk_thesis_degree_programm)
            thesis_degree_key = md5_columns(thesis_title, thesis_programm)
            if thesis_degree_key not in lnk_thesis_degree_programm_cache:
                hub_thesis_key = md5(thesis_title)
                hub_degree_key = md5(thesis_programm)
                insert_into_db("INSERT INTO lnk_thesis_degree_programm VALUES (%s, %s, %s, %s, %s);",
                               (thesis_degree_key, hub_thesis_key, hub_degree_key, load_date, 'DigiDigger'))
                lnk_thesis_degree_programm_cache.add(thesis_degree_key)

        # Insert the contact persons (hub_person)
        for thesis_contact in thesis_contacts:
            # Check if the contact persons name is not yet in the database
            if md5(thesis_contact) not in hub_contact_author_cache:
                thesis_person_id = generate_person_id()
                insert_into_db("INSERT INTO hub_person VALUES (%s, %s, %s, %s);",
                               (md5(thesis_person_id), thesis_person_id, load_date, 'DigiDigger'))
                hub_contact_author_cache.add(md5(thesis_contact))
                person_id_dict[thesis_contact] = thesis_person_id

                # Insert the person satellite (sat_person) for contacts
                hash_diff = md5(thesis_contact)
                if hash_diff not in sat_person_cache:
                    insert_into_db("INSERT INTO sat_person VALUES (%s, %s, %s, %s, %s);",
                                   (md5(thesis_person_id), load_date, hash_diff, 'DigiDigger', thesis_contact))
                    sat_person_cache.add(hash_diff)

            # Insert the thesis contact link (lnk_thesis_contact)
            # Before get the person_id of the contact as it was generated before
            thesis_person_id = person_id_dict[thesis_contact]
            thesis_contact_key = md5_columns(thesis_title, thesis_person_id)
            if thesis_contact_key not in lnk_thesis_contact_cache:
                hub_thesis_key = md5(thesis_title)
                hub_person_key = md5(thesis_person_id)
                insert_into_db("INSERT INTO lnk_thesis_contact VALUES (%s, %s, %s, %s, %s);",
                               (thesis_contact_key, hub_thesis_key, hub_person_key, load_date, 'DigiDigger'))
                lnk_thesis_contact_cache.add(thesis_contact_key)

        # Insert the author (hub_person)
        if md5(thesis_author) not in hub_contact_author_cache:
            author_person_id = generate_person_id()
            insert_into_db("INSERT INTO hub_person VALUES (%s, %s, %s, %s);",
                           (md5(author_person_id), author_person_id, load_date, 'DigiDigger'))
            hub_contact_author_cache.add(md5(thesis_author))
            person_id_dict[thesis_author] = author_person_id

            # Insert the person satellite (sat_person) for author
            hash_diff = md5(thesis_author)
            if hash_diff not in sat_person_cache:
                insert_into_db("INSERT INTO sat_person VALUES (%s, %s, %s, %s, %s);",
                               (md5(author_person_id), load_date, hash_diff, 'DigiDigger', thesis_author))
                sat_person_cache.add(hash_diff)

        # Insert the detail author link (lnk_detail_author)
        # Before get the person_id of the author as it was generated before
        author_person_id = person_id_dict[thesis_author]
        detail_author_key = md5_columns(thesis_id, author_person_id)
        if detail_author_key not in lnk_detail_author_cache:
            hub_details_key = md5(thesis_id)
            hub_person_key = md5(author_person_id)
            insert_into_db("INSERT INTO lnk_detail_author VALUES (%s, %s, %s, %s, %s);",
                           (detail_author_key, hub_details_key, hub_person_key, load_date, 'DigiDigger'))
            lnk_detail_author_cache.add(detail_author_key)

        # Insert the departements (hub_departement)
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
        for thesis_course in thesis_courses:
            if md5(thesis_course) not in hub_course_cache and thesis_course != "None":
                insert_into_db("INSERT INTO hub_course VALUES (%s, %s, %s, %s);",
                               (md5(thesis_course), thesis_course, load_date, 'DigiDigger'))
                hub_course_cache.add(md5(thesis_course))

            # Insert the detail course link (lnk_detail_course)
            thesis_degree_key = md5_columns(thesis_id, thesis_course)
            if thesis_degree_key not in lnk_detail_course_cache:
                hub_details_key = md5(thesis_id)
                hub_course_key = md5(thesis_course)
                insert_into_db("INSERT INTO lnk_detail_course VALUES (%s, %s, %s, %s, %s);",
                               (thesis_degree_key, hub_details_key, hub_course_key, load_date, 'DigiDigger'))
                lnk_detail_course_cache.add(thesis_degree_key)

        # Calculate the progress of database import
        imported_thesis += 1
        if imported_thesis == number_of_thesis or imported_thesis % 1000 == 0:
            import_progress = round((imported_thesis / number_of_thesis) * 100)
            print('Database import progress: {}%'.format(import_progress))


data_set_path = "../data-uol-thesis-topics"
db_topics_filename = "db-topics.csv"
db_topics_add_filename = "db-topics-additional.csv"
export_dir_set = set()

print('Starting the import and transformation of the data set ({}).'.format(data_set_path))
for dirname in os.listdir(data_set_path):
    export_dir_set.add(dirname)

# Ensure sorted exported dir list and exclude hidden/ system folders
export_dir_set = sorted(export_dir_set)
export_dir_set[:] = [d for d in export_dir_set if not d.startswith('.')]

# Variables for calculation of extraction and transformation progress
number_of_dirs = len(export_dir_set)
number_of_finished_dirs = 0

# Dataframe variable for the output of the transform process (all thesis data)
transformed_thesis_df = None

# Iterate over every export folder in the data set directory
for export_dir in export_dir_set:

    # Calculate the progress of Extraction and Transformation process
    progress = round((number_of_finished_dirs / number_of_dirs) * 100)
    print('Processing export folder: {} -> Progress: {}%'.format(export_dir, progress))

    # Build export file paths
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

    # Load data from db-topics-additional.csv (see README.md: Step 1)
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

    # Add the export date to the merged data (load_dts for the database tables)
    export_date = "{}-{}-{}".format(export_dir[:4], export_dir[4:6], export_dir[6:8])
    merged_df['export_date'] = export_date

    # Check if the merge was successful by comparing length of all Dataframes
    if not (len(topic_df.index) == len(topic_detail_df.index) == len(html_details_df.index) == len(merged_df.index)):
        print("Error: Number of topics in consolidation Dataframes differ!")
        sys.exit()

    # Append the merged Dataframe for this export folder to the Dataframe with all exports
    if transformed_thesis_df is not None:
        transformed_thesis_df = pd.concat([transformed_thesis_df, merged_df], ignore_index=True)
    else:
        # The first daily export can be assigned directly
        transformed_thesis_df = merged_df

    # Increase counter for progress
    number_of_finished_dirs += 1

print("Processing of {} export folders finished.".format(number_of_finished_dirs))

# Add the removal date of the thesis (when possible due to missing export data, see README.md Step 1).
print("Trying to determine removal date of thesis data...")
transformed_thesis_df = add_removal_date(transformed_thesis_df)
print("Finished to determine removal date of thesis data.")

# KPIs for the ETL process (see README.md, Step 5)
print("Total number of thesis entries imported: {}.".format(len(transformed_thesis_df)))
print("Finished the import and transformation of the data set ({}).".format(data_set_path))

# Import merged thesis data in the database
print("Starting with the database import of the transformed thesis data.")
load_data_into_db(transformed_thesis_df)

print("Finished the the database import of the transformed thesis data. Exiting script.")
