import os
import time
import psycopg2
import matplotlib.pyplot as plt
import numpy as np

def build_optimal_histogram(data, num_buckets=20):
    n = len(data)
    if n == 0:
        return [], []
    if n <= num_buckets:
        return [(data[i], data[i]) for i in range(n)], [1]*n

    arr = np.array(data, dtype=np.float64)
    pref = np.zeros(n + 1, dtype=np.float64)
    pref2 = np.zeros(n + 1, dtype=np.float64)
    np.cumsum(arr, out=pref[1:])
    np.cumsum(arr**2, out=pref2[1:])

    dp = np.full((num_buckets + 1, n + 1), np.inf, dtype=np.float64)
    parent = np.zeros((num_buckets + 1, n + 1), dtype=np.int32)

    j_arr = np.arange(1, n + 1)
    sum_x = pref[j_arr]
    sum_x2 = pref2[j_arr]
    dp[1, 1:] = np.maximum(0.0, sum_x2 - (sum_x**2) / j_arr)

    for b in range(2, num_buckets + 1):
        for i in range(b, n + 1):
            j_vals = np.arange(b - 1, i)
            sx = pref[i] - pref[j_vals]
            sx2 = pref2[i] - pref2[j_vals]
            cnt = i - j_vals
            c_vals = dp[b - 1, j_vals] + np.maximum(0.0, sx2 - (sx**2) / cnt)
            best_idx = np.argmin(c_vals)
            dp[b, i] = c_vals[best_idx]
            parent[b, i] = j_vals[best_idx]

    splits = [n]
    curr_b, curr_i = num_buckets, n
    while curr_b > 1:
        p = int(parent[curr_b, curr_i])
        splits.append(p)
        curr_i = p
        curr_b -= 1
    splits.append(0)
    splits.reverse()

    bucket_boundaries = []
    bucket_counts = []
    for k in range(len(splits) - 1):
        s_idx, e_idx = splits[k], splits[k+1]
        bucket_counts.append(e_idx - s_idx)
        bucket_boundaries.append((arr[s_idx], arr[e_idx - 1]))

    return bucket_boundaries, bucket_counts

def string_to_float(s):
    res = 0.0
    for i, ch in enumerate(s[:8]):
        res += ord(ch) / (256 ** (i + 1))
    return res

def fetch_sample(cur, sample_size, col_name='id'):
    cur.execute("SELECT setseed(0.42);")
    pct = max(0.01, (sample_size * 100.0) / 2528312)
    query = f"SELECT {col_name} FROM title TABLESAMPLE BERNOULLI({pct:.4f}) LIMIT {sample_size};"
    cur.execute(query)
    rows = [r[0] for r in cur.fetchall()]
    if len(rows) < sample_size:
        cur.execute("SELECT setseed(0.42);")
        cur.execute(f"SELECT {col_name} FROM title ORDER BY random() LIMIT {sample_size};")
        rows = [r[0] for r in cur.fetchall()]
    return rows

def compute_max_selectivity_error(bucket_boundaries, bucket_counts, sample_data):
    if not sample_data or not bucket_boundaries:
        return 0.0
    sample_n = len(sample_data)
    errors = []
    
    quantiles = np.linspace(min(sample_data), max(sample_data), 10)
    for q in quantiles:
        actual_sel = sum(1 for x in sample_data if x <= q) / sample_n
        
        est_count = 0
        for (low, high), cnt in zip(bucket_boundaries, bucket_counts):
            if high <= q:
                est_count += cnt
            elif low <= q < high:
                frac = (q - low) / max(1e-6, (high - low))
                est_count += cnt * frac
        est_sel = est_count / sample_n
        errors.append(abs(est_sel - actual_sel))
        
    return max(errors) if errors else 0.0

def generate_histogram_plot(bounds, counts, sample_data, title_str, save_path, is_string=False):
    plt.figure(figsize=(10, 8))
    labels = []
    if is_string:
        cum_cnt = 0
        for cnt in counts:
            start_str = sample_data[cum_cnt][:15]
            cum_cnt += cnt
            end_str = sample_data[cum_cnt - 1][:15]
            labels.append(f"['{start_str}' - '{end_str}']")
        color_choice = '#4682b4'
        ylabel_str = 'Value Boundaries String Buckets (Y-axis)'
    else:
        labels = [f"[{int(b[0])} - {int(b[1])}]" for b in bounds]
        color_choice = '#2e8b57'
        ylabel_str = 'Value Boundaries Bucket Intervals (Y-axis)'

    plt.barh(range(len(counts)), counts, color=color_choice, edgecolor='black', alpha=0.8)
    plt.yticks(range(len(counts)), labels, fontsize=8)
    plt.xlabel('Frequency (X-axis)')
    plt.ylabel(ylabel_str)
    plt.title(title_str)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

def run_q2():
    os.makedirs('plots', exist_ok=True)
    conn = psycopg2.connect(dbname='imdbload')
    cur = conn.cursor()

    sample_sizes = [1000, 3000, 5000]
    num_buckets = 20

    timings_id = {}
    errors_id = {}
    timings_title = {}
    hist_results = {}

    print("=== Running Q2 Vectorized DP Experiments ===")
    for N in sample_sizes:
        print(f"\n--- Processing Sample Size N = {N} ---")
        
        id_sample = fetch_sample(cur, N, 'id')
        id_sample.sort()
        
        t0 = time.time()
        id_bounds, id_counts = build_optimal_histogram(id_sample, num_buckets=num_buckets)
        t1 = time.time()
        elapsed_id = t1 - t0
        err_id = compute_max_selectivity_error(id_bounds, id_counts, id_sample)
        
        timings_id[N] = elapsed_id
        errors_id[N] = err_id
        print(f"[id] N={N}: Build Time = {elapsed_id:.4f}s, Max Selectivity Error = {err_id:.6f}")

        title_sample = fetch_sample(cur, N, 'title')
        title_sample.sort()
        title_encoded = [string_to_float(t) for t in title_sample]
        
        t0 = time.time()
        title_bounds_num, title_counts = build_optimal_histogram(title_encoded, num_buckets=num_buckets)
        t1 = time.time()
        elapsed_title = t1 - t0
        timings_title[N] = elapsed_title
        print(f"[title] N={N}: Build Time = {elapsed_title:.4f}s")

        hist_results[N] = {
            'id_bounds': id_bounds,
            'id_counts': id_counts,
            'id_sample': id_sample,
            'elapsed_id': elapsed_id,
            'err_id': err_id,
            'title_bounds_num': title_bounds_num,
            'title_counts': title_counts,
            'title_sample': title_sample,
            'elapsed_title': elapsed_title
        }

        # Generate plots for N=1000 and N=3000
        if N in [1000, 3000]:
            generate_histogram_plot(
                id_bounds, id_counts, id_sample,
                f'Optimal Serial Histogram (B={num_buckets}) for title.id (N={N})',
                f'plots/q2_histogram_id_{N}.png',
                is_string=False
            )
            generate_histogram_plot(
                title_bounds_num, title_counts, title_sample,
                f'Optimal Serial Histogram (B={num_buckets}) for title.title (N={N})',
                f'plots/q2_histogram_title_{N}.png',
                is_string=True
            )

    X = np.array(sample_sizes)
    Y = np.array([timings_id[n] for n in sample_sizes])
    slope, intercept = np.polyfit(X, Y, 1)
    
    full_table_N = 2528312
    extrapolated_time = slope * full_table_N + intercept
    print(f"\n=== Linear Regression Extrapolation ===")
    print(f"Slope m = {slope:.8f} s/sample, Intercept c = {intercept:.6f} s")
    print(f"Extrapolated Build Time for Full Table (N={full_table_N:,}): {extrapolated_time:.2f} seconds ({extrapolated_time/60:.2f} minutes)")

    plt.figure(figsize=(8, 5))
    plt.plot(sample_sizes, Y, 'o-', color='#d9534f', linewidth=2, markersize=8, label='Measured Timings')
    x_line = np.linspace(500, 6000, 100)
    plt.plot(x_line, slope * x_line + intercept, '--', color='#333333', label=f'Linear Fit (y={slope:.2e}x+{intercept:.2f})')
    plt.xlabel('Sample Size N')
    plt.ylabel('Build Time (Seconds)')
    plt.title('Sample Size vs Histogram Build Time')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('plots/q2_sample_size_vs_time.png', dpi=300)
    plt.close()

    plt.figure(figsize=(8, 5))
    err_vals = [errors_id[n] for n in sample_sizes]
    plt.plot(sample_sizes, err_vals, 's-', color='#0275d8', linewidth=2, markersize=8)
    plt.xlabel('Sample Size N')
    plt.ylabel('Max Selectivity Error')
    plt.title('Sample Size vs Max Selectivity Error')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('plots/q2_sample_size_vs_error.png', dpi=300)
    plt.close()

    conn.close()
    print("\nQ2 execution completed! All plots saved in plots/.")
    
    return {
        'timings_id': timings_id,
        'errors_id': errors_id,
        'timings_title': timings_title,
        'extrapolated_time': extrapolated_time,
        'slope': slope,
        'intercept': intercept,
        'hist_results': hist_results
    }

if __name__ == '__main__':
    run_q2()
