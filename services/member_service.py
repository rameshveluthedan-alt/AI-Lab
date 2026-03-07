"""
services/member_service.py
--------------------------
Business-logic layer for Member operations.
Enforces validation rules before delegating to db/crud.py.
"""

import re
import logging
from datetime import date
from typing import Dict, List, Optional, Tuple
from db import crud

logger = logging.getLogger(__name__)

EMAIL_PATTERN = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")
VALID_GENDERS = ("Male", "Female", "Other")


def _validate_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(email))


def add_member(
    name: str,
    gender: str,
    age: int,
    mobile_number: str,
    email: str,
) -> Tuple[bool, str]:
    """
    Validate and register a new library member.

    Returns:
        (success: bool, message: str)
    """
    if not name.strip():
        return False, "Name cannot be empty."
    if gender not in VALID_GENDERS:
        return False, f"Gender must be one of: {', '.join(VALID_GENDERS)}."
    if age <= 0:
        return False, "Age must be a positive integer."
    if not _validate_email(email.strip()):
        return False, "Invalid email format."

    data = {
        "name": name.strip(),
        "gender": gender,
        "age": age,
        "mobile_number": mobile_number.strip(),
        "email": email.strip().lower(),
        "join_date": str(date.today()),
    }
    try:
        member_id = crud.insert_member(data)
        logger.info("Added member id=%s name='%s'", member_id, name)
        return True, f"Member '{name}' registered (ID: {member_id})."
    except Exception as e:
        if "UNIQUE" in str(e):
            return False, "A member with this email already exists."
        logger.error("add_member error: %s", e)
        return False, f"Database error: {e}"


def update_member(
    member_id: int,
    name: str,
    gender: str,
    age: int,
    mobile_number: str,
    email: str,
) -> Tuple[bool, str]:
    """Update an existing member record."""
    if not name.strip():
        return False, "Name is required."
    if gender not in VALID_GENDERS:
        return False, f"Gender must be one of: {', '.join(VALID_GENDERS)}."
    if age <= 0:
        return False, "Age must be positive."
    if not _validate_email(email.strip()):
        return False, "Invalid email format."

    data = {
        "name": name.strip(),
        "gender": gender,
        "age": age,
        "mobile_number": mobile_number.strip(),
        "email": email.strip().lower(),
    }
    try:
        updated = crud.update_member(member_id, data)
        if updated:
            return True, f"Member ID {member_id} updated successfully."
        return False, "Member not found."
    except Exception as e:
        if "UNIQUE" in str(e):
            return False, "Email is already used by another member."
        logger.error("update_member error: %s", e)
        return False, f"Database error: {e}"


def delete_member(member_id: int) -> Tuple[bool, str]:
    """
    Delete a member only if they have no active (unreturned) book issues.
    """
    active = crud.fetch_active_transactions_for_member(member_id)
    if active:
        return False, "Cannot delete: member has unreturned books."
    try:
        deleted = crud.delete_member(member_id)
        if deleted:
            return True, f"Member ID {member_id} deleted."
        return False, "Member not found."
    except Exception as e:
        logger.error("delete_member error: %s", e)
        return False, f"Database error: {e}"


def get_all_members() -> List[Dict]:
    return crud.fetch_all_members()


def search_members(query: str) -> List[Dict]:
    if not query.strip():
        return crud.fetch_all_members()
    return crud.search_members(query.strip())


def get_member_by_id(member_id: int) -> Optional[Dict]:
    return crud.fetch_member_by_id(member_id)
