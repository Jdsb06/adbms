# Join Order Benchmark (JOB) & Histogram Analysis (ADBMS Assignment 0 & 1)

This repository contains the complete implementation, database loading automation, histogram algorithms, visualizations, LaTeX source code, and PDF report generation for **Assignment 0** and **Assignment 1 (Histogram)**.

---

## 📁 Categorized Directory Structure

```text
A1/
├── scripts/                        # Executable automation scripts & SQL queries
│   ├── load_job.sh                 # Database loader script
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
│   ├── LLM_Conversations.md       # AI assistant interaction log (.md)
│   └── Assignment 1 Histogram.pdf  # Assignment prompt PDF
│
├── plots/                          # Generated visualization charts (.png)
│   ├── q1_histogram_id.png
│   ├── q1_histogram_title.png
│   ├── q2_histogram_id_3000.png
│   ├── q2_histogram_title_3000.png
│   ├── q2_sample_size_vs_time.png
│   └── q2_sample_size_vs_error.png
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

## 🚀 Quick Start (Single-Command Execution)

To reproduce the entire benchmark and re-generate all LaTeX source files and PDFs:

```bash
# 1. Load database into PostgreSQL (extracts CSVs, creates DB, imports tables, builds indexes & runs ANALYZE)
./scripts/load_job.sh

# 2. Setup Python environment and install dependencies
python3 -m venv venv
./venv/bin/pip install psycopg2-binary matplotlib numpy pandas

# 3. Run complete benchmark, re-generate plots, convert to LaTeX (.tex) & compile PDFs
./venv/bin/python3 scripts/generate_report.py && ./venv/bin/python3 scripts/export_llm_chat.py && ./venv/bin/python3 scripts/build_pdf_from_tex.py
```

---

## 📊 Database Credentials & Prerequisites
- **OS**: Ubuntu Linux
- **PostgreSQL Engine**: PostgreSQL 16+ (tested on PostgreSQL 18.6)
- **LaTeX Engine**: `pdflatex` (TeX Live 2025)
- Standard local PostgreSQL user socket access:
```bash
sudo -u postgres createuser -s $USER
sudo -u postgres createdb imdbload -O $USER
```
