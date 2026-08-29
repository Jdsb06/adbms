#!/bin/bash
set -e

DB_NAME="imdbload"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

echo "=== 1. Checking IMDB CSV dataset ==="
if [ ! -f "imdb.tgz" ] && [ ! -f "title.csv" ]; then
    echo "Downloading imdb.tgz dataset..."
    wget -q --show-progress http://event.cwi.nl/da/job/imdb.tgz -O imdb.tgz || wget -q --show-progress https://homepages.cwi.nl/~boncz/job/imdb.tgz -O imdb.tgz
fi

if [ ! -f "title.csv" ]; then
    echo "Extracting imdb.tgz..."
    tar -xzf imdb.tgz
fi

echo "=== 2. Creating Database '$DB_NAME' if not present ==="
if ! psql -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "Creating database $DB_NAME..."
    createdb "$DB_NAME"
else
    echo "Database '$DB_NAME' already exists."
fi

echo "=== 3. Loading Schema, Importing CSVs, Building Indexes & Analyzing ==="
psql -d "$DB_NAME" -f import_job.sql

echo "=== JOB Database Loaded Successfully! ==="
