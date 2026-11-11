
import json
import os
import uuid

import psycopg
import pytest
from dotenv import load_dotenv

from fil.ingestion.raw_events import upsert_raw_events

import time

load_dotenv()


@pytest.fixture
def db_conn():
    """Open a connection and roll back all test changes."""
    conn = psycopg.connect(
        host="127.0.0.1",
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=5,
    )

    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()


@pytest.fixture
def test_source():
    """Create a unique match ID and source path for each test."""
    match_id = uuid.uuid4().int % 1_000_000_000

    return {
        "match_id": match_id,
        "source_file_path": f"pytest/events/{uuid.uuid4()}.json",
    }


def make_events(event_type="Pass"):
    """Create a small, valid events JSON array."""
    return json.dumps([
        {
            "id": str(uuid.uuid4()),
            "type": {"name": event_type},
        }
    ]).encode("utf-8")


def get_event_row(conn, source_file_path):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, content_hash, ingested_at, updated_at
            FROM raw.events_json
            WHERE source_file_path = %s
            """,
            (source_file_path,),
        )
        return cur.fetchone()


def test_insert_then_skip(db_conn, test_source):
    """Identical content must not update the existing row."""
    raw_bytes = make_events()

    first = upsert_raw_events(
        db_conn, test_source["match_id"],
        test_source["source_file_path"], raw_bytes
    )
    row_before = get_event_row(
        db_conn, test_source["source_file_path"]
    )

    time.sleep(0.01)

    second = upsert_raw_events(
        db_conn, test_source["match_id"],
        test_source["source_file_path"], raw_bytes
    )
    row_after = get_event_row(
        db_conn, test_source["source_file_path"]
    )

    assert first == "inserted"
    assert second == "skipped"
    assert row_before == row_after


def test_changed_bytes_updates(db_conn, test_source):
    """Changed content must update the row and timestamp."""
    first_bytes = make_events("Pass")
    changed_bytes = make_events("Shot")

    first = upsert_raw_events(
        db_conn, test_source["match_id"],
        test_source["source_file_path"], first_bytes
    )
    row_before = get_event_row(
        db_conn, test_source["source_file_path"]
    )

    second = upsert_raw_events(
        db_conn, test_source["match_id"],
        test_source["source_file_path"], changed_bytes
    )
    row_after = get_event_row(
        db_conn, test_source["source_file_path"]
    )

    assert first == "inserted"
    assert second == "updated"
    assert row_after[1] != row_before[1]
    assert row_after[3] > row_before[3]


def test_rollback_leaves_no_row(db_conn, test_source):
    """An uncommitted insertion must disappear after rollback."""
    status = upsert_raw_events(
        db_conn,
        test_source["match_id"],
        test_source["source_file_path"],
        make_events(),
    )

    assert status == "inserted"
    assert get_event_row(
        db_conn, test_source["source_file_path"]
    ) is not None

    db_conn.rollback()

    assert get_event_row(
        db_conn, test_source["source_file_path"]
    ) is None


def test_non_array_payload_raises(db_conn, test_source):
    """A JSON object is not a valid events array."""
    invalid_bytes = json.dumps({
        "id": "not-an-events-array"
    }).encode("utf-8")

    with pytest.raises(ValueError, match="JSON array"):
        upsert_raw_events(
            db_conn,
            test_source["match_id"],
            test_source["source_file_path"],
            invalid_bytes,
        )

    assert get_event_row(
        db_conn, test_source["source_file_path"]
    ) is None

def test_duplicate_match_id_different_path_raises(db_conn, test_source):
    """One match ID cannot belong to two different source paths."""
    match_id = test_source["match_id"]
    original_path = test_source["source_file_path"]
    duplicate_path = f"pytest/events/{uuid.uuid4()}.json"

    first = upsert_raw_events(
        db_conn,
        match_id,
        original_path,
        make_events(),
    )

    assert first == "inserted"

    with pytest.raises(psycopg.errors.UniqueViolation):
        upsert_raw_events(
            db_conn,
            match_id,
            duplicate_path,
            make_events(),
        )