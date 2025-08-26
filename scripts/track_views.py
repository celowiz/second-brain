"""
GitHub Repository Traffic Tracker

This script fetches and stores repository traffic data from GitHub's API.
It maintains both a SQLite database and an Excel file with historical view counts.

The data is stored in the data/ directory:
- data/traffic.db: SQLite database with historical traffic data
- data/traffic.xlsx: Excel export of the traffic data
"""

import os
import sys
from pathlib import Path
import sqlite3
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# Configuration
REPO = "celowiz/second-brain"
TOKEN = os.getenv("GITHUB_TOKEN")
if not TOKEN:
    print("Error: GITHUB_TOKEN environment variable not set", file=sys.stderr)
    sys.exit(1)

# Ensure data directory exists
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "traffic.db"
EXCEL_PATH = DATA_DIR / "traffic.xlsx"

def setup_database(conn):
    """Create the database schema if it doesn't exist."""
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS views (
        timestamp TEXT PRIMARY KEY,
        count INTEGER,
        uniques INTEGER
    )
    """)
    conn.commit()

def fetch_traffic_data():
    """Fetch traffic data from GitHub API."""
    url = f"https://api.github.com/repos/{REPO}/traffic/views"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"GitHub API Error: {response.status_code}, {response.text}")
    
    return response.json()

def update_database(conn, data):
    """Update the database with new traffic data."""
    cur = conn.cursor()
    for entry in data["views"]:
        timestamp = entry["timestamp"][:10]  # YYYY-MM-DD
        count = entry["count"]
        uniques = entry["uniques"]

        cur.execute("""
        INSERT INTO views (timestamp, count, uniques)
        VALUES (?, ?, ?)
        ON CONFLICT(timestamp) DO UPDATE SET
            count = excluded.count,
            uniques = excluded.uniques
        """, (timestamp, count, uniques))
    
    conn.commit()

def export_to_excel(conn):
    """Export the database to an Excel file."""
    query = "SELECT * FROM views ORDER BY timestamp"
    df = pd.read_sql(query, conn)
    df.to_excel(EXCEL_PATH, index=False)

def main():
    """Main execution function."""
    try:
        # Fetch data
        data = fetch_traffic_data()
        
        # Update database
        with sqlite3.connect(DB_PATH) as conn:
            setup_database(conn)
            update_database(conn, data)
            print("✅ Traffic data saved/updated in SQLite database.")
            
            # Export to Excel
            export_to_excel(conn)
            print("📊 History exported to Excel file.")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()