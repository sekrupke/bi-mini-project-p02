-- Create Metabase Database
CREATE DATABASE metabase;

-- Create the Thesis Database with a own user and necessary grants
CREATE DATABASE thesis;
CREATE USER thesis_user with encrypted password 'aB2Ck91mN0LeA';
GRANT ALL PRIVILEGES ON DATABASE thesis TO thesis_user;
GRANT ALL ON schema public TO thesis_user;

-- Insert all tables specified in the Data Vault Model, therefore connect to thesis database
\connect thesis
-- Hub HUB_DEGREE_PROGRAMM
CREATE TABLE HUB_DEGREE_PROGRAMM (
    HUB_DEGREE_KEY char(32) PRIMARY KEY,
    DEGREE_PROGRAMM_NAME varchar(255),
    HUB_Load_DTS date,
    HUB_Rec_SRC varchar(60)
);
ALTER TABLE HUB_DEGREE_PROGRAMM OWNER TO thesis_user;

-- Link LNK_THESIS_DEGREE_PROGRAMM
CREATE TABLE LNK_THESIS_DEGREE_PROGRAMM (
    LNK_THESIS_DEGREE_KEY char(32) PRIMARY KEY,
    HUB_THESIS_KEY char(32),
    HUB_DEGREE_KEY char(32),
    LNK_Load_DTS date,
    LNK_Rec_SRC varchar(60)
);
ALTER TABLE LNK_THESIS_DEGREE_PROGRAMM OWNER TO thesis_user;

-- Hub HUB_DEPARTEMENT
CREATE TABLE HUB_DEPARTEMENT (
    HUB_DEPARTEMENT_KEY char(32) PRIMARY KEY,
    DEPARTEMENT_NAME varchar(255),
    HUB_Load_DTS date,
    HUB_Rec_SRC varchar(60)
);
ALTER TABLE HUB_DEPARTEMENT OWNER TO thesis_user;

-- Link LNK_DETAIL_DEPARTEMENT
CREATE TABLE LNK_DETAIL_DEPARTEMENT (
    LNK_DETAIL_DEPARTMENT_KEY char(32) PRIMARY KEY,
    HUB_DETAILS_KEY char(32),
    HUB_DEPARTEMENT_KEY char(32),
    LNK_Load_DTS date,
    LNK_Rec_SRC varchar(60)
);
ALTER TABLE LNK_DETAIL_DEPARTEMENT OWNER TO thesis_user;

-- Link LNK_DETAIL_COURSE
CREATE TABLE LNK_DETAIL_COURSE (
    LNK_DETAIL_COURSE_KEY char(32) PRIMARY KEY,
    HUB_DETAILS_KEY char(32),
    HUB_COURSE_KEY char(32),
    LNK_Load_DTS date,
    LNK_Rec_SRC varchar(60)
);
ALTER TABLE LNK_DETAIL_COURSE OWNER TO thesis_user;

-- Hub HUB_COURSE
 CREATE TABLE HUB_COURSE (
    HUB_COURSE_KEY char(32) PRIMARY KEY,
    COURSE_NAME varchar(255),
    HUB_Load_DTS date,
    HUB_Rec_SRC varchar(60)
);
ALTER TABLE HUB_COURSE OWNER TO thesis_user;

-- Hub HUB_PERSON
CREATE TABLE HUB_PERSON (
    HUB_PERSON_KEY char(32) PRIMARY KEY,
    PERSON_ID numeric,
    HUB_Load_DTS date,
    HUB_Rec_SRC varchar(60)
);
ALTER TABLE HUB_PERSON OWNER TO thesis_user;

-- Sat SAT_PERSON
CREATE TABLE SAT_PERSON (
    SAT_PERSON_KEY char(32),
    SAT_LOAD_DTS date,
    HASH_DIFF char(32),
    SAT_Rec_SRC varchar(60),
    FULLNAME varchar(250),
    PRIMARY KEY (SAT_PERSON_KEY, SAT_LOAD_DTS)
);
ALTER TABLE SAT_PERSON OWNER TO thesis_user;

-- Link LNK_DETAIL_AUTHOR
CREATE TABLE LNK_DETAIL_AUTHOR (
    LNK_THESIS_AUTHOR_KEY char(32) PRIMARY KEY,
    HUB_DETAILS_KEY char(32),
    HUB_PERSON_KEY char(32),
    LNK_Load_DTS date,
    LNK_Rec_SRC varchar(60)
);
ALTER TABLE LNK_DETAIL_AUTHOR OWNER TO thesis_user;

-- Link LNK_THESIS_CONTACT
CREATE TABLE LNK_THESIS_CONTACT (
    LNK_THESIS_CONTACT_KEY char(32) PRIMARY KEY,
    HUB_THESIS_KEY char(32),
    HUB_PERSON_KEY char(32),
    LNK_Load_DTS date,
    LNK_Rec_SRC varchar(60)
);
ALTER TABLE LNK_THESIS_CONTACT OWNER TO thesis_user;

-- Hub HUB_THESIS
CREATE TABLE HUB_THESIS (
    HUB_THESIS_KEY char(32) PRIMARY KEY,
    TITLE varchar(255),
    HUB_Load_DTS date,
    HUB_Rec_SRC varchar(60)
);
ALTER TABLE HUB_THESIS OWNER TO thesis_user;

-- Sat SAT_THESIS
CREATE TABLE SAT_THESIS (
    SAT_THESIS_KEY char(32),
    SAT_LOAD_DTS date,
    HASH_DIFF char(32),
    SAT_Rec_SRC varchar(60),
    TYPE_OF_THESIS varchar(100),
    TYPE_OF_WORK varchar(100),
    STATUS varchar(25),
    CREATED date,
    REMOVED date,
    TOPIC_ID char(32),
    PRIMARY KEY (SAT_THESIS_KEY, SAT_LOAD_DTS)
);
ALTER TABLE SAT_THESIS OWNER TO thesis_user;

-- Hub HUB_DETAIL
CREATE TABLE HUB_DETAIL (
    HUB_DETAILS_KEY char(32) PRIMARY KEY,
    DETAIL_ID char(32),
    HUB_Load_DTS date,
    HUB_Rec_SRC varchar(60)
);
ALTER TABLE HUB_DETAIL OWNER TO thesis_user;

-- Link LNK_THESIS_DETAILS
CREATE TABLE LNK_THESIS_DETAILS (
    LNK_THESIS_DETAILS_KEY char(32) PRIMARY KEY,
    HUB_THESIS_KEY char(32),
    HUB_DETAILS_KEY char(32),
    LNK_Load_DTS date,
    LNK_Rec_SRC varchar(60)
);
ALTER TABLE LNK_THESIS_DETAILS OWNER TO thesis_user;

-- Sat SAT_DETAILS
CREATE TABLE SAT_DETAILS (
    SAT_DETAILS_KEY char(32),
    SAT_LOAD_DTS date,
    HASH_DIFF char(32),
    SAT_Rec_SRC varchar(60),
    DESCRIPTION text,
    HOME_INSTITUTION varchar(255),
    PROBLEM_STATEMENT text,
    REQUIREMENT text,
    URL_TOPIC_DETAILS varchar(255),
    PRIMARY KEY (SAT_DETAILS_KEY, SAT_LOAD_DTS)
);
ALTER TABLE SAT_DETAILS OWNER TO thesis_user;