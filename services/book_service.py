"""
services/book_service.py
------------------------
Business-logic layer for Book operations.
Validates inputs and delegates persistence to db/crud.py.
"""

import logging
from typing import Dict, List, Optional, Tuple
from db import crud

logger = logging.getLogger(__name__)

VALID_CATEGORIES = [
    "Fiction", "Non-Fiction", "Science", "Technology", "History",
    "Biography", "Children", "Self-Help", "Mystery", "Romance", "Other"
]


def add_book(
    title: str,
    author: str,
    category: str,
    total_copies: int,
    isbn: Optional[str] = None,
    published_year: Optional[int] = None,
) -> Tuple[bool, str]:
    """
    Validate and add a new book to the library.

    Returns:
        (success: bool, message: str)
    """
    # --- Validation ---
    if not title.strip():
        return False, "Title cannot be empty."
    if not author.strip():
        return False, "Author cannot be empty."
    if total_copies < 1:
        return False, "Total copies must be at least 1."
    if published_year and (published_year < 1000 or published_year > 2100):
        return False, "Published year seems invalid."

    data = {
        "title": title.strip(),
        "author": author.strip(),
        "category": category,
        "isbn": isbn.strip() if isbn else None,
        "published_year": published_year,
        "total_copies": total_copies,
        "available_copies": total_copies,  # all copies available on add
    }
    try:
        book_id = crud.insert_book(data)
        logger.info("Added book id=%s title='%s'", book_id, title)
        return True, f"Book '{title}' added successfully (ID: {book_id})."
    except Exception as e:
        logger.error("add_book error: %s", e)
        return False, f"Database error: {e}"


def update_book(
    book_id: int,
    title: str,
    author: str,
    category: str,
    total_copies: int,
    available_copies: int,
    isbn: Optional[str] = None,
    published_year: Optional[int] = None,
) -> Tuple[bool, str]:
    """Update an existing book record."""
    if not title.strip() or not author.strip():
        return False, "Title and Author are required."
    if total_copies < 0 or available_copies < 0:
        return False, "Copies cannot be negative."
    if available_copies > total_copies:
        return False, "Available copies cannot exceed total copies."

    data = {
        "title": title.strip(),
        "author": author.strip(),
        "category": category,
        "isbn": isbn,
        "published_year": published_year,
        "total_copies": total_copies,
        "available_copies": available_copies,
    }
    try:
        updated = crud.update_book(book_id, data)
        if updated:
            return True, f"Book ID {book_id} updated successfully."
        return False, "Book not found."
    except Exception as e:
        logger.error("update_book error: %s", e)
        return False, f"Database error: {e}"


def delete_book(book_id: int) -> Tuple[bool, str]:
    """
    Delete a book only if it has no active (unreturned) transactions.
    """
    active = crud.fetch_active_transactions_for_book(book_id)
    if active:
        return False, "Cannot delete: book has active (unreturned) issues."
    try:
        deleted = crud.delete_book(book_id)
        if deleted:
            return True, f"Book ID {book_id} deleted."
        return False, "Book not found."
    except Exception as e:
        logger.error("delete_book error: %s", e)
        return False, f"Database error: {e}"


def get_all_books() -> List[Dict]:
    """Return all books."""
    return crud.fetch_all_books()


def search_books(query: str) -> List[Dict]:
    """Search books by title, author, or category."""
    if not query.strip():
        return crud.fetch_all_books()
    return crud.search_books(query.strip())


def get_book_by_id(book_id: int) -> Optional[Dict]:
    """Return a single book or None."""
    return crud.fetch_book_by_id(book_id)
