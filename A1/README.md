# Join Order Benchmark (JOB) & Histogram Analysis (ADBMS Assignment 0 & 1)

This repository contains the complete implementation, database loading automation, optimal serial histogram dynamic programming algorithm, statistical visualizations, LaTeX source code, and PDF report generation for **Assignment 0** and **Assignment 1 (Histogram)**.

---

## ⚡ Single-Command Execution (Automated Evaluator)

As required by evaluation guidelines, the entire submission pipeline—database extraction, schema loading, index creation, histogram execution, plot generation, report compilation, LaTeX conversion, and PDF building—runs end-to-end via **a single command**:

```bash
./run_all.sh
```

---

## 📁 Categorized Directory Structure

```text
A1/
├── run_all.sh                      # Master single-command executable runner
├── scripts/                        # Executable automation scripts & SQL queries
│   ├── load_job.sh                 # Database loader script (downloads/extracts CSVs & creates DB)
│   ├── import_job.sql              # Schema, CSV import & index creation SQL script
│   ├── get_cardinalities.sql       # Table row count & primary key query
│   ├── solution_q1.py              # Q1: PostgreSQL equi-depth histogram analysis
│   ├── solution_q2.py              # Q2: Dynamic Programming V-Optimal Serial Histogram
│   ├── generate_report.py          # Master benchmark runner & report compiler
│   ├── export_llm_chat.py          # Transcribes conversation log into markdown
│   └── build_pdf_from_tex.py       # Converts markdown reports to LaTeX (.tex) and compiles PDF
│
├── reports/                        # Final submission documents & PDF prompt
│   ├── Assignment_Report.pdf       # Compiled Assignment 0 & 1 Report (PDF)
│   ├── Assignment_Report.tex       # LaTeX source file for Assignment 0 & 1 Report
│   ├── Assignment_Report.md        # Assignment 0 & 1 Report (.md)
│   ├── LLM_Conversations.pdf       # AI assistant interaction log (PDF)
│   ├── LLM_Conversations.tex       # LaTeX source file for AI assistant log
│   ├── LLM_Conversations.md        # AI assistant interaction log (.md)
│   └── Assignment 1 Histogram.pdf  # Assignment requirement PDF prompt
│
├── plots/                          # Generated visualization charts (.png)
│   ├── q1_histogram_id.png         # Q1: title.id PostgreSQL equi-depth histogram
│   ├── q1_histogram_title.png      # Q1: title.title PostgreSQL equi-depth histogram
│   ├── q2_histogram_id_1000.png    # Q2: N=1000 title.id optimal histogram
│   ├── q2_histogram_title_1000.png # Q2: N=1000 title.title optimal histogram
│   ├── q2_histogram_id_3000.png    # Q2: N=3000 title.id optimal histogram
│   ├── q2_histogram_title_3000.png # Q2: N=3000 title.title optimal histogram
│   ├── q2_sample_size_vs_time.png  # Q2: Sample Size vs Build Time plot
│   └── q2_sample_size_vs_error.png # Q2: Sample Size vs Max Selectivity Error plot
│
├── data/                           # IMDB dataset CSVs & archives (gitignored)
│   ├── imdb.tgz
│   └── *.csv
│
├── job/                            # Join Order Benchmark (JOB) queries & schema
├── .gitignore                      # Git exclusion rules
└── README.md                       # Repository documentation
```

---

## 🛠️ Execution Pipeline & Command Parameters

If executing individual stages separately, the parameters and scripts are configured as follows:

| Stage | Command / Script | Parameters & Output |
| :--- | :--- | :--- |
| **1. Database Loading** | `./scripts/load_job.sh` | Extracts `imdb.tgz`, creates DB `imdbload`, imports 21 tables, builds foreign key indexes, runs `ANALYZE`. |
| **2. Q1 Analysis** | `./venv/bin/python3 scripts/solution_q1.py` | Queries `pg_stats` for `title.id` and `title.title`, generates 100-bucket equi-depth plots (`q1_histogram_id.png`, `q1_histogram_title.png`). |
| **3. Q2 Benchmark** | `./venv/bin/python3 scripts/solution_q2.py` | Runs $O(B \cdot N^2)$ DP optimal histogram for $N \in \{1000, 3000, 5000\}$, $B=20$, generates 6 plots, linear regression coefficients $m, c$, and quantile error tables. |
| **4. Report Compiler** | `./venv/bin/python3 scripts/generate_report.py` | Executes Q1 and Q2 benchmarks and writes `reports/Assignment_Report.md`. |
| **5. LLM Transcriber** | `./venv/bin/python3 scripts/export_llm_chat.py` | Extracts JSONL conversation logs and generates `reports/LLM_Conversations.md`. |
| **6. LaTeX & PDF Builder** | `./venv/bin/python3 scripts/build_pdf_from_tex.py` | Converts Markdown to LaTeX (`xltabular` multi-page tables, `C` columns) and compiles `reports/Assignment_Report.pdf` and `reports/LLM_Conversations.pdf`. |

---

## 💻 System Requirements & Prerequisites
- **OS**: Ubuntu Linux (tested on 26.04 LTS / 24.04 LTS)
- **PostgreSQL Engine**: PostgreSQL 16+ (tested on PostgreSQL 18.6)
- **TeX Engine**: `pdflatex` (TeX Live 2025/Debian)
- **Python**: Python 3.10+
