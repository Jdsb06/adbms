import os
import psycopg2
import matplotlib.pyplot as plt
import numpy as np

def parse_pg_array(arr_val):
    if arr_val is None:
        return []
    if isinstance(arr_val, list):
        return [str(x) for x in arr_val]
    if isinstance(arr_val, str):
        s = arr_val.strip()
        if s.startswith('{') and s.endswith('}'):
            s = s[1:-1]
        if not s:
            return []
        import csv
        import io
        f = io.StringIO(s)
        reader = csv.reader(f)
        try:
            return next(reader)
        except Exception:
            return s.split(',')
    return []

def run_q1():
    os.makedirs('plots', exist_ok=True)
    conn = psycopg2.connect(dbname='imdbload')
    cur = conn.cursor()

    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = [r[0] for r in cur.fetchall()]
    cardinalities = {}
    total_db_rows = 0
    for t in tables:
        cur.execute(f'SELECT count(*) FROM "{t}";')
        cnt = cur.fetchone()[0]
        cardinalities[t] = cnt
        total_db_rows += cnt

    cur.execute("SELECT count(*) FROM title;")
    total_rows = cur.fetchone()[0]
    print(f"Total rows in title table: {total_rows}")

    cur.execute("""
        SELECT attname, null_frac, avg_width, n_distinct, most_common_vals, most_common_freqs, histogram_bounds
        FROM pg_stats
        WHERE tablename = 'title' AND attname IN ('id', 'title');
    """)
    rows = cur.fetchall()

    stats = {}
    for r in rows:
        attname, null_frac, avg_width, n_distinct, mcv, mcf, bounds = r
        stats[attname] = {
            'null_frac': null_frac,
            'avg_width': avg_width,
            'n_distinct': n_distinct,
            'mcv': mcv,
            'mcf': mcf,
            'bounds': parse_pg_array(bounds)
        }

    print("\n=== Stats fetched from pg_stats ===")
    for col in ['id', 'title']:
        b = stats[col]['bounds']
        b_len = len(b) if b else 0
        print(f"Column '{col}': {b_len} boundary values ({b_len - 1 if b_len else 0} buckets)")

    raw_id_bounds = stats['id']['bounds']
    id_bounds = [int(x) for x in raw_id_bounds if x.isdigit()]
    title_bounds = stats['title']['bounds']

    cur.execute("SELECT count(*) FROM title WHERE title < 'Race';")
    actual_race_count = cur.fetchone()[0]
    actual_race_sel = actual_race_count / total_rows

    cur.execute("EXPLAIN SELECT * FROM title WHERE title < 'Race';")
    explain_race = cur.fetchall()
    est_race_count = 0
    for line in explain_race:
        text = line[0]
        if 'rows=' in text:
            parts = text.split('rows=')[1].split()[0]
            est_race_count = int(parts)
            break
    est_race_sel = est_race_count / total_rows

    cur.execute("SELECT count(*) FROM title WHERE id < 350000;")
    actual_id_count = cur.fetchone()[0]
    actual_id_sel = actual_id_count / total_rows

    cur.execute("EXPLAIN SELECT * FROM title WHERE id < 350000;")
    explain_id = cur.fetchall()
    est_id_count = 0
    for line in explain_id:
        text = line[0]
        if 'rows=' in text:
            parts = text.split('rows=')[1].split()[0]
            est_id_count = int(parts)
            break
    est_id_sel = est_id_count / total_rows

    err_race = abs(est_race_sel - actual_race_sel)
    err_id = abs(est_id_sel - actual_id_sel)
    max_err = max(err_race, err_id)
    rel_err_race = (err_race / actual_race_sel) * 100 if actual_race_sel > 0 else 0
    rel_err_id = (err_id / actual_id_sel) * 100 if actual_id_sel > 0 else 0

    print("\n=== Query Selectivities & Errors ===")
    print(f"Query 1 (title < 'Race'): Actual={actual_race_count} ({actual_race_sel:.6f}), Est={est_race_count} ({est_race_sel:.6f}), Absolute Error={err_race:.6f}, Rel Error={rel_err_race:.2f}%")
    print(f"Query 2 (id < 350000): Actual={actual_id_count} ({actual_id_sel:.6f}), Est={est_id_count} ({est_id_sel:.6f}), Absolute Error={err_id:.6f}, Rel Error={rel_err_id:.2f}%")

    # Plot 1: Histogram for title.id
    if len(id_bounds) > 1:
        plt.figure(figsize=(10, 5))
        num_buckets_id = len(id_bounds) - 1
        freq_per_bucket_id = total_rows / num_buckets_id
        bucket_centers = [(id_bounds[i] + id_bounds[i+1])/2 for i in range(num_buckets_id)]
        bucket_widths = [max(1, id_bounds[i+1] - id_bounds[i]) for i in range(num_buckets_id)]

        plt.bar(bucket_centers, [freq_per_bucket_id]*num_buckets_id, width=bucket_widths, color='#2b5c8f', edgecolor='black', alpha=0.7)
        plt.title('PostgreSQL Equi-Depth Histogram for title.id')
        plt.xlabel('id Value Boundaries')
        plt.ylabel('Frequency (Rows per Bucket)')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig('plots/q1_histogram_id.png', dpi=300)
        plt.close()

    # Plot 2: Histogram for title.title
    if len(title_bounds) > 1:
        plt.figure(figsize=(12, 5))
        num_buckets_title = len(title_bounds) - 1
        freq_per_bucket_title = total_rows / num_buckets_title

        step = max(1, num_buckets_title // 10)
        x_indices = list(range(num_buckets_title))
        
        plt.bar(x_indices, [freq_per_bucket_title]*num_buckets_title, color='#4682b4', edgecolor='black', width=0.8, alpha=0.7)
        plt.xticks(x_indices[::step], [title_bounds[i][:15] for i in range(0, num_buckets_title, step)], rotation=45, ha='right', fontsize=9)
        plt.title('PostgreSQL Equi-Depth Histogram for title.title')
        plt.xlabel('title Boundary Values (Lexicographical Order)')
        plt.ylabel('Frequency (Rows per Bucket)')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig('plots/q1_histogram_title.png', dpi=300)
        plt.close()

    conn.close()
    print("\nQ1 execution completed! Plots saved in plots/.")

    return {
        'tables': tables,
        'cardinalities': cardinalities,
        'total_db_rows': total_db_rows,
        'id_bounds_list': id_bounds,
        'title_bounds_list': title_bounds,
        'max_err': max_err,
        'act_race_cnt': actual_race_count,
        'act_race_sel': actual_race_sel,
        'est_race_cnt': est_race_count,
        'est_race_sel': est_race_sel,
        'err_race': err_race,
        'act_id_cnt': actual_id_count,
        'act_id_sel': actual_id_sel,
        'est_id_cnt': est_id_count,
        'est_id_sel': est_id_sel,
        'err_id': err_id
    }

if __name__ == '__main__':
    run_q1()
