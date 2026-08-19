from hydro_yearbook_digitizer.naming import (
    daily_station_workbook_name,
    master_workbook_name,
    monthly_summary_workbook_name,
    station_index_workbook_name,
    station_workbook_name,
)


def test_station_workbook_name() -> None:
    assert station_workbook_name(42, "双龙湾", "逐日平均流量") == "042-双龙湾-逐日平均流量.xlsx"


def test_station_workbook_name_removes_windows_invalid_characters() -> None:
    assert station_workbook_name(1, "甲/乙站", "流量:m³/s") == "001-甲_乙站-流量_m³_s.xlsx"


def test_master_workbook_name() -> None:
    assert master_workbook_name("永定河流域", 1962) == "00_永定河流域_1962_总表.xlsx"


def test_daily_station_workbook_name_preserves_source_identity_parts() -> None:
    assert (
        daily_station_workbook_name(7, "饮马河", "丰镇（黑三）", "流量")
        == "007-饮马河-丰镇（黑三）-流量-日值表.xlsx"
    )


def test_monthly_summary_workbook_name() -> None:
    assert (
        monthly_summary_workbook_name("永定河", 2024, "含沙量")
        == "2024-永定河-含沙量-月值总表.xlsx"
    )


def test_station_index_workbook_name() -> None:
    assert station_index_workbook_name() == "站点与目录索引.xlsx"
