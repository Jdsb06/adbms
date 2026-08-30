# Join Order Benchmark (JOB) & Histogram Analysis (ADBMS Assignment 0 & 1)

This repository contains the complete implementation, database loading automation, histogram algorithms, visualizations, and report generation for **Assignment 0** and **Assignment 1 (Histogram)**.

---

## 📁 Categorized Directory Structure

```text
A1/
├── scripts/                    # Automation scripts & SQL queries
│   ├── load_job.sh             # Main automated database loader script
│   ├── import_job.sql          # Schema, CSV import & index creation SQL script
│   ├── get_cardinalities.sql   # SQL query for table row counts & primary keys
│   ├── solution_q1.py          # Q1: PostgreSQL equi-depth histogram analysis
│   ├── solution_q2.py          # Q2: Dynamic Programming V-Optimal Serial Histogram
│   ├── generate_report.py      # Master benchmark runner & report compiler
│   ├── export_llm_chat.py      # Transcribes conversation log into markdown
│   └── convert_to_doc.py       # Converts markdown reports to Word .docx
├── reports/                    # Final submission documents & PDF reference
│   ├── Assignment_Report.docx  # Final Assignment 0 & 1 Report (.docx)
│   ├── Assignment_Report.md    # Final Assignment 0 & 1 Report (.md)
│   ├── LLM_Conversations.docx  # AI assistant interaction log (.docx)
│   ├── LLM_Conversations.md    # AI assistant interaction log (.md)
│   └── Assignment 1 Histogram.pdf # Original assignment prompt PDF
├── plots/                      # Generated histogram & experiment plots (.png)
│   ├── q1_histogram_id.png
│   ├── q1_histogram_title.png
│   ├── q2_histogram_id_3000.png
│   ├── q2_histogram_title_3000.png
│   ├── q2_sample_size_vs_time.png
│   └── q2_sample_size_vs_error.png
├── data/                       # IMDB dataset archives & extracted CSV files (gitignored)
│   ├── imdb.tgz
│   └── *.csv
├── job/                        # Join Order Benchmark (JOB) queries & schema definitions
└── README.md                   # Repository documentation
```

---

## 🚀 Quick Start (Single-Command Execution)

To reproduce the entire benchmark and re-generate all reports/plots:

```bash
# 1. Load database into PostgreSQL (extracts CSVs, creates DB, imports tables, builds indexes & runs ANALYZE)
./scripts/load_job.sh

# 2. Setup Python environment and install dependencies
python3 -m venv venv
./venv/bin/pip install psycopg2-binary matplotlib numpy pandas python-docx markdown

# 3. Run complete benchmark, re-generate plots & compile Word (.docx) reports
./venv/bin/python3 scripts/generate_report.py && ./venv/bin/python3 scripts/export_llm_chat.py && ./venv/bin/python3 scripts/convert_to_doc.py
```

---

## 📊 Database Credentials & Prerequisites
- **OS**: Ubuntu Linux
- **PostgreSQL Engine**: PostgreSQL 16+ (tested on PostgreSQL 18.6)
- Standard local PostgreSQL user socket access:
```bash
sudo -u postgres createuser -s $USER
sudo -u postgres createdb imdbload -O $USER
```
