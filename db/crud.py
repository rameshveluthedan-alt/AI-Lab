"""
db/crud.py
----------
Low-level CRUD helpers that execute parameterized SQL against the database.
All functions accept/return plain Python types (dicts, lists, primitives).
Higher-level business logic lives in the services/ layer.
"""

import logging
from typing import Any, Dict, List, Optional
from db.connection import get_connection

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
# BOOKS
# ══════════════════════════════════════════════════════════════════

def insert_book(data: Dict[str, Any]) -> int:
    """Insert a new book record. Returns the new book_id."""
    sql = """
        INSERT INTO books (title, author, category, isbn, published_year,
                           total_copies, available_copies)
        VALUES (:title, :author, :category, :isbn, :published_year,
                :total_copies, :available_copies)
    """
    with get_connection() as conn:
        cursor = conn.execute(sql, data)
        conn.commit()
        return cursor.lastrowid


def fetch_all_books() -> List[Dict]:
    """Return all book records as a list of dicts."""
    sql = "SELECT * FROM books ORDER BY title"
    with get_connection() as conn:
        rows = conn.execute(sql).fetchall()
    return [dict(r) for r in rows]


def fetch_book_by_id(book_id: int) -> Optional[Dict]:
    """Return a single book dict or None."""
    sql = "SELECT * FROM books WHERE book_id = ?"
    with get_connection() as conn:
        row = conn.execute(sql, (book_id,)).fetchone()
    return dict(row) if row else None


def search_books(query: str) -> List[Dict]:
    """Full-text search across title, author, and category (case-insensitive)."""
    like = f"%{query}%"
    sql = """
        SELECT * FROM books
        WHERE title LIKE ? OR author LIKE ? OR category LIKE ?
        ORDER BY title
    """
    with get_connection() as conn:
        rows = conn.execute(sql, (like, like, like)).fetchall()
    return [dict(r) for r in rows]


def update_book(book_id: int, data: Dict[str, Any]) -> bool:
    """Update book fields. Returns True on success."""
    sql = """
        UPDATE books
        SET title=:title, author=:author, category=:category,
            isbn=:isbn, published_year=:published_year,
            total_copies=:total_copies, available_copies=:available_copies
        WHERE book_id=:book_id
    """
    data["book_id"] = book_id
    with get_connection() as conn:
        cursor = conn.execute(sql, data)
        conn.commit()
    return cursor.rowcount > 0


def delete_book(book_id: int) -> bool:
    """Delete a book record. Returns True on success."""
    sql = "DELETE FROM books WHERE book_id = ?"
    with get_connection() as conn:
        cursor = conn.execute(sql, (book_id,))
        conn.commit()
    return cursor.rowcount > 0


def decrement_available_copies(book_id: int, conn) -> None:
    """Decrement available_copies by 1 within an existing connection."""
    conn.execute(
        "UPDATE books SET available_copies = available_copies - 1 WHERE book_id = ?",
        (book_id,)
    )


def increment_available_copies(book_id: int, conn) -> None:
    """Increment available_copies by 1 within an existing connection."""
    conn.execute(
        "UPDATE books SET available_copies = available_copies + 1 WHERE book_id = ?",
        (book_id,)
    )


# ══════════════════════════════════════════════════════════════════
# MEMBERS
# ══════════════════════════════════════════════════════════════════

def insert_member(data: Dict[str, Any]) -> int:
    """Insert a new member. Returns new member_id."""
    sql = """
        INSERT INTO members (name, gender, age, mobile_number, email, join_date)
        VALUES (:name, :gender, :age, :mobile_number, :email, :join_date)
    """
    with get_connection() as conn:
        cursor = conn.execute(sql, data)
        conn.commit()
        return cursor.lastrowid


def fetch_all_members() -> List[Dict]:
    """Return all member records."""
    sql = "SELECT * FROM members ORDER BY name"
    with get_connection() as conn:
        rows = conn.execute(sql).fetchall()
    return [dict(r) for r in rows]


def fetch_member_by_id(member_id: int) -> Optional[Dict]:
    """Return a single member dict or None."""
    sql = "SELECT * FROM members WHERE member_id = ?"
    with get_connection() as conn:
        row = conn.execute(sql, (member_id,)).fetchone()
    return dict(row) if row else None


def search_members(query: str) -> List[Dict]:
    """Search members by name or email."""
    like = f"%{query}%"
    sql = """
        SELECT * FROM members
        WHERE name LIKE ? OR email LIKE ?
        ORDER BY name
    """
    with get_connection() as conn:
        rows = conn.execute(sql, (like, like)).fetchall()
    return [dict(r) for r in rows]


def update_member(member_id: int, data: Dict[str, Any]) -> bool:
    """Update member fields. Returns True on success."""
    sql = """
        UPDATE members
        SET name=:name, gender=:gender, age=:age,
            mobile_number=:mobile_number, email=:email
        WHERE member_id=:member_id
    """
    data["member_id"] = member_id
    with get_connection() as conn:
        cursor = conn.execute(sql, data)
        conn.commit()
    return cursor.rowcount > 0


def delete_member(member_id: int) -> bool:
    """Delete a member record. Returns True on success."""
    sql = "DELETE FROM members WHERE member_id = ?"
    with get_connection() as conn:
        cursor = conn.execute(sql, (member_id,))
        conn.commit()
    return cursor.rowcount > 0


# ══════════════════════════════════════════════════════════════════
# TRANSACTIONS
# ══════════════════════════════════════════════════════════════════

def insert_transaction(data: Dict[str, Any]) -> int:
    """Insert a new transaction record. Returns new transaction_id."""
    sql = """
        INSERT INTO transactions (book_id, member_id, issue_date, status)
        VALUES (:book_id, :member_id, :issue_date, :status)
    """
    with get_connection() as conn:
        cursor = conn.execute(sql, data)
        conn.commit()
        return cursor.lastrowid


def fetch_all_transactions() -> List[Dict]:
    """Return all transactions with book title and member name joined."""
    sql = """
        SELECT t.*, b.title AS book_title, m.name AS member_name
        FROM transactions t
        JOIN books b ON t.book_id = b.book_id
        JOIN members m ON t.member_id = m.member_id
        ORDER BY t.issue_date DESC
    """
    with get_connection() as conn:
        rows = conn.execute(sql).fetchall()
    return [dict(r) for r in rows]


def fetch_active_transactions_for_member(member_id: int) -> List[Dict]:
    """Return currently-issued (unreturned) transactions for a member."""
    sql = """
        SELECT * FROM transactions
        WHERE member_id = ? AND status = 'Issued'
    """
    with get_connection() as conn:
        rows = conn.execute(sql, (member_id,)).fetchall()
    return [dict(r) for r in rows]


def fetch_active_transactions_for_book(book_id: int) -> List[Dict]:
    """Return currently-issued (unreturned) transactions for a book."""
    sql = """
        SELECT * FROM transactions
        WHERE book_id = ? AND status = 'Issued'
    """
    with get_connection() as conn:
        rows = conn.execute(sql, (book_id,)).fetchall()
    return [dict(r) for r in rows]


def fetch_transaction_by_id(transaction_id: int) -> Optional[Dict]:
    """Return a single transaction dict or None."""
    sql = "SELECT * FROM transactions WHERE transaction_id = ?"
    with get_connection() as conn:
        row = conn.execute(sql, (transaction_id,)).fetchone()
    return dict(row) if row else None


def mark_transaction_returned(transaction_id: int, return_date: str, conn) -> None:
    """Update a transaction to Returned status within an existing connection."""
    conn.execute(
        """UPDATE transactions
           SET status='Returned', return_date=?
           WHERE transaction_id=?""",
        (return_date, transaction_id)
    )
