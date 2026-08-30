#!/bin/bash
set -e

DB_NAME="imdbload"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$ROOT_DIR"
mkdir -p data

echo "=== 1. Checking IMDB CSV dataset ==="
if [ ! -f "data/imdb.tgz" ] && [ ! -f "data/title.csv" ]; then
    echo "Downloading imdb.tgz dataset..."
    wget -q --show-progress http://event.cwi.nl/da/job/imdb.tgz -O data/imdb.tgz || wget -q --show-progress https://homepages.cwi.nl/~boncz/job/imdb.tgz -O data/imdb.tgz
fi

if [ ! -f "data/title.csv" ]; then
    echo "Extracting data/imdb.tgz into data/..."
    tar -xzf data/imdb.tgz -C data/
fi

echo "=== 2. Creating Database '$DB_NAME' if not present ==="
if ! psql -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "Creating database $DB_NAME..."
    createdb "$DB_NAME"
else
    echo "Database '$DB_NAME' already exists."
fi

echo "=== 3. Loading Schema, Importing CSVs, Building Indexes & Analyzing ==="
psql -d "$DB_NAME" -f scripts/import_job.sql

echo "=== JOB Database Loaded Successfully! ==="
