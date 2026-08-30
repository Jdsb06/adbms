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
SELECT tablename, attname, null_frac, avg_width, n_distinct, histogram_bounds
FROM pg_stats
WHERE tablename = 'title' AND attname IN ('id', 'title');
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

### 5. Bucket Boundaries Summary
- **`id` Column Boundaries**: Starts at `1` and ends at `2528312` across 100 equi-depth quantiles.
- **`title` Column Boundaries**: Sample string boundaries range lexicographically from initial titles up to final lexicographical titles.

### 6. Histogram Visualization
![Histogram for title.id](../plots/q1_histogram_id.png)

![Histogram for title.title](../plots/q1_histogram_title.png)

### 7. Max Selectivity Error
- **Max Selectivity Error** across tested range queries is **0.002550** (or **0.2550%** absolute error).
- **Calculation Formula**:
  $$\text{Selectivity Error} = |\text{Estimated Selectivity} - \text{Actual Selectivity}| = \left|\frac{E}{N} - \frac{A}{N}\right|$$

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
- **Estimated Row Count**: 1,921,965
- **Estimated Selectivity**: **0.760177** (76.02%)
- **Selectivity Error**: **0.001512** (Relative Error: **0.20%**)

#### Query 2: `SELECT * FROM title WHERE title.id < 350000;`
- **Actual Row Count**: 349,999
- **Actual Selectivity**: **0.138432** (13.84%)
- **Estimated Row Count**: 356,446
- **Estimated Selectivity**: **0.140982** (14.10%)
- **Selectivity Error**: **0.002550** (Relative Error: **1.84%**)

---

## Q2. Optimal Serial Histogram Construction ($B=20$ Buckets)

### 1. Histogram Visualizations for $N = 3000$ Samples (Horizontal Bar Plots)
*As specified, value-boundaries are plotted on the Y-axis and frequency on the X-axis.*

![Optimal Serial Histogram for title.id (N=3000)](../plots/q2_histogram_id_3000.png)

![Optimal Serial Histogram for title.title (N=3000)](../plots/q2_histogram_title_3000.png)

### 2. Execution Build Time
- **$N=1000$**: **0.1853 seconds**
- **$N=3000$**: **0.9767 seconds**
- **$N=5000$**: **2.2994 seconds**

### 3. Frequency Bucket Boundaries ($N=3000$, $B=20$)
The 20 optimal buckets partition data to minimize intra-bucket variance (SSE). Bucket frequency counts vary dynamically to optimize error reduction.

### 4. Max Selectivity Error for Optimal Histogram ($N=3000$)
- **Max Selectivity Error**: **0.002248**
- **Calculation**: Computed across 10 evaluation range quantiles comparing optimal bucket cumulative frequency estimation against empirical sample distribution.

### 5. Timings Across Sample Sizes
| Sample Size ($N$) | Build Time (Seconds) | Max Selectivity Error |
| :---: | :---: | :---: |
| **1000** | 0.1853s | 0.004565 |
| **3000** | 0.9767s | 0.002248 |
| **5000** | 2.2994s | 0.003013 |

### 6. Linear Regression Extrapolation for Full Table ($N = 2,528,312$)
Using linear regression model $T(N) = m \cdot N + c$:
- **Slope ($m$)**: `0.00052852` seconds / sample
- **Intercept ($c$)**: `-0.431751` seconds
- **Extrapolated Time for Full Table ($N=2,528,312$)**:
  $$T(2,528,312) = (0.00052852 \times 2,528,312) + (-0.431751) = \mathbf{1335.83\text{ seconds}} \quad (\mathbf{22.26\text{ minutes}})$$

### 7. Sample Size vs Time Relationship Plot
![Sample Size vs Time](../plots/q2_sample_size_vs_time.png)

### 8. Sample Size vs Max Selectivity Error Relationship Plot
![Sample Size vs Max Selectivity Error](../plots/q2_sample_size_vs_error.png)

### 9. Impact of Bucket Count ($B$) Choice
- **Fewer Buckets (e.g., $B = 5$ or $10$)**:
  - **Pros**: Lower memory footprint in system catalog, faster histogram build time ($O(B \cdot N^2)$ decreases), faster query optimization time.
  - **Cons**: Coarser resolution, leading to higher selectivity estimation errors, especially for skewed or non-uniform data distributions.
- **More Buckets (e.g., $B = 50$ or $100$)**:
  - **Pros**: Finer granularity, significantly lower selectivity estimation error, highly accurate cost estimation for complex query joins.
  - **Cons**: Higher histogram construction time, larger storage overhead in catalog, and slightly higher plan generation latency during query execution.
