from __future__ import annotations

from convert_results import clean_csv_cell, parse_context_window


def test_parse_context_window_converts_k_and_m_suffixes() -> None:
    assert parse_context_window("128k") == "128000"
    assert parse_context_window("1.5M") == "1500000"
    assert parse_context_window("unknown") == "unknown"


def test_clean_csv_cell_normalizes_numeric_values() -> None:
    assert clean_csv_cell("$1,234.50", 20) == "1234.50"
    assert clean_csv_cell("98%", 5) == "98"
    assert clean_csv_cell("--", 5) == ""
    assert clean_csv_cell("1.05M", 1) == "1050000"
