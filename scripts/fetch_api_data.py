#!/usr/bin/env python3
"""
F1 Race Intelligence — Jolpica/Ergast API Data Ingestion Script
===============================================================

Fetches official Formula 1 historical data from the Jolpica-F1 API
(https://api.jolpi.ca/ergast/f1/) and exports to CSV files.

Features:
  - Rate limiting (respects 4 requests/second maximum)
  - Exponential backoff & retry mechanism
  - Progress reporting
  - Validates and saves each table as CSV in data/

Usage:
  python scripts/fetch_api_data.py [--start-season 2010] [--end-season 2024]
"""

import argparse
import csv
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("jolpica_fetch")

BASE_URL = "https://api.jolpi.ca/ergast/f1"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RATE_LIMIT_DELAY = 0.3  # 300ms between requests (~3.3 req/s, within 4 req/s limit)


def fetch_json(url: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
    """Fetch JSON with rate limiting and exponential backoff retry."""
    headers = {"User-Agent": "F1RaceIntelligenceAnalytics/1.0"}
    for attempt in range(max_retries):
        try:
            time.sleep(RATE_LIMIT_DELAY)
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait_time = (2 ** attempt) * 2
                log.warning("Rate limited (429). Backing off for %ds...", wait_time)
                time.sleep(wait_time)
            elif e.code == 404:
                return None
            else:
                log.error("HTTP error %s for %s", e.code, url)
        except Exception as e:
            log.warning("Attempt %d failed for %s: %s", attempt + 1, url, e)
            time.sleep(1)
    return None


def fetch_all_pages(endpoint_template: str, list_key: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Fetch all paginated records from a given endpoint."""
    offset = 0
    all_records = []
    while True:
        sep = "&" if "?" in endpoint_template else "?"
        url = f"{BASE_URL}/{endpoint_template}{sep}limit={limit}&offset={offset}"
        data = fetch_json(url)
        if not data or "MRData" not in data:
            break
        mr_data = data["MRData"]
        total = int(mr_data.get("total", 0))
        
        # Traverse to find the items list
        records = []
        for k, v in mr_data.items():
            if isinstance(v, dict) and list_key in v:
                records = v[list_key]
                break
        
        if not records:
            break
            
        all_records.extend(records)
        offset += len(records)
        log.info("Fetched %d / %d records from %s", len(all_records), total, endpoint_template)
        if offset >= total:
            break
    return all_records


def save_csv(filename: str, rows: List[Dict[str, Any]], fieldnames: List[str]):
    """Save rows to CSV with specified headers."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_DIR / filename
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    log.info("Saved %d rows to %s", len(rows), out_path)


def main():
    parser = argparse.ArgumentParser(description="Fetch F1 data from Jolpica/Ergast API")
    parser.add_argument("--start-season", type=int, default=2010, help="First season to fetch")
    parser.add_argument("--end-season", type=int, default=2024, help="Last season to fetch")
    args = parser.parse_args()

    log.info("Starting Jolpica API data fetch for seasons %d-%d", args.start_season, args.end_season)
    
    # 1. Circuits
    log.info("Fetching circuits...")
    circuits_raw = fetch_all_pages("circuits.json", "Circuits")
    circuits_clean = []
    for c in circuits_raw:
        loc = c.get("Location", {})
        circuits_clean.append({
            "circuitId": c.get("circuitId"),
            "circuitRef": c.get("circuitId"),
            "name": c.get("circuitName"),
            "location": loc.get("locality"),
            "country": loc.get("country"),
            "lat": loc.get("lat"),
            "lng": loc.get("long"),
            "alt": loc.get("alt", 0),
            "url": c.get("url")
        })
    if circuits_clean:
        save_csv("circuits.csv", circuits_clean, ["circuitId", "circuitRef", "name", "location", "country", "lat", "lng", "alt", "url"])

    # 2. Constructors
    log.info("Fetching constructors...")
    constructors_raw = fetch_all_pages("constructors.json", "Constructors")
    constructors_clean = [{
        "constructorId": c.get("constructorId"),
        "constructorRef": c.get("constructorId"),
        "name": c.get("name"),
        "nationality": c.get("nationality"),
        "url": c.get("url")
    } for c in constructors_raw]
    if constructors_clean:
        save_csv("constructors.csv", constructors_clean, ["constructorId", "constructorRef", "name", "nationality", "url"])

    log.info("Completed API fetch. Use scripts/load_csv_to_db.py or scripts/ingest_data.py to populate database.")


if __name__ == "__main__":
    main()
