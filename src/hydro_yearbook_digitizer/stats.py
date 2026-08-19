from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable


@dataclass(frozen=True)
class MonthlyStats:
    mean: Decimal
    maximum: Decimal
    maximum_days: tuple[int, ...]
    minimum: Decimal
    minimum_days: tuple[int, ...]
    count: int


def calculate_monthly_stats(values: Iterable[tuple[int, Decimal]]) -> MonthlyStats:
    """Calculate statistics from valid numeric daily values only."""
    items = list(values)
    if not items:
        raise ValueError("at least one numeric daily value is required")

    total = sum((value for _, value in items), Decimal("0"))
    maximum = max(value for _, value in items)
    minimum = min(value for _, value in items)
    return MonthlyStats(
        mean=total / Decimal(len(items)),
        maximum=maximum,
        maximum_days=tuple(day for day, value in items if value == maximum),
        minimum=minimum,
        minimum_days=tuple(day for day, value in items if value == minimum),
        count=len(items),
    )
