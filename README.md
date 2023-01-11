# BI Mini-Project P02

## Introduction
This is a BI Mini Project that was developed at the University of Oldenburg. The project is based on a dataset of thesis topics offered at the university.

## Requirements/ Prerequisites
Following requirements are needed for the project:
* Unix System Environment
* Python installed
* Docker and Docker Compose installed

## Milestones of the project
The project consists of 4 major Milestones which are described in detail in this document.
* Step 1: Review of the Data Set
* Step 2: Data Vault Model
* Step 3: Database Schema
* Step 4: ETL-Process
* Step 5: Visualization and KPIs (Project Tasks)

## Step 1: Review of the Data Set
The dataset includes daily HTML-Export of all thesis topics with additional data (thesis topic details). There is also a CSV and JSON Representation of the thesis topics and thesis topic details in the dataset.
As the data is exported from the Stud.IP-Thesis Plugin which implements a pagination, there are multiple HTML-Export per day. Also every detail page (when following the link on the thesis list) is present in the data set via a single HTML-Export.

The image describes the structure of the data set (number of files in /additional reduced for image):
![Thesis topics data description](presentation/thesis_topics_data.png)

`Note: The HTML-Export in the data set only contains the first three pages and the last page of the thesis topic list. This unintentionally missing data is considered by best effort but may result in inconsistent results later on!`

The first step is to analyze the given data and data fields across the files in the data set.
Analyzing the HTML Exports and CSV/JSON-files yields to a list of all available data fields, with some internal fields only given in the CSV/JSON-files like the "topic_id".
After that semantically equivalent (same content) data fields in the thesis topic list and thesis topic details are considered. By a randomized sample of 30 thesis topic details the equality of data fields was investigated. This yields to following fields that are assumed to contain the same data (left side of equal sign referring topics list, right side the topic details):
* "Title"
* "Type of thesis"
* "Type of work"
* "Degree programmes" = "Study data: Degree programmes"
* "Contact Person" = "Study data: Contact person"
* "Status"
* "Created"

Furthermore, the different files in the data set contain different data fields. For example the "Study data: Departements"-Field of the HTML-Export is missing in the CSV/JSON Files. Also, the field names change between German and English, so they must be translated to English. Considering the equivalent data fields and showing the possible origins of the data fields for the ETL process yields the following table:

| Thesis Topic List Fields | Thesis Topic Detail Fields    | Possible Origins for extraction                       |
|--------------------------|-------------------------------|-------------------------------------------------------|
| Title                    | Title                         | List + Detail HTML-Export, **db-topics.json+csv**     |
| Type of thesis           | Type of thesis                | List + Detail HTML-Export, **db-topics.json+csv**     |
| Degree programmes        | Study data: Degree programmes | List + Detail HTML-Export, **db-topics.json+csv**     |  
| Type of work             | Type of work                  | List + Detail HTML-Export, **db-topics.json+csv**     |  
| Contact person           | Study data: Contact person    | List + Detail HTML-Export, **db-topics.json+csv**     |  
| Status                   | Status                        | List + Detail HTML-Export, **db-topics.json+csv**     |  
| Created                  | Created                       | List + Detail HTML-Export, **db-topics.json+csv**     |  
|                          | Author                        | Detail HTML-Export, **db-topics-additional.json+csv** |
|                          | Description                   | Detail HTML-Export, **db-topics-additional.json+csv** |
|                          | Home institution              | Detail HTML-Export, **db-topics-additional.json+csv** |
|                          | Problem statement             | Detail HTML-Export, **db-topics-additional.json+csv** |
|                          | Requirement                   | Detail HTML-Export, **db-topics-additional.json+csv** |
|                          | Study data: Departements      | **Detail HTML-Export**                                |
|                          | Study data: Assigned courses  | **Detail HTML-Export**                                |
|                          | topic_id                      | **db-topics.json+csv**, db-topics-additional.json+csv |
|                          | url_topic_details             | **db-topics.json+csv**                                |

For reference of column "Possible Origins", see the folder structure image in this section. The marked (bold) origins show the preferred file for accessing this information later on in the ETL process. A file is **preferred** when it is the only file where this data field is available or when it is already structured convenient (JSON, XML) for extraction. The table concludes this step of the project.

## Step 2: Data Vault Model
The Data Vault Model was created by considering the data set and with the goal to not loose any data.
The following picture shows the Data Vault Model:

<<dummy.png>>

The following decisions or assumptions were made while creating the model:
