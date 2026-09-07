#!/usr/bin/env bash
set -e

echo "======================================================="
echo " ADBMS Assignment 0 & 1: End-to-End Single-Command Runner"
echo "======================================================="

# 1. Load JOB dataset into PostgreSQL
echo ""
echo "[Step 1/4] Checking & Loading JOB Database into PostgreSQL..."
./scripts/load_job.sh

# 2. Setup Python virtualenv if not present
echo ""
echo "[Step 2/5] Verifying Python Environment & Dependencies..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install psycopg2-binary matplotlib numpy pandas python-docx
fi

# 3. Run Q1 & Q2 master benchmark and generate plots + markdown report
echo ""
echo "[Step 3/5] Running Master Benchmark, Generating Plots & Markdown Report..."
python3 scripts/generate_report.py
python3 scripts/export_llm_chat.py

# 4. Convert Markdown to LaTeX and compile PDF reports
echo ""
echo "[Step 4/5] Converting Markdown to LaTeX and Compiling PDFs..."
python3 scripts/build_pdf_from_tex.py

# 5. Convert Markdown to Word Documents (.docx)
echo ""
echo "[Step 5/5] Converting Markdown to Word Documents (.docx)..."
python3 scripts/convert_md_to_docx.py

echo ""
echo "======================================================="
echo " SUCCESS! All benchmarks, plots, TeX, PDFs & DOCX generated."
echo " Output PDF:  reports/Assignment_Report.pdf"
echo " Output DOCX: reports/Assignment_Report.docx"
echo " Output TeX:  reports/Assignment_Report.tex"
echo " LLM Log PDF:  reports/LLM_Conversations.pdf"
echo " LLM Log DOCX: reports/LLM_Conversations.docx"
echo "======================================================="
