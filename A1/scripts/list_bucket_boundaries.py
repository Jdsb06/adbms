import psycopg2
import csv
import json

def get_db_bounds():
    conn = psycopg2.connect(dbname='imdbload')
    cur = conn.cursor()
    bounds_dict = {}
    for col in ['id', 'title']:
        cur.execute(f'''
            SELECT array_to_json(histogram_bounds)
            FROM pg_stats
            WHERE tablename = 'title' AND attname = '{col}';
        ''')
        res = cur.fetchone()[0]
        bounds_dict[col] = res if res else []
    conn.close()
    return bounds_dict

def get_csv_bounds():
    csv_dict = {}
    with open('/tmp/stats.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            col = row['attname']
            raw_b = row['histogram_bounds']
            csv_dict[col] = raw_b
    return csv_dict

if __name__ == '__main__':
    db_bounds = get_db_bounds()
    print("=== Database Bucket Boundaries (Default target=100, 101 boundary values / 100 buckets) ===")
    
    print("\n--- title.id Bucket Boundaries (101 values) ---")
    id_b = db_bounds['id']
    for idx, val in enumerate(id_b):
        print(f"B{idx:03d}: {val}")

    print("\n--- title.title Bucket Boundaries (101 values) ---")
    title_b = db_bounds['title']
    for idx, val in enumerate(title_b):
        print(f"B{idx:03d}: {val}")
