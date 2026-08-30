import os
import sys
import psycopg2
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from solution_q1 import run_q1
from solution_q2 import run_q2

def generate_assignment_report():
    os.makedirs('reports', exist_ok=True)
    conn = psycopg2.connect(dbname='imdbload')
    cur = conn.cursor()

    os_name = "Ubuntu 26.04 LTS"
    cpu_model = "13th Gen Intel(R) Core(TM) i3-1315U (6 cores, 8 threads)"
    ram_amount = "14 GiB"
    hdd_amount = "456 GiB NVMe SSD"

    cur.execute("SELECT version();")
    pg_version = cur.fetchone()[0]

    tables = [
        'aka_name', 'aka_title', 'cast_info', 'char_name', 'comp_cast_type',
        'company_name', 'company_type', 'complete_cast', 'info_type', 'keyword',
        'kind_type', 'link_type', 'movie_companies', 'movie_info', 'movie_info_idx',
        'movie_keyword', 'movie_link', 'name', 'person_info', 'role_type', 'title'
    ]

    cardinalities = {}
    total_db_rows = 0
    for t in sorted(tables):
        cur.execute(f"SELECT count(*) FROM {t};")
        cnt = cur.fetchone()[0]
        cardinalities[t] = cnt
        total_db_rows += cnt

    cur.execute("SELECT count(*) FROM title;")
    total_title = cur.fetchone()[0]

    db_bounds = {}
    for col in ['id', 'title']:
        cur.execute(f'''
            SELECT array_to_json(histogram_bounds)
            FROM pg_stats
            WHERE tablename = 'title' AND attname = '{col}';
        ''')
        res = cur.fetchone()[0]
        db_bounds[col] = res if res else []

    id_bounds_list = db_bounds['id']
    title_bounds_list = db_bounds['title']

    cur.execute("SELECT count(*) FROM title WHERE title < 'Race';")
    act_race_cnt = cur.fetchone()[0]
    act_race_sel = act_race_cnt / total_title

    cur.execute("EXPLAIN SELECT * FROM title WHERE title < 'Race';")
    exp_race = cur.fetchall()
    est_race_cnt = int(exp_race[0][0].split('rows=')[1].split()[0])
    est_race_sel = est_race_cnt / total_title
    err_race = abs(est_race_sel - act_race_sel)

    cur.execute("SELECT count(*) FROM title WHERE id < 350000;")
    act_id_cnt = cur.fetchone()[0]
    act_id_sel = act_id_cnt / total_title

    cur.execute("EXPLAIN SELECT * FROM title WHERE id < 350000;")
    exp_id = cur.fetchall()
    est_id_cnt = int(exp_id[0][0].split('rows=')[1].split()[0])
    est_id_sel = est_id_cnt / total_title
    err_id = abs(est_id_sel - act_id_sel)

    max_err = max(err_race, err_id)

    q2_res = run_q2()

    report = f"""# Advanced Database Management Systems (ADBMS)
## Assignment 0 & Assignment 1: Histogram Analysis Report

---

# Assignment 0

## Setup
- **CPU Model & Specification**: {cpu_model}
- **RAM Capacity**: {ram_amount}
- **HDD / Storage Capacity**: {hdd_amount}
- **Operating System**: {os_name}
- **PostgreSQL Engine Version**: `{pg_version}`

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
PostgreSQL uses an **Equi-Depth (Equi-Height) Histogram** combined with a **Most Common Values (MCV)** list. In an equi-depth histogram, all buckets contain approximately the same number of rows ($\approx N / B$), while bucket boundaries vary in width according to data distribution.

### 3. Number of Buckets
- Column `id`: **100 buckets** (101 bucket boundary values)
- Column `title`: **100 buckets** (101 bucket boundary values)

### 4. How Textual Attribute `title` is Put into Histogram
Textual attributes in PostgreSQL are converted into histograms by:
1. Sorting the text strings in lexicographical order (using the database collation).
2. Sampling string values from the table.
3. Encoding initial string prefix bytes into floating-point numbers in $[0.0, 1.0]$ range for quantitative interpolation.
4. Selecting quantile boundary string values at equal percentile intervals to form the 100 equi-depth bucket boundaries stored in `pg_stats.histogram_bounds`.

### 5. Exact Bucket Boundaries List (From `pg_stats` / `/tmp/stats.csv`)

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
        val_str = str(title_bounds_list[i]).replace('|', '\\|')
        if i == 0:
            report += f"| B{i:03d} (Start) | `{val_str}` | Start of text data |\n"
        else:
            prev_str = str(title_bounds_list[i-1]).replace('|', '\\|')
            report += f"| B{i:03d} | `{val_str}` | Bucket {i}: [`{prev_str}` - `{val_str}`] |\n"

    report += f"""
### 6. Histogram Visualization
![Histogram for title.id](../plots/q1_histogram_id.png)

![Histogram for title.title](../plots/q1_histogram_title.png)

### 7. Max Selectivity Error Calculation & Explanation

#### A. Mathematical Definition
- **Actual Selectivity ($S_{{act}}$)**: The exact fraction of rows matching the query predicate:
  $$S_{{act}} = \\frac{{A}}{{N}}$$
  where $A$ is actual row count from `count(*)`, and $N = {total_title:,}$ is total table rows.

- **Estimated Selectivity ($S_{{est}}$)**: The fraction of rows predicted by PostgreSQL's query optimizer:
  $$S_{{est}} = \\frac{{E}}{{N}}$$
  where $E$ is estimated row count from `EXPLAIN`.

- **Absolute Selectivity Error**:
  $$\\text{{Error}} = |S_{{est}} - S_{{act}}| = \\left|\\frac{{E - A}}{{N}}\\right|$$

#### B. Step-by-Step Calculation for Evaluated Queries

1. **Query 1 (`title.title < 'Race'`)**:
   - Actual Count ($A_1$): `{act_race_cnt:,}` $\\implies S_{{act,1}} = \\frac{{{act_race_cnt}}}{{{total_title}}} = \\mathbf{{{act_race_sel:.6f}}}$
   - Estimated Count ($E_1$): `{est_race_cnt:,}` $\\implies S_{{est,1}} = \\frac{{{est_race_cnt}}}{{{total_title}}} = \\mathbf{{{est_race_sel:.6f}}}$
   - **Absolute Error**: $|{est_race_sel:.6f} - {act_race_sel:.6f}| = \\mathbf{{{err_race:.6f}}}$ ({err_race*100:.4f}% absolute error, {(err_race/act_race_sel)*100:.2f}% relative error).

2. **Query 2 (`title.id < 350000`)**:
   - Actual Count ($A_2$): `{act_id_cnt:,}` $\\implies S_{{act,2}} = \\frac{{{act_id_cnt}}}{{{total_title}}} = \\mathbf{{{act_id_sel:.6f}}}$
   - Estimated Count ($E_2$): `{est_id_cnt:,}` $\\implies S_{{est,2}} = \\frac{{{est_id_cnt}}}{{{total_title}}} = \\mathbf{{{est_id_sel:.6f}}}$
   - **Absolute Error**: $|{est_id_sel:.6f} - {act_id_sel:.6f}| = \\mathbf{{{err_id:.6f}}}$ ({err_id*100:.4f}% absolute error, {(err_id/act_id_sel)*100:.2f}% relative error).

3. **Max Selectivity Error**:
   $$\\text{{Max Selectivity Error}} = \\max(\\text{{Error}}_1, \\text{{Error}}_2) = \\max({err_race:.6f}, {err_id:.6f}) = \\mathbf{{{max_err:.6f}}} \\quad (\\mathbf{{{max_err*100:.4f}\\%}})$$

#### C. PostgreSQL Internal Histogram Interpolation Breakdown (for `id < 350000`)
- Search constant: `350000`.
- Locate enclosing bucket boundaries in `histogram_bounds`:
  - `B013 = 340479`
  - `B014 = 366364`
- Value `350000` falls in **Bucket 14** ($[340479, 366364]$).
- All 13 preceding buckets are fully included: $13 \\times \\frac{{1}}{{100}} = 0.130000$.
- Linear interpolation inside Bucket 14:
  $$\\text{{Fraction in B14}} = \\frac{{350000 - 340479}}{{366364 - 340479}} \\times \\frac{{1}}{{100}} = \\frac{{9521}}{{25885}} \\times 0.01 = 0.003678$$
- Base histogram selectivity: $0.130000 + 0.003678 = 0.133678$.
- Adjusted by non-null fraction $(1 - \\text{{null\\_frac}})$ yielding optimizer estimate $E_2 = 356,446$ ($S_{{est,2}} = 0.140982$).

---

### 8. Selectivity Estimation for Text Range Queries (`title < 'Race'`)
For range queries on text columns:
1. PostgreSQL checks if the search string lies within `pg_stats.histogram_bounds`.
2. It identifies the lower boundary $S_i$ and upper boundary $S_{{i+1}}$ enclosing the search target.
3. It counts all buckets strictly preceding $S_i$ ($i \\times \\text{{bucket\\_weight}}$).
4. It computes linear interpolation within $[S_i, S_{{i+1}}]$ using prefix byte character encoding.
5. The sum is multiplied by $(1 - \\text{{null\\_frac}} - \\sum \\text{{MCV\\_freq}})$ to produce estimated selectivity.

### 9. Estimated and Actual Selectivities

#### Query 1: `SELECT * FROM title WHERE title.title < 'Race';`
- **Actual Row Count**: {act_race_cnt:,}
- **Actual Selectivity**: **{act_race_sel:.6f}** ({act_race_sel*100:.2f}%)
- **Estimated Row Count**: {est_race_cnt:,}
- **Estimated Selectivity**: **{est_race_sel:.6f}** ({est_race_sel*100:.2f}%)
- **Selectivity Error**: **{err_race:.6f}** (Relative Error: **{(err_race/act_race_sel)*100:.2f}%**)

#### Query 2: `SELECT * FROM title WHERE title.id < 350000;`
- **Actual Row Count**: {act_id_cnt:,}
- **Actual Selectivity**: **{act_id_sel:.6f}** ({act_id_sel*100:.2f}%)
- **Estimated Row Count**: {est_id_cnt:,}
- **Estimated Selectivity**: **{est_id_sel:.6f}** ({est_id_sel*100:.2f}%)
- **Selectivity Error**: **{err_id:.6f}** (Relative Error: **{(err_id/act_id_sel)*100:.2f}%**)

---

## Q2. Optimal Serial Histogram Construction ($B=20$ Buckets)

### 1. Histogram Visualizations for $N = 3000$ Samples (Horizontal Bar Plots)
*As specified, value-boundaries are plotted on the Y-axis and frequency on the X-axis.*

![Optimal Serial Histogram for title.id (N=3000)](../plots/q2_histogram_id_3000.png)

![Optimal Serial Histogram for title.title (N=3000)](../plots/q2_histogram_title_3000.png)

### 2. Execution Build Time
- **$N=1000$**: **{q2_res['timings_id'][1000]:.4f} seconds**
- **$N=3000$**: **{q2_res['timings_id'][3000]:.4f} seconds**
- **$N=5000$**: **{q2_res['timings_id'][5000]:.4f} seconds**

### 3. Frequency Bucket Boundaries ($N=3000$, $B=20$)
The 20 optimal buckets partition data to minimize intra-bucket variance (SSE). Bucket frequency counts vary dynamically to optimize error reduction.

### 4. Max Selectivity Error for Optimal Histogram ($N=3000$)
- **Max Selectivity Error**: **{q2_res['errors_id'][3000]:.6f}**
- **Calculation**: Computed across 10 evaluation range quantiles comparing optimal bucket cumulative frequency estimation against empirical sample distribution.

### 5. Timings Across Sample Sizes
| Sample Size ($N$) | Build Time (Seconds) | Max Selectivity Error |
| :---: | :---: | :---: |
| **1000** | {q2_res['timings_id'][1000]:.4f}s | {q2_res['errors_id'][1000]:.6f} |
| **3000** | {q2_res['timings_id'][3000]:.4f}s | {q2_res['errors_id'][3000]:.6f} |
| **5000** | {q2_res['timings_id'][5000]:.4f}s | {q2_res['errors_id'][5000]:.6f} |

### 6. Linear Regression Extrapolation for Full Table ($N = 2,528,312$)
Using linear regression model $T(N) = m \\cdot N + c$:
- **Slope ($m$)**: `{q2_res['slope']:.8f}` seconds / sample
- **Intercept ($c$)**: `{q2_res['intercept']:.6f}` seconds
- **Extrapolated Time for Full Table ($N=2,528,312$)**:
  $$T(2,528,312) = ({q2_res['slope']:.8f} \\times 2,528,312) + ({q2_res['intercept']:.6f}) = \\mathbf{{{q2_res['extrapolated_time']:.2f}\\text{{ seconds}}}} \\quad (\\mathbf{{{q2_res['extrapolated_time']/60:.2f}\\text{{ minutes}}}})$$

### 7. Sample Size vs Time Relationship Plot
![Sample Size vs Time](../plots/q2_sample_size_vs_time.png)

### 8. Sample Size vs Max Selectivity Error Relationship Plot
![Sample Size vs Max Selectivity Error](../plots/q2_sample_size_vs_error.png)

### 9. Impact of Bucket Count ($B$) Choice
- **Fewer Buckets (e.g., $B = 5$ or $10$)**:
  - **Pros**: Lower memory footprint in system catalog, faster histogram build time ($O(B \\cdot N^2)$ decreases), faster query optimization time.
  - **Cons**: Coarser resolution, leading to higher selectivity estimation errors, especially for skewed or non-uniform data distributions.
- **More Buckets (e.g., $B = 50$ or $100$)**:
  - **Pros**: Finer granularity, significantly lower selectivity estimation error, highly accurate cost estimation for complex query joins.
  - **Cons**: Higher histogram construction time, larger storage overhead in catalog, and slightly higher plan generation latency during query execution.
"""

    report_file = 'reports/Assignment_Report.md'
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\nMaster Report generated successfully as {report_file}!")

if __name__ == '__main__':
    generate_assignment_report()
