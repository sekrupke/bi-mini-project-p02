# Setup the BI Mini-Project P02

This manual describes all requirements and steps to prepare and execute this BI Mini-Project.

## Requirements/ Prerequisites
Following requirements are needed for the project:
* Unix System Environment (Linux/ MacOS)
* [Python3 installed](https://www.python.org/)
* Pip installed
* Docker and Docker Compose installed (for later PostgreSQL and Metabase installation)

## Preparing the Data Set
The data set must be downloaded from https://cloudstorage.elearning.uni-oldenburg.de/s/XXXXXXXXXXXX. After that the data 
set can be unzipped and the folder "data-uol-thesis-topics" must be placed in the **root folder** of this project. This is 
the folder directly containing the daily thesis exports.

`Note: The files (names) and structure of the data set must not change.`

While reviewing the data set cleaning or removal of wrong data/ duplicated data may be necessary.
In the thesis data set are 3 duplicated folders (20210719_****). They seem to have the same content and are the oldest
exports, maybe they were used for test purposes of the export. 
Removing two of the three duplicated folders:\
`rm -r data-uol-thesis-topics/20210719_2cb1/`\
`rm -r data-uol-thesis-topics/20210719_4196/`

Another issue in the dataset can be missing files, as in the export from 20220908. In the folder `data-uol-thesis-topics/20220908_2b64/` several files (like db-topics.csv) are missing. Therefore, we delete the export from that day:\
`rm -r data-uol-thesis-topics/20220908_2b64/`

## Installing PostgreSQL and Metabase
The PostgreSQL Database is required for the import of the thesis data and for the Metabase application. Metabase is 
needed for data visualisation and creation of dashboards. 
As the infrastructure is automated by Docker and Docker Compose, we just need to run the file _docker-compose.yml_ to install PostgreSQL and Metabase:\
`cd infrastructure`\
`docker-compose up`

The creation of the databases "thesis" and "metabase" with tables, users etc. is fully automated as the SQL-script (database/create.sql) is copied into "docker-entrypoint-initdb.d" and executed automatically.

## Creating Python Environment
For development a virtual Python environment is recommended to track and install the requirements. This step is only 
required once when no virtual environment is present.

Move to the etl folder:\
`cd etl`

Create the virtual environment:\
`python3 -m venv venv`

Activate (use) the required virtual environment:\
`source ./venv/bin/activate`

Download and installation of the Python Requirements:\
`pip install -r requirements.txt`

## Execute the ETL process
The ETL process is fully automated by a Python Script, that also loads the data into the Database "thesis".

Start the Python script for extract and transform steps (activated virtual environment):\
`python3 consolidate.py`

## Configuring and using Metabase
TODO: Describe