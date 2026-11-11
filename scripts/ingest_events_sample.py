
import json
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from fil.ingestion.http_client import fetch_bytes
from fil.ingestion.raw_events import upsert_raw_events


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

BASE_URL = "https://raw.githubusercontent.com/hudl/open-data/master/data"

MATCH_IDS = [3857254, 3857255, 3857256]


def main():
    # Download and validate the files before opening
    # the database transaction.
    downloaded_files = []

    for match_id in MATCH_IDS:
        source_path = f"statsbomb/events/{match_id}.json"
        url = f"{BASE_URL}/events/{match_id}.json"

        raw_bytes = fetch_bytes(url)
        events = json.loads(raw_bytes)

        if not isinstance(events, list):
            raise ValueError(
                f"Expected events array for match {match_id}"
            )

        print(
            f"Match {match_id}: "
            f"{len(raw_bytes):,} bytes "
            f"({len(raw_bytes) / (1024 * 1024):.2f} MiB), "
            f"{len(events):,} events"
        )

        downloaded_files.append(
            (match_id, source_path, raw_bytes)
        )

    # One transaction for the entire batch.
    with psycopg.connect(
        host="127.0.0.1",
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=5,
    ) as conn:

        for match_id, source_path, raw_bytes in downloaded_files:
            status = upsert_raw_events(
                conn,
                match_id,
                source_path,
                raw_bytes,
            )

            print(f"[{status.upper()}] Match {match_id}")

    # The connection context commits on successful exit.
    print("SUCCESS: Events ingestion batch committed!")


if __name__ == "__main__":
    main()
