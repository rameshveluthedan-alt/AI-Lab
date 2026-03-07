"""
db/connection.py
----------------
Manages the SQLite database connection.
Foreign key enforcement is enabled on every connection.
"""

import sqlite3
import logging
import os

# Resolve the DB path relative to this file's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "library.db")

logger = logging.getLogger(__name__)


def get_connection() -> sqlite3.Connection:
    """
    Return a new SQLite connection with:
    - Row factory set to sqlite3.Row (dict-like access)
    - Foreign key enforcement enabled
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        logger.error("Failed to connect to database: %s", e)
        raise
