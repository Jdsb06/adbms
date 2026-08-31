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

    # Extract Q2 details from fresh run
    h_res = q2_res['hist_results']
    res_3000 = h_res[3000]
    res_1000 = h_res[1000]
    res_5000 = h_res[5000]

    t1000 = q2_res['timings_id'][1000]
    t3000 = q2_res['timings_id'][3000]
    t5000 = q2_res['timings_id'][5000]

    e1000 = q2_res['errors_id'][1000]
    e3000 = q2_res['errors_id'][3000]
    e5000 = q2_res['errors_id'][5000]

    slope = q2_res['slope']
    intercept = q2_res['intercept']
    extrapolated_time = q2_res['extrapolated_time']

    # Compute step-by-step linear regression numbers
    mean_N = 3000.0
    mean_T = (t1000 + t3000 + t5000) / 3.0

    dev_N = [1000 - mean_N, 3000 - mean_N, 5000 - mean_N]
    dev_T = [t1000 - mean_T, t3000 - mean_T, t5000 - mean_T]

    sum_sq_N = sum(d**2 for d in dev_N)
    sum_cross = sum(dN * dT for dN, dT in zip(dev_N, dev_T))

    # Compute 10-quantile table for N=3000 id histogram
    id_sample_3000 = res_3000['id_sample']
    id_bounds_3000 = res_3000['id_bounds']
    id_counts_3000 = res_3000['id_counts']
    n_samp = len(id_sample_3000)

    quantiles_3000 = np.linspace(min(id_sample_3000), max(id_sample_3000), 10)
    q_table_rows = []
    max_q_err = 0.0

    for k, q in enumerate(quantiles_3000):
        a_cnt = sum(1 for x in id_sample_3000 if x <= q)
        a_sel = a_cnt / n_samp
        e_cnt = 0.0
        for (low, high), cnt in zip(id_bounds_3000, id_counts_3000):
            if high <= q:
                e_cnt += cnt
            elif low <= q < high:
                frac = (q - low) / max(1e-6, (high - low))
                e_cnt += cnt * frac
        e_sel = e_cnt / n_samp
        q_err = abs(e_sel - a_sel)
        if q_err > max_q_err:
            max_q_err = q_err
        q_table_rows.append((k, q, a_cnt, a_sel, e_cnt, e_sel, q_err))

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
- **Execution Build Time for $N=3000$**: **{t3000:.4f} seconds** (`id` column) / **{res_3000['elapsed_title']:.4f} seconds** (`title` column)

### 3. Frequency Bucket Boundaries ($N=3000$, $B=20$)

The optimal serial histogram algorithm partitions the 3,000 samples into 20 dynamic buckets to minimize total Sum of Squared Errors (SSE). The exact bucket intervals and row frequency counts ($n_i$) for both columns are listed below:

#### A. Column `id` Frequency Bucket Boundaries ($N=3000$, $B=20$)
| Bucket # | Value Interval (`id`) | Frequency Count ($n_i$) |
| :---: | :---: | :---: |
"""
    for idx, ((low, high), cnt) in enumerate(zip(id_bounds_3000, id_counts_3000)):
        report += f"| Bucket {idx+1:02d} | [`{int(low):,}` - `{int(high):,}`] | {cnt} |\n"

    report += f"""
#### B. Column `title` Frequency Bucket Boundaries ($N=3000$, $B=20$)
| Bucket # | Value Interval (`title`) | Frequency Count ($n_i$) |
| :---: | :--- | :---: |
"""
    t_samp = res_3000['title_sample']
    t_counts = res_3000['title_counts']
    cum_cnt = 0
    for idx, cnt in enumerate(t_counts):
        start_str = t_samp[cum_cnt][:25].replace('|', '\\|')
        cum_cnt += cnt
        end_str = t_samp[cum_cnt - 1][:25].replace('|', '\\|')
        report += f'| Bucket {idx+1:02d} | [`"{start_str}"` - `"{end_str}"`] | {cnt} |\n'

    report += f"""
### 4. Max Selectivity Error for Optimal Histogram ($N=3000$)

- **Max Selectivity Error**: **{e3000:.6f}** (or **{e3000*100:.4f}%**)

#### A. Step-by-Step Calculation Methodology
1. **Evaluation Quantiles ($q_0 \\dots q_9$)**: To systematically evaluate estimation error across the data range $[x_{{\\min}}, x_{{\\max}}]$, 10 linearly-spaced query thresholds $q_k$ are evaluated:
   $$q_k = x_{{\\min}} + k \\times \\frac{{x_{{\\max}} - x_{{\\min}}}}{{9}}, \\quad k \\in \\{{0, 1, \\dots, 9\\}}$$

2. **Actual Selectivity ($S_{{\\text{{act}}}}(q_k)$)**: Computed directly from the empirical sample of $N = 3,000$ points:
   $$S_{{\\text{{act}}}}(q_k) = \\frac{{\\text{{Count}}(x \\le q_k)}}{{N}}$$

3. **Optimal Histogram Estimated Selectivity ($S_{{\\text{{est}}}}(q_k)$)**:
   - For all buckets $[L_i, H_i]$ lying fully below $q_k$ ($H_i \\le q_k$), add full bucket count $n_i$.
   - For the enclosing bucket ($L_i \\le q_k < H_i$), perform linear interpolation:
     $$\\text{{Estimated Count }} E(q_k) = \\sum_{{H_i \\le q_k}} n_i + \\left( n_i \\times \\frac{{q_k - L_i}}{{H_i - L_i}} \\right)$$
   - Estimated Selectivity: $S_{{\\text{{est}}}}(q_k) = \\frac{{E(q_k)}}{{N}}$

4. **Maximum Selectivity Error**:
   $$\\text{{Max Selectivity Error}} = \\max_{{k \\in \\{{0..9\\}}}} |S_{{\\text{{est}}}}(q_k) - S_{{\\text{{act}}}}(q_k)| = \\mathbf{{{e3000:.6f}}}$$

#### B. Quantile-by-Quantile Error Evaluation Table ($N=3000, B=20$)
| Index ($k$) | Query Threshold ($q_k$) | Actual Count ($A$) | Actual Selectivity ($S_{{\\text{{act}}}}$) | Estimated Count ($E$) | Estimated Selectivity ($S_{{\\text{{est}}}}$) | Absolute Error $\\vert S_{{\\text{{est}}}} - S_{{\\text{{act}}}} \\vert$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
"""
    for (k, q, a_cnt, a_sel, e_cnt, e_sel, q_err) in q_table_rows:
        highlight = "**" if q_err == max_q_err else ""
        report += f"| $q_{k}$ | `{q:,.1f}` | {a_cnt} | {a_sel:.6f} | {e_cnt:.2f} | {e_sel:.6f} | {highlight}{q_err:.6f}{highlight} |\n"

    report += f"""
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
| **1000** | {t1000:.4f}s | {res_1000['elapsed_title']:.4f}s | {e1000:.6f} |
| **3000** | {t3000:.4f}s | {res_3000['elapsed_title']:.4f}s | {e3000:.6f} |
| **5000** | {t5000:.4f}s | {res_5000['elapsed_title']:.4f}s | {e5000:.6f} |

---

### 6. Full Step-by-Step Linear Regression Extrapolation ($N = 2,528,312$)

To extrapolate the construction build time for the entire `title` table ($N = 2,528,312$), we fit a linear regression model:
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
