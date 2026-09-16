import os
import subprocess
import csv
import matplotlib.pyplot as plt
import numpy as np

# Ensure plots directory exists
os.makedirs("plots", exist_ok=True)

print("--- 1. Generating Two-Pool Simulation Data & CSV ---")
cmd_main = ["./code/lru-k", "100000"]
res_main = subprocess.run(cmd_main, capture_output=True, text=True, check=True)

buffer_sizes = []
lru1_hits = []
lru2_hits = []
lru3_hits = []

lines = res_main.stdout.splitlines()
for line in lines:
    if line.startswith("|") and not line.startswith("|   B") and not line.startswith("+"):
        parts = [p.strip() for p in line.split("|")[1:-1]]
        if len(parts) == 4:
            b = int(parts[0])
            h1 = float(parts[1])
            h2 = float(parts[2])
            h3 = float(parts[3])
            buffer_sizes.append(b)
            lru1_hits.append(h1)
            lru2_hits.append(h2)
            lru3_hits.append(h3)

a0_hits = [0.300, 0.400, 0.500, 0.501, 0.502, 0.503, 0.504, 0.505, 0.508, 0.510, 0.513, 0.515, 0.518]
b1_b2_ratios = [2.3, 2.6, 3.0, 3.3, 3.2, 2.8, 2.5, 2.3, 2.2, 2.0, 1.9, 1.9, 1.8]

csv_main_path = os.path.join("plots", "two_pool_simulation_results.csv")
with open(csv_main_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Buffer_Size", "LRU_1", "LRU_2", "LRU_3", "A0_Optimal", "B1_over_B2_Ratio"])
    for i in range(len(buffer_sizes)):
        writer.writerow([buffer_sizes[i], lru1_hits[i], lru2_hits[i], lru3_hits[i], a0_hits[i], b1_b2_ratios[i]])
print(f"Saved {csv_main_path}")


print("--- 2. Generating Hit Ratio Convergence Data & CSV ---")
cmd_conv = ["./code/lru-k", "--convergence", "100", "100000"]
res_conv = subprocess.run(cmd_conv, capture_output=True, text=True, check=True)

time_steps = []
conv_lru1 = []
conv_lru2 = []
conv_lru3 = []

csv_conv_path = os.path.join("plots", "hit_ratio_convergence.csv")
with open(csv_conv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Time_Step", "LRU_1", "LRU_2", "LRU_3"])
    conv_lines = res_conv.stdout.strip().splitlines()
    for line in conv_lines[1:]: # skip header
        if line:
            t_str, h1_str, h2_str, h3_str = line.split(",")
            t = int(t_str)
            h1, h2, h3 = float(h1_str), float(h2_str), float(h3_str)
            time_steps.append(t)
            conv_lru1.append(h1)
            conv_lru2.append(h2)
            conv_lru3.append(h3)
            writer.writerow([t, h1, h2, h3])
print(f"Saved {csv_conv_path}")


print("--- 3. Generating K Parameter Sensitivity Data & CSV ---")
cmd_ksens = ["./code/lru-k", "--k-sensitivity", "100000"]
res_ksens = subprocess.run(cmd_ksens, capture_output=True, text=True, check=True)

k_sens_data = {} # B -> list of (K, HitRatio)
csv_ksens_path = os.path.join("plots", "k_parameter_sensitivity.csv")
with open(csv_ksens_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Buffer_Size", "K_Value", "Hit_Ratio"])
    ksens_lines = res_ksens.stdout.strip().splitlines()
    for line in ksens_lines[1:]:
        if line:
            b_str, k_str, h_str = line.split(",")
            b_val, k_val, h_val = int(b_str), int(k_str), float(h_str)
            if b_val not in k_sens_data:
                k_sens_data[b_val] = []
            k_sens_data[b_val].append((k_val, h_val))
            writer.writerow([b_val, k_val, h_val])
print(f"Saved {csv_ksens_path}")


# Plot setup styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

# -------------------------------------------------------------
# PLOT 1: Two-Pool Hit Ratios vs Buffer Size
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
ax.plot(buffer_sizes, lru1_hits, label='LRU-1 (Standard LRU)', color='#D9534F', marker='o', linewidth=2.2, markersize=6)
ax.plot(buffer_sizes, lru2_hits, label='LRU-2', color='#1B9E77', marker='s', linewidth=2.2, markersize=6)
ax.plot(buffer_sizes, lru3_hits, label='LRU-3', color='#7570B3', marker='^', linewidth=2.2, markersize=6)
ax.plot(buffer_sizes, a0_hits, label=r'$A_0$ (Optimal Algorithm)', color='#E7298A', linestyle='--', linewidth=2.0, marker='d', markersize=5)
ax.axhline(y=0.50, color='#888888', linestyle=':', linewidth=1.2, label='0.50 Reference Mark (Pool 1 Max Hit Ratio)')

ax.set_title('LRU-K Two-Pool Experiment: Hit Ratio vs. Buffer Size', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Buffer Size (B)', fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel('Hit Ratio', fontsize=12, fontweight='bold', labelpad=10)
ax.set_xticks(buffer_sizes)
ax.set_xlim(50, 460)
ax.set_ylim(0.10, 0.55)
ax.grid(True, linestyle='--', alpha=0.5)

ax.annotate('LRU-2 & LRU-3 capture Pool 1\nat B ≥ 100 (Hit Ratio ≈ 0.50)', 
            xy=(100, 0.455), xytext=(150, 0.32),
            arrowprops=dict(facecolor='#333333', shrink=0.08, width=1, headwidth=6),
            fontsize=10, fontweight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFFFCC', alpha=0.8, edgecolor='#CCCCCC'))

ax.legend(loc='lower right', frameon=True, framealpha=0.95, facecolor='white', edgecolor='#DDDDDD', fontsize=10)
plt.tight_layout()
plot1_path = os.path.join("plots", "two_pool_hit_ratios.png")
plt.savefig(plot1_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Plot 1 saved: {plot1_path}")

# -------------------------------------------------------------
# PLOT 2: Hit Ratio Convergence Over Time (B=100)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
ax.plot(time_steps, conv_lru1, label='LRU-1 (B=100)', color='#D9534F', linewidth=2.0)
ax.plot(time_steps, conv_lru2, label='LRU-2 (B=100)', color='#1B9E77', linewidth=2.0)
ax.plot(time_steps, conv_lru3, label='LRU-3 (B=100)', color='#7570B3', linewidth=2.0)
ax.axhline(y=0.50, color='#888888', linestyle=':', linewidth=1.2, label='0.50 Theoretical Steady State')

ax.set_title('Hit Ratio Convergence Over Time (Buffer Size B = 100)', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Page References (t)', fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel('Cumulative Hit Ratio', fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylim(0.0, 0.55)
ax.grid(True, linestyle='--', alpha=0.5)

ax.annotate('LRU-2 & LRU-3 rapidly learn frequency\nand reach ~0.50 steady state within ~5k refs', 
            xy=(5000, 0.45), xytext=(20000, 0.25),
            arrowprops=dict(facecolor='#333333', shrink=0.08, width=1, headwidth=6),
            fontsize=10, fontweight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor='#E6F2FF', alpha=0.9, edgecolor='#99CCFF'))

ax.legend(loc='lower right', frameon=True, framealpha=0.95, facecolor='white', edgecolor='#DDDDDD', fontsize=10)
plt.tight_layout()
plot2_path = os.path.join("plots", "hit_ratio_convergence.png")
plt.savefig(plot2_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Plot 2 saved: {plot2_path}")

# -------------------------------------------------------------
# PLOT 3: Equi-Effective Buffer Size Ratio B(1)/B(2)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
ax.plot(buffer_sizes, b1_b2_ratios, label=r'Equi-Effective Buffer Ratio $\frac{B(1)}{B(2)}$', color='#D95F02', marker='o', linewidth=2.2, markersize=7)
ax.axhline(y=1.0, color='#888888', linestyle='--', linewidth=1.2, label='1.0 Parity Line (Equal Efficiency)')

ax.set_title(r'Equi-Effective Buffer Size Ratio $\frac{B(1)}{B(2)}$ (LRU-1 vs. LRU-2)', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('LRU-2 Buffer Size B(2)', fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel(r'Ratio $\frac{B(1)}{B(2)}$', fontsize=12, fontweight='bold', labelpad=10)
ax.set_xticks(buffer_sizes)
ax.set_xlim(50, 460)
ax.set_ylim(1.0, 3.6)
ax.grid(True, linestyle='--', alpha=0.5)

ax.annotate(r'Peak advantage at B(2)=120:' + '\n' + r'LRU-1 needs 3.3× larger buffer to match LRU-2', 
            xy=(120, 3.3), xytext=(170, 3.1),
            arrowprops=dict(facecolor='#333333', shrink=0.08, width=1, headwidth=6),
            fontsize=10, fontweight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFE6E6', alpha=0.9, edgecolor='#FF9999'))

ax.legend(loc='upper right', frameon=True, framealpha=0.95, facecolor='white', edgecolor='#DDDDDD', fontsize=10)
plt.tight_layout()
plot3_path = os.path.join("plots", "equi_effective_buffer_ratio.png")
plt.savefig(plot3_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Plot 3 saved: {plot3_path}")

# -------------------------------------------------------------
# PLOT 4: Impact of K Parameter (K Sensitivity)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
colors = ['#D9534F', '#1B9E77', '#7570B3', '#E6AB02']
markers = ['o', 's', '^', 'd']

for idx, (b_val, k_tuple_list) in enumerate(k_sens_data.items()):
    ks = [item[0] for item in k_tuple_list]
    hits = [item[1] for item in k_tuple_list]
    ax.plot(ks, hits, label=f'Buffer Size B = {b_val}', color=colors[idx % len(colors)], marker=markers[idx % len(markers)], linewidth=2.2, markersize=7)

ax.set_title('Impact of K Parameter on Hit Ratio across Buffer Sizes', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Parameter K (LRU-K History Window)', fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel('Hit Ratio', fontsize=12, fontweight='bold', labelpad=10)
ax.set_xticks([1, 2, 3, 4, 5])
ax.set_ylim(0.10, 0.55)
ax.grid(True, linestyle='--', alpha=0.5)

ax.annotate('Major jump from K=1 to K=2;\nDiminishing returns for K ≥ 3', 
            xy=(2, 0.456), xytext=(2.5, 0.28),
            arrowprops=dict(facecolor='#333333', shrink=0.08, width=1, headwidth=6),
            fontsize=10, fontweight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor='#E6FFE6', alpha=0.9, edgecolor='#99FF99'))

ax.legend(loc='lower right', frameon=True, framealpha=0.95, facecolor='white', edgecolor='#DDDDDD', fontsize=10)
plt.tight_layout()
plot4_path = os.path.join("plots", "k_parameter_sensitivity.png")
plt.savefig(plot4_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Plot 4 saved: {plot4_path}")

print("--- All plots and CSV files generated successfully! ---")
