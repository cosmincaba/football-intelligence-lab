import json
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from fil.ingestion.http_client import fetch_bytes
from fil.ingestion.raw_matches import upsert_raw_match

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

BASE_URL = (
    "https://raw.githubusercontent.com/"
    "hudl/open-data/master/data"
)

def main():
    # Download competition catalog
    competition_bytes = fetch_bytes(
        f"{BASE_URL}/competitions.json"
    )
    competitions = json.loads(competition_bytes)

    # Find the men's 2022 World Cup
    world_cup = next(
        competition
        for competition in competitions
        if competition["competition_name"] == "FIFA World Cup"
        and competition["season_name"] == "2022"
        and competition["competition_gender"] == "male"
    )

    competition_id = world_cup["competition_id"]
    season_id = world_cup["season_id"]

    print(
        f"Found World Cup 2022:"
        f"competition = {competition_id}, season = {season_id}"
    )

    # Download the match files

    matches_url = (
        f"{BASE_URL}/matches/"
        f"{competition_id}/{season_id}.json"
    )

    matches_bytes = fetch_bytes(matches_url)
    matches = json.loads(matches_bytes)

    sample_matches = sorted(
        matches,
        key=lambda match: match["match_id"],
    )[:3]

    print(f"Selected {len(sample_matches)} matches")

    # Connect to PostgreSQL
    with psycopg.connect(
        host="127.0.0.1",
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=5,
    ) as conn:


        for match in sample_matches:
            match_id = match["match_id"]

            source_path = (
                f"statsbomb/matches/"
                f"{competition_id}/{season_id}/"
                f"{match_id}.json"
            )

            raw_bytes = json.dumps(
                match,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")

            result = upsert_raw_match(
                conn,
                source_path,
                raw_bytes,
            )

            print(f"[{result.upper()}] Match {match_id}")

        # Exiting the connection context successfully
        # commits the entire transaction.

    print("SUCCESS: Sample ingestion committed!")


if __name__ == "__main__":
    main()