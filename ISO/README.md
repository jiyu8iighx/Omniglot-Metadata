### Reference Names

The "Ref_Name" column in the download tables contains a reference  name by which this language is identified in the standard. The Reference Name is employed for ease of use of the code set, and does not imply it is to be preferred in any application to any other name that may be  associated with the particular code element as given in the [Language Names Index](https://iso639-3.sil.org/code_tables/download_tables#Language Names Index).

Note: We wish to avoid use of any pejorative name as the Reference  Name. If you are aware of any instance in which a code element uses a  pejorative or derogatory name as the Reference Name, please bring this  to our attention at the contact email address below.

### Complete Set of Tables

A complete set of all current code tables in UTF-8 encoding,  containing the main ISO 639-3 table, the Language Names Index Table, the Macrolanguage Mappings, and the Retired Code Element Mappings, is  available here: 

- [iso-639-3_Code_Tables_20250715.zip](https://iso639-3.sil.org/sites/iso639-3/files/downloads/iso-639-3_Code_Tables_20250715.zip)

### ISO 639-3 Code Set

*NOTE:*  The "Ref_Name" column in this table contains a  reference name by which this language is identified in the standard. The Reference Name is employed for ease of use of the code set, and does  not imply it is to be preferred in any application to any other name  that may be associated with the particular code element as given in the [Language Names Index](https://iso639-3.sil.org/code_tables/download_tables#Language Names Index).

The complete code table of active code elements may be downloaded by clicking the following link.

- [Download ISO 639-3 code set](https://iso639-3.sil.org/sites/iso639-3/files/downloads/iso-639-3.tab) 

The following declaration is a sample formal definition for a SQL  database table into which the tab-delimited file can be loaded (Comment  column added 18 Oct 2007):

```
CREATE TABLE [ISO_639-3] (
         Id      char(3) NOT NULL,  -- The three-letter 639-3 identifier
         Part2B  char(3) NULL,      -- Equivalent 639-2 identifier of the bibliographic applications 
                                    -- code set, if there is one
         Part2T  char(3) NULL,      -- Equivalent 639-2 identifier of the terminology applications code 
                                    -- set, if there is one
         Part1   char(2) NULL,      -- Equivalent 639-1 identifier, if there is one    
         Scope   char(1) NOT NULL,  -- I(ndividual), M(acrolanguage), S(pecial)
         Type    char(1) NOT NULL,  -- A(ncient), C(onstructed),  
                                    -- E(xtinct), H(istorical), L(iving), S(pecial)
         Ref_Name   varchar(150) NOT NULL,   -- Reference language name 
         Comment    varchar(150) NULL)       -- Comment relating to one or more of the columns
```

### Language Names Index

In ISO 639-2, there are multiple name forms for some identified  languages. The ISO 639-3 code tables now include a language name index  with multiple names associated with many code elements (primarily in  English forms or variant anglicized spellings of indigenous names). The  reference name from the Ref_Name field of the main table is included as  an entry in this table, thus every code element has at least one row  occurrence in the Language Names Index table. The name appears in two  forms, a "print" form used in most contexts, and an inverted form which  fronts a language name root, e.g., "Isthmus Zapotec" and "Zapotec,  Isthmus". Where there is no root part to the name, the Print_Name and  the Inverted_Name contain identical strings. The Language Names Index  may be downloaded by clicking the following link

- Download [ISO 639-3 Language Names Index](https://iso639-3.sil.org/sites/iso639-3/files/downloads/iso-639-3_Name_Index.tab) 

The following declaration is a sample formal definition for a SQL  database table into which the tab-delimited file can be loaded:

```
CREATE TABLE [ISO_639-3_Names] (
         Id             char(3)     NOT NULL,  -- The three-letter 639-3 identifier
         Print_Name     varchar(75) NOT NULL,  -- One of the names associated with this identifier 
         Inverted_Name  varchar(75) NOT NULL)  -- The inverted form of this Print_Name form   
```

### Macrolanguage Mappings

The complete set of mappings from macrolanguages to the individual  languages that comprise them may be downloaded by clicking the following link.

- Download [ISO 639-3 macrolanguage mappings](https://iso639-3.sil.org/sites/iso639-3/files/downloads/iso-639-3-macrolanguages.tab)

The table has three columns (this is a change from previous versions  of this table). The first identifies a macrolanguage and the second  identifies one of its members. The third specifies the status of the  individual member language, as being Active or Deprecated (Retired).  (This last column is actually redundant, but indicates to the user which table will contain the identifier as primary key: the main code set  table for active code elements, or the retirement mappings table  for deprecated code elements.) Thus a given macrolanguage has as many  rows as it has individual languages that are its members. The following  declaration is a sample formal definition for a SQL database table into  which the tab-delimited file can be loaded:

```
CREATE TABLE [ISO_639-3_Macrolanguages] (
         M_Id      char(3) NOT NULL,   -- The identifier for a macrolanguage
         I_Id      char(3) NOT NULL,   -- The identifier for an individual language
                                       -- that is a member of the macrolanguage
         I_Status  char(1) NOT NULL)   -- A (active) or R (retired) indicating the
                                       -- status of the individual code element
```

### Deprecated (Retired) Code Element Mappings

The annual update to the 639-3 code set will include a complete  listing of the code elements that have been deprecated with instructions on how to update existing data. Although the word "retired" was  previously used for codes no longer in use, we now use the  word "deprecated" as the code will continue to have the same meaning  that was originally established for it. Deprecated codes are not reused  for another meaning in the code set.

Since the initial release of ISO/FDIS 639-3 and prior to the release  of ISO 639-3, there was one list of retirements (deprecations), a  correction to the alignment between ISO 639-3 and ISO 639-2. It is  included in the Deprecated Code Element Mappings because it has been a  source of confusion for users. The Deprecated Code Element Mappings  table may be downloaded by clicking the following link.

- Download [ISO 639-3 deprecated code mappings](https://iso639-3.sil.org/sites/iso639-3/files/downloads/iso-639-3_Retirements.tab)

The table has five columns; the first has the affected identifier,  the second has a coded value for the reason the deprecation was  necessary, the third contains a single identifier if the deprecated  identifier maps unambiguously to another identifier, the fourth contains a prose statement about what should be done to update a code element  split, and the fifth gives the date the change was made effective. The  following declaration is a sample formal definition for a SQL database  table into which the tab-delimited file can be loaded:

```
CREATE TABLE [ISO_639-3_Retirements] (
         Id          char(3)      NOT NULL,     -- The three-letter 639-3 identifier
         Ref_Name    varchar(150) NOT NULL,     -- reference name of language
         Ret_Reason  char(1)      NOT NULL,     -- code for retirement: C (change), D (duplicate),
                                                -- N (non-existent), S (split), M (merge)
         Change_To   char(3)      NULL,         -- in the cases of C, D, and M, the identifier 
                                                -- to which all instances of this Id should be changed
         Ret_Remedy  varchar(300) NULL,         -- The instructions for updating an instance
                                                -- of the retired (split) identifier
         Effective   date         NOT NULL)     -- The date the retirement became effective
```

