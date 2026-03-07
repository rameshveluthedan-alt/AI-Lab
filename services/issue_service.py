"""
services/issue_service.py
-------------------------
Handles the Issue and Return book workflows.
Both operations are performed atomically (single transaction).
"""

import logging
from datetime import date
from typing import Dict, List, Tuple
from db.connection import get_connection
from db import crud

logger = logging.getLogger(__name__)


def issue_book(book_id: int, member_id: int) -> Tuple[bool, str]:
    """
    Issue a book to a member.

    Business rules enforced:
    - Book must exist
    - Member must exist
    - available_copies must be >= 1

    All DB changes (decrement + insert transaction) are atomic.
    """
    book = crud.fetch_book_by_id(book_id)
    if not book:
        return False, f"Book ID {book_id} not found."

    member = crud.fetch_member_by_id(member_id)
    if not member:
        return False, f"Member ID {member_id} not found."

    if book["available_copies"] < 1:
        return False, f"No available copies of '{book['title']}'."

    try:
        with get_connection() as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            # Atomic: decrement copies and record transaction together
            crud.decrement_available_copies(book_id, conn)
            conn.execute(
                """INSERT INTO transactions (book_id, member_id, issue_date, status)
                   VALUES (?, ?, ?, 'Issued')""",
                (book_id, member_id, str(date.today()))
            )
            conn.commit()

        logger.info(
            "Issued book_id=%s to member_id=%s on %s", book_id, member_id, date.today()
        )
        return True, (
            f"✅ '{book['title']}' issued to {member['name']} on {date.today()}."
        )
    except Exception as e:
        logger.error("issue_book error: %s", e)
        return False, f"Database error: {e}"


def return_book(transaction_id: int) -> Tuple[bool, str]:
    """
    Process the return of an issued book.

    Business rules enforced:
    - Transaction must exist and have status 'Issued'

    All DB changes (increment copies + update transaction) are atomic.
    """
    txn = crud.fetch_transaction_by_id(transaction_id)
    if not txn:
        return False, f"Transaction ID {transaction_id} not found."
    if txn["status"] == "Returned":
        return False, "This book has already been returned."

    book = crud.fetch_book_by_id(txn["book_id"])
    return_date = str(date.today())

    try:
        with get_connection() as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            crud.mark_transaction_returned(transaction_id, return_date, conn)
            crud.increment_available_copies(txn["book_id"], conn)
            conn.commit()

        logger.info(
            "Returned transaction_id=%s book_id=%s on %s",
            transaction_id, txn["book_id"], return_date
        )
        book_title = book["title"] if book else f"Book #{txn['book_id']}"
        return True, f"✅ '{book_title}' returned successfully on {return_date}."
    except Exception as e:
        logger.error("return_book error: %s", e)
        return False, f"Database error: {e}"


def get_all_transactions() -> List[Dict]:
    """Return all transactions with joined book/member info."""
    return crud.fetch_all_transactions()


def get_active_issues() -> List[Dict]:
    """Return only currently-issued (unreturned) transactions."""
    all_txns = crud.fetch_all_transactions()
    return [t for t in all_txns if t["status"] == "Issued"]
