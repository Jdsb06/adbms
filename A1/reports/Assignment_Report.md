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
psql uses an equi depth histogram , where bucket bounderies are as such so that roughly the same number of tuples in each bucket

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
3. Encoding initial string prefix bytes into floating point numbers in $[0.0, 1.0]$ range for quantitative interpolation like laptop will be broken to lap with l = 108, a=97, p=112 then by 256 as between 0 and 1 , lap will be around 0.42 , we can then see where a key belongs between two keeys 
4. Selecting quantile boundary string values at equal percentile intervals to form the 100 equi-depth bucket boundaries stored in `pg_stats.histogram_bounds`.

### 5. Exact Bucket Boundaries List (From `pg_stats`)

#### A. Column `id` Bucket Boundaries (101 values, 100 buckets)
| Bucket Index | Boundary Value (`id`) | Bucket Interval |
| :---: | :---: | :--- |
| B000 (Start) | `71` | Start of table data |
| B001 | `22629` | Bucket 1: [`71` - `22629`] |
| B002 | `47883` | Bucket 2: [`22629` - `47883`] |
| B003 | `70297` | Bucket 3: [`47883` - `70297`] |
| B004 | `96345` | Bucket 4: [`70297` - `96345`] |
| B005 | `122972` | Bucket 5: [`96345` - `122972`] |
| B006 | `151571` | Bucket 6: [`122972` - `151571`] |
| B007 | `178176` | Bucket 7: [`151571` - `178176`] |
| B008 | `202083` | Bucket 8: [`178176` - `202083`] |
| B009 | `228264` | Bucket 9: [`202083` - `228264`] |
| B010 | `253450` | Bucket 10: [`228264` - `253450`] |
| B011 | `277435` | Bucket 11: [`253450` - `277435`] |
| B012 | `302244` | Bucket 12: [`277435` - `302244`] |
| B013 | `327412` | Bucket 13: [`302244` - `327412`] |
| B014 | `351277` | Bucket 14: [`327412` - `351277`] |
| B015 | `375269` | Bucket 15: [`351277` - `375269`] |
| B016 | `398105` | Bucket 16: [`375269` - `398105`] |
| B017 | `419318` | Bucket 17: [`398105` - `419318`] |
| B018 | `447243` | Bucket 18: [`419318` - `447243`] |
| B019 | `470857` | Bucket 19: [`447243` - `470857`] |
| B020 | `497328` | Bucket 20: [`470857` - `497328`] |
| B021 | `523098` | Bucket 21: [`497328` - `523098`] |
| B022 | `548386` | Bucket 22: [`523098` - `548386`] |
| B023 | `573721` | Bucket 23: [`548386` - `573721`] |
| B024 | `597600` | Bucket 24: [`573721` - `597600`] |
| B025 | `620953` | Bucket 25: [`597600` - `620953`] |
| B026 | `644334` | Bucket 26: [`620953` - `644334`] |
| B027 | `669359` | Bucket 27: [`644334` - `669359`] |
| B028 | `694359` | Bucket 28: [`669359` - `694359`] |
| B029 | `719940` | Bucket 29: [`694359` - `719940`] |
| B030 | `746531` | Bucket 30: [`719940` - `746531`] |
| B031 | `772412` | Bucket 31: [`746531` - `772412`] |
| B032 | `799868` | Bucket 32: [`772412` - `799868`] |
| B033 | `822650` | Bucket 33: [`799868` - `822650`] |
| B034 | `846897` | Bucket 34: [`822650` - `846897`] |
| B035 | `872174` | Bucket 35: [`846897` - `872174`] |
| B036 | `897463` | Bucket 36: [`872174` - `897463`] |
| B037 | `923221` | Bucket 37: [`897463` - `923221`] |
| B038 | `945908` | Bucket 38: [`923221` - `945908`] |
| B039 | `973357` | Bucket 39: [`945908` - `973357`] |
| B040 | `1000734` | Bucket 40: [`973357` - `1000734`] |
| B041 | `1023461` | Bucket 41: [`1000734` - `1023461`] |
| B042 | `1048673` | Bucket 42: [`1023461` - `1048673`] |
| B043 | `1071915` | Bucket 43: [`1048673` - `1071915`] |
| B044 | `1100137` | Bucket 44: [`1071915` - `1100137`] |
| B045 | `1124383` | Bucket 45: [`1100137` - `1124383`] |
| B046 | `1149120` | Bucket 46: [`1124383` - `1149120`] |
| B047 | `1175291` | Bucket 47: [`1149120` - `1175291`] |
| B048 | `1201852` | Bucket 48: [`1175291` - `1201852`] |
| B049 | `1228957` | Bucket 49: [`1201852` - `1228957`] |
| B050 | `1257141` | Bucket 50: [`1228957` - `1257141`] |
| B051 | `1284123` | Bucket 51: [`1257141` - `1284123`] |
| B052 | `1308942` | Bucket 52: [`1284123` - `1308942`] |
| B053 | `1335382` | Bucket 53: [`1308942` - `1335382`] |
| B054 | `1361256` | Bucket 54: [`1335382` - `1361256`] |
| B055 | `1387631` | Bucket 55: [`1361256` - `1387631`] |
| B056 | `1411606` | Bucket 56: [`1387631` - `1411606`] |
| B057 | `1436629` | Bucket 57: [`1411606` - `1436629`] |
| B058 | `1461485` | Bucket 58: [`1436629` - `1461485`] |
| B059 | `1487317` | Bucket 59: [`1461485` - `1487317`] |
| B060 | `1510970` | Bucket 60: [`1487317` - `1510970`] |
| B061 | `1533534` | Bucket 61: [`1510970` - `1533534`] |
| B062 | `1560080` | Bucket 62: [`1533534` - `1560080`] |
| B063 | `1586138` | Bucket 63: [`1560080` - `1586138`] |
| B064 | `1612928` | Bucket 64: [`1586138` - `1612928`] |
| B065 | `1638329` | Bucket 65: [`1612928` - `1638329`] |
| B066 | `1661883` | Bucket 66: [`1638329` - `1661883`] |
| B067 | `1686067` | Bucket 67: [`1661883` - `1686067`] |
| B068 | `1711184` | Bucket 68: [`1686067` - `1711184`] |
| B069 | `1735833` | Bucket 69: [`1711184` - `1735833`] |
| B070 | `1763217` | Bucket 70: [`1735833` - `1763217`] |
| B071 | `1788453` | Bucket 71: [`1763217` - `1788453`] |
| B072 | `1814568` | Bucket 72: [`1788453` - `1814568`] |
| B073 | `1836400` | Bucket 73: [`1814568` - `1836400`] |
| B074 | `1861486` | Bucket 74: [`1836400` - `1861486`] |
| B075 | `1887550` | Bucket 75: [`1861486` - `1887550`] |
| B076 | `1914087` | Bucket 76: [`1887550` - `1914087`] |
| B077 | `1938329` | Bucket 77: [`1914087` - `1938329`] |
| B078 | `1962799` | Bucket 78: [`1938329` - `1962799`] |
| B079 | `1988458` | Bucket 79: [`1962799` - `1988458`] |
| B080 | `2014885` | Bucket 80: [`1988458` - `2014885`] |
| B081 | `2038757` | Bucket 81: [`2014885` - `2038757`] |
| B082 | `2064538` | Bucket 82: [`2038757` - `2064538`] |
| B083 | `2089516` | Bucket 83: [`2064538` - `2089516`] |
| B084 | `2115434` | Bucket 84: [`2089516` - `2115434`] |
| B085 | `2140641` | Bucket 85: [`2115434` - `2140641`] |
| B086 | `2166812` | Bucket 86: [`2140641` - `2166812`] |
| B087 | `2190040` | Bucket 87: [`2166812` - `2190040`] |
| B088 | `2218367` | Bucket 88: [`2190040` - `2218367`] |
| B089 | `2246129` | Bucket 89: [`2218367` - `2246129`] |
| B090 | `2270048` | Bucket 90: [`2246129` - `2270048`] |
| B091 | `2295684` | Bucket 91: [`2270048` - `2295684`] |
| B092 | `2322768` | Bucket 92: [`2295684` - `2322768`] |
| B093 | `2345812` | Bucket 93: [`2322768` - `2345812`] |
| B094 | `2373919` | Bucket 94: [`2345812` - `2373919`] |
| B095 | `2397988` | Bucket 95: [`2373919` - `2397988`] |
| B096 | `2425418` | Bucket 96: [`2397988` - `2425418`] |
| B097 | `2449900` | Bucket 97: [`2425418` - `2449900`] |
| B098 | `2475221` | Bucket 98: [`2449900` - `2475221`] |
| B099 | `2502193` | Bucket 99: [`2475221` - `2502193`] |
| B100 | `2528277` | Bucket 100: [`2502193` - `2528277`] |

#### B. Column `title` Bucket Boundaries (101 values, 100 buckets)
| Bucket Index | Boundary Value (`title`) | Lexicographical Interval |
| :---: | :--- | :--- |
| B000 (Start) | `\$25 Million Dollar Hoax` | Start of text data |
| B001 | `(#1.126)` | Bucket 1: [`\$25 Million Dollar Hoax` - `(#1.126)`] |
| B002 | `(#1.200)` | Bucket 2: [`(#1.126)` - `(#1.200)`] |
| B003 | `(#13.49)` | Bucket 3: [`(#1.200)` - `(#13.49)`] |
| B004 | `(#1.5527)` | Bucket 4: [`(#13.49)` - `(#1.5527)`] |
| B005 | `(#1.765)` | Bucket 5: [`(#1.5527)` - `(#1.765)`] |
| B006 | `(1961-05-01)` | Bucket 6: [`(#1.765)` - `(1961-05-01)`] |
| B007 | `(1978-12-09)` | Bucket 7: [`(1961-05-01)` - `(1978-12-09)`] |
| B008 | `(1993-01-04)` | Bucket 8: [`(1978-12-09)` - `(1993-01-04)`] |
| B009 | `(1997-01-16)` | Bucket 9: [`(1993-01-04)` - `(1997-01-16)`] |
| B010 | `(1999-07-05)` | Bucket 10: [`(1997-01-16)` - `(1999-07-05)`] |
| B011 | `(2001-05-05)` | Bucket 11: [`(1999-07-05)` - `(2001-05-05)`] |
| B012 | `(2003-03-11)` | Bucket 12: [`(2001-05-05)` - `(2003-03-11)`] |
| B013 | `(2004-09-18)` | Bucket 13: [`(2003-03-11)` - `(2004-09-18)`] |
| B014 | `(2005-12-07)` | Bucket 14: [`(2004-09-18)` - `(2005-12-07)`] |
| B015 | `(2007-05-09)` | Bucket 15: [`(2005-12-07)` - `(2007-05-09)`] |
| B016 | `(2008-10-29)` | Bucket 16: [`(2007-05-09)` - `(2008-10-29)`] |
| B017 | `(2010-06-15)` | Bucket 17: [`(2008-10-29)` - `(2010-06-15)`] |
| B018 | `(2011-09-20)` | Bucket 18: [`(2010-06-15)` - `(2011-09-20)`] |
| B019 | `(2012-08-16)` | Bucket 19: [`(2011-09-20)` - `(2012-08-16)`] |
| B020 | `(#2.112)` | Bucket 20: [`(2012-08-16)` - `(#2.112)`] |
| B021 | `(#3.120)` | Bucket 21: [`(#2.112)` - `(#3.120)`] |
| B022 | `(#4.84)` | Bucket 22: [`(#3.120)` - `(#4.84)`] |
| B023 | `(#7.13)` | Bucket 23: [`(#4.84)` - `(#7.13)`] |
| B024 | `Abschiede` | Bucket 24: [`(#7.13)` - `Abschiede`] |
| B025 | `After All I've Said!` | Bucket 25: [`Abschiede` - `After All I've Said!`] |
| B026 | `All for Love` | Bucket 26: [`After All I've Said!` - `All for Love`] |
| B027 | `And the Wind Cries... Wendigo` | Bucket 27: [`All for Love` - `And the Wind Cries... Wendigo`] |
| B028 | `Arena total 12 - Volle Spermabacken` | Bucket 28: [`And the Wind Cries... Wendigo` - `Arena total 12 - Volle Spermabacken`] |
| B029 | `Auf den Hund gekommen` | Bucket 29: [`Arena total 12 - Volle Spermabacken` - `Auf den Hund gekommen`] |
| B030 | `Bandaged` | Bucket 30: [`Auf den Hund gekommen` - `Bandaged`] |
| B031 | `Best Neighbor` | Bucket 31: [`Bandaged` - `Best Neighbor`] |
| B032 | `Blood Bank` | Bucket 32: [`Best Neighbor` - `Blood Bank`] |
| B033 | `Brudekronen` | Bucket 33: [`Blood Bank` - `Brudekronen`] |
| B034 | `Care Bears: The Giving Festival Movie` | Bucket 34: [`Brudekronen` - `Care Bears: The Giving Festival Movie`] |
| B035 | `Chief Guard Saldeath's Trap! Level 3: Starvation Hell!` | Bucket 35: [`Care Bears: The Giving Festival Movie` - `Chief Guard Saldeath's Trap! Level 3: Starvation Hell!`] |
| B036 | `Come and Get It` | Bucket 36: [`Chief Guard Saldeath's Trap! Level 3: Starvation Hell!` - `Come and Get It`] |
| B037 | `Crni fond` | Bucket 37: [`Come and Get It` - `Crni fond`] |
| B038 | `Das ist mein Tagwerk` | Bucket 38: [`Crni fond` - `Das ist mein Tagwerk`] |
| B039 | `Delta Queen` | Bucket 39: [`Das ist mein Tagwerk` - `Delta Queen`] |
| B040 | `Deux filles en cavale` | Bucket 40: [`Delta Queen` - `Deux filles en cavale`] |
| B041 | `Dishin on Dishes` | Bucket 41: [`Deux filles en cavale` - `Dishin on Dishes`] |
| B042 | `Drift` | Bucket 42: [`Dishin on Dishes` - `Drift`] |
| B043 | `El Aborto` | Bucket 43: [`Drift` - `El Aborto`] |
| B044 | `Ensayo de una noche de bodas` | Bucket 44: [`El Aborto` - `Ensayo de una noche de bodas`] |
| B045 | `Fake Orgasm` | Bucket 45: [`Ensayo de una noche de bodas` - `Fake Orgasm`] |
| B046 | `First Place` | Bucket 46: [`Fake Orgasm` - `First Place`] |
| B047 | `Freeride World Tour` | Bucket 47: [`First Place` - `Freeride World Tour`] |
| B048 | `Gerhard Haderer - Der Kult-Karikaturist` | Bucket 48: [`Freeride World Tour` - `Gerhard Haderer - Der Kult-Karikaturist`] |
| B049 | `Grad Nite` | Bucket 49: [`Gerhard Haderer - Der Kult-Karikaturist` - `Grad Nite`] |
| B050 | `Hanging On` | Bucket 50: [`Grad Nite` - `Hanging On`] |
| B051 | `Herz über Kopf` | Bucket 51: [`Hanging On` - `Herz über Kopf`] |
| B052 | `Horny College Schoolgirls` | Bucket 52: [`Herz über Kopf` - `Horny College Schoolgirls`] |
| B053 | `I Hope I Am Crazy` | Bucket 53: [`Horny College Schoolgirls` - `I Hope I Am Crazy`] |
| B054 | `Instinto fatal` | Bucket 54: [`I Hope I Am Crazy` - `Instinto fatal`] |
| B055 | `Jai Bajrang` | Bucket 55: [`Instinto fatal` - `Jai Bajrang`] |
| B056 | `Judgment Day` | Bucket 56: [`Jai Bajrang` - `Judgment Day`] |
| B057 | `Kenny Chesney: Road Case - The Movie` | Bucket 57: [`Judgment Day` - `Kenny Chesney: Road Case - The Movie`] |
| B058 | `Kreuzfeuer` | Bucket 58: [`Kenny Chesney: Road Case - The Movie` - `Kreuzfeuer`] |
| B059 | `La mitad` | Bucket 59: [`Kreuzfeuer` - `La mitad`] |
| B060 | `LeBron vs Kobe` | Bucket 60: [`La mitad` - `LeBron vs Kobe`] |
| B061 | `Le trait d'union` | Bucket 61: [`LeBron vs Kobe` - `Le trait d'union`] |
| B062 | `Long Time Legends` | Bucket 62: [`Le trait d'union` - `Long Time Legends`] |
| B063 | `Macula` | Bucket 63: [`Long Time Legends` - `Macula`] |
| B064 | `Máscaras mojadas` | Bucket 64: [`Macula` - `Máscaras mojadas`] |
| B065 | `Midnight Eyes` | Bucket 65: [`Máscaras mojadas` - `Midnight Eyes`] |
| B066 | `Monsters Inside Me` | Bucket 66: [`Midnight Eyes` - `Monsters Inside Me`] |
| B067 | `My Name Is Manolete` | Bucket 67: [`Monsters Inside Me` - `My Name Is Manolete`] |
| B068 | `New York Fight Clubs` | Bucket 68: [`My Name Is Manolete` - `New York Fight Clubs`] |
| B069 | `Nun va Goldoon` | Bucket 69: [`New York Fight Clubs` - `Nun va Goldoon`] |
| B070 | `Only Schmucks Pay Income Tax` | Bucket 70: [`Nun va Goldoon` - `Only Schmucks Pay Income Tax`] |
| B071 | `Paidali Padleli Phule` | Bucket 71: [`Only Schmucks Pay Income Tax` - `Paidali Padleli Phule`] |
| B072 | `Peter Townend` | Bucket 72: [`Paidali Padleli Phule` - `Peter Townend`] |
| B073 | `Pop rendez-vous` | Bucket 73: [`Peter Townend` - `Pop rendez-vous`] |
| B074 | `Punto y raya` | Bucket 74: [`Pop rendez-vous` - `Punto y raya`] |
| B075 | `Red Boot Diaries` | Bucket 75: [`Punto y raya` - `Red Boot Diaries`] |
| B076 | `Rocket Dog` | Bucket 76: [`Red Boot Diaries` - `Rocket Dog`] |
| B077 | `Sammy Hagar` | Bucket 77: [`Rocket Dog` - `Sammy Hagar`] |
| B078 | `Secret Life of Cats` | Bucket 78: [`Sammy Hagar` - `Secret Life of Cats`] |
| B079 | `Shihe no meikyu` | Bucket 79: [`Secret Life of Cats` - `Shihe no meikyu`] |
| B080 | `Sluby i rozstania` | Bucket 80: [`Shihe no meikyu` - `Sluby i rozstania`] |
| B081 | `Splintered` | Bucket 81: [`Sluby i rozstania` - `Splintered`] |
| B082 | `Sucre noir` | Bucket 82: [`Splintered` - `Sucre noir`] |
| B083 | `Take Down` | Bucket 83: [`Sucre noir` - `Take Down`] |
| B084 | `The \$1.98 Beauty Show` | Bucket 84: [`Take Down` - `The \$1.98 Beauty Show`] |
| B085 | `The Brewing of Coffee Date` | Bucket 85: [`The \$1.98 Beauty Show` - `The Brewing of Coffee Date`] |
| B086 | `The Diamond Smugglers!` | Bucket 86: [`The Brewing of Coffee Date` - `The Diamond Smugglers!`] |
| B087 | `The Gray Seasons` | Bucket 87: [`The Diamond Smugglers!` - `The Gray Seasons`] |
| B088 | `The Last Superhero` | Bucket 88: [`The Gray Seasons` - `The Last Superhero`] |
| B089 | `The Murderer` | Bucket 89: [`The Last Superhero` - `The Murderer`] |
| B090 | `The Real Deal` | Bucket 90: [`The Murderer` - `The Real Deal`] |
| B091 | `The Student Who Never Was` | Bucket 91: [`The Real Deal` - `The Student Who Never Was`] |
| B092 | `The World Through the Eyes of Children` | Bucket 92: [`The Student Who Never Was` - `The World Through the Eyes of Children`] |
| B093 | `To Mars...` | Bucket 93: [`The World Through the Eyes of Children` - `To Mars...`] |
| B094 | `Troubled Waters` | Bucket 94: [`To Mars...` - `Troubled Waters`] |
| B095 | `Understudies` | Bucket 95: [`Troubled Waters` - `Understudies`] |
| B096 | `Venecia` | Bucket 96: [`Understudies` - `Venecia`] |
| B097 | `Walt and Lavinia` | Bucket 97: [`Venecia` - `Walt and Lavinia`] |
| B098 | `While Shepherds Watched` | Bucket 98: [`Walt and Lavinia` - `While Shepherds Watched`] |
| B099 | `Xin leng xue shi san ying` | Bucket 99: [`While Shepherds Watched` - `Xin leng xue shi san ying`] |
| B100 | `ZZ Top: Sleeping Bag` | Bucket 100: [`Xin leng xue shi san ying` - `ZZ Top: Sleeping Bag`] |

### 6. Histogram Visualization
![Histogram for title.id](../plots/q1_histogram_id.png)

![Histogram for title.title](../plots/q1_histogram_title.png)

### 7. Max Selectivity Error
- **Max Selectivity Error**: Since `default_statistics_target` is 100, there are 100 buckets. Therefore, the maximum selectivity error for a range query is bounded by:
$$\text{Max Error} \le \frac{1}{B} = \frac{1}{100} = 0.01 \quad (1.0\%)$$
For evaluated queries(q9), the observed maximum selectivity error is **0.8592%** (0.008592), which strictly satisfies $\text{Max Error} \le 1.0\%$.

---
### 8: Selectivity Estimation for Text Columns
To estimate selectivity for a range query on a text column like title, psql first looks at the histogrambounds array in pgstats to figure out which bucket contains the query string, once it finds the target bucket, it counts all the full buckets that come before it. since it uses an equidepth histogram, each full bucket represents a fixed fraction of the total rows.   For the specific bucket where the string actually falls, psql assumes the data is uniformly distributed and uses linear interpolation. It converts the first few bytes of the strings into floating point numbers between 0 and 1. This allows it to calculate the mathematical fraction of exactly where the query string sits between the buckets minimum and maximum boundaries. finally it adds this fractional piece to the sum of the preceding full buckets to get the final overall selectivity estimate

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
- **Estimated Selectivity:** The planner estimated 1,939,865 rows: $S_{est} = \frac{1939865}{2528312} \approx 0.7673$ (76.73%).

- **Observation:** The absolute error is roughly 0.86%.

**Query 2: `id < 350000`**
```sql
EXPLAIN ANALYZE SELECT * FROM title WHERE title.id < '350000';
```
- **Actual Selectivity:** The query returned 349,999 matching rows: $S_{act} = \frac{349999}{2528312} \approx 0.1384$ (13.84%).

```sql
EXPLAIN SELECT * FROM title WHERE title.id < '350000';
```
- **Estimated Selectivity:** The planner estimated 352,649 rows: $S_{est} = \frac{352649}{2528312} \approx 0.1395$ (13.95%).

- **Observation:** The absolute error here is about 0.10%.

---

## Q2. Optimal Serial Histogram Construction ($B=10$ Buckets)

### 1. Histogram Visualizations for Exact $N = 3000$ Samples (Slide-9 Upright Vertical Block Plots)
*As defined in lecture Slide 9, a Serial Histogram sorts domain values by their ordered frequencies ($f(v_{(1)}) \le f(v_{(2)}) \le \dots \le f(v_{(m)})$) and partitions the frequency space to minimize frequency variance $\sum n_i V_i$. The upright vertical block plots below feature Frequencies on the X-axis (ordered ascending) and Value Set / Stacked Domain Elements on the Y-axis:*

![Correct Conceptual Plot for Unique title.id (N=3000)](../plots/q2_histogram_id_3000.png)

![Q2: For title.title (N=3000) - Correct V-Optimal Serial Histogram](../plots/q2_histogram_title_3000.png)

### 2. Execution Build Time (Average over 3 Runs)
- **Average Build Time for $N=3000$**: **0.0018 seconds** (`id` column) / **0.0048 seconds** (`title` column)

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
| **1000** | `title` | `0.637000` | `0.625000` | `0.169333` | **`0.477111`** | `0.0015s` |
| **3000** | `id` | `0.022444` | `0.009556` | `0.009889` | **`0.013963`** | `0.0018s` |
| **3000** | `title` | `0.612556` | `0.609000` | `0.616667` | **`0.612741`** | `0.0048s` |
| **5000** | `id` | `0.013578` | `0.005778` | `0.007556` | **`0.008970`** | `0.0029s` |
| **5000** | `title` | `0.603667` | `0.600667` | `0.606400` | **`0.603578`** | `0.0080s` |

---

### 6. Full Step-by-Step Linear Regression Extrapolation ($N = 2,528,312$)

To extrapolate the construction build time for the entire `title` table ($N = 2,528,312$), we fit a linear regression model on the 3-run average measured build times:
$$T(N) = m \cdot N + c$$

#### A. Sample Data Points $(N_i, T_i)$
- Point 1: $(N_1, T_1) = (1000, 0.0006)$
- Point 2: $(N_2, T_2) = (3000, 0.0018)$
- Point 3: $(N_3, T_3) = (5000, 0.0029)$

#### B. Mean Calculations
- $\bar{N} = \frac{1000 + 3000 + 5000}{3} = \mathbf{3000}$
- $\bar{T} = \frac{0.0006 + 0.0018 + 0.0029}{3} = \mathbf{0.0018\text{ seconds}}$

#### C. Deviations & Sum of Products
| $N_i$ | $T_i$ (s) | $(N_i - \bar{N})$ | $(T_i - \bar{T})$ | $(N_i - \bar{N})^2$ | $(N_i - \bar{N})(T_i - \bar{T})$ |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1000 | 0.0006 | -2000 | -0.0012 | 4,000,000 | 2.3471 |
| 3000 | 0.0018 | 0 | 0.0000 | 0 | 0.0000 |
| 5000 | 0.0029 | +2000 | 0.0012 | 4,000,000 | 2.3192 |
| **Sum** | | | | **8,000,000** | **4.6663** |

#### D. Slope ($m$) and Intercept ($c$) Formulas
- **Slope ($m$)**:
  $$m = \frac{\sum (N_i - \bar{N})(T_i - \bar{T})}{\sum (N_i - \bar{N})^2} = \frac{4.6663}{8,000,000} = \mathbf{0.00000058\text{ seconds / sample}}$$

- **Intercept ($c$)**:
  $$c = \bar{T} - m \cdot \bar{N} = 0.0018 - (0.00000058 \times 3000) = \mathbf{0.000018\text{ seconds}}$$

#### E. Extrapolated Build Time for Full Table ($N = 2,528,312$)
$$T(2,528,312) = (0.00000058 \times 2,528,312) + (0.000018) = \mathbf{1.47\text{ seconds}} \quad (\mathbf{0.02\text{ minutes}})$$

---

### 7. Sample Size vs Time Relationship Plot
![Sample Size vs Time](../plots/q2_sample_size_vs_time.png)

---

### 8. Sample Size vs Max Selectivity Error Relationship Plot
![Sample Size vs Max Selectivity Error](../plots/q2_sample_size_vs_error.png)

---

## 9: The Trade-off of Bucket Counts
Picking the number of buckets B is basically a trade off between how fast the histogram builds and how accurate the query planners estimates are.  If we use a small number of buckets, the DP algo runs much faster since its time complexity is O(B*N^2). It also saves memory in the system catalog and keeps query planning times short. The major downside is that wide buckets lead to higher selectivity errors. The database has to assume the data is uniformly distributed inside those large buckets, which usually isnt true and causes the estimates to lose resolution.  On the other hand using more buckets gives the optimizer a highdefinition picture of the actual data distribution, significantly dropping the max selectivity error. The catch is that computing these optimal partitions takes considerably more CPU time, uses more storage space, and adds overhead during the query planning phase before execution can begin.
