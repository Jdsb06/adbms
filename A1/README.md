# Join Order Benchmark (JOB) & Histogram Analysis (ADBMS Assignment 0 & 1)

This repository contains the complete implementation, database loading automation, histogram algorithms, and report generation for **Assignment 0** and **Assignment 1 (Histogram)**.

---

## 🚀 Quick Start (Single-Command Execution)

To reproduce the entire benchmark, run the following automated pipeline:

```bash
# 1. Load the database (Extracts CSVs, creates DB, imports tables, builds FK indexes & runs ANALYZE)
./load_job.sh

# 2. Setup Python Virtual Environment and install dependencies
python3 -m venv venv
./venv/bin/pip install psycopg2-binary matplotlib numpy pandas python-docx markdown

# 3. Run complete histogram benchmark, generate all plots, compile reports & export docx
./venv/bin/python3 generate_report.py && ./venv/bin/python3 export_llm_chat.py && ./venv/bin/python3 convert_to_doc.py
```

---

## 📂 Repository Structure

- `load_job.sh`: Shell script to extract IMDB dataset, create PostgreSQL database `imdbload`, load CSV files, build indexes, and execute `ANALYZE`.
- `import_job.sql`: SQL script containing schema creation, `\copy` statements for 21 tables, foreign key indexes, and `ANALYZE`.
- `get_cardinalities.sql`: SQL query script to retrieve primary keys and cardinalities (`count(*)`) across all 21 tables.
- `solution_q1.py`: Python script extracting PostgreSQL equi-depth histograms from `pg_stats`, calculating range selectivities and max selectivity errors.
- `solution_q2.py`: Python script implementing Vectorized Dynamic Programming for V-Optimal Serial Histograms ($B=20$ buckets) across sample sizes 1000, 3000, and 5000, with build-time extrapolation.
- `generate_report.py`: Master runner executing Q1 & Q2 benchmarks and compiling `Assignment_Report.md`.
- `export_llm_chat.py`: Script exporting the complete LLM interaction transcript to `LLM_Conversations.md`.
- `convert_to_doc.py`: Converter generating Word `.docx` documents (`Assignment_Report.docx` and `LLM_Conversations.docx`).
- `Assignment_Report.docx` / `Assignment_Report.md`: Main submission document for Assignment 0 & 1.
- `LLM_Conversations.docx` / `LLM_Conversations.md`: Complete record of interactions with the AI assistant.
- `q1_*.png`, `q2_*.png`: Generated plot visualizations.

---

## 📊 Prerequisites & System Requirements
- **OS**: Ubuntu Linux 22.04 LTS / 24.04 LTS / 26.04 LTS
- **PostgreSQL**: PostgreSQL 16+ (tested on PostgreSQL 18.6)
- **Python**: Python 3.10+ with `psycopg2-binary`, `matplotlib`, `numpy`, `pandas`, `python-docx`

### Database Credentials
The scripts connect to PostgreSQL database `imdbload` on `localhost`. Ensure your system user has permissions or has created the role and database:
```bash
sudo -u postgres createuser -s $USER
sudo -u postgres createdb imdbload -O $USER
```
