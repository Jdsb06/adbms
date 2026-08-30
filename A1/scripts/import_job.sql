-- Complete SQL script to create schema, import CSV data, add indexes, and analyze tables for JOB database

-- 1. Create Schema
\i job/job/schema.sql

-- 2. Import Data from CSV files located in data/ directory
\copy aka_name FROM 'data/aka_name.csv' WITH (FORMAT csv, ESCAPE '\');
\copy aka_title FROM 'data/aka_title.csv' WITH (FORMAT csv, ESCAPE '\');
\copy cast_info FROM 'data/cast_info.csv' WITH (FORMAT csv, ESCAPE '\');
\copy char_name FROM 'data/char_name.csv' WITH (FORMAT csv, ESCAPE '\');
\copy comp_cast_type FROM 'data/comp_cast_type.csv' WITH (FORMAT csv, ESCAPE '\');
\copy company_name FROM 'data/company_name.csv' WITH (FORMAT csv, ESCAPE '\');
\copy company_type FROM 'data/company_type.csv' WITH (FORMAT csv, ESCAPE '\');
\copy complete_cast FROM 'data/complete_cast.csv' WITH (FORMAT csv, ESCAPE '\');
\copy info_type FROM 'data/info_type.csv' WITH (FORMAT csv, ESCAPE '\');
\copy keyword FROM 'data/keyword.csv' WITH (FORMAT csv, ESCAPE '\');
\copy kind_type FROM 'data/kind_type.csv' WITH (FORMAT csv, ESCAPE '\');
\copy link_type FROM 'data/link_type.csv' WITH (FORMAT csv, ESCAPE '\');
\copy movie_companies FROM 'data/movie_companies.csv' WITH (FORMAT csv, ESCAPE '\');
\copy movie_info FROM 'data/movie_info.csv' WITH (FORMAT csv, ESCAPE '\');
\copy movie_info_idx FROM 'data/movie_info_idx.csv' WITH (FORMAT csv, ESCAPE '\');
\copy movie_keyword FROM 'data/movie_keyword.csv' WITH (FORMAT csv, ESCAPE '\');
\copy movie_link FROM 'data/movie_link.csv' WITH (FORMAT csv, ESCAPE '\');
\copy name FROM 'data/name.csv' WITH (FORMAT csv, ESCAPE '\');
\copy person_info FROM 'data/person_info.csv' WITH (FORMAT csv, ESCAPE '\');
\copy role_type FROM 'data/role_type.csv' WITH (FORMAT csv, ESCAPE '\');
\copy title FROM 'data/title.csv' WITH (FORMAT csv, ESCAPE '\');

-- 3. Create Foreign Key Indexes
\i job/job/fkindexes.sql

-- 4. ANALYZE all tables to generate histograms and optimizer statistics
ANALYZE;
