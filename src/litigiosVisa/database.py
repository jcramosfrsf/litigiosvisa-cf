from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Optional
import os

DATA_DIR = Path(__file__).parent.parent.parent / "data"
DB_PATH = DATA_DIR / "dispute.db"


def init_database():
    """Initialize the mock database with sample dispute data."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS merchants (
            merchant_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            country TEXT,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS disputes (
            dispute_id TEXT PRIMARY KEY,
            merchant_id TEXT,
            cardholder_id TEXT,
            amount REAL,
            currency TEXT,
            dispute_category TEXT,
            status TEXT,
            reason_code TEXT,
            transaction_date TEXT,
            created_at TEXT,
            resolved_at TEXT,
            outcome TEXT,
            FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            merchant_id TEXT,
            cardholder_id TEXT,
            amount REAL,
            currency TEXT,
            transaction_type TEXT,
            status TEXT,
            timestamp TEXT,
            FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id)
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM merchants")
    if cursor.fetchone()[0] == 0:
        insert_mock_data(cursor)

    conn.commit()
    conn.close()


def insert_mock_data(cursor):
    """Insert mock data for demonstration."""

    merchants = [
        ("M001", "Amazon.com", "E-commerce", "US", "2025-01-15"),
        ("M002", "Walmart", "Retail", "US", "2025-02-01"),
        ("M003", "Netflix", "Streaming", "US", "2025-01-20"),
        ("M004", "Spotify", "Streaming", "SE", "2025-02-10"),
        ("M005", "Best Buy", "Electronics", "US", "2025-03-01"),
        ("M006", "Target", "Retail", "US", "2025-02-15"),
        ("M007", "Airbnb", "Travel", "US", "2025-03-05"),
        ("M008", "Uber", "Transportation", "US", "2025-01-25"),
        ("M009", "Starbucks", "Food & Beverage", "US", "2025-02-20"),
        ("M010", "Apple Store", "Electronics", "US", "2025-03-10"),
    ]
    cursor.executemany("INSERT INTO merchants VALUES (?, ?, ?, ?, ?)", merchants)

    import datetime

    base_date = "2026-01-15"

    disputes = [
        (
            "DSP001",
            "M001",
            "CH001",
            149.99,
            "USD",
            "CDT-002",
            "pending",
            "13",
            "2026-01-10",
            "2026-01-12",
            None,
            None,
        ),
        (
            "DSP002",
            "M002",
            "CH002",
            89.50,
            "USD",
            "CDT-001",
            "resolved",
            "30",
            "2026-01-05",
            "2026-01-08",
            "2026-01-20",
            "approved",
        ),
        (
            "DSP003",
            "M003",
            "CH003",
            15.99,
            "USD",
            "CDT-004",
            "pending",
            "30",
            "2026-01-12",
            "2026-01-14",
            None,
            None,
        ),
        (
            "DSP004",
            "M004",
            "CH004",
            9.99,
            "USD",
            "CDT-005",
            "investigating",
            "10",
            "2026-01-08",
            "2026-01-10",
            None,
            None,
        ),
        (
            "DSP005",
            "M005",
            "CH005",
            599.00,
            "USD",
            "CDT-003",
            "resolved",
            "45",
            "2025-12-28",
            "2026-01-02",
            "2026-01-18",
            "rejected",
        ),
        (
            "DSP006",
            "M006",
            "CH006",
            45.00,
            "USD",
            "CDT-009",
            "pending",
            "72",
            "2026-01-11",
            "2026-01-13",
            None,
            None,
        ),
        (
            "DSP007",
            "M007",
            "CH007",
            350.00,
            "USD",
            "CDT-001",
            "resolved",
            "30",
            "2026-01-03",
            "2026-01-06",
            "2026-01-22",
            "approved",
        ),
        (
            "DSP008",
            "M008",
            "CH008",
            24.50,
            "USD",
            "CDT-002",
            "pending",
            "13",
            "2026-01-13",
            "2026-01-15",
            None,
            None,
        ),
        (
            "DSP009",
            "M009",
            "CH009",
            12.75,
            "USD",
            "CDT-002",
            "resolved",
            "13",
            "2026-01-09",
            "2026-01-11",
            "2026-01-19",
            "approved",
        ),
        (
            "DSP010",
            "M010",
            "CH010",
            1299.00,
            "USD",
            "CDT-008",
            "investigating",
            "49",
            "2026-01-07",
            "2026-01-09",
            None,
            None,
        ),
        (
            "DSP011",
            "M001",
            "CH011",
            79.99,
            "USD",
            "CDT-003",
            "pending",
            "45",
            "2026-01-14",
            "2026-01-16",
            None,
            None,
        ),
        (
            "DSP012",
            "M003",
            "CH012",
            15.99,
            "USD",
            "CDT-006",
            "resolved",
            "72",
            "2026-01-02",
            "2026-01-04",
            "2026-01-15",
            "approved",
        ),
    ]
    cursor.executemany(
        "INSERT INTO disputes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", disputes
    )

    transactions = [
        (
            "TXN001",
            "M001",
            "CH001",
            149.99,
            "USD",
            "purchase",
            "completed",
            "2026-01-10 14:30:00",
        ),
        (
            "TXN002",
            "M001",
            "CH001",
            149.99,
            "USD",
            "purchase",
            "completed",
            "2026-01-10 14:31:00",
        ),
        (
            "TXN003",
            "M002",
            "CH002",
            89.50,
            "USD",
            "purchase",
            "completed",
            "2026-01-05 10:15:00",
        ),
        (
            "TXN004",
            "M003",
            "CH003",
            15.99,
            "USD",
            "recurring",
            "completed",
            "2026-01-12 08:00:00",
        ),
        (
            "TXN005",
            "M004",
            "CH004",
            9.99,
            "USD",
            "purchase",
            "completed",
            "2026-01-08 16:45:00",
        ),
        (
            "TXN006",
            "M005",
            "CH005",
            599.00,
            "USD",
            "purchase",
            "completed",
            "2025-12-28 19:20:00",
        ),
        (
            "TXN007",
            "M006",
            "CH006",
            45.00,
            "USD",
            "purchase",
            "completed",
            "2026-01-11 12:00:00",
        ),
        (
            "TXN008",
            "M007",
            "CH007",
            350.00,
            "USD",
            "purchase",
            "completed",
            "2026-01-03 15:30:00",
        ),
        (
            "TXN009",
            "M008",
            "CH008",
            24.50,
            "USD",
            "purchase",
            "completed",
            "2026-01-13 09:10:00",
        ),
        (
            "TXN010",
            "M009",
            "CH009",
            12.75,
            "USD",
            "purchase",
            "completed",
            "2026-01-09 11:25:00",
        ),
    ]
    cursor.executemany(
        "INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?)", transactions
    )


def execute_query(sql: str) -> list[dict]:
    """Execute a read-only SQL query and return results."""
    if not DB_PATH.exists():
        init_database()

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute(sql)
        results = [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        return [{"error": str(e)}]
    finally:
        conn.close()

    return results


def get_table_schema(table_name: str) -> dict:
    """Get schema information for a table."""
    if not DB_PATH.exists():
        init_database()

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [
        {"cid": row[0], "name": row[1], "type": row[2]} for row in cursor.fetchall()
    ]

    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]

    conn.close()

    return {"table": table_name, "columns": columns, "row_count": count}
