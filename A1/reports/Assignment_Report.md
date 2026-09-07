# Advanced Database Management Systems (ADBMS)
## Assignment 0 & Assignment 1: Histogram Analysis Report

---

# Assignment 0

## Setup
- **CPU Model & Specification**: 13th Gen Intel(R) Core(TM) i3-1315U (6 cores, 8 threads)
- **RAM Capacity**: 14 GiB
- **HDD / Storage Capacity**: 456 GiB NVMe SSD
- **Operating System**: Ubuntu 26.04 LTS
- **PostgreSQL Engine Version**: `PostgreSQL 18.6 (Ubuntu 18.6-0ubuntu0.26.04.1) on x86_64-pc-linux-gnu, compiled by gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0, 64-bit`

## Database
- **Database Name**: Join Order Benchmark (2013 Snapshot)
- **Total Tables**: 21
- **Total Relational Tuples**: 74,190,187

### Table Cardinalities & Primary Keys

| Table Name | Primary Key Column | Cardinality (`count(*)`) |
| :--- | :---: | :---: |
| `aka_name` | `id` | 901,343 |
| `aka_title` | `id` | 361,472 |
| `cast_info` | `id` | 36,244,344 |
| `char_name` | `id` | 3,140,339 |
| `comp_cast_type` | `id` | 4 |
| `company_name` | `id` | 234,997 |
| `company_type` | `id` | 4 |
| `complete_cast` | `id` | 135,086 |
| `info_type` | `id` | 113 |
| `keyword` | `id` | 134,170 |
| `kind_type` | `id` | 7 |
| `link_type` | `id` | 18 |
| `movie_companies` | `id` | 2,609,129 |
| `movie_info` | `id` | 14,835,720 |
| `movie_info_idx` | `id` | 1,380,035 |
| `movie_keyword` | `id` | 4,523,930 |
| `movie_link` | `id` | 29,997 |
| `name` | `id` | 4,167,491 |
| `person_info` | `id` | 2,963,664 |
| `role_type` | `id` | 12 |
| `title` | `id` | 2,528,312 |

---

# Assignment 1: Histogram

## Q1. Histogram Analysis for `id` and `title` Columns of `title` Table

### 1. Corresponding SQL Query
to see what all colums needed form `pg_stats'
```sql
\d pg_stats;
```
to see histogram boundary values and other relevent  stored in `pg_stats`:
```sql
SELECT 
    attname, 
    null_frac, 
    n_distinct, 
    most_common_vals, 
    most_common_freqs, 
    histogram_bounds 
FROM pg_stats
WHERE tablename = 'title' 
  AND attname IN ('id', 'title');
```

### 2. Kind of Histogram
PSQL uses an Equi Depth Histogram combined with a Most Common Values list. In an equidepth histogram, all buckets contain approximately the same number of rows ($approx N / B$), while bucket boundaries vary in width according to data distribution

### 3. Number of Buckets
- Column `id`: **100 buckets** (101 bucket boundary values)
- Column `title`: **100 buckets** (101 bucket boundary values)
- extra -  to see the defualt number of buckets
```sql
SHOW default_statistics_target;
```

### 4. How Textual Attribute `title` is Put into Histogram
textual attribute “title” is put into histogram as:
1. sorting the text strings in lexicographical order like bannana and apple will be apple, bannana after sorting
2. Sampling string values from the table like table title has around 2.5M rows , it will only sample around 30K
3. Encoding initial string prefix bytes into floating-point numbers in $[0.0, 1.0]$ range for quantitative interpolation like laptop will be broken to lap with l = 108, a=97, p=112 then by 256 as between 0 and 1 , lap will be around 0.42 , we can then see where a key belongs between two keeys 
4. Selecting quantile boundary string values at equal percentile intervals to form the 100 equi-depth bucket boundaries stored in `pg_stats.histogram_bounds`.

### 5. Exact Bucket Boundaries List (From `pg_stats`)

#### A. Column `id` Bucket Boundaries (101 values, 100 buckets)
| Bucket Index | Boundary Value (`id`) | Bucket Interval |
| :---: | :---: | :--- |
| B000 (Start) | `59` | Start of table data |
| B001 | `23714` | Bucket 1: [`59` - `23714`] |
| B002 | `48149` | Bucket 2: [`23714` - `48149`] |
| B003 | `72817` | Bucket 3: [`48149` - `72817`] |
| B004 | `95729` | Bucket 4: [`72817` - `95729`] |
| B005 | `121074` | Bucket 5: [`95729` - `121074`] |
| B006 | `144977` | Bucket 6: [`121074` - `144977`] |
| B007 | `169683` | Bucket 7: [`144977` - `169683`] |
| B008 | `196989` | Bucket 8: [`169683` - `196989`] |
| B009 | `223879` | Bucket 9: [`196989` - `223879`] |
| B010 | `248693` | Bucket 10: [`223879` - `248693`] |
| B011 | `273990` | Bucket 11: [`248693` - `273990`] |
| B012 | `298306` | Bucket 12: [`273990` - `298306`] |
| B013 | `324285` | Bucket 13: [`298306` - `324285`] |
| B014 | `351943` | Bucket 14: [`324285` - `351943`] |
| B015 | `377665` | Bucket 15: [`351943` - `377665`] |
| B016 | `402562` | Bucket 16: [`377665` - `402562`] |
| B017 | `427165` | Bucket 17: [`402562` - `427165`] |
| B018 | `450041` | Bucket 18: [`427165` - `450041`] |
| B019 | `476541` | Bucket 19: [`450041` - `476541`] |
| B020 | `504001` | Bucket 20: [`476541` - `504001`] |
| B021 | `530892` | Bucket 21: [`504001` - `530892`] |
| B022 | `554936` | Bucket 22: [`530892` - `554936`] |
| B023 | `579382` | Bucket 23: [`554936` - `579382`] |
| B024 | `605662` | Bucket 24: [`579382` - `605662`] |
| B025 | `635724` | Bucket 25: [`605662` - `635724`] |
| B026 | `660098` | Bucket 26: [`635724` - `660098`] |
| B027 | `685503` | Bucket 27: [`660098` - `685503`] |
| B028 | `711514` | Bucket 28: [`685503` - `711514`] |
| B029 | `738280` | Bucket 29: [`711514` - `738280`] |
| B030 | `761949` | Bucket 30: [`738280` - `761949`] |
| B031 | `786224` | Bucket 31: [`761949` - `786224`] |
| B032 | `813130` | Bucket 32: [`786224` - `813130`] |
| B033 | `839650` | Bucket 33: [`813130` - `839650`] |
| B034 | `865127` | Bucket 34: [`839650` - `865127`] |
| B035 | `890846` | Bucket 35: [`865127` - `890846`] |
| B036 | `916422` | Bucket 36: [`890846` - `916422`] |
| B037 | `942321` | Bucket 37: [`916422` - `942321`] |
| B038 | `966414` | Bucket 38: [`942321` - `966414`] |
| B039 | `992402` | Bucket 39: [`966414` - `992402`] |
| B040 | `1018536` | Bucket 40: [`992402` - `1018536`] |
| B041 | `1042654` | Bucket 41: [`1018536` - `1042654`] |
| B042 | `1067771` | Bucket 42: [`1042654` - `1067771`] |
| B043 | `1095109` | Bucket 43: [`1067771` - `1095109`] |
| B044 | `1118783` | Bucket 44: [`1095109` - `1118783`] |
| B045 | `1143773` | Bucket 45: [`1118783` - `1143773`] |
| B046 | `1166042` | Bucket 46: [`1143773` - `1166042`] |
| B047 | `1189434` | Bucket 47: [`1166042` - `1189434`] |
| B048 | `1214917` | Bucket 48: [`1189434` - `1214917`] |
| B049 | `1238698` | Bucket 49: [`1214917` - `1238698`] |
| B050 | `1265284` | Bucket 50: [`1238698` - `1265284`] |
| B051 | `1289292` | Bucket 51: [`1265284` - `1289292`] |
| B052 | `1316374` | Bucket 52: [`1289292` - `1316374`] |
| B053 | `1341809` | Bucket 53: [`1316374` - `1341809`] |
| B054 | `1368155` | Bucket 54: [`1341809` - `1368155`] |
| B055 | `1390856` | Bucket 55: [`1368155` - `1390856`] |
| B056 | `1415494` | Bucket 56: [`1390856` - `1415494`] |
| B057 | `1440189` | Bucket 57: [`1415494` - `1440189`] |
| B058 | `1470241` | Bucket 58: [`1440189` - `1470241`] |
| B059 | `1495070` | Bucket 59: [`1470241` - `1495070`] |
| B060 | `1521219` | Bucket 60: [`1495070` - `1521219`] |
| B061 | `1548321` | Bucket 61: [`1521219` - `1548321`] |
| B062 | `1573875` | Bucket 62: [`1548321` - `1573875`] |
| B063 | `1601158` | Bucket 63: [`1573875` - `1601158`] |
| B064 | `1626461` | Bucket 64: [`1601158` - `1626461`] |
| B065 | `1651255` | Bucket 65: [`1626461` - `1651255`] |
| B066 | `1676102` | Bucket 66: [`1651255` - `1676102`] |
| B067 | `1699392` | Bucket 67: [`1676102` - `1699392`] |
| B068 | `1723296` | Bucket 68: [`1699392` - `1723296`] |
| B069 | `1748662` | Bucket 69: [`1723296` - `1748662`] |
| B070 | `1775889` | Bucket 70: [`1748662` - `1775889`] |
| B071 | `1803023` | Bucket 71: [`1775889` - `1803023`] |
| B072 | `1829223` | Bucket 72: [`1803023` - `1829223`] |
| B073 | `1857858` | Bucket 73: [`1829223` - `1857858`] |
| B074 | `1881086` | Bucket 74: [`1857858` - `1881086`] |
| B075 | `1903361` | Bucket 75: [`1881086` - `1903361`] |
| B076 | `1927998` | Bucket 76: [`1903361` - `1927998`] |
| B077 | `1951928` | Bucket 77: [`1927998` - `1951928`] |
| B078 | `1976104` | Bucket 78: [`1951928` - `1976104`] |
| B079 | `1999905` | Bucket 79: [`1976104` - `1999905`] |
| B080 | `2024316` | Bucket 80: [`1999905` - `2024316`] |
| B081 | `2049744` | Bucket 81: [`2024316` - `2049744`] |
| B082 | `2074672` | Bucket 82: [`2049744` - `2074672`] |
| B083 | `2100120` | Bucket 83: [`2074672` - `2100120`] |
| B084 | `2124364` | Bucket 84: [`2100120` - `2124364`] |
| B085 | `2150361` | Bucket 85: [`2124364` - `2150361`] |
| B086 | `2173917` | Bucket 86: [`2150361` - `2173917`] |
| B087 | `2197820` | Bucket 87: [`2173917` - `2197820`] |
| B088 | `2221024` | Bucket 88: [`2197820` - `2221024`] |
| B089 | `2245759` | Bucket 89: [`2221024` - `2245759`] |
| B090 | `2270744` | Bucket 90: [`2245759` - `2270744`] |
| B091 | `2295634` | Bucket 91: [`2270744` - `2295634`] |
| B092 | `2322099` | Bucket 92: [`2295634` - `2322099`] |
| B093 | `2348175` | Bucket 93: [`2322099` - `2348175`] |
| B094 | `2373305` | Bucket 94: [`2348175` - `2373305`] |
| B095 | `2398600` | Bucket 95: [`2373305` - `2398600`] |
| B096 | `2424733` | Bucket 96: [`2398600` - `2424733`] |
| B097 | `2448930` | Bucket 97: [`2424733` - `2448930`] |
| B098 | `2473750` | Bucket 98: [`2448930` - `2473750`] |
| B099 | `2500889` | Bucket 99: [`2473750` - `2500889`] |
| B100 | `2528043` | Bucket 100: [`2500889` - `2528043`] |

#### B. Column `title` Bucket Boundaries (101 values, 100 buckets)
| Bucket Index | Boundary Value (`title`) | Lexicographical Interval |
| :---: | :--- | :--- |
| B000 (Start) | `\$` | Start of text data |
| B001 | `(#1.13234)` | Bucket 1: [`\$` - `(#1.13234)`] |
| B002 | `(#12.138)` | Bucket 2: [`(#1.13234)` - `(#12.138)`] |
| B003 | `(#1.38)` | Bucket 3: [`(#12.138)` - `(#1.38)`] |
| B004 | `(#1.59)` | Bucket 4: [`(#1.38)` - `(#1.59)`] |
| B005 | `(#1.828)` | Bucket 5: [`(#1.59)` - `(#1.828)`] |
| B006 | `(1967-08-21)` | Bucket 6: [`(#1.828)` - `(1967-08-21)`] |
| B007 | `(1982-10-13)` | Bucket 7: [`(1967-08-21)` - `(1982-10-13)`] |
| B008 | `(1994-03-11)` | Bucket 8: [`(1982-10-13)` - `(1994-03-11)`] |
| B009 | `(1998-04-17)` | Bucket 9: [`(1994-03-11)` - `(1998-04-17)`] |
| B010 | `(2000-03-01)` | Bucket 10: [`(1998-04-17)` - `(2000-03-01)`] |
| B011 | `(2002-01-27)` | Bucket 11: [`(2000-03-01)` - `(2002-01-27)`] |
| B012 | `(2003-11-04)` | Bucket 12: [`(2002-01-27)` - `(2003-11-04)`] |
| B013 | `(2005-01-17)` | Bucket 13: [`(2003-11-04)` - `(2005-01-17)`] |
| B014 | `(2006-03-17)` | Bucket 14: [`(2005-01-17)` - `(2006-03-17)`] |
| B015 | `(2007-06-13)` | Bucket 15: [`(2006-03-17)` - `(2007-06-13)`] |
| B016 | `(2008-10-16)` | Bucket 16: [`(2007-06-13)` - `(2008-10-16)`] |
| B017 | `(2010-07-19)` | Bucket 17: [`(2008-10-16)` - `(2010-07-19)`] |
| B018 | `(2011-09-07)` | Bucket 18: [`(2010-07-19)` - `(2011-09-07)`] |
| B019 | `(2012-09-05)` | Bucket 19: [`(2011-09-07)` - `(2012-09-05)`] |
| B020 | `(#21.44)` | Bucket 20: [`(2012-09-05)` - `(#21.44)`] |
| B021 | `(#3.11)` | Bucket 21: [`(#21.44)` - `(#3.11)`] |
| B022 | `(#44.31)` | Bucket 22: [`(#3.11)` - `(#44.31)`] |
| B023 | `(#6.56)` | Bucket 23: [`(#44.31)` - `(#6.56)`] |
| B024 | `Abide` | Bucket 24: [`(#6.56)` - `Abide`] |
| B025 | `A Flock of Trouble` | Bucket 25: [`Abide` - `A Flock of Trouble`] |
| B026 | `All New! Meredith Baxter on Broken Marriages, Drinking and Coming Out` | Bucket 26: [`A Flock of Trouble` - `All New! Meredith Baxter on Broken Marriages, Drinking and Coming Out`] |
| B027 | `Andrew and Eric and the Last Crusade` | Bucket 27: [`All New! Meredith Baxter on Broken Marriages, Drinking and Coming Out` - `Andrew and Eric and the Last Crusade`] |
| B028 | `Ark` | Bucket 28: [`Andrew and Eric and the Last Crusade` - `Ark`] |
| B029 | `Aurora` | Bucket 29: [`Ark` - `Aurora`] |
| B030 | `Barcos congeladores` | Bucket 30: [`Aurora` - `Barcos congeladores`] |
| B031 | `Besuch im Fernsehstudio` | Bucket 31: [`Barcos congeladores` - `Besuch im Fernsehstudio`] |
| B032 | `Blondinen im Piss-Ring` | Bucket 32: [`Besuch im Fernsehstudio` - `Blondinen im Piss-Ring`] |
| B033 | `Broke` | Bucket 33: [`Blondinen im Piss-Ring` - `Broke`] |
| B034 | `Can't Live with Them: Part 2` | Bucket 34: [`Broke` - `Can't Live with Them: Part 2`] |
| B035 | `Chelsea on the Rocks` | Bucket 35: [`Can't Live with Them: Part 2` - `Chelsea on the Rocks`] |
| B036 | `Collateral Damage` | Bucket 36: [`Chelsea on the Rocks` - `Collateral Damage`] |
| B037 | `Cross Country Vacation` | Bucket 37: [`Collateral Damage` - `Cross Country Vacation`] |
| B038 | `Das perfekte Promi-Dinner in Frankfurt` | Bucket 38: [`Cross Country Vacation` - `Das perfekte Promi-Dinner in Frankfurt`] |
| B039 | `Der Alchimist` | Bucket 39: [`Das perfekte Promi-Dinner in Frankfurt` - `Der Alchimist`] |
| B040 | `Die heimliche Hochzeit` | Bucket 40: [`Der Alchimist` - `Die heimliche Hochzeit`] |
| B041 | `Doomsday Preppers` | Bucket 41: [`Die heimliche Hochzeit` - `Doomsday Preppers`] |
| B042 | `Educating Mandy` | Bucket 42: [`Doomsday Preppers` - `Educating Mandy`] |
| B043 | `Embraceable You: Give It Time` | Bucket 43: [`Educating Mandy` - `Embraceable You: Give It Time`] |
| B044 | `Even Further Abroad` | Bucket 44: [`Embraceable You: Give It Time` - `Even Further Abroad`] |
| B045 | `Fear America` | Bucket 45: [`Even Further Abroad` - `Fear America`] |
| B046 | `Forbidden Fruit` | Bucket 46: [`Fear America` - `Forbidden Fruit`] |
| B047 | `Gaia's dagboek` | Bucket 47: [`Forbidden Fruit` - `Gaia's dagboek`] |
| B048 | `Give Us This Night` | Bucket 48: [`Gaia's dagboek` - `Give Us This Night`] |
| B049 | `Gurtrug Nr. 1` | Bucket 49: [`Give Us This Night` - `Gurtrug Nr. 1`] |
| B050 | `Hellacious Acres: The Case of John Glass` | Bucket 50: [`Gurtrug Nr. 1` - `Hellacious Acres: The Case of John Glass`] |
| B051 | `Hold That Mork` | Bucket 51: [`Hellacious Acres: The Case of John Glass` - `Hold That Mork`] |
| B052 | `Hurdy Gurdy` | Bucket 52: [`Hold That Mork` - `Hurdy Gurdy`] |
| B053 | `Independence Day` | Bucket 53: [`Hurdy Gurdy` - `Independence Day`] |
| B054 | `Is There a Doctor in the House?` | Bucket 54: [`Independence Day` - `Is There a Doctor in the House?`] |
| B055 | `Jimmy and the Wild Honey Hunters` | Bucket 55: [`Is There a Doctor in the House?` - `Jimmy and the Wild Honey Hunters`] |
| B056 | `Kampf ums Tor zur Welt` | Bucket 56: [`Jimmy and the Wild Honey Hunters` - `Kampf ums Tor zur Welt`] |
| B057 | `Klara's Opfer` | Bucket 57: [`Kampf ums Tor zur Welt` - `Klara's Opfer`] |
| B058 | `Lady of the Lake` | Bucket 58: [`Klara's Opfer` - `Lady of the Lake`] |
| B059 | `Lately There Have Been Many Misunderstandings in the Zimmerman Home` | Bucket 59: [`Lady of the Lake` - `Lately There Have Been Many Misunderstandings in the Zimmerman Home`] |
| B060 | `Les caquets de l'accouchée` | Bucket 60: [`Lately There Have Been Many Misunderstandings in the Zimmerman Home` - `Les caquets de l'accouchée`] |
| B061 | `Little Friends of the Wild` | Bucket 61: [`Les caquets de l'accouchée` - `Little Friends of the Wild`] |
| B062 | `Low Tide: Dance Guitar Dance` | Bucket 62: [`Little Friends of the Wild` - `Low Tide: Dance Guitar Dance`] |
| B063 | `Mäntsälän kapina` | Bucket 63: [`Low Tide: Dance Guitar Dance` - `Mäntsälän kapina`] |
| B064 | `Melodies Reborn` | Bucket 64: [`Mäntsälän kapina` - `Melodies Reborn`] |
| B065 | `Mite` | Bucket 65: [`Melodies Reborn` - `Mite`] |
| B066 | `Mugenryoku: Ide densetsu` | Bucket 66: [`Mite` - `Mugenryoku: Ide densetsu`] |
| B067 | `Negative Vibes` | Bucket 67: [`Mugenryoku: Ide densetsu` - `Negative Vibes`] |
| B068 | `No Place to Hide` | Bucket 68: [`Negative Vibes` - `No Place to Hide`] |
| B069 | `Old Scores` | Bucket 69: [`No Place to Hide` - `Old Scores`] |
| B070 | `Otmica majora` | Bucket 70: [`Old Scores` - `Otmica majora`] |
| B071 | `Passeio da Fama` | Bucket 71: [`Otmica majora` - `Passeio da Fama`] |
| B072 | `Pirates of the Dark Matter` | Bucket 72: [`Passeio da Fama` - `Pirates of the Dark Matter`] |
| B073 | `Préparez vos mouchoirs` | Bucket 73: [`Pirates of the Dark Matter` - `Préparez vos mouchoirs`] |
| B074 | `Qui est mon père?` | Bucket 74: [`Préparez vos mouchoirs` - `Qui est mon père?`] |
| B075 | `Renkinjutsu` | Bucket 75: [`Qui est mon père?` - `Renkinjutsu`] |
| B076 | `Roommates` | Bucket 76: [`Renkinjutsu` - `Roommates`] |
| B077 | `Santa Claus and the Clubman` | Bucket 77: [`Roommates` - `Santa Claus and the Clubman`] |
| B078 | `Segunda oportunidad` | Bucket 78: [`Santa Claus and the Clubman` - `Segunda oportunidad`] |
| B079 | `Shola Jo Bhadke` | Bucket 79: [`Segunda oportunidad` - `Shola Jo Bhadke`] |
| B080 | `Slippery Garage Floor` | Bucket 80: [`Shola Jo Bhadke` - `Slippery Garage Floor`] |
| B081 | `Spider-Man 3` | Bucket 81: [`Slippery Garage Floor` - `Spider-Man 3`] |
| B082 | `Studio à louer` | Bucket 82: [`Spider-Man 3` - `Studio à louer`] |
| B083 | `Tajne pohrby` | Bucket 83: [`Studio à louer` - `Tajne pohrby`] |
| B084 | `Th 6` | Bucket 84: [`Tajne pohrby` - `Th 6`] |
| B085 | `The Bouquet` | Bucket 85: [`Th 6` - `The Bouquet`] |
| B086 | `The Diplomat's Club` | Bucket 86: [`The Bouquet` - `The Diplomat's Club`] |
| B087 | `The Golden Age` | Bucket 87: [`The Diplomat's Club` - `The Golden Age`] |
| B088 | `The Lair of General Grievous` | Bucket 88: [`The Golden Age` - `The Lair of General Grievous`] |
| B089 | `The Myth Makers` | Bucket 89: [`The Lair of General Grievous` - `The Myth Makers`] |
| B090 | `The Ranch King's Daughter` | Bucket 90: [`The Myth Makers` - `The Ranch King's Daughter`] |
| B091 | `The Spirit of Enterprise` | Bucket 91: [`The Ranch King's Daughter` - `The Spirit of Enterprise`] |
| B092 | `The Winning Hand` | Bucket 92: [`The Spirit of Enterprise` - `The Winning Hand`] |
| B093 | `Toda Max` | Bucket 93: [`The Winning Hand` - `Toda Max`] |
| B094 | `Tricks of the Trade` | Bucket 94: [`Toda Max` - `Tricks of the Trade`] |
| B095 | `Uncle Sam's Defenders` | Bucket 95: [`Tricks of the Trade` - `Uncle Sam's Defenders`] |
| B096 | `Vaseline Smile` | Bucket 96: [`Uncle Sam's Defenders` - `Vaseline Smile`] |
| B097 | `Walking with Cavemen` | Bucket 97: [`Vaseline Smile` - `Walking with Cavemen`] |
| B098 | `White Rabbits` | Bucket 98: [`Walking with Cavemen` - `White Rabbits`] |
| B099 | `www.blowyourheadoff.com` | Bucket 99: [`White Rabbits` - `www.blowyourheadoff.com`] |
| B100 | `Zwölfte Folge` | Bucket 100: [`www.blowyourheadoff.com` - `Zwölfte Folge`] |

### 6. Histogram Visualization
![Histogram for title.id](../plots/q1_histogram_id.png)

![Histogram for title.title](../plots/q1_histogram_title.png)

### 7. Max Selectivity Error
- **Max Selectivity Error**: Since `default_statistics_target` is 100, there are 100 buckets. Therefore, the maximum selectivity error for a range query is bounded by:
$$\text{Max Error} \le \frac{1}{B} = \frac{1}{100} = 0.01 \quad (1.0\%)$$
For evaluated queries(q9), the observed maximum selectivity error is **0.8374%** (0.008374), which strictly satisfies $\text{Max Error} \le 1.0\%$.

---
### 8: Selectivity Estimation for Text Columns
Selectivity estimate is done for range query on text column such as “title” in PSQL such as:
*The engine scans the `histogram_bounds` array stored under pg_stats to locate the specific bucket where the target string  is, after that it counts all complete buckets preceding the target bucket. Each full bucket represents a fixed fraction of total rows (1/B). For the target bucket, PostgreSQL converts initial string bytes into floating-point numbers in $[0.0, 1.0]$ range for interpolation as explain in part 4,  assuming uniform distribution inside the target bucket, it calculates the target's position using:

$$\text{Fraction} = \frac{\text{Query Value} - \text{Bucket Min}}{\text{Bucket Max} - \text{Bucket Min}}$$
*   Final Calculation is done by adding the fractional bucket estimate to the sum of preceding full buckets to get the final estimated selectivity.

### 9: Estimated vs. Actual Selectivities

To calculate estimated and actual selectivities of the queries and moreover there accuracy we compare estimated rows (from `EXPLAIN`) against actual rows (from `EXPLAIN ANALYZE`).
Total row count ($N$) for the `title` table is 2,528,312.

**Query 1: `title < 'Race'`**
```sql 
EXPLAIN ANALYZE SELECT * FROM title WHERE title.title < 'Race';
```
- **Actual Selectivity:** The query physically returned 1,918,141 matching rows: $S_{act} = \frac{1918141}{2528312} \approx 0.7587$ (75.87%).

```sql
EXPLAIN SELECT * FROM title WHERE title.title < 'Race';
```
- **Estimated Selectivity:** The planner estimated 1,939,313 rows: $S_{est} = \frac{1939313}{2528312} \approx 0.7670$ (76.70%).

- **Observation:** The absolute error is roughly 0.84%.

**Query 2: `id < 350000`**
```sql
EXPLAIN ANALYZE SELECT * FROM title WHERE title.id < '350000';
```
- **Actual Selectivity:** The query returned 349,999 matching rows: $S_{act} = \frac{349999}{2528312} \approx 0.1384$ (13.84%).

```sql
EXPLAIN SELECT * FROM title WHERE title.id < '350000';
```
- **Estimated Selectivity:** The planner estimated 352,255 rows: $S_{est} = \frac{352255}{2528312} \approx 0.1393$ (13.93%).

- **Observation:** The absolute error here is about 0.09%.

---

## Q2. Optimal Serial Histogram Construction ($B=10$ Buckets)

### 1. Histogram Visualizations for Exact $N = 3000$ Samples (Slide-9 Upright Vertical Block Plots)
*As defined in lecture Slide 9, a Serial Histogram sorts domain values by their ordered frequencies ($f(v_{(1)}) \le f(v_{(2)}) \le \dots \le f(v_{(m)})$) and partitions the frequency space to minimize frequency variance $\sum n_i V_i$. The upright vertical block plots below feature Frequencies on the X-axis (ordered ascending) and Value Set / Stacked Domain Elements on the Y-axis:*

![Correct Conceptual Plot for Unique title.id (N=3000)](../plots/q2_histogram_id_3000.png)

![Q2: For title.title (N=3000) - Correct V-Optimal Serial Histogram](../plots/q2_histogram_title_3000.png)

### 2. Execution Build Time (Average over 3 Runs)
- **Average Build Time for $N=3000$**: **0.2118 seconds** (`id` column) / **0.3122 seconds** (`title` column)

### 3. Frequency Bucket Boundaries ($N=3000$, $B=10$)

The optimal serial histogram algorithm partitions the exact 3,000 samples into dynamic frequency buckets ($B=10$). The exact bucket value ranges, distinct domain value counts ($n_i$), and frequency distributions for both columns are listed below:

#### A. Column `id` Serial Frequency Bucket Boundaries ($N=3000$, $B=10$)
| Bucket # | Value Range (`id`) | Distinct Values ($n_i$) | Frequency Range | Average Frequency ($ar{f}_i$) |
| :---: | :---: | :---: | :---: | :---: |
| Bucket 01 | [`1,234` - `2,528,274`] | 3000 | 1 | 1.00 |

#### B. Column `title` Serial Frequency Bucket Boundaries ($N=3000$, $B=10$)
| Bucket # | Value Range (`title`) | Distinct Values ($n_i$) | Frequency Range | Average Frequency ($ar{f}_i$) |
| :---: | :--- | :---: | :---: | :---: |
| Bucket 01 | [`"\$#!+ Happens"` ... `"Ônna no kaôyaku"`] | 2773 | 1 | 1.00 |
| Bucket 02 | [`"(#1.132)"` ... `"The Box"`] | 35 | 2 | 2.00 |
| Bucket 03 | [`"(#1.118)"` ... `"(#4.1)"`] | 8 | 3 | 3.00 |
| Bucket 04 | [`"(#1.11)"` ... `"(#3.1)"`] | 5 | 4 | 4.00 |
| Bucket 05 | [`"(#1.10)"` ... `"Pilot"`] | 4 | 5 | 5.00 |
| Bucket 06 | [`"(#1.7)"` ... `"(#1.9)"`] | 2 | 6 | 6.00 |
| Bucket 07 | [`"(#1.6)"` ... `"(#1.8)"`] | 2 | 8 | 8.00 |
| Bucket 08 | [`"(#1.5)"` ... `"(#1.5)"`] | 1 | 11 | 11.00 |
| Bucket 09 | [`"(#1.1)"` ... `"(#1.2)"`] | 2 | 13 | 13.00 |
| Bucket 10 | [`"(#1.3)"` ... `"(#1.4)"`] | 2 | 14 | 14.00 |

### 4. 3-Run Selectivity Error Calculation & Average ($N=3000$)

As required to account for sample randomness, the selectivity error evaluation was executed across **3 independent runs** (with exact sample size $N=3000$). All three run errors are listed below along with their computed average:

#### A. 3-Run Max Selectivity Error Summary ($N=3000$)
| Column | Run 1 Max Error | Run 2 Max Error | Run 3 Max Error | **Average Max Selectivity Error** |
| :---: | :---: | :---: | :---: | :---: |
| `id` | `0.022444` | `0.009556` | `0.009889` | **`0.013963`** (1.3963%) |
| `title` | `0.612556` | `0.609000` | `0.616667` | **`0.612741`** (61.2741%) |

#### B. Quantile-by-Quantile Error Evaluation Table for Run 1 ($N=3000, B=10$)
| Index ($k$) | Query Threshold ($q_k$) | Actual Count ($A$) | Actual Selectivity ($S_{\text{act}}$) | Estimated Count ($E$) | Estimated Selectivity ($S_{\text{est}}$) | Absolute Error $\vert S_{\text{est}} - S_{\text{act}} \vert$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| $q_{0}$ | `1,234.0` | 1 | 0.000333 | 0.00 | 0.000000 | 0.000333 |
| $q_{1}$ | `282,016.2` | 352 | 0.117333 | 333.33 | 0.111111 | 0.006222 |
| $q_{2}$ | `562,798.4` | 673 | 0.224333 | 666.67 | 0.222222 | 0.002111 |
| $q_{3}$ | `843,580.7` | 966 | 0.322000 | 1000.00 | 0.333333 | 0.011333 |
| $q_{4}$ | `1,124,362.9` | 1307 | 0.435667 | 1333.33 | 0.444444 | 0.008778 |
| $q_{5}$ | `1,405,145.1` | 1613 | 0.537667 | 1666.67 | 0.555556 | 0.017889 |
| $q_{6}$ | `1,685,927.3` | 1946 | 0.648667 | 2000.00 | 0.666667 | 0.018000 |
| $q_{7}$ | `1,966,709.6` | 2266 | 0.755333 | 2333.33 | 0.777778 | **0.022444** |
| $q_{8}$ | `2,247,491.8` | 2623 | 0.874333 | 2666.67 | 0.888889 | 0.014556 |
| $q_{9}$ | `2,528,274.0` | 3000 | 1.000000 | 3000.00 | 1.000000 | 0.000000 |

### 5. Histograms Across Exact Sample Sizes ($N = 1000, 3000, 5000$)

Below are the optimal serial histogram visualizations ($B=10$) for exact sample sizes $N=1000$, $N=3000$, and $N=5000$:N=5000$:

#### A. Sample Size $N = 1000$ Histograms
![Sample Size: N=1000, title.id Serial Hist.](../plots/q2_histogram_id_1000.png)

![Sample Size: N=1000, title.title Serial Hist.](../plots/q2_histogram_title_1000.png)

#### B. Sample Size $N = 3000$ Histograms
![Correct Conceptual Plot for Unique title.id (N=3000)](../plots/q2_histogram_id_3000.png)

![Q2: For title.title (N=3000) - Correct V-Optimal Serial Histogram](../plots/q2_histogram_title_3000.png)

#### C. Sample Size $N = 5000$ Histograms
![Sample Size: N=5000, title.id Serial Hist.](../plots/q2_histogram_id_5000.png)

![Sample Size: N=5000, title.title Serial Hist.](../plots/q2_histogram_title_5000.png)

#### D. Comprehensive 3-Run Summary Table Across Exact Sample Sizes
| Exact Sample Size ($N$) | Column | Run 1 Error | Run 2 Error | Run 3 Error | **Average Max Error** | Average Build Time |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1000** | `id` | `0.020667` | `0.013333` | `0.016556` | **`0.016852`** | `0.2370s` |
| **1000** | `title` | `0.637000` | `0.625000` | `0.169333` | **`0.477111`** | `0.3204s` |
| **3000** | `id` | `0.022444` | `0.009556` | `0.009889` | **`0.013963`** | `0.2118s` |
| **3000** | `title` | `0.612556` | `0.609000` | `0.616667` | **`0.612741`** | `0.3122s` |
| **5000** | `id` | `0.013578` | `0.005778` | `0.007556` | **`0.008970`** | `0.2394s` |
| **5000** | `title` | `0.603667` | `0.600667` | `0.606400` | **`0.603578`** | `0.3256s` |

---

### 6. Full Step-by-Step Linear Regression Extrapolation ($N = 2,528,312$)

To extrapolate the construction build time for the entire `title` table ($N = 2,528,312$), we fit a linear regression model on the 3-run average measured build times:
$$T(N) = m \cdot N + c$$

#### A. Sample Data Points $(N_i, T_i)$
- Point 1: $(N_1, T_1) = (1000, 0.2370)$
- Point 2: $(N_2, T_2) = (3000, 0.2118)$
- Point 3: $(N_3, T_3) = (5000, 0.2394)$

#### B. Mean Calculations
- $\bar{N} = \frac{1000 + 3000 + 5000}{3} = \mathbf{3000}$
- $\bar{T} = \frac{0.2370 + 0.2118 + 0.2394}{3} = \mathbf{0.2294\text{ seconds}}$

#### C. Deviations & Sum of Products
| $N_i$ | $T_i$ (s) | $(N_i - \bar{N})$ | $(T_i - \bar{T})$ | $(N_i - \bar{N})^2$ | $(N_i - \bar{N})(T_i - \bar{T})$ |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1000 | 0.2370 | -2000 | 0.0076 | 4,000,000 | -15.2143 |
| 3000 | 0.2118 | 0 | -0.0176 | 0 | -0.0000 |
| 5000 | 0.2394 | +2000 | 0.0100 | 4,000,000 | 20.0143 |
| **Sum** | | | | **8,000,000** | **4.8000** |

#### D. Slope ($m$) and Intercept ($c$) Formulas
- **Slope ($m$)**:
  $$m = \frac{\sum (N_i - \bar{N})(T_i - \bar{T})}{\sum (N_i - \bar{N})^2} = \frac{4.8000}{8,000,000} = \mathbf{0.00000060\text{ seconds / sample}}$$

- **Intercept ($c$)**:
  $$c = \bar{T} - m \cdot \bar{N} = 0.2294 - (0.00000060 \times 3000) = \mathbf{0.227576\text{ seconds}}$$

#### E. Extrapolated Build Time for Full Table ($N = 2,528,312$)
$$T(2,528,312) = (0.00000060 \times 2,528,312) + (0.227576) = \mathbf{1.74\text{ seconds}} \quad (\mathbf{0.03\text{ minutes}})$$

---

### 7. Sample Size vs Time Relationship Plot
![Sample Size vs Time](../plots/q2_sample_size_vs_time.png)

---

### 8. Sample Size vs Max Selectivity Error Relationship Plot
![Sample Size vs Max Selectivity Error](../plots/q2_sample_size_vs_error.png)

---

## 9: The Trade-off of Bucket Counts

When building a histogram, choosing the number of buckets ($B$) is a classic trade off between performance and accuracy.

**Choosing Fewer Buckets (e.g., 5 to 10)**
If we use a small number of buckets, the biggest advantage is speed and efficiency. The histogram takes up very little memory in the system catalog and builds much faster because the time complexity of our algorithm, $O(B \cdot N^2)$, drops significantly. The query planner also spends less time analyzing it. However, the major downside is that we lose a lot of data resolution. Because the buckets are so wide, the internal mathematical estimates become much less accurate, especially if the data is heavily skewed or unevenly distributed.

**Choosing More Buckets (e.g., 50 to 100)**
On the flip side, using a large number of buckets gives the database a high-definition view of how the data is distributed. The estimates become incredibly precise, which leads to much lower selectivity errors and helps the query optimizer make smarter decisions for complex joins. The catch is that this accuracy comes at a heavy system cost. It takes noticeably longer to calculate and construct the histogram, consumes more storage space, and adds a slight delay to the query planning phase before execution can actually begin.
