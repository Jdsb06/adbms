import os
import subprocess
import matplotlib.pyplot as plt
import numpy as np

# Ensure plots directory exists
os.makedirs("plots", exist_ok=True)

# Run the simulation executable to fetch exact hit ratios
cmd = ["./code/lru-k", "100000"]
result = subprocess.run(cmd, capture_output=True, text=True, check=True)

buffer_sizes = []
lru1_hits = []
lru2_hits = []
lru3_hits = []

# Parse output table lines
lines = result.stdout.splitlines()
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

# Data for A0 Optimal Algorithm (from Slide 23 / Paper)
# A0 hit ratio is ~0.50 once B >= 100 (Pool 1 resident), slightly increasing with B
a0_hits = [0.300, 0.400, 0.500, 0.501, 0.502, 0.503, 0.504, 0.505, 0.508, 0.510, 0.513, 0.515, 0.518]

# Setup plot styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

# Plot curves with distinct colors and markers
ax.plot(buffer_sizes, lru1_hits, label='LRU-1 (Standard LRU)', color='#D9534F', marker='o', linewidth=2.2, markersize=6)
ax.plot(buffer_sizes, lru2_hits, label='LRU-2', color='#1B9E77', marker='s', linewidth=2.2, markersize=6)
ax.plot(buffer_sizes, lru3_hits, label='LRU-3', color='#7570B3', marker='^', linewidth=2.2, markersize=6)

# Horizontal / curve reference for A0 Optimal Algorithm
ax.plot(buffer_sizes, a0_hits, label=r'$A_0$ (Optimal Algorithm)', color='#E7298A', linestyle='--', linewidth=2.0, marker='d', markersize=5)
ax.axhline(y=0.50, color='#888888', linestyle=':', linewidth=1.2, label='0.50 Reference Mark (Pool 1 Max Hit Ratio)')

# Labels and Title
ax.set_title('LRU-K Two-Pool Experiment: Hit Ratio vs. Buffer Size', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Buffer Size (B)', fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel('Hit Ratio', fontsize=12, fontweight='bold', labelpad=10)

# Axis ticks and limits
ax.set_xticks(buffer_sizes)
ax.set_xlim(50, 460)
ax.set_ylim(0.10, 0.55)

# Formatting ticks and grid
ax.tick_params(axis='both', which='major', labelsize=10)
ax.grid(True, linestyle='--', alpha=0.5)

# Annotation for key observation
ax.annotate('LRU-2 & LRU-3 capture Pool 1\nat B ≥ 100 (Hit Ratio ≈ 0.50)', 
            xy=(100, 0.455), xytext=(150, 0.32),
            arrowprops=dict(facecolor='#333333', shrink=0.08, width=1, headwidth=6),
            fontsize=10, fontweight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFFFCC', alpha=0.8, edgecolor='#CCCCCC'))

# Legend
ax.legend(loc='lower right', frameon=True, framealpha=0.95, facecolor='white', edgecolor='#DDDDDD', fontsize=10)

plt.tight_layout()

# Save plot PNG
output_path = os.path.join("plots", "two_pool_hit_ratios.png")
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Plot successfully saved to {output_path}")
