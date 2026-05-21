from __future__ import annotations

from datetime import date
from pathlib import Path

from convert_results import clean_csv_cell, parse_context_window, update_upload_dates


def test_parse_context_window_converts_k_and_m_suffixes() -> None:
    assert parse_context_window("128k") == "128000"
    assert parse_context_window("1.5M") == "1500000"
    assert parse_context_window("unknown") == "unknown"


def test_clean_csv_cell_normalizes_numeric_values() -> None:
    assert clean_csv_cell("$1,234.50", 20) == "1234.50"
    assert clean_csv_cell("98%", 5) == "98"
    assert clean_csv_cell("--", 5) == ""
    assert clean_csv_cell("1.05M", 1) == "1050000"


def test_update_upload_dates_rewrites_template_and_html_dates(tmp_path: Path) -> None:
    template = tmp_path / "compare_models_template.py"
    html = tmp_path / "index.html"
    template.write_text(
        'Data updated: May 15, 2026\nconst dataUpdated = "May 15, 2026";\n',
        encoding="utf-8",
    )
    html.write_text(
        'Data updated: May 15, 2026\nconst dataUpdated = "May 15, 2026";\n',
        encoding="utf-8",
    )

    updated_files = update_upload_dates([template, html], date(2026, 5, 20))

    assert updated_files == 2
    assert "Data updated: May 20, 2026" in template.read_text(encoding="utf-8")
    assert 'const dataUpdated = "May 20, 2026"' in html.read_text(encoding="utf-8")
