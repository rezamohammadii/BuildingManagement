"""
Database layer for the Building Management web app.
Handles SQLite connection setup and schema creation.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "building.db")


def get_connection():
    """Return a new SQLite connection with row factory and FK support enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database():
    """Create all tables if they do not already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            total_units INTEGER NOT NULL,
            charge_amount REAL NOT NULL,
            is_configured INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS units (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unit_number INTEGER NOT NULL UNIQUE,
            people_count INTEGER NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unit_number INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_date TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS water_bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_month TEXT NOT NULL,
            total_amount REAL NOT NULL,
            total_people INTEGER NOT NULL,
            cost_per_person REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS water_bill_shares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            water_bill_id INTEGER NOT NULL,
            unit_number INTEGER NOT NULL,
            people_count INTEGER NOT NULL,
            share_amount REAL NOT NULL,
            FOREIGN KEY (water_bill_id) REFERENCES water_bills (id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            expense_date TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def is_configured() -> bool:
    conn = get_connection()
    row = conn.execute("SELECT is_configured FROM settings WHERE id = 1").fetchone()
    conn.close()
    return bool(row and row["is_configured"] == 1)
