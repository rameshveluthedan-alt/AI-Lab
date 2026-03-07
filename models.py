"""
models.py
---------
Dataclass models representing core entities in the Library Management System.
Designed to be extensible for future AI/ML integration.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import date


@dataclass
class Book:
    """Represents a library book."""
    title: str
    author: str
    category: str
    total_copies: int
    available_copies: int
    isbn: Optional[str] = None
    published_year: Optional[int] = None
    book_id: Optional[int] = None


@dataclass
class Member:
    """Represents a library member."""
    name: str
    gender: str           # 'Male' | 'Female' | 'Other'
    age: int
    mobile_number: str
    email: str
    join_date: Optional[str] = None
    member_id: Optional[int] = None


@dataclass
class Transaction:
    """Represents a book issue/return transaction."""
    book_id: int
    member_id: int
    issue_date: str
    return_date: Optional[str] = None
    status: str = "Issued"   # 'Issued' | 'Returned'
    transaction_id: Optional[int] = None
