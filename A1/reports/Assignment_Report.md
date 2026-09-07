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
| B000 (Start) | `66` | Start of table data |
| B001 | `26031` | Bucket 1: [`66` - `26031`] |
| B002 | `49984` | Bucket 2: [`26031` - `49984`] |
| B003 | `74833` | Bucket 3: [`49984` - `74833`] |
| B004 | `101140` | Bucket 4: [`74833` - `101140`] |
| B005 | `127437` | Bucket 5: [`101140` - `127437`] |
| B006 | `153864` | Bucket 6: [`127437` - `153864`] |
| B007 | `179570` | Bucket 7: [`153864` - `179570`] |
| B008 | `203627` | Bucket 8: [`179570` - `203627`] |
| B009 | `227342` | Bucket 9: [`203627` - `227342`] |
| B010 | `249558` | Bucket 10: [`227342` - `249558`] |
| B011 | `274050` | Bucket 11: [`249558` - `274050`] |
| B012 | `300161` | Bucket 12: [`274050` - `300161`] |
| B013 | `326810` | Bucket 13: [`300161` - `326810`] |
| B014 | `353628` | Bucket 14: [`326810` - `353628`] |
| B015 | `378794` | Bucket 15: [`353628` - `378794`] |
| B016 | `401971` | Bucket 16: [`378794` - `401971`] |
| B017 | `426990` | Bucket 17: [`401971` - `426990`] |
| B018 | `453094` | Bucket 18: [`426990` - `453094`] |
| B019 | `480643` | Bucket 19: [`453094` - `480643`] |
| B020 | `505273` | Bucket 20: [`480643` - `505273`] |
| B021 | `531162` | Bucket 21: [`505273` - `531162`] |
| B022 | `559018` | Bucket 22: [`531162` - `559018`] |
| B023 | `582792` | Bucket 23: [`559018` - `582792`] |
| B024 | `605800` | Bucket 24: [`582792` - `605800`] |
| B025 | `632265` | Bucket 25: [`605800` - `632265`] |
| B026 | `656668` | Bucket 26: [`632265` - `656668`] |
| B027 | `683413` | Bucket 27: [`656668` - `683413`] |
| B028 | `708726` | Bucket 28: [`683413` - `708726`] |
| B029 | `732854` | Bucket 29: [`708726` - `732854`] |
| B030 | `759074` | Bucket 30: [`732854` - `759074`] |
| B031 | `784282` | Bucket 31: [`759074` - `784282`] |
| B032 | `812447` | Bucket 32: [`784282` - `812447`] |
| B033 | `836574` | Bucket 33: [`812447` - `836574`] |
| B034 | `863283` | Bucket 34: [`836574` - `863283`] |
| B035 | `888391` | Bucket 35: [`863283` - `888391`] |
| B036 | `914667` | Bucket 36: [`888391` - `914667`] |
| B037 | `939512` | Bucket 37: [`914667` - `939512`] |
| B038 | `962926` | Bucket 38: [`939512` - `962926`] |
| B039 | `987759` | Bucket 39: [`962926` - `987759`] |
| B040 | `1013055` | Bucket 40: [`987759` - `1013055`] |
| B041 | `1039398` | Bucket 41: [`1013055` - `1039398`] |
| B042 | `1062735` | Bucket 42: [`1039398` - `1062735`] |
| B043 | `1090405` | Bucket 43: [`1062735` - `1090405`] |
| B044 | `1116673` | Bucket 44: [`1090405` - `1116673`] |
| B045 | `1142039` | Bucket 45: [`1116673` - `1142039`] |
| B046 | `1163912` | Bucket 46: [`1142039` - `1163912`] |
| B047 | `1192171` | Bucket 47: [`1163912` - `1192171`] |
| B048 | `1215031` | Bucket 48: [`1192171` - `1215031`] |
| B049 | `1241261` | Bucket 49: [`1215031` - `1241261`] |
| B050 | `1266561` | Bucket 50: [`1241261` - `1266561`] |
| B051 | `1291888` | Bucket 51: [`1266561` - `1291888`] |
| B052 | `1318652` | Bucket 52: [`1291888` - `1318652`] |
| B053 | `1343336` | Bucket 53: [`1318652` - `1343336`] |
| B054 | `1369813` | Bucket 54: [`1343336` - `1369813`] |
| B055 | `1398034` | Bucket 55: [`1369813` - `1398034`] |
| B056 | `1422999` | Bucket 56: [`1398034` - `1422999`] |
| B057 | `1449897` | Bucket 57: [`1422999` - `1449897`] |
| B058 | `1474101` | Bucket 58: [`1449897` - `1474101`] |
| B059 | `1497897` | Bucket 59: [`1474101` - `1497897`] |
| B060 | `1522641` | Bucket 60: [`1497897` - `1522641`] |
| B061 | `1546054` | Bucket 61: [`1522641` - `1546054`] |
| B062 | `1569842` | Bucket 62: [`1546054` - `1569842`] |
| B063 | `1597944` | Bucket 63: [`1569842` - `1597944`] |
| B064 | `1624272` | Bucket 64: [`1597944` - `1624272`] |
| B065 | `1649906` | Bucket 65: [`1624272` - `1649906`] |
| B066 | `1677958` | Bucket 66: [`1649906` - `1677958`] |
| B067 | `1702991` | Bucket 67: [`1677958` - `1702991`] |
| B068 | `1726251` | Bucket 68: [`1702991` - `1726251`] |
| B069 | `1752554` | Bucket 69: [`1726251` - `1752554`] |
| B070 | `1778916` | Bucket 70: [`1752554` - `1778916`] |
| B071 | `1807938` | Bucket 71: [`1778916` - `1807938`] |
| B072 | `1832794` | Bucket 72: [`1807938` - `1832794`] |
| B073 | `1857494` | Bucket 73: [`1832794` - `1857494`] |
| B074 | `1883037` | Bucket 74: [`1857494` - `1883037`] |
| B075 | `1909532` | Bucket 75: [`1883037` - `1909532`] |
| B076 | `1934685` | Bucket 76: [`1909532` - `1934685`] |
| B077 | `1958564` | Bucket 77: [`1934685` - `1958564`] |
| B078 | `1982713` | Bucket 78: [`1958564` - `1982713`] |
| B079 | `2006262` | Bucket 79: [`1982713` - `2006262`] |
| B080 | `2030390` | Bucket 80: [`2006262` - `2030390`] |
| B081 | `2056098` | Bucket 81: [`2030390` - `2056098`] |
| B082 | `2081337` | Bucket 82: [`2056098` - `2081337`] |
| B083 | `2105688` | Bucket 83: [`2081337` - `2105688`] |
| B084 | `2129827` | Bucket 84: [`2105688` - `2129827`] |
| B085 | `2152469` | Bucket 85: [`2129827` - `2152469`] |
| B086 | `2176821` | Bucket 86: [`2152469` - `2176821`] |
| B087 | `2200577` | Bucket 87: [`2176821` - `2200577`] |
| B088 | `2228756` | Bucket 88: [`2200577` - `2228756`] |
| B089 | `2252971` | Bucket 89: [`2228756` - `2252971`] |
| B090 | `2278837` | Bucket 90: [`2252971` - `2278837`] |
| B091 | `2303457` | Bucket 91: [`2278837` - `2303457`] |
| B092 | `2329311` | Bucket 92: [`2303457` - `2329311`] |
| B093 | `2354302` | Bucket 93: [`2329311` - `2354302`] |
| B094 | `2378735` | Bucket 94: [`2354302` - `2378735`] |
| B095 | `2405535` | Bucket 95: [`2378735` - `2405535`] |
| B096 | `2430421` | Bucket 96: [`2405535` - `2430421`] |
| B097 | `2453702` | Bucket 97: [`2430421` - `2453702`] |
| B098 | `2478306` | Bucket 98: [`2453702` - `2478306`] |
| B099 | `2504204` | Bucket 99: [`2478306` - `2504204`] |
| B100 | `2528285` | Bucket 100: [`2504204` - `2528285`] |

#### B. Column `title` Bucket Boundaries (101 values, 100 buckets)
| Bucket Index | Boundary Value (`title`) | Lexicographical Interval |
| :---: | :--- | :--- |
| B000 (Start) | `\$ucces Part One` | Start of text data |
| B001 | `(#1.1299)` | Bucket 1: [`\$ucces Part One` - `(#1.1299)`] |
| B002 | `(#12.141)` | Bucket 2: [`(#1.1299)` - `(#12.141)`] |
| B003 | `(#1.3792)` | Bucket 3: [`(#12.141)` - `(#1.3792)`] |
| B004 | `(#1.56)` | Bucket 4: [`(#1.3792)` - `(#1.56)`] |
| B005 | `(#18.11)` | Bucket 5: [`(#1.56)` - `(#18.11)`] |
| B006 | `(1968-06-18)` | Bucket 6: [`(#18.11)` - `(1968-06-18)`] |
| B007 | `(1982-11-08)` | Bucket 7: [`(1968-06-18)` - `(1982-11-08)`] |
| B008 | `(1993-12-27)` | Bucket 8: [`(1982-11-08)` - `(1993-12-27)`] |
| B009 | `(1998-02-10)` | Bucket 9: [`(1993-12-27)` - `(1998-02-10)`] |
| B010 | `(2000-03-28)` | Bucket 10: [`(1998-02-10)` - `(2000-03-28)`] |
| B011 | `(2002-02-22)` | Bucket 11: [`(2000-03-28)` - `(2002-02-22)`] |
| B012 | `2003 AXA Liberty Bowl` | Bucket 12: [`(2002-02-22)` - `2003 AXA Liberty Bowl`] |
| B013 | `(2005-04-14)` | Bucket 13: [`2003 AXA Liberty Bowl` - `(2005-04-14)`] |
| B014 | `(2006-08-15)` | Bucket 14: [`(2005-04-14)` - `(2006-08-15)`] |
| B015 | `(2007-11-04)` | Bucket 15: [`(2006-08-15)` - `(2007-11-04)`] |
| B016 | `(2009-04-16)` | Bucket 16: [`(2007-11-04)` - `(2009-04-16)`] |
| B017 | `(2010-11-13)` | Bucket 17: [`(2009-04-16)` - `(2010-11-13)`] |
| B018 | `(2012-01-09)` | Bucket 18: [`(2010-11-13)` - `(2012-01-09)`] |
| B019 | `2012 BMW 1 Series ActiveE Electric Car` | Bucket 19: [`(2012-01-09)` - `2012 BMW 1 Series ActiveE Electric Car`] |
| B020 | `(#2.33)` | Bucket 20: [`2012 BMW 1 Series ActiveE Electric Car` - `(#2.33)`] |
| B021 | `(#3.32)` | Bucket 21: [`(#2.33)` - `(#3.32)`] |
| B022 | `(#5.1)` | Bucket 22: [`(#3.32)` - `(#5.1)`] |
| B023 | `(#7.186)` | Bucket 23: [`(#5.1)` - `(#7.186)`] |
| B024 | `A Candle for St. Jude` | Bucket 24: [`(#7.186)` - `A Candle for St. Jude`] |
| B025 | `Aftermath` | Bucket 25: [`A Candle for St. Jude` - `Aftermath`] |
| B026 | `Alte Schule` | Bucket 26: [`Aftermath` - `Alte Schule`] |
| B027 | `Anita's Africa` | Bucket 27: [`Alte Schule` - `Anita's Africa`] |
| B028 | `Asik Garip` | Bucket 28: [`Anita's Africa` - `Asik Garip`] |
| B029 | `A Yen for Lester` | Bucket 29: [`Asik Garip` - `A Yen for Lester`] |
| B030 | `Beatmania IIDX 18: Resort Anthem` | Bucket 30: [`A Yen for Lester` - `Beatmania IIDX 18: Resort Anthem`] |
| B031 | `Bill's Thud` | Bucket 31: [`Beatmania IIDX 18: Resort Anthem` - `Bill's Thud`] |
| B032 | `Bôryaku` | Bucket 32: [`Bill's Thud` - `Bôryaku`] |
| B033 | `Business Must Not Interfere` | Bucket 33: [`Bôryaku` - `Business Must Not Interfere`] |
| B034 | `Celebrities at SEMA 2008` | Bucket 34: [`Business Must Not Interfere` - `Celebrities at SEMA 2008`] |
| B035 | `Christos Chrissopoulos` | Bucket 35: [`Celebrities at SEMA 2008` - `Christos Chrissopoulos`] |
| B036 | `Company` | Bucket 36: [`Christos Chrissopoulos` - `Company`] |
| B037 | `Dad's Army` | Bucket 37: [`Company` - `Dad's Army`] |
| B038 | `Dear Diary` | Bucket 38: [`Dad's Army` - `Dear Diary`] |
| B039 | `Der Reinfall` | Bucket 39: [`Dear Diary` - `Der Reinfall`] |
| B040 | `Die Übermacht` | Bucket 40: [`Der Reinfall` - `Die Übermacht`] |
| B041 | `Double Exposure` | Bucket 41: [`Die Übermacht` - `Double Exposure`] |
| B042 | `Ego` | Bucket 42: [`Double Exposure` - `Ego`] |
| B043 | `El zagal y las ovejas` | Bucket 43: [`Ego` - `El zagal y las ovejas`] |
| B044 | `Every Day Above Ground Is a Good Day` | Bucket 44: [`El zagal y las ovejas` - `Every Day Above Ground Is a Good Day`] |
| B045 | `Ferien auf dem Martinshof` | Bucket 45: [`Every Day Above Ground Is a Good Day` - `Ferien auf dem Martinshof`] |
| B046 | `Forgiving Your P.E. Teacher` | Bucket 46: [`Ferien auf dem Martinshof` - `Forgiving Your P.E. Teacher`] |
| B047 | `Game Over` | Bucket 47: [`Forgiving Your P.E. Teacher` - `Game Over`] |
| B048 | `God and the Man` | Bucket 48: [`Game Over` - `God and the Man`] |
| B049 | `Gyözelemröl gyözelemre` | Bucket 49: [`God and the Man` - `Gyözelemröl gyözelemre`] |
| B050 | `Hemingway` | Bucket 50: [`Gyözelemröl gyözelemre` - `Hemingway`] |
| B051 | `Homeland in War` | Bucket 51: [`Hemingway` - `Homeland in War`] |
| B052 | `Ich oder Du` | Bucket 52: [`Homeland in War` - `Ich oder Du`] |
| B053 | `Inheritance` | Bucket 53: [`Ich oder Du` - `Inheritance`] |
| B054 | `It's a Wonderful Life` | Bucket 54: [`Inheritance` - `It's a Wonderful Life`] |
| B055 | `Joe Curren` | Bucket 55: [`It's a Wonderful Life` - `Joe Curren`] |
| B056 | `Karen Han` | Bucket 56: [`Joe Curren` - `Karen Han`] |
| B057 | `Kobe Bryant` | Bucket 57: [`Karen Han` - `Kobe Bryant`] |
| B058 | `La garçonne` | Bucket 58: [`Kobe Bryant` - `La garçonne`] |
| B059 | `La terre étrangère` | Bucket 59: [`La garçonne` - `La terre étrangère`] |
| B060 | `Les étrangers` | Bucket 60: [`La terre étrangère` - `Les étrangers`] |
| B061 | `Little Rock: The Politics of Murder` | Bucket 61: [`Les étrangers` - `Little Rock: The Politics of Murder`] |
| B062 | `Lucka 21` | Bucket 62: [`Little Rock: The Politics of Murder` - `Lucka 21`] |
| B063 | `Mar adentro` | Bucket 63: [`Lucka 21` - `Mar adentro`] |
| B064 | `Memoirs` | Bucket 64: [`Mar adentro` - `Memoirs`] |
| B065 | `Miss Shellagh's Miniskirt` | Bucket 65: [`Memoirs` - `Miss Shellagh's Miniskirt`] |
| B066 | `Mr. Lincoln's Springfield` | Bucket 66: [`Miss Shellagh's Miniskirt` - `Mr. Lincoln's Springfield`] |
| B067 | `Napfény a jégen` | Bucket 67: [`Mr. Lincoln's Springfield` - `Napfény a jégen`] |
| B068 | `Një natë pa dritë` | Bucket 68: [`Napfény a jégen` - `Një natë pa dritë`] |
| B069 | `Odcinek 35` | Bucket 69: [`Një natë pa dritë` - `Odcinek 35`] |
| B070 | `Operation Moonshine` | Bucket 70: [`Odcinek 35` - `Operation Moonshine`] |
| B071 | `Panic Room` | Bucket 71: [`Operation Moonshine` - `Panic Room`] |
| B072 | `Pgisha Iveret` | Bucket 72: [`Panic Room` - `Pgisha Iveret`] |
| B073 | `Postia` | Bucket 73: [`Pgisha Iveret` - `Postia`] |
| B074 | `Que a paz sexa con vosco` | Bucket 74: [`Postia` - `Que a paz sexa con vosco`] |
| B075 | `Relieved of Command/Belafonte/Who Poisoned the Children?` | Bucket 75: [`Que a paz sexa con vosco` - `Relieved of Command/Belafonte/Who Poisoned the Children?`] |
| B076 | `Roll Call` | Bucket 76: [`Relieved of Command/Belafonte/Who Poisoned the Children?` - `Roll Call`] |
| B077 | `Sammie Johnsin in Mexico` | Bucket 77: [`Roll Call` - `Sammie Johnsin in Mexico`] |
| B078 | `Seizure Dogs` | Bucket 78: [`Sammie Johnsin in Mexico` - `Seizure Dogs`] |
| B079 | `Show #486 - Wie geht es Speedy? & Playmobil Don Giovanni` | Bucket 79: [`Seizure Dogs` - `Show #486 - Wie geht es Speedy? & Playmobil Don Giovanni`] |
| B080 | `Snow Buddies/Aristocats` | Bucket 80: [`Show #486 - Wie geht es Speedy? & Playmobil Don Giovanni` - `Snow Buddies/Aristocats`] |
| B081 | `Spooky Spots` | Bucket 81: [`Snow Buddies/Aristocats` - `Spooky Spots`] |
| B082 | `Sucedió en el internado` | Bucket 82: [`Spooky Spots` - `Sucedió en el internado`] |
| B083 | `Targets` | Bucket 83: [`Sucedió en el internado` - `Targets`] |
| B084 | `The Amazing Race Philippines` | Bucket 84: [`Targets` - `The Amazing Race Philippines`] |
| B085 | `The Case of the Purple Pool` | Bucket 85: [`The Amazing Race Philippines` - `The Case of the Purple Pool`] |
| B086 | `The Education of Shelby Knox` | Bucket 86: [`The Case of the Purple Pool` - `The Education of Shelby Knox`] |
| B087 | `The Grudge` | Bucket 87: [`The Education of Shelby Knox` - `The Grudge`] |
| B088 | `The Light in Her Eyes` | Bucket 88: [`The Grudge` - `The Light in Her Eyes`] |
| B089 | `The Oddball Parade` | Bucket 89: [`The Light in Her Eyes` - `The Oddball Parade`] |
| B090 | `The Revenger` | Bucket 90: [`The Oddball Parade` - `The Revenger`] |
| B091 | `The Take Out` | Bucket 91: [`The Revenger` - `The Take Out`] |
| B092 | `They are Five` | Bucket 92: [`The Take Out` - `They are Five`] |
| B093 | `Tomodachi` | Bucket 93: [`They are Five` - `Tomodachi`] |
| B094 | `True Anal Stories 23` | Bucket 94: [`Tomodachi` - `True Anal Stories 23`] |
| B095 | `Un esprit clairvoyant` | Bucket 95: [`True Anal Stories 23` - `Un esprit clairvoyant`] |
| B096 | `Very Bad Men` | Bucket 96: [`Un esprit clairvoyant` - `Very Bad Men`] |
| B097 | `Watashi no kokoro wa papa no mono` | Bucket 97: [`Very Bad Men` - `Watashi no kokoro wa papa no mono`] |
| B098 | `White Wedding` | Bucket 98: [`Watashi no kokoro wa papa no mono` - `White Wedding`] |
| B099 | `Yama ga aru kara...... Part 5` | Bucket 99: [`White Wedding` - `Yama ga aru kara...... Part 5`] |
| B100 | `Þorsteinn Pálsson` | Bucket 100: [`Yama ga aru kara...... Part 5` - `Þorsteinn Pálsson`] |

### 6. Histogram Visualization
![Histogram for title.id](../plots/q1_histogram_id.png)

![Histogram for title.title](../plots/q1_histogram_title.png)

### 7. Max Selectivity Error
- **Max Selectivity Error**: Since `default_statistics_target` is 100, there are 100 buckets. Therefore, the maximum selectivity error for a range query is bounded by:
$$\text{Max Error} \le \frac{1}{B} = \frac{1}{100} = 0.01 \quad (1.0\%)$$
For evaluated queries(q9), the observed maximum selectivity error is **0.8031%** (0.008031), which strictly satisfies $\text{Max Error} \le 1.0\%$.

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
- **Estimated Selectivity:** The planner estimated 1,938,445 rows: $S_{est} = \frac{1938445}{2528312} \approx 0.7667$ (76.67%).

- **Observation:** The absolute error is roughly 0.80%.

**Query 2: `id < 350000`**
```sql
EXPLAIN ANALYZE SELECT * FROM title WHERE title.id < '350000';
```
- **Actual Selectivity:** The query returned 349,999 matching rows: $S_{act} = \frac{349999}{2528312} \approx 0.1384$ (13.84%).

```sql
EXPLAIN SELECT * FROM title WHERE title.id < '350000';
```
- **Estimated Selectivity:** The planner estimated 350,549 rows: $S_{est} = \frac{350549}{2528312} \approx 0.1386$ (13.86%).

- **Observation:** The absolute error here is about 0.02%.

---

## Q2. Optimal Serial Histogram Construction ($B=10$ Buckets)

### 1. Histogram Visualizations for Exact $N = 3000$ Samples (Slide-9 Upright Vertical Block Plots)
*As defined in lecture Slide 9, a Serial Histogram sorts domain values by their ordered frequencies ($f(v_{(1)}) \le f(v_{(2)}) \le \dots \le f(v_{(m)})$) and partitions the frequency space to minimize frequency variance $\sum n_i V_i$. The upright vertical block plots below feature Frequencies on the X-axis (ordered ascending) and Value Set / Stacked Domain Elements on the Y-axis:*

![Correct Conceptual Plot for Unique title.id (N=3000)](../plots/q2_histogram_id_3000.png)

![Q2: For title.title (N=3000) - Correct V-Optimal Serial Histogram](../plots/q2_histogram_title_3000.png)

### 2. Execution Build Time (Average over 3 Runs)
- **Average Build Time for $N=3000$**: **0.0017 seconds** (`id` column) / **0.0062 seconds** (`title` column)

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
| **1000** | `id` | `0.020667` | `0.013333` | `0.016556` | **`0.016852`** | `0.0006s` |
| **1000** | `title` | `0.637000` | `0.625000` | `0.169333` | **`0.477111`** | `0.0013s` |
| **3000** | `id` | `0.022444` | `0.009556` | `0.009889` | **`0.013963`** | `0.0017s` |
| **3000** | `title` | `0.612556` | `0.609000` | `0.616667` | **`0.612741`** | `0.0062s` |
| **5000** | `id` | `0.013578` | `0.005778` | `0.007556` | **`0.008970`** | `0.0033s` |
| **5000** | `title` | `0.603667` | `0.600667` | `0.606400` | **`0.603578`** | `0.0080s` |

---

### 6. Full Step-by-Step Linear Regression Extrapolation ($N = 2,528,312$)

To extrapolate the construction build time for the entire `title` table ($N = 2,528,312$), we fit a linear regression model on the 3-run average measured build times:
$$T(N) = m \cdot N + c$$

#### A. Sample Data Points $(N_i, T_i)$
- Point 1: $(N_1, T_1) = (1000, 0.0006)$
- Point 2: $(N_2, T_2) = (3000, 0.0017)$
- Point 3: $(N_3, T_3) = (5000, 0.0033)$

#### B. Mean Calculations
- $\bar{N} = \frac{1000 + 3000 + 5000}{3} = \mathbf{3000}$
- $\bar{T} = \frac{0.0006 + 0.0017 + 0.0033}{3} = \mathbf{0.0019\text{ seconds}}$

#### C. Deviations & Sum of Products
| $N_i$ | $T_i$ (s) | $(N_i - \bar{N})$ | $(T_i - \bar{T})$ | $(N_i - \bar{N})^2$ | $(N_i - \bar{N})(T_i - \bar{T})$ |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1000 | 0.0006 | -2000 | -0.0013 | 4,000,000 | 2.5680 |
| 3000 | 0.0017 | 0 | -0.0002 | 0 | -0.0000 |
| 5000 | 0.0033 | +2000 | 0.0014 | 4,000,000 | 2.8752 |
| **Sum** | | | | **8,000,000** | **5.4433** |

#### D. Slope ($m$) and Intercept ($c$) Formulas
- **Slope ($m$)**:
  $$m = \frac{\sum (N_i - \bar{N})(T_i - \bar{T})}{\sum (N_i - \bar{N})^2} = \frac{5.4433}{8,000,000} = \mathbf{0.00000068\text{ seconds / sample}}$$

- **Intercept ($c$)**:
  $$c = \bar{T} - m \cdot \bar{N} = 0.0019 - (0.00000068 \times 3000) = \mathbf{-0.000172\text{ seconds}}$$

#### E. Extrapolated Build Time for Full Table ($N = 2,528,312$)
$$T(2,528,312) = (0.00000068 \times 2,528,312) + (-0.000172) = \mathbf{1.72\text{ seconds}} \quad (\mathbf{0.03\text{ minutes}})$$

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
