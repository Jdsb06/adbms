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

def build_optimal_serial_histogram(raw_data, num_buckets=10, is_string=False):
    """
    Constructs an optimal Serial Histogram (B = 10 buckets) by grouping domain items
    by unique frequencies first.
    If the number of unique frequencies D <= B, creates D buckets (one per unique frequency).
    If D > B, runs Dynamic Programming on the D unique frequency groups to find the B
    optimal frequency intervals minimizing sum(n_i * V_i).
    """
    if is_string:
        val_map = {v: string_to_float(v) for v in set(raw_data)}
        counts = Counter(raw_data)
        distinct_items = sorted(counts.keys(), key=lambda v: (counts[v], val_map[v]))
    else:
        val_map = {v: float(v) for v in set(raw_data)}
        counts = Counter(raw_data)
        distinct_items = sorted(counts.keys(), key=lambda v: (counts[v], float(v)))

    # Group domain items by unique frequency values
    freq_groups = {}
    for v in distinct_items:
        f = counts[v]
        if f not in freq_groups:
            freq_groups[f] = []
        freq_groups[f].append(v)

    unique_freqs = sorted(freq_groups.keys())
    m_freqs = len(unique_freqs)

    if m_freqs <= num_buckets:
        buckets = []
        for f in unique_freqs:
            b_items = freq_groups[f]
            cnt = len(b_items)
            tot_tuples = cnt * f
            b_num_vals = [val_map[v] for v in b_items]
            buckets.append({
                'distinct_count': cnt,
                'min_freq': f,
                'max_freq': f,
                'avg_freq': float(f),
                'total_tuples': tot_tuples,
                'val_min': min(b_num_vals),
                'val_max': max(b_num_vals),
                'sample_min_str': str(b_items[0])[:15],
                'sample_max_str': str(b_items[-1])[:15],
                'values': b_items
            })
        return buckets

    # If m_freqs > num_buckets, run DP over unique frequency groups
    n_groups = m_freqs
    group_counts = np.array([len(freq_groups[f]) for f in unique_freqs], dtype=np.float64)
    group_freqs = np.array(unique_freqs, dtype=np.float64)

    pref_cnt = np.zeros(n_groups + 1, dtype=np.float64)
    pref_tup = np.zeros(n_groups + 1, dtype=np.float64)
    pref_sq = np.zeros(n_groups + 1, dtype=np.float64)

    np.cumsum(group_counts, out=pref_cnt[1:])
    np.cumsum(group_counts * group_freqs, out=pref_tup[1:])
    np.cumsum(group_counts * (group_freqs**2), out=pref_sq[1:])

    dp = np.full((num_buckets + 1, n_groups + 1), np.inf, dtype=np.float64)
    parent = np.zeros((num_buckets + 1, n_groups + 1), dtype=np.int32)

    j_arr = np.arange(1, n_groups + 1)
    c_cnt = pref_cnt[j_arr]
    c_tup = pref_tup[j_arr]
    c_sq = pref_sq[j_arr]
    dp[1, 1:] = np.maximum(0.0, c_sq - (c_tup**2) / c_cnt)

    for b in range(2, num_buckets + 1):
        for i in range(b, n_groups + 1):
            j_vals = np.arange(b - 1, i)
            dx_cnt = pref_cnt[i] - pref_cnt[j_vals]
            dx_tup = pref_tup[i] - pref_tup[j_vals]
            dx_sq = pref_sq[i] - pref_sq[j_vals]
            c_vals = dp[b - 1, j_vals] + np.maximum(0.0, dx_sq - (dx_tup**2) / dx_cnt)
            best_idx = np.argmin(c_vals)
            dp[b, i] = c_vals[best_idx]
            parent[b, i] = j_vals[best_idx]

    splits = [n_groups]
    curr_b, curr_i = num_buckets, n_groups
    while curr_b > 1:
        p = int(parent[curr_b, curr_i])
        splits.append(p)
        curr_i = p
        curr_b -= 1
    splits.append(0)
    splits.reverse()

    buckets = []
    for k in range(len(splits) - 1):
        s_g, e_g = splits[k], splits[k+1]
        b_freqs_groups = unique_freqs[s_g:e_g]
        b_items = []
        for fg in b_freqs_groups:
            b_items.extend(freq_groups[fg])

        b_num_vals = [val_map[v] for v in b_items]
        cnt = len(b_items)
        tot_tuples = sum(counts[v] for v in b_items)
        avg_f = tot_tuples / cnt if cnt > 0 else 0.0

        buckets.append({
            'distinct_count': cnt,
            'min_freq': int(b_freqs_groups[0]),
            'max_freq': int(b_freqs_groups[-1]),
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
    Plots conceptual serial histogram for unique title.id column matching Slide 9:
    - X-axis: Frequencies (horizontal axis, value = 1)
    - Y-axis: Value Set (vertical axis, height = N = sample_size)
    - Upright vertical block centered at Frequency = 1
    """
    plt.figure(figsize=(9, 6))
    ax = plt.gca()

    # Upright vertical bar centered at Frequency = 1 with width = 0.6 and height = sample_size
    ax.bar(1.0, sample_size, width=0.6, color='#2b5c8f', edgecolor='black', linewidth=1.8, alpha=0.85, label=f'Sample IDs (N={sample_size:,})')
    ax.plot([1.0], [sample_size], 'ro', markersize=10, label='Frequency = 1 (Zero Variance)')

    ax.set_xlim(0, 4)
    ax.set_ylim(0, sample_size * 1.15)

    ax.set_xticks([1.0])
    ax.set_xticklabels(['1'], fontsize=11, fontweight='bold')
    ax.set_xlabel('Frequencies', fontsize=12, fontweight='bold')
    ax.set_ylabel('Value Set (Number of Distinct IDs)', fontsize=12, fontweight='bold')
    ax.set_title(title_str, fontsize=12, fontweight='bold', pad=15)

    props = dict(boxstyle='round,pad=0.6', facecolor='#ffffcc', edgecolor='#d9534f', alpha=0.95)
    ax.text(0.05, 0.92, note_str, transform=ax.transAxes, fontsize=9.5, verticalalignment='top', bbox=props)

    # Label on top of bar showing n_i
    ax.text(1.0, sample_size * 1.02, f'{sample_size:,} IDs\n(F = 1)', ha='center', va='bottom', fontsize=10, fontweight='bold', color='#2b5c8f')

    ax.grid(True, linestyle='--', alpha=0.4, axis='y')
    ax.legend(loc='upper right', fontsize=9.5)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

def generate_title_histogram_plot(buckets, title_str, save_path, note_str):
    """
    Plots conceptual V-Optimal serial histogram for title.title matching Slide 9:
    - X-axis: Frequencies (Ordered Ascending)
    - Y-axis: Value Set (Number of Distinct Titles / Stacked Elements)
    - Upright vertical blocks for each bucket spanning across frequency intervals.
    """
    plt.figure(figsize=(11, 7))
    ax = plt.gca()

    num_b = len(buckets)
    colors = cm.tab10(np.linspace(0, 1, max(10, num_b)))

    # Map bucket positions along the X-axis cleanly
    x_centers = []
    x_widths = []
    x_ticks = []
    x_tick_labels = []

    curr_x = 1.0
    for i, b in enumerate(buckets):
        f_min, f_max = b['min_freq'], b['max_freq']
        n_dist = b['distinct_count']
        tot_t = b['total_tuples']

        # Determine block width on frequency axis
        w = max(0.8, (f_max - f_min + 1) * 0.7)
        x_center = curr_x + w / 2.0

        c = colors[i % len(colors)]
        # Draw upright vertical block
        ax.bar(x_center, n_dist, width=w * 0.9, color=c, edgecolor='black', linewidth=1.5, alpha=0.85)

        # Label bucket info above or inside the vertical block
        f_str = f'{f_min}' if f_min == f_max else f'{f_min}-{f_max}'
        bar_text = f'B{i+1:02d}\nn={n_dist:,}\n(F:{f_str})'

        # Position text according to height
        text_y = n_dist + (max(b['distinct_count'] for b in buckets) * 0.02)
        ax.text(x_center, text_y, bar_text, ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='black')

        x_ticks.append(x_center)
        f_label = f'{f_min}' if f_min == f_max else f'{f_min}-{f_max}'
        x_tick_labels.append(f_label)

        curr_x += w + 0.4

    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_tick_labels, fontsize=9.5, fontweight='bold')
    ax.set_xlabel('Frequencies (Ordered Ascending)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Value Set (Number of Distinct Titles)', fontsize=12, fontweight='bold')
    ax.set_title(title_str, fontsize=12, fontweight='bold', pad=15)

    max_n = max(b['distinct_count'] for b in buckets)
    ax.set_ylim(0, max_n * 1.18)
    ax.set_xlim(0, curr_x + 0.5)

    props = dict(boxstyle='round,pad=0.6', facecolor='#e6f2ff', edgecolor='#0275d8', alpha=0.95)
    ax.text(0.45, 0.95, note_str, transform=ax.transAxes, fontsize=9.5, verticalalignment='top', bbox=props)

    ax.grid(True, linestyle='--', alpha=0.4, axis='y')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

def run_q2():
    os.makedirs('plots', exist_ok=True)
    conn = psycopg2.connect(dbname='imdbload')
    cur = conn.cursor()

    sample_sizes = [1000, 3000, 5000]
    num_buckets = 10
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
                raw_data = fetch_sample(cur, N, col, seed=s)
                
                # Measure pure algorithmic CPU construction time over 100 iterations
                REPEAT = 100
                t0 = time.perf_counter()
                for _ in range(REPEAT):
                    buckets = build_optimal_serial_histogram(raw_data, num_buckets=num_buckets, is_string=is_str)
                t1 = time.perf_counter()
                elapsed = (t1 - t0) / float(REPEAT)

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
                    note = 'title.title serial V-Optimal bucket boundaries (B=10)'
                elif N == 1000:
                    t_str = 'Sample Size: N=1000, title.title Serial Hist.'
                    note = 'title.title serial V-Optimal bucket boundaries (B=10, N=1000)'
                else:
                    t_str = 'Sample Size: N=5000, title.title Serial Hist.'
                    note = 'title.title serial V-Optimal bucket boundaries (B=10, N=5000)'
                generate_title_histogram_plot(run_buckets[0], t_str, f'plots/q2_histogram_title_{N}.png', note)

    # Linear Regression Extrapolation on Average Timings for 'id'
    X = np.array(sample_sizes, dtype=np.float64)
    Y = np.array([results['id'][n]['avg_time'] for n in sample_sizes], dtype=np.float64)
    slope, intercept = np.polyfit(X, Y, 1)
    if slope <= 0:
        slope = max(1e-6, float(Y[-1] - Y[0]) / float(X[-1] - X[0]))
        if slope <= 0:
            slope = 1e-6
        intercept = float(np.mean(Y) - slope * np.mean(X))

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
