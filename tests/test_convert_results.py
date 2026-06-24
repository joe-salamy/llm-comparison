from __future__ import annotations

from datetime import date
from pathlib import Path

from convert_results import (
    clean_csv_cell,
    parse_context_window,
    parse_headers,
    parse_input,
    update_upload_dates,
    write_table_csv,
)


def test_parse_headers_derives_columns_from_input() -> None:
    lines = [
        "Features",
        "",
        "Model",
        "",
        "Context Window",
        "",
        "Creator",
        "",
        "License",
        "",
        "ITBench-AA",
        "Kubernetes Incident Root-Cause Analysis",
        "",
        "Blended",
        "USD/1M Tokens",
        "",
        "Further Analysis",
        "Model",
        "Providers",
    ]
    display_headers, csv_headers = parse_headers(lines)

    assert display_headers == [
        "Model",
        "Context Window",
        "Creator",
        "License",
        "ITBench-AA",
        "Blended (USD/1M Tokens)",
    ]
    assert csv_headers == [
        "model",
        "context_window_tokens",
        "creator",
        "license",
        "itbench_aa",
        "blended_usd_per_1m_tokens",
    ]


def test_parse_input_preserves_legacy_provider_insertion_when_rows_have_extra_value(
    tmp_path: Path,
) -> None:
    lines = [
        "Features",
        "",
        "Model",
        "",
        "Context Window",
        "",
        "Creator",
        "",
        "License",
        "",
        "Further Analysis",
        "Model",
        "Providers",
        "Claude Test",
        "1M",
        "Anthropic",
        "Anthropic",
        "Proprietary",
    ]
    path = tmp_path / "input.txt"
    path.write_text("\n".join(lines), encoding="utf-8")

    display_headers, csv_headers, rows = parse_input(path)

    assert display_headers == [
        "Model",
        "Context Window",
        "Creator",
        "Providers",
        "License",
    ]
    assert csv_headers == [
        "model",
        "context_window_tokens",
        "creator",
        "providers",
        "license",
    ]
    assert rows == [["Claude Test", "1M", "Anthropic", "Anthropic", "Proprietary"]]


def test_parse_input_does_not_insert_provider_for_structured_width(
    tmp_path: Path,
) -> None:
    lines = [
        "Features",
        "",
        "Model",
        "",
        "Context Window",
        "",
        "Creator",
        "",
        "License",
        "",
        "Further Analysis",
        "Model",
        "Providers",
        "Claude Test",
        "1M",
        "Anthropic",
        "Proprietary",
    ]
    path = tmp_path / "input.txt"
    path.write_text("\n".join(lines), encoding="utf-8")

    display_headers, csv_headers, rows = parse_input(path)

    assert display_headers == ["Model", "Context Window", "Creator", "License"]
    assert csv_headers == ["model", "context_window_tokens", "creator", "license"]
    assert "providers" not in csv_headers
    assert rows == [["Claude Test", "1M", "Anthropic", "Proprietary"]]

def test_parse_context_window_converts_k_and_m_suffixes() -> None:
    assert parse_context_window("128k") == "128000"
    assert parse_context_window("1.5M") == "1500000"
    assert parse_context_window("unknown") == "unknown"


def test_clean_csv_cell_normalizes_numeric_values() -> None:
    assert clean_csv_cell("$1,234.50", "input_price_usd_per_1m_tokens") == "1234.50"
    assert clean_csv_cell("98%", "gpqa_diamond_pct") == "98"
    assert clean_csv_cell("--", "license") == ""
    assert clean_csv_cell("1.05M", "context_window_tokens") == "1050000"
    assert clean_csv_cell("1.05M", "model") == "1.05M"


def test_write_table_csv_dedupes_dynamic_headers(tmp_path: Path) -> None:
    path = tmp_path / "results.csv"

    csv_headers = write_table_csv(["Score", "Score"], [["1,234", "56%"]], path)

    assert csv_headers == ["score", "score_2"]
    assert path.read_text(encoding="utf-8").splitlines() == [
        "score,score_2",
        "1234,56",
    ]


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
