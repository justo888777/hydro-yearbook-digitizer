from decimal import Decimal

from hydro_yearbook_digitizer.stats import calculate_monthly_stats


def test_calculate_monthly_stats_and_ties() -> None:
    result = calculate_monthly_stats(
        [(1, Decimal("1.0")), (2, Decimal("3.0")), (3, Decimal("3.0"))]
    )
    assert result.mean == Decimal("7.0") / Decimal(3)
    assert result.maximum == Decimal("3.0")
    assert result.maximum_days == (2, 3)
    assert result.minimum == Decimal("1.0")
    assert result.minimum_days == (1,)
