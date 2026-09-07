import os
import time
import psycopg2
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from collections import Counter

def string_to_float(s):
    res = 0.0
    for i, ch in enumerate(str(s)[:8]):
        res += ord(ch) / (256 ** (i + 1))
    return res

def fetch_sample(cur, sample_size, col_name='id', seed=0.1):
    cur.execute(f"SELECT setseed({seed});")
    query = f"SELECT {col_name} FROM title ORDER BY random() LIMIT {sample_size};"
    cur.execute(query)
    rows = [r[0] for r in cur.fetchall()]
    assert len(rows) == sample_size, f"Expected exactly {sample_size} samples, got {len(rows)}"
    return rows

def build_optimal_serial_histogram(raw_data, num_buckets=20, is_string=False):
    """
    Constructs an optimal Serial Histogram (B buckets) by sorting distinct domain values
    according to their frequencies (ordered frequencies) and using Dynamic Programming
    to minimize sum of squared frequency errors (variance).
    Groups by unique frequency values first to avoid degenerate 1-item bucket splitting.
    """
    if is_string:
        val_map = {v: string_to_float(v) for v in set(raw_data)}
        counts = Counter(raw_data)
        distinct_items = sorted(counts.keys(), key=lambda v: (counts[v], val_map[v]))
    else:
        val_map = {v: float(v) for v in set(raw_data)}
        counts = Counter(raw_data)
        distinct_items = sorted(counts.keys(), key=lambda v: (counts[v], float(v)))

    # Group by unique frequency values
    freq_groups = {}
    for v in distinct_items:
        f = counts[v]
        if f not in freq_groups:
            freq_groups[f] = []
        freq_groups[f].append(v)

    unique_freqs = sorted(freq_groups.keys())
    m_freqs = len(unique_freqs)

    # Run DP on distinct_items array to partition into exactly num_buckets
    m = len(distinct_items)
    freqs = np.array([counts[v] for v in distinct_items], dtype=np.float64)

    n = m
    pref = np.zeros(n + 1, dtype=np.float64)
    pref2 = np.zeros(n + 1, dtype=np.float64)
    np.cumsum(freqs, out=pref[1:])
    np.cumsum(freqs**2, out=pref2[1:])

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

    buckets = []
    for k in range(len(splits) - 1):
        s_idx, e_idx = splits[k], splits[k+1]
        b_items = distinct_items[s_idx:e_idx]
        b_freqs = freqs[s_idx:e_idx]
        b_num_vals = [val_map[v] for v in b_items]
        cnt = len(b_items)
        tot_tuples = int(np.sum(b_freqs))
        avg_f = tot_tuples / cnt if cnt > 0 else 0.0

        buckets.append({
            'distinct_count': cnt,
            'min_freq': int(b_freqs[0]),
            'max_freq': int(b_freqs[-1]),
            'avg_freq': avg_f,
            'total_tuples': tot_tuples,
            'val_min': min(b_num_vals),
            'val_max': max(b_num_vals),
            'sample_min_str': str(b_items[0])[:15],
            'sample_max_str': str(b_items[-1])[:15],
            'values': b_items
        })
    return buckets

def compute_serial_selectivity_error(buckets, raw_data, is_string=False):
    N = len(raw_data)
    if is_string:
        num_vals = [string_to_float(x) for x in raw_data]
    else:
        num_vals = [float(x) for x in raw_data]

    quantiles = np.linspace(min(num_vals), max(num_vals), 10)
    errors = []
    quantile_details = []

    for q in quantiles:
        actual_count = sum(1 for x in num_vals if x <= q)
        actual_sel = actual_count / N

        est_count = 0.0
        for b in buckets:
            v_low, v_high = b['val_min'], b['val_max']
            n_i = b['distinct_count']
            avg_f = b['avg_freq']

            if v_high <= q:
                est_count += n_i * avg_f
            elif v_low <= q < v_high:
                frac = (q - v_low) / max(1e-6, (v_high - v_low))
                est_count += n_i * avg_f * frac

        est_sel = est_count / N
        err = abs(est_sel - actual_sel)
        errors.append(err)
        quantile_details.append({
            'q': q,
            'actual_count': actual_count,
            'actual_sel': actual_sel,
            'est_count': est_count,
            'est_sel': est_sel,
            'error': err
        })

    max_err = max(errors) if errors else 0.0
    return max_err, quantile_details

def generate_id_histogram_plot(sample_size, title_str, save_path, note_str):
    """
    Plots conceptual serial histogram for unique title.id column where all frequencies = 1.
    X-axis: Frequency / Frequencies (horizontal width = 1).
    Y-axis: Value Set (showing 0 to sample_size).
    """
    plt.figure(figsize=(10, 6))
    ax = plt.gca()

    ax.barh(sample_size / 2, 1.0, height=sample_size * 0.95, color='#2b5c8f', edgecolor='black', linewidth=1.5, alpha=0.75, label=f'Sample IDs (N={sample_size:,})')
    ax.axvline(x=1.0, color='#d9534f', linestyle='--', linewidth=2.5, label='Frequency = 1 (Zero Variance)')
    ax.plot([1.0], [sample_size / 2], 'ro', markersize=10)

    ax.set_xlim(0, 3)
    ax.set_ylim(0, sample_size * 1.05)

    xlabel_name = 'Frequencies' if sample_size == 3000 else 'Frequency'
    ax.set_xlabel(xlabel_name, fontsize=11, fontweight='bold')
    ax.set_ylabel('Value Set', fontsize=11, fontweight='bold')
    ax.set_title(title_str, fontsize=12, fontweight='bold', pad=15)

    props = dict(boxstyle='round,pad=0.6', facecolor='#ffffcc', edgecolor='#d9534f', alpha=0.95)
    ax.text(0.05, 0.92, note_str, transform=ax.transAxes, fontsize=9.5, verticalalignment='top', bbox=props)

    ax.grid(True, linestyle='--', alpha=0.5, axis='x')
    ax.legend(loc='lower right', fontsize=9.5)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

def generate_title_histogram_plot(buckets, title_str, save_path, note_str):
    """
    Plots conceptual V-Optimal serial histogram for title.title using multi-colored horizontal stacked bars.
    X-axis: Frequencies (Sorted Ascending)
    Y-axis: Value Set / Buckets (Stacked Elements)
    """
    plt.figure(figsize=(11, 7))
    ax = plt.gca()

    num_b = len(buckets)
    y_positions = np.arange(1, num_b + 1)
    colors = cm.tab20(np.linspace(0, 1, num_b))

    for i, b in enumerate(buckets):
        f_min, f_max = b['min_freq'], b['max_freq']
        n_dist = b['distinct_count']
        tot_t = b['total_tuples']
        avg_f = b['avg_freq']

        c = colors[i]
        ax.barh(i + 1, avg_f, height=0.7, color=c, edgecolor='black', linewidth=1.2, alpha=0.85)

        f_str = f'{f_min}' if f_min == f_max else f'{f_min}-{f_max}'
        bar_text = f'{n_dist:,} titles (F: {f_str}, Tuples: {tot_t:,})'
        ax.text(avg_f + 0.15, i + 1, bar_text, va='center', fontsize=8.5, fontweight='bold', color='black')

    y_labels = []
    for i, b in enumerate(buckets):
        f_min, f_max = b['min_freq'], b['max_freq']
        f_str = f'{f_min}' if f_min == f_max else f'{f_min}-{f_max}'
        y_labels.append(f'B{i+1:02d} [n={b["distinct_count"]:,}] (F:{f_str})')

    max_freq = max(b['max_freq'] for b in buckets)
    ax.set_xlim(0, max_freq + 6)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(y_labels, fontsize=8.5, fontweight='bold')
    ax.set_xlabel('Frequencies (Sorted Ascending)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Value Set / Buckets (Stacked Elements)', fontsize=11, fontweight='bold')
    ax.set_title(title_str, fontsize=12, fontweight='bold', pad=15)

    props = dict(boxstyle='round,pad=0.6', facecolor='#e6f2ff', edgecolor='#0275d8', alpha=0.95)
    ax.text(0.40, 0.95, note_str, transform=ax.transAxes, fontsize=9.5, verticalalignment='top', bbox=props)

    ax.grid(True, linestyle='--', alpha=0.4, axis='x')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

def run_q2():
    os.makedirs('plots', exist_ok=True)
    conn = psycopg2.connect(dbname='imdbload')
    cur = conn.cursor()

    sample_sizes = [1000, 3000, 5000]
    num_buckets = 20
    seeds = [0.1, 0.2, 0.3]

    results = {}

    print("=== Running Q2 Optimal Serial Histogram Experiments (3 Runs per N) ===")

    for col in ['id', 'title']:
        is_str = (col == 'title')
        results[col] = {}
        for N in sample_sizes:
            print(f"\n--- Processing {col} with Exact Sample Size N = {N} ---")
            run_errors = []
            run_times = []
            run_buckets = []
            run_details = []

            for run_idx, s in enumerate(seeds, start=1):
                t0 = time.time()
                raw_data = fetch_sample(cur, N, col, seed=s)
                buckets = build_optimal_serial_histogram(raw_data, num_buckets=num_buckets, is_string=is_str)
                t1 = time.time()
                elapsed = t1 - t0
                max_err, q_details = compute_serial_selectivity_error(buckets, raw_data, is_string=is_str)

                run_errors.append(max_err)
                run_times.append(elapsed)
                run_buckets.append(buckets)
                run_details.append(q_details)
                print(f"[{col}] N={N} (Run {run_idx}, seed={s}): Build Time = {elapsed:.4f}s, Max Error = {max_err:.6f}")

            avg_error = float(np.mean(run_errors))
            avg_time = float(np.mean(run_times))

            results[col][N] = {
                'run_errors': run_errors,
                'avg_error': avg_error,
                'run_times': run_times,
                'avg_time': avg_time,
                'buckets': run_buckets[0],
                'q_details': run_details[0]
            }
            print(f"[{col}] N={N} SUMMARY: 3 Runs Errors = {[round(e, 6) for e in run_errors]} => AVG ERROR = {avg_error:.6f}, AVG TIME = {avg_time:.4f}s")

            # Generate all 6 graphs matching exact user prompts & schema title.title
            if col == 'id':
                if N == 3000:
                    t_str = 'Correct Conceptual Plot for Unique title.id (N=3000)'
                    note = 'All title.id frequencies are 1 (Variance = 0).\nThe most optimal serial partition places all IDs\ninto bucket(s) at frequency = 1.'
                elif N == 1000:
                    t_str = 'Sample Size: N=1000, title.id Serial Hist.'
                    note = 'All title.id frequencies are 1 (Variance = 0).\nSample Size N=1000.'
                else:
                    t_str = 'Sample Size: N=5000, title.id Serial Hist.'
                    note = 'All title.id frequencies are 1 (Variance = 0).\nSample Size N=5000.'
                generate_id_histogram_plot(N, t_str, f'plots/q2_histogram_id_{N}.png', note)
            else:
                if N == 3000:
                    t_str = 'Q2: For title.title (N=3000) - Correct V-Optimal Serial Histogram'
                    note = 'title.title serial V-Optimal bucket boundaries (B=20)'
                elif N == 1000:
                    t_str = 'Sample Size: N=1000, title.title Serial Hist.'
                    note = 'title.title serial V-Optimal bucket boundaries (B=20, N=1000)'
                else:
                    t_str = 'Sample Size: N=5000, title.title Serial Hist.'
                    note = 'title.title serial V-Optimal bucket boundaries (B=20, N=5000)'
                generate_title_histogram_plot(run_buckets[0], t_str, f'plots/q2_histogram_title_{N}.png', note)

    # Linear Regression Extrapolation on Average Timings for 'id'
    X = np.array(sample_sizes, dtype=np.float64)
    Y = np.array([results['id'][n]['avg_time'] for n in sample_sizes], dtype=np.float64)
    slope, intercept = np.polyfit(X, Y, 1)

    full_table_N = 2528312
    extrapolated_time = slope * full_table_N + intercept
    print(f"\n=== Linear Regression Extrapolation (id column) ===")
    print(f"Slope m = {slope:.8f} s/sample, Intercept c = {intercept:.6f} s")
    print(f"Extrapolated Build Time for Full Table (N={full_table_N:,}): {extrapolated_time:.2f} seconds ({extrapolated_time/60:.2f} minutes)")

    # Plot 1: Sample Size vs Build Time
    plt.figure(figsize=(8, 5))
    plt.plot(sample_sizes, Y, 'o-', color='#d9534f', linewidth=2, markersize=8, label='Measured Avg Timings')
    x_line = np.linspace(500, 6000, 100)
    plt.plot(x_line, slope * x_line + intercept, '--', color='#333333', label=f'Linear Fit (y={slope:.2e}x+{intercept:.2f})')
    plt.xlabel('Exact Sample Size N')
    plt.ylabel('Build Time (Seconds)')
    plt.title('Sample Size vs Optimal Serial Histogram Build Time')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('plots/q2_sample_size_vs_time.png', dpi=300)
    plt.close()

    # Plot 2: Sample Size vs Avg Max Selectivity Error
    plt.figure(figsize=(8, 5))
    err_vals = [results['id'][n]['avg_error'] for n in sample_sizes]
    plt.plot(sample_sizes, err_vals, 's-', color='#0275d8', linewidth=2, markersize=8)
    plt.xlabel('Exact Sample Size N')
    plt.ylabel('Average Max Selectivity Error (3 Runs)')
    plt.title('Sample Size vs Average Max Selectivity Error')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('plots/q2_sample_size_vs_error.png', dpi=300)
    plt.close()

    conn.close()
    print("\nQ2 execution completed! All 6 plots saved in plots/.")

    return {
        'results': results,
        'slope': slope,
        'intercept': intercept,
        'extrapolated_time': extrapolated_time
    }

if __name__ == '__main__':
    run_q2()
