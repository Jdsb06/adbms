import os
import sys
import psycopg2
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from solution_q1 import run_q1
from solution_q2 import run_q2

def generate_assignment_report():
    print("=== Generating Master Assignment Report ===")
    
    # Run Q1 & Q2
    q1_data = run_q1()
    q2_data = run_q2()

    tables = q1_data['tables']
    cardinalities = q1_data['cardinalities']
    total_db_rows = q1_data['total_db_rows']
    id_bounds_list = q1_data['id_bounds_list']
    title_bounds_list = q1_data['title_bounds_list']
    max_err = q1_data['max_err']

    total_title = cardinalities.get('title', 2528312)

    act_race_cnt = q1_data['act_race_cnt']
    act_race_sel = q1_data['act_race_sel']
    est_race_cnt = q1_data['est_race_cnt']
    est_race_sel = q1_data['est_race_sel']
    err_race = q1_data['err_race']

    act_id_cnt = q1_data['act_id_cnt']
    act_id_sel = q1_data['act_id_sel']
    est_id_cnt = q1_data['est_id_cnt']
    est_id_sel = q1_data['est_id_sel']
    err_id = q1_data['err_id']

    q2_results = q2_data['results']
    slope = q2_data['slope']
    intercept = q2_data['intercept']
    extrapolated_time = q2_data['extrapolated_time']

    res_1000 = q2_results['id'][1000]
    res_3000 = q2_results['id'][3000]
    res_5000 = q2_results['id'][5000]

    res_title_1000 = q2_results['title'][1000]
    res_title_3000 = q2_results['title'][3000]
    res_title_5000 = q2_results['title'][5000]

    t1000 = res_1000['avg_time']
    t3000 = res_3000['avg_time']
    t5000 = res_5000['avg_time']

    e1000 = res_1000['avg_error']
    e3000 = res_3000['avg_error']
    e5000 = res_5000['avg_error']

    mean_T = (t1000 + t3000 + t5000) / 3.0
    dev_N = [-2000, 0, 2000]
    dev_T = [t1000 - mean_T, t3000 - mean_T, t5000 - mean_T]
    sum_cross = sum(dn * dt for dn, dt in zip(dev_N, dev_T))

    buckets_3000_id = res_3000['buckets']
    q_details_3000 = res_3000['q_details']

    report = f"""# Advanced Database Management Systems (ADBMS)
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
- **Total Relational Tuples**: {total_db_rows:,}

### Table Cardinalities & Primary Keys

| Table Name | Primary Key Column | Cardinality (`count(*)`) |
| :--- | :---: | :---: |
"""
    for t in sorted(tables):
        report += f"| `{t}` | `id` | {cardinalities[t]:,} |\n"

    report += f"""
---

# Assignment 1: Histogram

## Q1. Histogram Analysis for `id` and `title` Columns of `title` Table

### 1. Corresponding SQL Query
to see what all colums needed form `pg_stats'
```sql
\\d pg_stats;
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

#### A. Column `id` Bucket Boundaries ({len(id_bounds_list)} values, 100 buckets)
| Bucket Index | Boundary Value (`id`) | Bucket Interval |
| :---: | :---: | :--- |
"""
    for i in range(len(id_bounds_list)):
        if i == 0:
            report += f"| B{i:03d} (Start) | `{id_bounds_list[i]}` | Start of table data |\n"
        else:
            report += f"| B{i:03d} | `{id_bounds_list[i]}` | Bucket {i}: [`{id_bounds_list[i-1]}` - `{id_bounds_list[i]}`] |\n"

    report += f"""
#### B. Column `title` Bucket Boundaries ({len(title_bounds_list)} values, 100 buckets)
| Bucket Index | Boundary Value (`title`) | Lexicographical Interval |
| :---: | :--- | :--- |
"""
    for i in range(len(title_bounds_list)):
        val_str = str(title_bounds_list[i]).replace('|', '\\|').replace('$', '\\$')
        if i == 0:
            report += f"| B{i:03d} (Start) | `{val_str}` | Start of text data |\n"
        else:
            prev_str = str(title_bounds_list[i-1]).replace('|', '\\|').replace('$', '\\$')
            report += f"| B{i:03d} | `{val_str}` | Bucket {i}: [`{prev_str}` - `{val_str}`] |\n"

    report += f"""
### 6. Histogram Visualization
![Histogram for title.id](../plots/q1_histogram_id.png)

![Histogram for title.title](../plots/q1_histogram_title.png)

### 7. Max Selectivity Error
- **Max Selectivity Error**: Since `default_statistics_target` is 100, there are 100 buckets. Therefore, the maximum selectivity error for a range query is bounded by:
$$\\text{{Max Error}} \\le \\frac{{1}}{{B}} = \\frac{{1}}{{100}} = 0.01 \\quad (1.0\\%)$$
For evaluated queries(q9), the observed maximum selectivity error is **{max_err*100:.4f}%** ({max_err:.6f}), which strictly satisfies $\\text{{Max Error}} \\le 1.0\\%$.

---
### 8: Selectivity Estimation for Text Columns
Selectivity estimate is done for range query on text column such as “title” in PSQL such as:
*The engine scans the `histogram_bounds` array stored under pg_stats to locate the specific bucket where the target string  is, after that it counts all complete buckets preceding the target bucket. Each full bucket represents a fixed fraction of total rows (1/B). For the target bucket, PostgreSQL converts initial string bytes into floating-point numbers in $[0.0, 1.0]$ range for interpolation as explain in part 4,  assuming uniform distribution inside the target bucket, it calculates the target's position using:

$$\\text{{Fraction}} = \\frac{{\\text{{Query Value}} - \\text{{Bucket Min}}}}{{\\text{{Bucket Max}} - \\text{{Bucket Min}}}}$$
*   Final Calculation is done by adding the fractional bucket estimate to the sum of preceding full buckets to get the final estimated selectivity.

### 9: Estimated vs. Actual Selectivities

To calculate estimated and actual selectivities of the queries and moreover there accuracy we compare estimated rows (from `EXPLAIN`) against actual rows (from `EXPLAIN ANALYZE`).
Total row count ($N$) for the `title` table is {total_title:,}.

**Query 1: `title < 'Race'`**
```sql 
EXPLAIN ANALYZE SELECT * FROM title WHERE title.title < 'Race';
```
- **Actual Selectivity:** The query physically returned {act_race_cnt:,} matching rows: $S_{{act}} = \\frac{{{act_race_cnt}}}{{{total_title}}} \\approx {act_race_sel:.4f}$ ({act_race_sel*100:.2f}%).

```sql
EXPLAIN SELECT * FROM title WHERE title.title < 'Race';
```
- **Estimated Selectivity:** The planner estimated {est_race_cnt:,} rows: $S_{{est}} = \\frac{{{est_race_cnt}}}{{{total_title}}} \\approx {est_race_sel:.4f}$ ({est_race_sel*100:.2f}%).

- **Observation:** The absolute error is roughly {err_race*100:.2f}%.

**Query 2: `id < 350000`**
```sql
EXPLAIN ANALYZE SELECT * FROM title WHERE title.id < '350000';
```
- **Actual Selectivity:** The query returned {act_id_cnt:,} matching rows: $S_{{act}} = \\frac{{{act_id_cnt}}}{{{total_title}}} \\approx {act_id_sel:.4f}$ ({act_id_sel*100:.2f}%).

```sql
EXPLAIN SELECT * FROM title WHERE title.id < '350000';
```
- **Estimated Selectivity:** The planner estimated {est_id_cnt:,} rows: $S_{{est}} = \\frac{{{est_id_cnt}}}{{{total_title}}} \\approx {est_id_sel:.4f}$ ({est_id_sel*100:.2f}%).

- **Observation:** The absolute error here is about {err_id*100:.2f}%.

---

## Q2. Optimal Serial Histogram Construction ($B=20$ Buckets)

### 1. Histogram Visualizations for Exact $N = 3000$ Samples (Slide-Faithful Horizontal Bar Plots)
*As defined in lecture slides, a Serial Histogram sorts domain values by their ordered frequencies ($f(v_{{(1)}}) \le f(v_{{(2)}}) \le \dots \le f(v_{{(m)}})$) and partitions the frequency space to minimize frequency variance $\sum n_i V_i$. The horizontal bar charts below plot Frequencies on the X-axis and Value Set / Buckets on the Y-axis:*

![Optimal Serial Histogram for title.id (N=3000)](../plots/q2_histogram_id_3000.png)

![Optimal Serial Histogram for title.title (N=3000)](../plots/q2_histogram_title_3000.png)

### 2. Execution Build Time (Average over 3 Runs)
- **Average Build Time for $N=3000$**: **{t3000:.4f} seconds** (`id` column) / **{res_title_3000['avg_time']:.4f} seconds** (`title` column)

### 3. Frequency Bucket Boundaries ($N=3000$, $B=20$)

The optimal serial histogram algorithm partitions the exact 3,000 samples into 20 dynamic frequency buckets. The exact bucket value ranges, distinct domain value counts ($n_i$), and frequency distributions for both columns are listed below:

#### A. Column `id` Serial Frequency Bucket Boundaries ($N=3000$, $B=20$)
| Bucket # | Value Range (`id`) | Distinct Values ($n_i$) | Frequency Range | Average Frequency ($\\bar{{f}}_i$) |
| :---: | :---: | :---: | :---: | :---: |
"""
    for idx, b in enumerate(buckets_3000_id):
        v_low = int(b['val_min'])
        v_high = int(b['val_max'])
        f_min = b['min_freq']
        f_max = b['max_freq']
        f_str = f"{f_min}" if f_min == f_max else f"{f_min}-{f_max}"
        report += f"| Bucket {idx+1:02d} | [`{v_low:,}` - `{v_high:,}`] | {b['distinct_count']} | {f_str} | {b['avg_freq']:.2f} |\n"

    report += f"""
#### B. Column `title` Serial Frequency Bucket Boundaries ($N=3000$, $B=20$)
| Bucket # | Value Range (`title`) | Distinct Values ($n_i$) | Frequency Range | Average Frequency ($\\bar{{f}}_i$) |
| :---: | :--- | :---: | :---: | :---: |
"""
    for idx, b in enumerate(res_title_3000['buckets']):
        s_min = str(b['sample_min_str']).replace('|', '\\|').replace('$', '\\$')
        s_max = str(b['sample_max_str']).replace('|', '\\|').replace('$', '\\$')
        f_min = b['min_freq']
        f_max = b['max_freq']
        f_str = f"{f_min}" if f_min == f_max else f"{f_min}-{f_max}"
        report += f'| Bucket {idx+1:02d} | [`"{s_min}"` ... `"{s_max}"`] | {b["distinct_count"]} | {f_str} | {b["avg_freq"]:.2f} |\n'

    report += f"""
### 4. 3-Run Selectivity Error Calculation & Average ($N=3000$)

As required to account for sample randomness, the selectivity error evaluation was executed across **3 independent runs** (with exact sample size $N=3000$). All three run errors are listed below along with their computed average:

#### A. 3-Run Max Selectivity Error Summary ($N=3000$)
| Column | Run 1 Max Error | Run 2 Max Error | Run 3 Max Error | **Average Max Selectivity Error** |
| :---: | :---: | :---: | :---: | :---: |
| `id` | `{res_3000['run_errors'][0]:.6f}` | `{res_3000['run_errors'][1]:.6f}` | `{res_3000['run_errors'][2]:.6f}` | **`{e3000:.6f}`** ({e3000*100:.4f}%) |
| `title` | `{res_title_3000['run_errors'][0]:.6f}` | `{res_title_3000['run_errors'][1]:.6f}` | `{res_title_3000['run_errors'][2]:.6f}` | **`{res_title_3000['avg_error']:.6f}`** ({res_title_3000['avg_error']*100:.4f}%) |

#### B. Quantile-by-Quantile Error Evaluation Table for Run 1 ($N=3000, B=20$)
| Index ($k$) | Query Threshold ($q_k$) | Actual Count ($A$) | Actual Selectivity ($S_{{\\text{{act}}}}$) | Estimated Count ($E$) | Estimated Selectivity ($S_{{\\text{{est}}}}$) | Absolute Error $\\vert S_{{\\text{{est}}}} - S_{{\\text{{act}}}} \\vert$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
"""
    max_q_err = max(qd['error'] for qd in q_details_3000)
    for idx, qd in enumerate(q_details_3000):
        highlight = "**" if qd['error'] == max_q_err else ""
        report += f"| $q_{{{idx}}}$ | `{qd['q']:,.1f}` | {qd['actual_count']} | {qd['actual_sel']:.6f} | {qd['est_count']:.2f} | {qd['est_sel']:.6f} | {highlight}{qd['error']:.6f}{highlight} |\n"

    report += f"""
### 5. Histograms Across Exact Sample Sizes ($N = 1000, 3000, 5000$)

Below are the optimal serial histogram visualizations ($B=20$) for exact sample sizes $N=1000$ and $N=3000$:

#### A. Sample Size $N = 1000$ Histograms
![Optimal Serial Histogram for title.id (N=1000)](../plots/q2_histogram_id_1000.png)

![Optimal Serial Histogram for title.title (N=1000)](../plots/q2_histogram_title_1000.png)

#### B. Sample Size $N = 3000$ Histograms
![Optimal Serial Histogram for title.id (N=3000)](../plots/q2_histogram_id_3000.png)

![Optimal Serial Histogram for title.title (N=3000)](../plots/q2_histogram_title_3000.png)

#### C. Comprehensive 3-Run Summary Table Across Exact Sample Sizes
| Exact Sample Size ($N$) | Column | Run 1 Error | Run 2 Error | Run 3 Error | **Average Max Error** | Average Build Time |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1000** | `id` | `{res_1000['run_errors'][0]:.6f}` | `{res_1000['run_errors'][1]:.6f}` | `{res_1000['run_errors'][2]:.6f}` | **`{e1000:.6f}`** | `{t1000:.4f}s` |
| **1000** | `title` | `{res_title_1000['run_errors'][0]:.6f}` | `{res_title_1000['run_errors'][1]:.6f}` | `{res_title_1000['run_errors'][2]:.6f}` | **`{res_title_1000['avg_error']:.6f}`** | `{res_title_1000['avg_time']:.4f}s` |
| **3000** | `id` | `{res_3000['run_errors'][0]:.6f}` | `{res_3000['run_errors'][1]:.6f}` | `{res_3000['run_errors'][2]:.6f}` | **`{e3000:.6f}`** | `{t3000:.4f}s` |
| **3000** | `title` | `{res_title_3000['run_errors'][0]:.6f}` | `{res_title_3000['run_errors'][1]:.6f}` | `{res_title_3000['run_errors'][2]:.6f}` | **`{res_title_3000['avg_error']:.6f}`** | `{res_title_3000['avg_time']:.4f}s` |
| **5000** | `id` | `{res_5000['run_errors'][0]:.6f}` | `{res_5000['run_errors'][1]:.6f}` | `{res_5000['run_errors'][2]:.6f}` | **`{e5000:.6f}`** | `{t5000:.4f}s` |
| **5000** | `title` | `{res_title_5000['run_errors'][0]:.6f}` | `{res_title_5000['run_errors'][1]:.6f}` | `{res_title_5000['run_errors'][2]:.6f}` | **`{res_title_5000['avg_error']:.6f}`** | `{res_title_5000['avg_time']:.4f}s` |

---

### 6. Full Step-by-Step Linear Regression Extrapolation ($N = 2,528,312$)

To extrapolate the construction build time for the entire `title` table ($N = 2,528,312$), we fit a linear regression model on the 3-run average measured build times:
$$T(N) = m \\cdot N + c$$

#### A. Sample Data Points $(N_i, T_i)$
- Point 1: $(N_1, T_1) = (1000, {t1000:.4f})$
- Point 2: $(N_2, T_2) = (3000, {t3000:.4f})$
- Point 3: $(N_3, T_3) = (5000, {t5000:.4f})$

#### B. Mean Calculations
- $\\bar{{N}} = \\frac{{1000 + 3000 + 5000}}{{3}} = \\mathbf{{3000}}$
- $\\bar{{T}} = \\frac{{{t1000:.4f} + {t3000:.4f} + {t5000:.4f}}}{{3}} = \\mathbf{{{mean_T:.4f}\\text{{ seconds}}}}$

#### C. Deviations & Sum of Products
| $N_i$ | $T_i$ (s) | $(N_i - \\bar{{N}})$ | $(T_i - \\bar{{T}})$ | $(N_i - \\bar{{N}})^2$ | $(N_i - \\bar{{N}})(T_i - \\bar{{T}})$ |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1000 | {t1000:.4f} | -2000 | {dev_T[0]:.4f} | 4,000,000 | {dev_N[0]*dev_T[0]:.4f} |
| 3000 | {t3000:.4f} | 0 | {dev_T[1]:.4f} | 0 | {dev_N[1]*dev_T[1]:.4f} |
| 5000 | {t5000:.4f} | +2000 | {dev_T[2]:.4f} | 4,000,000 | {dev_N[2]*dev_T[2]:.4f} |
| **Sum** | | | | **8,000,000** | **{sum_cross:.4f}** |

#### D. Slope ($m$) and Intercept ($c$) Formulas
- **Slope ($m$)**:
  $$m = \\frac{{\\sum (N_i - \\bar{{N}})(T_i - \\bar{{T}})}}{{\\sum (N_i - \\bar{{N}})^2}} = \\frac{{{sum_cross:.4f}}}{{8,000,000}} = \\mathbf{{{slope:.8f}\\text{{ seconds / sample}}}}$$

- **Intercept ($c$)**:
  $$c = \\bar{{T}} - m \\cdot \\bar{{N}} = {mean_T:.4f} - ({slope:.8f} \\times 3000) = \\mathbf{{{intercept:.6f}\\text{{ seconds}}}}$$

#### E. Extrapolated Build Time for Full Table ($N = 2,528,312$)
$$T(2,528,312) = ({slope:.8f} \\times 2,528,312) + ({intercept:.6f}) = \\mathbf{{{extrapolated_time:.2f}\\text{{ seconds}}}} \\quad (\\mathbf{{{extrapolated_time/60:.2f}\\text{{ minutes}}}})$$

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
If we use a small number of buckets, the biggest advantage is speed and efficiency. The histogram takes up very little memory in the system catalog and builds much faster because the time complexity of our algorithm, $O(B \\cdot N^2)$, drops significantly. The query planner also spends less time analyzing it. However, the major downside is that we lose a lot of data resolution. Because the buckets are so wide, the internal mathematical estimates become much less accurate, especially if the data is heavily skewed or unevenly distributed.

**Choosing More Buckets (e.g., 50 to 100)**
On the flip side, using a large number of buckets gives the database a high-definition view of how the data is distributed. The estimates become incredibly precise, which leads to much lower selectivity errors and helps the query optimizer make smarter decisions for complex joins. The catch is that this accuracy comes at a heavy system cost. It takes noticeably longer to calculate and construct the histogram, consumes more storage space, and adds a slight delay to the query planning phase before execution can actually begin.
"""

    report_file = 'reports/Assignment_Report.md'
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\nMaster Report generated successfully as {report_file}!")

if __name__ == '__main__':
    generate_assignment_report()
