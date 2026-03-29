"""
db/schema.py
------------
Creates the database schema (tables) if they do not already exist.
Run once on application startup via initialize_db().
"""

import logging
from db.connection import get_connection

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# DDL Statements
# ------------------------------------------------------------------

CREATE_BOOKS_TABLE = """
CREATE TABLE IF NOT EXISTS books (
    book_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT    NOT NULL,
    author          TEXT    NOT NULL,
    category        TEXT    NOT NULL,
    isbn            TEXT,
    published_year  INTEGER,
    total_copies    INTEGER NOT NULL CHECK(total_copies >= 0),
    available_copies INTEGER NOT NULL CHECK(available_copies >= 0)
);
"""

CREATE_MEMBERS_TABLE = """
CREATE TABLE IF NOT EXISTS members (
    member_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    gender        TEXT    NOT NULL CHECK(gender IN ('Male', 'Female', 'Other')),
    age           INTEGER NOT NULL CHECK(age > 0),
    mobile_number TEXT,
    email         TEXT    NOT NULL UNIQUE,
    join_date     TEXT    NOT NULL DEFAULT (DATE('now'))
);
"""

CREATE_TRANSACTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id        INTEGER NOT NULL REFERENCES books(book_id),
    member_id      INTEGER NOT NULL REFERENCES members(member_id),
    issue_date     TEXT    NOT NULL DEFAULT (DATE('now')),
    return_date    TEXT,
    status         TEXT    NOT NULL DEFAULT 'Issued'
                           CHECK(status IN ('Issued', 'Returned'))
);
"""


def initialize_db() -> None:
    """Create all tables if they don't exist. Safe to call on every startup."""
    try:
        with get_connection() as conn:
            conn.execute(CREATE_BOOKS_TABLE)
            conn.execute(CREATE_MEMBERS_TABLE)
            conn.execute(CREATE_TRANSACTIONS_TABLE)
            conn.commit()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error("Error initializing database: %s", e)
        raise
