from __future__ import annotations

import calendar


def is_valid_date(year: int, month: int, day: int) -> bool:
    if not 1 <= month <= 12 or day < 1:
        return False
    return day <= calendar.monthrange(year, month)[1]


def expected_special_state(year: int, month: int, day: int) -> str | None:
    """Return NOT_APPLICABLE for structurally invalid calendar cells."""
    return None if is_valid_date(year, month, day) else "NOT_APPLICABLE"
