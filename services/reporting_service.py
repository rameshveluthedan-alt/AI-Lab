"""
services/reporting_service.py
------------------------------
Generates analytical reports using Pandas.
Designed to be AI/ML-ready — each function returns a clean DataFrame
that can be fed directly into ML pipelines or visualisation layers.
"""

import logging
from datetime import date, timedelta
from typing import Optional
import pandas as pd
from db import crud

logger = logging.getLogger(__name__)


def _transactions_df() -> pd.DataFrame:
    """Load all transactions into a DataFrame (internal helper)."""
    rows = crud.fetch_all_transactions()
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    # Parse date columns
    df["issue_date"] = pd.to_datetime(df["issue_date"], errors="coerce")
    df["return_date"] = pd.to_datetime(df["return_date"], errors="coerce")
    return df


def report_all_issued_books() -> pd.DataFrame:
    """
    All books currently issued (status = 'Issued').
    Columns: transaction_id, book_title, member_name, issue_date, status
    """
    df = _transactions_df()
    if df.empty:
        return df
    issued = df[df["status"] == "Issued"].copy()
    cols = ["transaction_id", "book_title", "member_name", "issue_date", "status"]
    return issued[cols].reset_index(drop=True)


def report_overdue_books(overdue_days: int = 14) -> pd.DataFrame:
    """
    Books issued more than `overdue_days` ago and not yet returned.
    Adds a 'days_overdue' column for easy prioritisation.
    """
    df = _transactions_df()
    if df.empty:
        return df
    today = pd.Timestamp(date.today())
    cutoff = today - pd.Timedelta(days=overdue_days)
    overdue = df[
        (df["status"] == "Issued") & (df["issue_date"] < cutoff)
    ].copy()
    overdue["days_overdue"] = (today - overdue["issue_date"]).dt.days
    cols = ["transaction_id", "book_title", "member_name", "issue_date", "days_overdue"]
    return overdue[cols].sort_values("days_overdue", ascending=False).reset_index(drop=True)


def report_most_borrowed_books(top_n: int = 10) -> pd.DataFrame:
    """
    Top N most-borrowed books by total issue count.
    Useful for recommendation-engine training data.
    """
    df = _transactions_df()
    if df.empty:
        return df
    counts = (
        df.groupby(["book_id", "book_title"])
        .size()
        .reset_index(name="borrow_count")
        .sort_values("borrow_count", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    return counts


def report_member_borrowing_history(member_id: Optional[int] = None) -> pd.DataFrame:
    """
    Full borrowing history, optionally filtered to a single member.
    Returns: member_name, book_title, issue_date, return_date, status
    """
    df = _transactions_df()
    if df.empty:
        return df
    if member_id:
        df = df[df["member_id"] == member_id]
    cols = ["member_name", "book_title", "issue_date", "return_date", "status"]
    return df[cols].sort_values("issue_date", ascending=False).reset_index(drop=True)


def report_inventory() -> pd.DataFrame:
    """
    Full inventory report showing total vs. available copies per book.
    Adds an 'utilisation_pct' column — useful for demand forecasting.
    """
    books = crud.fetch_all_books()
    if not books:
        return pd.DataFrame()
    df = pd.DataFrame(books)
    df["issued_copies"] = df["total_copies"] - df["available_copies"]
    df["utilisation_pct"] = (
        df["issued_copies"] / df["total_copies"] * 100
    ).round(1)
    cols = [
        "book_id", "title", "author", "category",
        "total_copies", "available_copies", "issued_copies", "utilisation_pct"
    ]
    return df[cols].sort_values("utilisation_pct", ascending=False).reset_index(drop=True)


def dashboard_stats() -> dict:
    """
    Aggregate statistics for the dashboard overview panel.
    Returns a plain dict for easy Streamlit metric rendering.
    """
    books = crud.fetch_all_books()
    members = crud.fetch_all_members()
    transactions = crud.fetch_all_transactions()

    total_books = len(books)
    total_members = len(members)
    active_issues = sum(1 for t in transactions if t["status"] == "Issued")
    total_transactions = len(transactions)

    overdue_df = report_overdue_books()
    overdue_count = len(overdue_df) if not overdue_df.empty else 0

    return {
        "total_books": total_books,
        "total_members": total_members,
        "active_issues": active_issues,
        "total_transactions": total_transactions,
        "overdue_count": overdue_count,
    }
