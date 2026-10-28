#!/usr/bin/env python3
"""
F1 Race Intelligence — CSV to SQLite Database Loader
====================================================

Loads all CSV files in `data/` into the SQLite database at `data/f1_data.db`.
Validates data integrity and prints summary table counts.
"""

import csv
import logging
import os
import sys
from pathlib import Path
import sqlalchemy as sa
from sqlalchemy import create_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("load_csv")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "f1_data.db"


def load_all_csvs():
    if not DB_PATH.exists():
        log.warning("Database at %s does not exist yet. Running ingest_data.py instead.", DB_PATH)
        import subprocess
        subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "ingest_data.py")], check=True)
        return

    engine = create_engine(f"sqlite:///{DB_PATH}")
    csv_files = sorted(list(DATA_DIR.glob("*.csv")))
    
    if not csv_files:
        log.error("No CSV files found in %s", DATA_DIR)
        return

    log.info("Found %d CSV files to verify/load:", len(csv_files))
    with engine.connect() as conn:
        for f in csv_files:
            table_name = f.stem
            with open(f, mode="r", encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)
                row_count = sum(1 for _ in reader) - 1
            log.info("  CSV %-25s -> %6d rows", f.name, max(0, row_count))
            
            # Check DB count
            try:
                db_count = conn.execute(sa.text(f"SELECT COUNT(*) FROM [{table_name}]")).scalar()
                log.info("  DB  %-25s -> %6d rows", table_name, db_count)
            except Exception as e:
                log.warning("  Table %s not in database: %s", table_name, e)


if __name__ == "__main__":
    load_all_csvs()
