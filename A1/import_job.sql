-- Complete SQL script to create schema, import CSV data, add indexes, and analyze tables for JOB database

-- 1. Create Schema
\i job/job/schema.sql

-- 2. Import Data from CSV files (Assumes CSV files are in the current working directory)
\copy aka_name FROM 'aka_name.csv' WITH (FORMAT csv, ESCAPE '\');
\copy aka_title FROM 'aka_title.csv' WITH (FORMAT csv, ESCAPE '\');
\copy cast_info FROM 'cast_info.csv' WITH (FORMAT csv, ESCAPE '\');
\copy char_name FROM 'char_name.csv' WITH (FORMAT csv, ESCAPE '\');
\copy comp_cast_type FROM 'comp_cast_type.csv' WITH (FORMAT csv, ESCAPE '\');
\copy company_name FROM 'company_name.csv' WITH (FORMAT csv, ESCAPE '\');
\copy company_type FROM 'company_type.csv' WITH (FORMAT csv, ESCAPE '\');
\copy complete_cast FROM 'complete_cast.csv' WITH (FORMAT csv, ESCAPE '\');
\copy info_type FROM 'info_type.csv' WITH (FORMAT csv, ESCAPE '\');
\copy keyword FROM 'keyword.csv' WITH (FORMAT csv, ESCAPE '\');
\copy kind_type FROM 'kind_type.csv' WITH (FORMAT csv, ESCAPE '\');
\copy link_type FROM 'link_type.csv' WITH (FORMAT csv, ESCAPE '\');
\copy movie_companies FROM 'movie_companies.csv' WITH (FORMAT csv, ESCAPE '\');
\copy movie_info FROM 'movie_info.csv' WITH (FORMAT csv, ESCAPE '\');
\copy movie_info_idx FROM 'movie_info_idx.csv' WITH (FORMAT csv, ESCAPE '\');
\copy movie_keyword FROM 'movie_keyword.csv' WITH (FORMAT csv, ESCAPE '\');
\copy movie_link FROM 'movie_link.csv' WITH (FORMAT csv, ESCAPE '\');
\copy name FROM 'name.csv' WITH (FORMAT csv, ESCAPE '\');
\copy person_info FROM 'person_info.csv' WITH (FORMAT csv, ESCAPE '\');
\copy role_type FROM 'role_type.csv' WITH (FORMAT csv, ESCAPE '\');
\copy title FROM 'title.csv' WITH (FORMAT csv, ESCAPE '\');

-- 3. Create Foreign Key Indexes
\i job/job/fkindexes.sql

-- 4. ANALYZE all tables to generate histograms and optimizer statistics
ANALYZE;
