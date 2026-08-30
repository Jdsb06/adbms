-- SQL script to get PK column and cardinality for all 21 JOB tables
SELECT 'aka_name' AS table_name, 'id' AS primary_key, count(*) AS cardinality FROM aka_name
UNION ALL SELECT 'aka_title', 'id', count(*) FROM aka_title
UNION ALL SELECT 'cast_info', 'id', count(*) FROM cast_info
UNION ALL SELECT 'char_name', 'id', count(*) FROM char_name
UNION ALL SELECT 'comp_cast_type', 'id', count(*) FROM comp_cast_type
UNION ALL SELECT 'company_name', 'id', count(*) FROM company_name
UNION ALL SELECT 'company_type', 'id', count(*) FROM company_type
UNION ALL SELECT 'complete_cast', 'id', count(*) FROM complete_cast
UNION ALL SELECT 'info_type', 'id', count(*) FROM info_type
UNION ALL SELECT 'keyword', 'id', count(*) FROM keyword
UNION ALL SELECT 'kind_type', 'id', count(*) FROM kind_type
UNION ALL SELECT 'link_type', 'id', count(*) FROM link_type
UNION ALL SELECT 'movie_companies', 'id', count(*) FROM movie_companies
UNION ALL SELECT 'movie_info', 'id', count(*) FROM movie_info
UNION ALL SELECT 'movie_info_idx', 'id', count(*) FROM movie_info_idx
UNION ALL SELECT 'movie_keyword', 'id', count(*) FROM movie_keyword
UNION ALL SELECT 'movie_link', 'id', count(*) FROM movie_link
UNION ALL SELECT 'name', 'id', count(*) FROM name
UNION ALL SELECT 'person_info', 'id', count(*) FROM person_info
UNION ALL SELECT 'role_type', 'id', count(*) FROM role_type
UNION ALL SELECT 'title', 'id', count(*) FROM title
ORDER BY table_name;
