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
To inspect PostgreSQL internal statistics and histogram boundary values stored in `pg_stats`:
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
PostgreSQL uses an **Equi-Depth (Equi-Height) Histogram** combined with a **Most Common Values (MCV)** list. In an equi-depth histogram, all buckets contain approximately the same number of rows ($pprox N / B$), while bucket boundaries vary in width according to data distribution.

### 3. Number of Buckets
- Column `id`: **100 buckets** (101 bucket boundary values)
- Column `title`: **100 buckets** (101 bucket boundary values)

### 4. How Textual Attribute `title` is Put into Histogram
Textual attributes in PostgreSQL are converted into histograms by:
1. Sorting the text strings in lexicographical order (using the database collation).
2. Sampling string values from the table.
3. Encoding initial string prefix bytes into floating-point numbers in $[0.0, 1.0]$ range for quantitative interpolation.
4. Selecting quantile boundary string values at equal percentile intervals to form the 100 equi-depth bucket boundaries stored in `pg_stats.histogram_bounds`.

### 5. Exact Bucket Boundaries List (From `pg_stats`)

#### A. Column `id` Bucket Boundaries (101 values, 100 buckets)
| Bucket Index | Boundary Value (`id`) | Bucket Interval |
| :---: | :---: | :--- |
| B000 (Start) | `41` | Start of table data |
| B001 | `25598` | Bucket 1: [`41` - `25598`] |
| B002 | `50067` | Bucket 2: [`25598` - `50067`] |
| B003 | `75257` | Bucket 3: [`50067` - `75257`] |
| B004 | `101946` | Bucket 4: [`75257` - `101946`] |
| B005 | `129223` | Bucket 5: [`101946` - `129223`] |
| B006 | `155973` | Bucket 6: [`129223` - `155973`] |
| B007 | `181990` | Bucket 7: [`155973` - `181990`] |
| B008 | `208153` | Bucket 8: [`181990` - `208153`] |
| B009 | `234525` | Bucket 9: [`208153` - `234525`] |
| B010 | `259507` | Bucket 10: [`234525` - `259507`] |
| B011 | `287845` | Bucket 11: [`259507` - `287845`] |
| B012 | `314618` | Bucket 12: [`287845` - `314618`] |
| B013 | `340479` | Bucket 13: [`314618` - `340479`] |
| B014 | `366364` | Bucket 14: [`340479` - `366364`] |
| B015 | `393076` | Bucket 15: [`366364` - `393076`] |
| B016 | `418929` | Bucket 16: [`393076` - `418929`] |
| B017 | `443204` | Bucket 17: [`418929` - `443204`] |
| B018 | `472539` | Bucket 18: [`443204` - `472539`] |
| B019 | `497095` | Bucket 19: [`472539` - `497095`] |
| B020 | `521015` | Bucket 20: [`497095` - `521015`] |
| B021 | `547008` | Bucket 21: [`521015` - `547008`] |
| B022 | `571914` | Bucket 22: [`547008` - `571914`] |
| B023 | `600124` | Bucket 23: [`571914` - `600124`] |
| B024 | `624290` | Bucket 24: [`600124` - `624290`] |
| B025 | `648346` | Bucket 25: [`624290` - `648346`] |
| B026 | `673077` | Bucket 26: [`648346` - `673077`] |
| B027 | `698192` | Bucket 27: [`673077` - `698192`] |
| B028 | `723945` | Bucket 28: [`698192` - `723945`] |
| B029 | `747971` | Bucket 29: [`723945` - `747971`] |
| B030 | `774715` | Bucket 30: [`747971` - `774715`] |
| B031 | `801886` | Bucket 31: [`774715` - `801886`] |
| B032 | `825206` | Bucket 32: [`801886` - `825206`] |
| B033 | `852044` | Bucket 33: [`825206` - `852044`] |
| B034 | `878630` | Bucket 34: [`852044` - `878630`] |
| B035 | `903227` | Bucket 35: [`878630` - `903227`] |
| B036 | `929542` | Bucket 36: [`903227` - `929542`] |
| B037 | `951992` | Bucket 37: [`929542` - `951992`] |
| B038 | `976177` | Bucket 38: [`951992` - `976177`] |
| B039 | `1002223` | Bucket 39: [`976177` - `1002223`] |
| B040 | `1027496` | Bucket 40: [`1002223` - `1027496`] |
| B041 | `1053013` | Bucket 41: [`1027496` - `1053013`] |
| B042 | `1076669` | Bucket 42: [`1053013` - `1076669`] |
| B043 | `1101644` | Bucket 43: [`1076669` - `1101644`] |
| B044 | `1127312` | Bucket 44: [`1101644` - `1127312`] |
| B045 | `1153408` | Bucket 45: [`1127312` - `1153408`] |
| B046 | `1177087` | Bucket 46: [`1153408` - `1177087`] |
| B047 | `1200809` | Bucket 47: [`1177087` - `1200809`] |
| B048 | `1228132` | Bucket 48: [`1200809` - `1228132`] |
| B049 | `1251987` | Bucket 49: [`1228132` - `1251987`] |
| B050 | `1276194` | Bucket 50: [`1251987` - `1276194`] |
| B051 | `1300208` | Bucket 51: [`1276194` - `1300208`] |
| B052 | `1325279` | Bucket 52: [`1300208` - `1325279`] |
| B053 | `1350079` | Bucket 53: [`1325279` - `1350079`] |
| B054 | `1375217` | Bucket 54: [`1350079` - `1375217`] |
| B055 | `1399305` | Bucket 55: [`1375217` - `1399305`] |
| B056 | `1424915` | Bucket 56: [`1399305` - `1424915`] |
| B057 | `1447763` | Bucket 57: [`1424915` - `1447763`] |
| B058 | `1472187` | Bucket 58: [`1447763` - `1472187`] |
| B059 | `1496066` | Bucket 59: [`1472187` - `1496066`] |
| B060 | `1520933` | Bucket 60: [`1496066` - `1520933`] |
| B061 | `1548374` | Bucket 61: [`1520933` - `1548374`] |
| B062 | `1572984` | Bucket 62: [`1548374` - `1572984`] |
| B063 | `1597331` | Bucket 63: [`1572984` - `1597331`] |
| B064 | `1621524` | Bucket 64: [`1597331` - `1621524`] |
| B065 | `1646529` | Bucket 65: [`1621524` - `1646529`] |
| B066 | `1671841` | Bucket 66: [`1646529` - `1671841`] |
| B067 | `1697305` | Bucket 67: [`1671841` - `1697305`] |
| B068 | `1720750` | Bucket 68: [`1697305` - `1720750`] |
| B069 | `1746578` | Bucket 69: [`1720750` - `1746578`] |
| B070 | `1771397` | Bucket 70: [`1746578` - `1771397`] |
| B071 | `1796312` | Bucket 71: [`1771397` - `1796312`] |
| B072 | `1821069` | Bucket 72: [`1796312` - `1821069`] |
| B073 | `1846620` | Bucket 73: [`1821069` - `1846620`] |
| B074 | `1871455` | Bucket 74: [`1846620` - `1871455`] |
| B075 | `1897069` | Bucket 75: [`1871455` - `1897069`] |
| B076 | `1923039` | Bucket 76: [`1897069` - `1923039`] |
| B077 | `1951619` | Bucket 77: [`1923039` - `1951619`] |
| B078 | `1975550` | Bucket 78: [`1951619` - `1975550`] |
| B079 | `2001398` | Bucket 79: [`1975550` - `2001398`] |
| B080 | `2025488` | Bucket 80: [`2001398` - `2025488`] |
| B081 | `2048645` | Bucket 81: [`2025488` - `2048645`] |
| B082 | `2075506` | Bucket 82: [`2048645` - `2075506`] |
| B083 | `2099704` | Bucket 83: [`2075506` - `2099704`] |
| B084 | `2124027` | Bucket 84: [`2099704` - `2124027`] |
| B085 | `2146547` | Bucket 85: [`2124027` - `2146547`] |
| B086 | `2170970` | Bucket 86: [`2146547` - `2170970`] |
| B087 | `2195637` | Bucket 87: [`2170970` - `2195637`] |
| B088 | `2221366` | Bucket 88: [`2195637` - `2221366`] |
| B089 | `2249864` | Bucket 89: [`2221366` - `2249864`] |
| B090 | `2274023` | Bucket 90: [`2249864` - `2274023`] |
| B091 | `2299152` | Bucket 91: [`2274023` - `2299152`] |
| B092 | `2325178` | Bucket 92: [`2299152` - `2325178`] |
| B093 | `2352562` | Bucket 93: [`2325178` - `2352562`] |
| B094 | `2378000` | Bucket 94: [`2352562` - `2378000`] |
| B095 | `2403761` | Bucket 95: [`2378000` - `2403761`] |
| B096 | `2428038` | Bucket 96: [`2403761` - `2428038`] |
| B097 | `2452338` | Bucket 97: [`2428038` - `2452338`] |
| B098 | `2479928` | Bucket 98: [`2452338` - `2479928`] |
| B099 | `2505988` | Bucket 99: [`2479928` - `2505988`] |
| B100 | `2528305` | Bucket 100: [`2505988` - `2528305`] |

#### B. Column `title` Bucket Boundaries (101 values, 100 buckets)
| Bucket Index | Boundary Value (`title`) | Lexicographical Interval |
| :---: | :--- | :--- |
| B000 (Start) | `...` | Start of text data |
| B001 | `(#1.1302)` | Bucket 1: [`...` - `(#1.1302)`] |
| B002 | `(#1.219)` | Bucket 2: [`(#1.1302)` - `(#1.219)`] |
| B003 | `(#1.3662)` | Bucket 3: [`(#1.219)` - `(#1.3662)`] |
| B004 | `(#1.59)` | Bucket 4: [`(#1.3662)` - `(#1.59)`] |
| B005 | `(#1.846)` | Bucket 5: [`(#1.59)` - `(#1.846)`] |
| B006 | `(1968-02-14)` | Bucket 6: [`(#1.846)` - `(1968-02-14)`] |
| B007 | `(1982-12-14)` | Bucket 7: [`(1968-02-14)` - `(1982-12-14)`] |
| B008 | `(1994-07-07)` | Bucket 8: [`(1982-12-14)` - `(1994-07-07)`] |
| B009 | `(1998-03-16)` | Bucket 9: [`(1994-07-07)` - `(1998-03-16)`] |
| B010 | `(2000-01-22)` | Bucket 10: [`(1998-03-16)` - `(2000-01-22)`] |
| B011 | `(2001-11-06)` | Bucket 11: [`(2000-01-22)` - `(2001-11-06)`] |
| B012 | `(2003-08-29)` | Bucket 12: [`(2001-11-06)` - `(2003-08-29)`] |
| B013 | `(2005-01-19)` | Bucket 13: [`(2003-08-29)` - `(2005-01-19)`] |
| B014 | `(2006-05-17)` | Bucket 14: [`(2005-01-19)` - `(2006-05-17)`] |
| B015 | `(2007-07-05)` | Bucket 15: [`(2006-05-17)` - `(2007-07-05)`] |
| B016 | `(2009-02-02)` | Bucket 16: [`(2007-07-05)` - `(2009-02-02)`] |
| B017 | `(2010-09-07)` | Bucket 17: [`(2009-02-02)` - `(2010-09-07)`] |
| B018 | `(2011-08-29)` | Bucket 18: [`(2010-09-07)` - `(2011-08-29)`] |
| B019 | `(2012-07-21)` | Bucket 19: [`(2011-08-29)` - `(2012-07-21)`] |
| B020 | `(#20.140)` | Bucket 20: [`(2012-07-21)` - `(#20.140)`] |
| B021 | `(#2.92)` | Bucket 21: [`(#20.140)` - `(#2.92)`] |
| B022 | `(#4.172)` | Bucket 22: [`(#2.92)` - `(#4.172)`] |
| B023 | `(#6.163)` | Bucket 23: [`(#4.172)` - `(#6.163)`] |
| B024 | `Aamu joutuu pesemään tekojensa jälkipyykkiä` | Bucket 24: [`(#6.163)` - `Aamu joutuu pesemään tekojensa jälkipyykkiä`] |
| B025 | `Aflevering 2559` | Bucket 25: [`Aamu joutuu pesemään tekojensa jälkipyykkiä` - `Aflevering 2559`] |
| B026 | `A Little Trip` | Bucket 26: [`Aflevering 2559` - `A Little Trip`] |
| B027 | `An Atheist Named Faith` | Bucket 27: [`A Little Trip` - `An Atheist Named Faith`] |
| B028 | `Arabeskebi Pirosmanis temaze` | Bucket 28: [`An Atheist Named Faith` - `Arabeskebi Pirosmanis temaze`] |
| B029 | `Attenborough's Ark: Natural World Special` | Bucket 29: [`Arabeskebi Pirosmanis temaze` - `Attenborough's Ark: Natural World Special`] |
| B030 | `Baldur Blauzahn` | Bucket 30: [`Attenborough's Ark: Natural World Special` - `Baldur Blauzahn`] |
| B031 | `Best in Show Cakes` | Bucket 31: [`Baldur Blauzahn` - `Best in Show Cakes`] |
| B032 | `Blues` | Bucket 32: [`Best in Show Cakes` - `Blues`] |
| B033 | `Brown Before Green` | Bucket 33: [`Blues` - `Brown Before Green`] |
| B034 | `Captive Audience` | Bucket 34: [`Brown Before Green` - `Captive Audience`] |
| B035 | `Cheryl Cole's Night In` | Bucket 35: [`Captive Audience` - `Cheryl Cole's Night In`] |
| B036 | `Cobra Starship` | Bucket 36: [`Cheryl Cole's Night In` - `Cobra Starship`] |
| B037 | `CPM 22 e Babado Novo` | Bucket 37: [`Cobra Starship` - `CPM 22 e Babado Novo`] |
| B038 | `Dark Moon` | Bucket 38: [`CPM 22 e Babado Novo` - `Dark Moon`] |
| B039 | `De intrede van de Sint - Antwerpen 2011` | Bucket 39: [`Dark Moon` - `De intrede van de Sint - Antwerpen 2011`] |
| B040 | `Det' politiet: Part 2` | Bucket 40: [`De intrede van de Sint - Antwerpen 2011` - `Det' politiet: Part 2`] |
| B041 | `DIY Network Holiday Celebration` | Bucket 41: [`Det' politiet: Part 2` - `DIY Network Holiday Celebration`] |
| B042 | `Drugog puta nema!` | Bucket 42: [`DIY Network Holiday Celebration` - `Drugog puta nema!`] |
| B043 | `Elements` | Bucket 43: [`Drugog puta nema!` - `Elements`] |
| B044 | `Episode V - Tag der Abrechnung` | Bucket 44: [`Elements` - `Episode V - Tag der Abrechnung`] |
| B045 | `Famiresu tenshi purin` | Bucket 45: [`Episode V - Tag der Abrechnung` - `Famiresu tenshi purin`] |
| B046 | `Fleshdance` | Bucket 46: [`Famiresu tenshi purin` - `Fleshdance`] |
| B047 | `Fuga y misterio` | Bucket 47: [`Fleshdance` - `Fuga y misterio`] |
| B048 | `Girls' Generation and the Dangerous Boys` | Bucket 48: [`Fuga y misterio` - `Girls' Generation and the Dangerous Boys`] |
| B049 | `Guadalcanal/Leckie` | Bucket 49: [`Girls' Generation and the Dangerous Boys` - `Guadalcanal/Leckie`] |
| B050 | `Heaven on Earth` | Bucket 50: [`Guadalcanal/Leckie` - `Heaven on Earth`] |
| B051 | `Holiday` | Bucket 51: [`Heaven on Earth` - `Holiday`] |
| B052 | `Hurricane Katrina Aftermath` | Bucket 52: [`Holiday` - `Hurricane Katrina Aftermath`] |
| B053 | `Inauguração na Estrela - Lisboa` | Bucket 53: [`Hurricane Katrina Aftermath` - `Inauguração na Estrela - Lisboa`] |
| B054 | `Is There Still Hope for Gino and Mikay?` | Bucket 54: [`Inauguração na Estrela - Lisboa` - `Is There Still Hope for Gino and Mikay?`] |
| B055 | `Jindalee Lady` | Bucket 55: [`Is There Still Hope for Gino and Mikay?` - `Jindalee Lady`] |
| B056 | `Karina` | Bucket 56: [`Jindalee Lady` - `Karina`] |
| B057 | `Know Thy Partner` | Bucket 57: [`Karina` - `Know Thy Partner`] |
| B058 | `Ladrones de niños` | Bucket 58: [`Know Thy Partner` - `Ladrones de niños`] |
| B059 | `Late as a Mother****er` | Bucket 59: [`Ladrones de niños` - `Late as a Mother****er`] |
| B060 | `Les éperlans` | Bucket 60: [`Late as a Mother****er` - `Les éperlans`] |
| B061 | `Living Room Upgrade` | Bucket 61: [`Les éperlans` - `Living Room Upgrade`] |
| B062 | `Luha ng ina` | Bucket 62: [`Living Room Upgrade` - `Luha ng ina`] |
| B063 | `Männer sind auch nur Menschen` | Bucket 63: [`Luha ng ina` - `Männer sind auch nur Menschen`] |
| B064 | `Melissa` | Bucket 64: [`Männer sind auch nur Menschen` - `Melissa`] |
| B065 | `Mission to Africa` | Bucket 65: [`Melissa` - `Mission to Africa`] |
| B066 | `Mr. Deity and the Days` | Bucket 66: [`Mission to Africa` - `Mr. Deity and the Days`] |
| B067 | `Nanna & Lil' Puss Puss in 'The Honeymoonies'` | Bucket 67: [`Mr. Deity and the Days` - `Nanna & Lil' Puss Puss in 'The Honeymoonies'`] |
| B068 | `Ninna Hyttinen` | Bucket 68: [`Nanna & Lil' Puss Puss in 'The Honeymoonies'` - `Ninna Hyttinen`] |
| B069 | `Odoriko no yubiwa` | Bucket 69: [`Ninna Hyttinen` - `Odoriko no yubiwa`] |
| B070 | `Operation: Bank Job` | Bucket 70: [`Odoriko no yubiwa` - `Operation: Bank Job`] |
| B071 | `Papa wo sagashite!` | Bucket 71: [`Operation: Bank Job` - `Papa wo sagashite!`] |
| B072 | `Phantom Fever` | Bucket 72: [`Papa wo sagashite!` - `Phantom Fever`] |
| B073 | `Power of the South` | Bucket 73: [`Phantom Fever` - `Power of the South`] |
| B074 | `Quatre acteurs à bout de souffle` | Bucket 74: [`Power of the South` - `Quatre acteurs à bout de souffle`] |
| B075 | `Relative Air Pollution` | Bucket 75: [`Quatre acteurs à bout de souffle` - `Relative Air Pollution`] |
| B076 | `Rolling Stones` | Bucket 76: [`Relative Air Pollution` - `Rolling Stones`] |
| B077 | `San Diego, Bukarest, Paris` | Bucket 77: [`Rolling Stones` - `San Diego, Bukarest, Paris`] |
| B078 | `Seekers` | Bucket 78: [`San Diego, Bukarest, Paris` - `Seekers`] |
| B079 | `Shônen Tantei to Supai` | Bucket 79: [`Seekers` - `Shônen Tantei to Supai`] |
| B080 | `Smash Hit: She` | Bucket 80: [`Shônen Tantei to Supai` - `Smash Hit: She`] |
| B081 | `Spilling the Beans` | Bucket 81: [`Smash Hit: She` - `Spilling the Beans`] |
| B082 | `Strider 2` | Bucket 82: [`Spilling the Beans` - `Strider 2`] |
| B083 | `Take This Job and Shove It` | Bucket 83: [`Strider 2` - `Take This Job and Shove It`] |
| B084 | `The Accident` | Bucket 84: [`Take This Job and Shove It` - `The Accident`] |
| B085 | `The Captain's Son: Untitled` | Bucket 85: [`The Accident` - `The Captain's Son: Untitled`] |
| B086 | `The End of the World as We Know It` | Bucket 86: [`The Captain's Son: Untitled` - `The End of the World as We Know It`] |
| B087 | `The Healers` | Bucket 87: [`The End of the World as We Know It` - `The Healers`] |
| B088 | `The Lobsters Cook` | Bucket 88: [`The Healers` - `The Lobsters Cook`] |
| B089 | `The Odyssey` | Bucket 89: [`The Lobsters Cook` - `The Odyssey`] |
| B090 | `The Ring of Ultimate Power` | Bucket 90: [`The Odyssey` - `The Ring of Ultimate Power`] |
| B091 | `The Thing in Mrs. Faversham's Attic` | Bucket 91: [`The Ring of Ultimate Power` - `The Thing in Mrs. Faversham's Attic`] |
| B092 | `Thin Ice` | Bucket 92: [`The Thing in Mrs. Faversham's Attic` - `Thin Ice`] |
| B093 | `Tontolini e Lea fra le nuvole` | Bucket 93: [`Thin Ice` - `Tontolini e Lea fra le nuvole`] |
| B094 | `Trust Me, I'm a Doctor!` | Bucket 94: [`Tontolini e Lea fra le nuvole` - `Trust Me, I'm a Doctor!`] |
| B095 | `Undertryk` | Bucket 95: [`Trust Me, I'm a Doctor!` - `Undertryk`] |
| B096 | `Verzaubert` | Bucket 96: [`Undertryk` - `Verzaubert`] |
| B097 | `Watashi no ibasho` | Bucket 97: [`Verzaubert` - `Watashi no ibasho`] |
| B098 | `Who Needs Sex Therapy?` | Bucket 98: [`Watashi no ibasho` - `Who Needs Sex Therapy?`] |
| B099 | `Yasmina` | Bucket 99: [`Who Needs Sex Therapy?` - `Yasmina`] |
| B100 | `Zzzzzz` | Bucket 100: [`Yasmina` - `Zzzzzz`] |

### 6. Histogram Visualization
![Histogram for title.id](../plots/q1_histogram_id.png)

![Histogram for title.title](../plots/q1_histogram_title.png)

### 7. Max Selectivity Error Calculation & Explanation

#### A. Mathematical Definition
- **Actual Selectivity ($S_{act}$)**: The exact fraction of rows matching the query predicate:
  $$S_{act} = \frac{A}{N}$$
  where $A$ is actual row count from `count(*)`, and $N = 2,528,312$ is total table rows.

- **Estimated Selectivity ($S_{est}$)**: The fraction of rows predicted by PostgreSQL's query optimizer:
  $$S_{est} = \frac{E}{N}$$
  where $E$ is estimated row count from `EXPLAIN`.

- **Absolute Selectivity Error**:
  $$\text{Error} = |S_{est} - S_{act}| = \left|\frac{E - A}{N}\right|$$

#### B. Step-by-Step Calculation for Evaluated Queries

1. **Query 1 (`title.title < 'Race'`)**:
   - Actual Count ($A_1$): `1,918,141` $\implies S_{act,1} = \frac{1918141}{2528312} = \mathbf{0.758665}$
   - Estimated Count ($E_1$): `1,939,288` $\implies S_{est,1} = \frac{1939288}{2528312} = \mathbf{0.767029}$
   - **Absolute Error**: $|0.767029 - 0.758665| = \mathbf{0.008364}$ (0.8364% absolute error, 1.10% relative error).

2. **Query 2 (`title.id < 350000`)**:
   - Actual Count ($A_2$): `349,999` $\implies S_{act,2} = \frac{349999}{2528312} = \mathbf{0.138432}$
   - Estimated Count ($E_2$): `337,982` $\implies S_{est,2} = \frac{337982}{2528312} = \mathbf{0.133679}$
   - **Absolute Error**: $|0.133679 - 0.138432| = \mathbf{0.004753}$ (0.4753% absolute error, 3.43% relative error).

3. **Max Selectivity Error**:
   $$\text{Max Selectivity Error} = \max(\text{Error}_1, \text{Error}_2) = \max(0.008364, 0.004753) = \mathbf{0.008364} \quad (\mathbf{0.8364\%})$$

#### C. PostgreSQL Internal Histogram Interpolation Breakdown (for `id < 350000`)
- Search constant: `350000`.
- Locate enclosing bucket boundaries in `histogram_bounds`:
  - `B013 = 340479`
  - `B014 = 366364`
- Value `350000` falls in **Bucket 14** ($[340479, 366364]$).
- All 13 preceding buckets are fully included: $13 \times \frac{1}{100} = 0.130000$.
- Linear interpolation inside Bucket 14:
  $$\text{Fraction in B14} = \frac{350000 - 340479}{366364 - 340479} \times \frac{1}{100} = \frac{9521}{25885} \times 0.01 = 0.003678$$
- Base histogram selectivity: $0.130000 + 0.003678 = 0.133678$.
- Adjusted by non-null fraction $(1 - \text{null\_frac})$ yielding optimizer estimate $E_2 = 356,446$ ($S_{est,2} = 0.140982$).

---

### 8. Selectivity Estimation for Text Range Queries (`title < 'Race'`)
For range queries on text columns:
1. PostgreSQL checks if the search string lies within `pg_stats.histogram_bounds`.
2. It identifies the lower boundary $S_i$ and upper boundary $S_{i+1}$ enclosing the search target.
3. It counts all buckets strictly preceding $S_i$ ($i \times \text{bucket\_weight}$).
4. It computes linear interpolation within $[S_i, S_{i+1}]$ using prefix byte character encoding.
5. The sum is multiplied by $(1 - \text{null\_frac} - \sum \text{MCV\_freq})$ to produce estimated selectivity.

### 9. Estimated and Actual Selectivities

#### Query 1: `SELECT * FROM title WHERE title.title < 'Race';`
- **Actual Row Count**: 1,918,141
- **Actual Selectivity**: **0.758665** (75.87%)
- **Estimated Row Count**: 1,939,288
- **Estimated Selectivity**: **0.767029** (76.70%)
- **Selectivity Error**: **0.008364** (Relative Error: **1.10%**)

#### Query 2: `SELECT * FROM title WHERE title.id < 350000;`
- **Actual Row Count**: 349,999
- **Actual Selectivity**: **0.138432** (13.84%)
- **Estimated Row Count**: 337,982
- **Estimated Selectivity**: **0.133679** (13.37%)
- **Selectivity Error**: **0.004753** (Relative Error: **3.43%**)

---

## Q2. Optimal Serial Histogram Construction ($B=20$ Buckets)

### 1. Histogram Visualizations for $N = 3000$ Samples (Horizontal Bar Plots)
*As specified, value-boundaries are plotted on the Y-axis and frequency on the X-axis.*

![Optimal Serial Histogram for title.id (N=3000)](../plots/q2_histogram_id_3000.png)

![Optimal Serial Histogram for title.title (N=3000)](../plots/q2_histogram_title_3000.png)

### 2. Execution Build Time
- **Execution Build Time for $N=3000$**: **0.8290 seconds** (`id` column) / **0.8240 seconds** (`title` column)

### 3. Frequency Bucket Boundaries ($N=3000$, $B=20$)

The optimal serial histogram algorithm partitions the 3,000 samples into 20 dynamic buckets to minimize total Sum of Squared Errors (SSE). The exact bucket intervals and row frequency counts ($n_i$) for both columns are listed below:

#### A. Column `id` Frequency Bucket Boundaries ($N=3000$, $B=20$)
| Bucket # | Value Interval (`id`) | Frequency Count ($n_i$) |
| :---: | :---: | :---: |
| Bucket 01 | [`257` - `118,070`] | 150 |
| Bucket 02 | [`118,980` - `242,849`] | 145 |
| Bucket 03 | [`245,511` - `372,280`] | 151 |
| Bucket 04 | [`374,055` - `502,053`] | 158 |
| Bucket 05 | [`507,011` - `631,993`] | 161 |
| Bucket 06 | [`634,943` - `752,523`] | 138 |
| Bucket 07 | [`755,964` - `874,274`] | 155 |
| Bucket 08 | [`875,179` - `1,009,160`] | 164 |
| Bucket 09 | [`1,011,071` - `1,146,469`] | 166 |
| Bucket 10 | [`1,148,257` - `1,270,590`] | 145 |
| Bucket 11 | [`1,272,220` - `1,395,313`] | 132 |
| Bucket 12 | [`1,396,612` - `1,519,389`] | 155 |
| Bucket 13 | [`1,521,543` - `1,633,984`] | 152 |
| Bucket 14 | [`1,638,075` - `1,748,729`] | 120 |
| Bucket 15 | [`1,750,231` - `1,870,608`] | 139 |
| Bucket 16 | [`1,874,253` - `2,004,075`] | 147 |
| Bucket 17 | [`2,007,741` - `2,133,708`] | 156 |
| Bucket 18 | [`2,137,263` - `2,272,201`] | 160 |
| Bucket 19 | [`2,273,708` - `2,407,008`] | 153 |
| Bucket 20 | [`2,407,834` - `2,528,054`] | 153 |

#### B. Column `title` Frequency Bucket Boundaries ($N=3000$, $B=20$)
| Bucket # | Value Interval (`title`) | Frequency Count ($n_i$) |
| :---: | :--- | :---: |
| Bucket 01 | [`"'57 Chevy Part 2"` - `"(2013-05-31)"`] | 843 |
| Bucket 02 | [`"...And a School Bus"` - `"4000 en los Andes"`] | 23 |
| Bucket 03 | [`"6 Chefs Compete"` - `"99: Why do you say that?"`] | 6 |
| Bucket 04 | [`"A Bag of Evidence"` - `"Azul"`] | 179 |
| Bucket 05 | [`"B-Grade Celebrity/Bucks P"` - `"Buzios"`] | 116 |
| Bucket 06 | [`"Bîto Takeshi satsujin jik"` - `"Cynthia Rowley"`] | 100 |
| Bucket 07 | [`"D'abord ménagères"` - `"Dílerka"`] | 122 |
| Bucket 08 | [`"Easel Does It/Dinky at th"` - `"Futebol Entre Fluminense "`] | 146 |
| Bucket 09 | [`"Gakuen sai de yui, hansei"` - `"Humongous Hooters"`] | 153 |
| Bucket 10 | [`"Hämäläiset sukupidot Tamm"` - `"Jvartsmuli kundzuli"`] | 102 |
| Bucket 11 | [`"Jû"` - `"Lähtölaukaus"`] | 174 |
| Bucket 12 | [`"Lídin odjezd"` - `"Nyûsu môningu sateraito"`] | 170 |
| Bucket 13 | [`"O Bairro Salazar"` - `"Pérdida millonaria"`] | 143 |
| Bucket 14 | [`"Quando parliamo d'amore"` - `"Ryuu wo tsuru shounen"`] | 67 |
| Bucket 15 | [`"Rånemax tv-show"` - `"Sådan udvikler du dit bar"`] | 183 |
| Bucket 16 | [`"Súkromné jasle"` - `"Uyarukm Njan Nadaake"`] | 334 |
| Bucket 17 | [`"Vabzdziu dresuotojas"` - `"XFC 11: The Next Generati"`] | 100 |
| Bucket 18 | [`"Ya vozhatyy forposta"` - `"Zwischen uns beiden"`] | 34 |
| Bucket 19 | [`"¿Diana en peligro?"` - `"Åsa-Nisse i kronans kläde"`] | 3 |
| Bucket 20 | [`"Ôjo-sama to eiyû"` - `"Öbergs på Lillöga"`] | 2 |

### 4. Max Selectivity Error for Optimal Histogram ($N=3000$)

- **Max Selectivity Error**: **0.003720** (or **0.3720%**)

#### A. Step-by-Step Calculation Methodology
1. **Evaluation Quantiles ($q_0 \dots q_9$)**: To systematically evaluate estimation error across the data range $[x_{\min}, x_{\max}]$, 10 linearly-spaced query thresholds $q_k$ are evaluated:
   $$q_k = x_{\min} + k \times \frac{x_{\max} - x_{\min}}{9}, \quad k \in \{0, 1, \dots, 9\}$$

2. **Actual Selectivity ($S_{\text{act}}(q_k)$)**: Computed directly from the empirical sample of $N = 3,000$ points:
   $$S_{\text{act}}(q_k) = \frac{\text{Count}(x \le q_k)}{N}$$

3. **Optimal Histogram Estimated Selectivity ($S_{\text{est}}(q_k)$)**:
   - For all buckets $[L_i, H_i]$ lying fully below $q_k$ ($H_i \le q_k$), add full bucket count $n_i$.
   - For the enclosing bucket ($L_i \le q_k < H_i$), perform linear interpolation:
     $$\text{Estimated Count } E(q_k) = \sum_{H_i \le q_k} n_i + \left( n_i \times \frac{q_k - L_i}{H_i - L_i} \right)$$
   - Estimated Selectivity: $S_{\text{est}}(q_k) = \frac{E(q_k)}{N}$

4. **Maximum Selectivity Error**:
   $$\text{Max Selectivity Error} = \max_{k \in \{0..9\}} |S_{\text{est}}(q_k) - S_{\text{act}}(q_k)| = \mathbf{0.003720}$$

#### B. Quantile-by-Quantile Error Evaluation Table ($N=3000, B=20$)
| Index ($k$) | Query Threshold ($q_k$) | Actual Count ($A$) | Actual Selectivity ($S_{\text{act}}$) | Estimated Count ($E$) | Estimated Selectivity ($S_{\text{est}}$) | Absolute Error $\vert S_{\text{est}} - S_{\text{act}} \vert$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| $q_0$ | `257.0` | 1 | 0.000333 | 0.00 | 0.000000 | 0.000333 |
| $q_1$ | `281,123.3` | 342 | 0.114000 | 337.42 | 0.112473 | 0.001527 |
| $q_2$ | `561,989.7` | 668 | 0.222667 | 674.82 | 0.224941 | 0.002274 |
| $q_3$ | `842,856.0` | 1028 | 0.342667 | 1016.84 | 0.338946 | **0.003720** |
| $q_4$ | `1,123,722.3` | 1353 | 0.451000 | 1360.11 | 0.453371 | 0.002371 |
| $q_5$ | `1,404,588.7` | 1673 | 0.557667 | 1675.07 | 0.558357 | 0.000690 |
| $q_6$ | `1,685,455.0` | 2026 | 0.675333 | 2023.38 | 0.674461 | 0.000873 |
| $q_7$ | `1,966,321.3` | 2345 | 0.781667 | 2335.25 | 0.778417 | 0.003250 |
| $q_8$ | `2,247,187.7` | 2669 | 0.889667 | 2664.34 | 0.888114 | 0.001553 |
| $q_9$ | `2,528,054.0` | 3000 | 1.000000 | 3000.00 | 1.000000 | 0.000000 |

### 5. Histograms Across Sample Sizes ($N = 1000$ and $N = 3000$)

Below are the optimal serial histogram visualizations ($B=20$) for both sample sizes $N=1000$ and $N=3000$:

#### A. Sample Size $N = 1000$ Histograms
![Optimal Serial Histogram for title.id (N=1000)](../plots/q2_histogram_id_1000.png)

![Optimal Serial Histogram for title.title (N=1000)](../plots/q2_histogram_title_1000.png)

#### B. Sample Size $N = 3000$ Histograms
![Optimal Serial Histogram for title.id (N=3000)](../plots/q2_histogram_id_3000.png)

![Optimal Serial Histogram for title.title (N=3000)](../plots/q2_histogram_title_3000.png)

#### C. Summary Table Across Sample Sizes
| Sample Size ($N$) | Build Time (`id`) | Build Time (`title`) | Max Selectivity Error |
| :---: | :---: | :---: | :---: |
| **1000** | 0.1994s | 0.1719s | 0.004699 |
| **3000** | 0.8290s | 0.8240s | 0.003720 |
| **5000** | 2.1767s | 2.0974s | 0.002471 |

---

### 6. Full Step-by-Step Linear Regression Extrapolation ($N = 2,528,312$)

To extrapolate the construction build time for the entire `title` table ($N = 2,528,312$), we fit a linear regression model:
$$T(N) = m \cdot N + c$$

#### A. Sample Data Points $(N_i, T_i)$
- Point 1: $(N_1, T_1) = (1000, 0.1994)$
- Point 2: $(N_2, T_2) = (3000, 0.8290)$
- Point 3: $(N_3, T_3) = (5000, 2.1767)$

#### B. Mean Calculations
- $\bar{N} = \frac{1000 + 3000 + 5000}{3} = \mathbf{3000}$
- $\bar{T} = \frac{0.1994 + 0.8290 + 2.1767}{3} = \mathbf{1.0684\text{ seconds}}$

#### C. Deviations & Sum of Products
| $N_i$ | $T_i$ (s) | $(N_i - \bar{N})$ | $(T_i - \bar{T})$ | $(N_i - \bar{N})^2$ | $(N_i - \bar{N})(T_i - \bar{T})$ |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1000 | 0.1994 | -2000 | -0.8690 | 4,000,000 | 1738.0037 |
| 3000 | 0.8290 | 0 | -0.2394 | 0 | -0.0000 |
| 5000 | 2.1767 | +2000 | 1.1084 | 4,000,000 | 2216.7320 |
| **Sum** | | | | **8,000,000** | **3954.7358** |

#### D. Slope ($m$) and Intercept ($c$) Formulas
- **Slope ($m$)**:
  $$m = \frac{\sum (N_i - \bar{N})(T_i - \bar{T})}{\sum (N_i - \bar{N})^2} = \frac{3954.7358}{8,000,000} = \mathbf{0.00049434\text{ seconds / sample}}$$

- **Intercept ($c$)**:
  $$c = \bar{T} - m \cdot \bar{N} = 1.0684 - (0.00049434 \times 3000) = \mathbf{-0.414643\text{ seconds}}$$

#### E. Extrapolated Build Time for Full Table ($N = 2,528,312$)
$$T(2,528,312) = (0.00049434 \times 2,528,312) + (-0.414643) = \mathbf{1249.44\text{ seconds}} \quad (\mathbf{20.82\text{ minutes}})$$

---

### 7. Sample Size vs Time Relationship Plot
![Sample Size vs Time](../plots/q2_sample_size_vs_time.png)

---

### 8. Sample Size vs Max Selectivity Error Relationship Plot
![Sample Size vs Max Selectivity Error](../plots/q2_sample_size_vs_error.png)

---

### 9. Impact of Bucket Count ($B$) Choice
- **Fewer Buckets (e.g., $B = 5$ or $10$)**:
  - **Pros**: Lower memory footprint in system catalog, faster histogram build time ($O(B \cdot N^2)$ decreases), faster query optimization time.
  - **Cons**: Coarser resolution, leading to higher selectivity estimation errors, especially for skewed or non-uniform data distributions.
- **More Buckets (e.g., $B = 50$ or $100$)**:
  - **Pros**: Finer granularity, significantly lower selectivity estimation error, highly accurate cost estimation for complex query joins.
  - **Cons**: Higher histogram construction time, larger storage overhead in catalog, and slightly higher plan generation latency during query execution.
