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
The dataset includes daily HTML-Exports of all thesis topics with additional data (thesis topic details). There is also a CSV and JSON Representation of the thesis topics and thesis topic details in the dataset.
As the data is exported from the Stud.IP-Thesis Plugin which implements a pagination, there are multiple HTML-Exports per day. Also every detail page (when following the link on the thesis list) is present in the data set via a single HTML-Export.

The picture describes the structure of the data set (number of files in /additional reduced for image):
![Thesis topics data description](presentation/thesis_topics_data.png)

`Note: The HTML-Exports in the data set only contains the first three pages and the last page of the thesis topic list. This unintentionally missing data is considered by best effort but may result in inconsistent results later on!`

There are semantically equivalent data fields in the thesis topic list and thesis topic details. A simple Python script (TODO.py) was used to check the assumed equivalent data fields.

The following fields are treated as equivalent based on the Python script:
* "Title"
* "Type of thesis"
* "Type of work"
* "Degree programmes"
* "Contact Person" = "Author"
* "Status"
* "Created"

The table show the data fields in the data set, the left side shows the fields of the thesis topic list, the right side of the thesis topic details:
| Thesis Topic List Fields        | Thesis Topic Detail Fields |
| -------------------- | ------------- |
| Title                | Title          |
| Type of thesis       | Type of thesis           |
| Degree programmes    |           |
| Type of work         | Type of work          |
| Contact person       | Author          |
| Status               | Status          |
| Created              | Created          |
|                      | Description          |
|                      | Home institution          |
|                      | Problem statement          |
|                      | Requirement          |
|                      | Study data:         |
|                      | -- Departements          |
|                      | -- Degree programmes          |
|                      | -- Assigned courses           |
|                      | -- Contact person          |

## Step 2: Data Vault Model
The Data Vault Model was created by considering the data set and with the goal to not loose any data.
The following picture shows the Data Vault Model:

<<dummy.png>>

The following decisions or assumptions were made while creating the model:
