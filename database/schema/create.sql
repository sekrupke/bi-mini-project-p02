-- Hub HUB_DEGREE_PROGRAMM
CREATE TABLE HUB_DEGREE_PROGRAMM (
    HUB_DEGREE_KEY char(32) PRIMARY KEY,
    DEGREE_PROGRAMM_NAME varchar(255),
    HUB_Load_DTS date,
    HUB_Rec_SRC varchar(60)
);

-- Link LNK_THESIS_DEGREE_PROGRAMM
CREATE TABLE LNK_THESIS_DEGREE_PROGRAMM (
    LNK_DETAIL_COURSE_KEY char(32) PRIMARY KEY,
    HUB_THESIS_KEY char(32),
    HUB_DEGREE_KEY char(32),
    LNK_Load_DTS date,
    LNK_Rec_SRC varchar(60)
);

-- Hub HUB_DEPARTEMENT
CREATE TABLE HUB_DEPARTEMENT (
    HUB_DEPARTEMENT_KEY char(32) PRIMARY KEY,
    DEPARTEMENT_NAME varchar(255),
    HUB_Load_DTS date,
    HUB_Rec_SRC varchar(60)
);

-- Link LNK_DETAIL_DEPARTEMENT
CREATE TABLE LNK_DETAIL_DEPARTEMENT (
    LNK_DETAIL_DEPARTMENT_KEY char(32) PRIMARY KEY,
    HUB_DETAILS_KEY char(32),
    HUB_DEPARTEMENT_KEY char(32),
    LNK_Load_DTS date,
    LNK_Rec_SRC varchar(60)
);

-- Link LNK_DETAIL_COURSE
CREATE TABLE LNK_DETAIL_COURSE (
    LNK_DETAIL_COURSE_KEY char(32) PRIMARY KEY,
    HUB_DETAILS_KEY char(32),
    HUB_COURSE_KEY char(32),
    LNK_Load_DTS date,
    LNK_Rec_SRC varchar(60)
);

-- Hub HUB_COURSE
 CREATE TABLE HUB_COURSE (
    HUB_COURSE_KEY char(32) PRIMARY KEY,
    COURSE_NAME varchar(255),
    HUB_Load_DTS date,
    HUB_Rec_SRC varchar(60)
);

-- Hub HUB_PERSON
CREATE TABLE HUB_PERSON (
    HUB_PERSON_KEY char(32) PRIMARY KEY,
    PERSON_ID bigint,
    HUB_Load_DTS date,
    HUB_Rec_SRC varchar(60)
);

-- Sat SAT_PERSON
CREATE TABLE SAT_PERSON (
    SAT_PERSON_KEY char(32) PRIMARY KEY,
    SAT_LOAD_DTS date,
    HASH_DIFF char(32),
    SAT_Rec_SRC varchar(60),
    SALUTATION varchar(50),
    FIRSTNAME varchar(100),
    LASTNAME varchar(100),
    PRIMARY KEY (SAT_PERSON_KEY, SAT_LOAD_DTS)
);

-- Link LNK_DETAIL_AUTHOR
CREATE TABLE LNK_DETAIL_AUTHOR (
    LNK_THESIS_AUTHOR_KEY char(32) PRIMARY KEY,
    HUB_THESIS_KEY char(32),
    HUB_PERSON_KEY char(32),
    LNK_Load_DTS date,
    LNK_Rec_SRC varchar(60)
);

-- Link LNK_THESIS_CONTACT
CREATE TABLE LNK_THESIS_CONTACT (
    LNK_THESIS_CONTACT_KEY char(32) PRIMARY KEY,
    HUB_THESIS_KEY char(32),
    HUB_PERSON_KEY char(32),
    LNK_Load_DTS date,
    LNK_Rec_SRC varchar(60)
);

-- Hub HUB_THESIS
CREATE TABLE HUB_THESIS (
    HUB_THESIS_KEY char(32) PRIMARY KEY,
    TITLE varchar(255),
    HUB_Load_DTS date,
    HUB_Rec_SRC varchar(60)
);

-- Sat SAT_THESIS
CREATE TABLE SAT_THESIS (
    SAT_THESIS_KEY char(32) PRIMARY KEY,
    SAT_LOAD_DTS date,
    HASH_DIFF char(32),
    SAT_Rec_SRC varchar(60),
    TYPE_OF_THESIS varchar(100),
    TYPE_OF_WORK varchar(100),
    STATUS varchar(25),
    CREATED date,
    TOPIC_ID char(32),
    PRIMARY KEY (SAT_THESIS_KEY, SAT_LOAD_DTS)
);

-- Hub HUB_DETAIL
CREATE TABLE HUB_DETAIL (
    HUB_DETAILS_KEY char(32) PRIMARY KEY,
    DETAIL_ID char(32),
    HUB_Load_DTS date,
    HUB_Rec_SRC varchar(60)
);

-- Link LNK_THESIS_DETAILS
CREATE TABLE LNK_THESIS_DETAILS (
    LNK_THESIS_DETAILS_KEY char(32) PRIMARY KEY,
    HUB_THESIS_KEY char(32),
    HUB_DETAILS_KEY char(32),
    LNK_Load_DTS date,
    LNK_Rec_SRC varchar(60)
);

-- Sat SAT_DETAILS
CREATE TABLE SAT_DETAILS (
    HUB_THESIS_KEY char(32) PRIMARY KEY,
    SAT_LOAD_DTS date,
    HASH_DIFF char(32),
    SAT_Rec_SRC varchar(60),
    DESCRIPTION text,
    HOME_INSTITUTION varchar(255),
    PROBLEM_STATEMENT text,
    REQUIREMENT text,
    URL_TOPIC_DETAILS varchar(255),
    PRIMARY KEY (HUB_THESIS_KEY, SAT_LOAD_DTS)
);