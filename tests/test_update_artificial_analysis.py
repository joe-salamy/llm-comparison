from __future__ import annotations

import argparse
import asyncio
import subprocess
import sys
from datetime import UTC, date, datetime, tzinfo
from pathlib import Path

import pytest
from pytest import CaptureFixture, MonkeyPatch

import llm_comparison.update_artificial_analysis as updater
from llm_comparison.update_artificial_analysis import (
    CellSnapshot,
    HeaderSnapshot,
    extract_table,
)


def test_action_only_column_is_dropped_without_header_name() -> None:
    headers: list[HeaderSnapshot] = [{"text": "Model"}, {"text": "Unrelated Header"}]
    rows: list[list[CellSnapshot]] = [
        [
            {"text": "Claude", "linkText": "", "hasLink": False, "imageAlts": []},
            {
                "text": "Model Providers",
                "linkText": "Model Providers",
                "hasLink": True,
                "imageAlts": [],
            },
        ],
        [
            {"text": "Gemini", "linkText": "", "hasLink": False, "imageAlts": []},
            {
                "text": "Model Providers",
                "linkText": "Model Providers",
                "hasLink": True,
                "imageAlts": [],
            },
        ],
    ]

    display_headers, extracted_rows = extract_table({"headers": headers, "rows": rows})

    assert display_headers == ["Model"]
    assert extracted_rows == [["Claude"], ["Gemini"]]


def test_extra_cell_without_header_raises_instead_of_truncating() -> None:
    headers: list[HeaderSnapshot] = [{"text": "Model"}, {"text": "Creator"}]
    rows: list[list[CellSnapshot]] = [
        [
            {"text": "Claude", "linkText": "", "hasLink": False, "imageAlts": []},
            {"text": "Anthropic", "linkText": "", "hasLink": False, "imageAlts": []},
            {"text": "Extra", "linkText": "", "hasLink": False, "imageAlts": []},
        ]
    ]

    try:
        extract_table({"headers": headers, "rows": rows})
    except ValueError as exc:
        assert str(exc) == "Expected 2 raw columns per row; mismatches: row 1: 3"
    else:
        raise AssertionError("expected extract_table to reject unheadered cells")


def test_cell_text_preferred_over_duplicate_image_alt() -> None:
    display_headers, rows = extract_table(
        {
            "headers": [{"text": "Creator"}],
            "rows": [
                [
                    {
                        "text": "Anthropic",
                        "linkText": "",
                        "hasLink": False,
                        "imageAlts": ["Anthropic"],
                    }
                ]
            ],
        }
    )

    assert display_headers == ["Creator"]
    assert rows == [["Anthropic"]]


def test_image_alt_fallback_when_text_empty() -> None:
    display_headers, rows = extract_table(
        {
            "headers": [{"text": "Provider"}],
            "rows": [
                [
                    {
                        "text": "",
                        "linkText": "",
                        "hasLink": False,
                        "imageAlts": ["Provider X"],
                    }
                ]
            ],
        }
    )

    assert display_headers == ["Provider"]
    assert rows == [["Provider X"]]


def test_async_main_writes_data_and_timestamp_locally(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    calls: list[str] = []
    csv_path = tmp_path / "results.csv"
    html_path = tmp_path / "index.html"
    template_path = tmp_path / "template.py"
    uploaded_date = date(2026, 6, 27)

    async def fake_scrape_table(
        url: str, *, timeout_ms: int, headed: bool
    ) -> tuple[list[str], list[list[str]]]:
        assert url == "https://example.com"
        assert timeout_ms == 123
        assert headed is True
        assert capsys.readouterr().out == (
            "[1/3] Fetching the Artificial Analysis leaderboard...\n"
        )
        calls.append("scrape")
        return ["Model"], [["Claude"]]

    def fake_write_table_csv(
        display_headers: list[str], rows: list[list[str]], path: Path
    ) -> list[str]:
        assert display_headers == ["Model"]
        assert rows == [["Claude"]]
        assert path == csv_path
        calls.append("write")
        return ["model"]

    def fake_update_upload_dates(paths: list[Path], value: date) -> int:
        assert paths == [template_path, html_path]
        assert value == uploaded_date
        calls.append("date")
        return len(paths)

    monkeypatch.setattr(updater, "scrape_table", fake_scrape_table)
    monkeypatch.setattr(updater, "write_table_csv", fake_write_table_csv)
    monkeypatch.setattr(updater, "update_upload_dates", fake_update_upload_dates)

    args = argparse.Namespace(
        url="https://example.com",
        timeout_ms=123,
        headed=True,
        csv=csv_path,
        template=template_path,
        html=html_path,
        uploaded_date=uploaded_date,
    )

    asyncio.run(updater.async_main(args))

    assert calls == ["scrape", "write", "date"]
    assert capsys.readouterr().out.splitlines() == [
        "      Found 1 row across 1 column.",
        "[2/3] Saving generated data...",
        f"      Wrote 1 row to {csv_path}.",
        "      Updated the data timestamp in 2 files.",
        "[3/3] Update complete.",
    ]

def test_async_main_defaults_missing_uploaded_date_to_current_utc_time(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    csv_path = tmp_path / "results.csv"
    html_path = tmp_path / "index.html"
    template_path = tmp_path / "template.py"
    expected_timestamp = datetime(2026, 6, 29, 12, 34, 56, tzinfo=UTC)

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz: tzinfo | None = None) -> FixedDateTime:
            assert tz is UTC
            return cls(2026, 6, 29, 12, 34, 56, tzinfo=tz)

    async def fake_scrape_table(
        url: str, *, timeout_ms: int, headed: bool
    ) -> tuple[list[str], list[list[str]]]:
        assert capsys.readouterr().out == (
            "[1/3] Fetching the Artificial Analysis leaderboard...\n"
        )
        return ["Model"], [["Claude"]]

    def fake_write_table_csv(
        display_headers: list[str], rows: list[list[str]], path: Path
    ) -> list[str]:
        return ["model"]

    def fake_update_upload_dates(
        paths: list[Path], value: date | datetime
    ) -> int:
        assert paths == [template_path, html_path]
        assert value == expected_timestamp
        return len(paths)

    monkeypatch.setattr(updater, "datetime", FixedDateTime)
    monkeypatch.setattr(updater, "scrape_table", fake_scrape_table)
    monkeypatch.setattr(updater, "write_table_csv", fake_write_table_csv)
    monkeypatch.setattr(updater, "update_upload_dates", fake_update_upload_dates)

    args = argparse.Namespace(
        url="https://example.com",
        timeout_ms=123,
        headed=False,
        csv=csv_path,
        template=template_path,
        html=html_path,
        uploaded_date=None,
    )

    asyncio.run(updater.async_main(args))
    assert capsys.readouterr().out.splitlines() == [
        "      Found 1 row across 1 column.",
        "[2/3] Saving generated data...",
        f"      Wrote 1 row to {csv_path}.",
        "      Updated the data timestamp in 2 files.",
        "[3/3] Update complete.",
    ]


def test_default_paths_resolve_from_project_root() -> None:
    args = updater.parse_args([])

    assert args.csv == updater.PROJECT_ROOT / "data/results.csv"
    assert args.html == updater.PROJECT_ROOT / "public/index.html"
    assert args.template == (
        updater.PROJECT_ROOT / "src/llm_comparison/compare_models_template.py"
    )




@pytest.mark.parametrize("option", ["--skip-publish", "--publish-script"])
def test_publication_options_are_rejected(option: str) -> None:
    with pytest.raises(SystemExit):
        updater.parse_args([option])


def test_direct_script_execution_imports_package() -> None:
    script_path = Path("src/llm_comparison/update_artificial_analysis.py")

    result = subprocess.run(
        [sys.executable, str(script_path), "--help"],
        check=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
    )

    assert "Update Artificial Analysis leaderboard data automatically." in result.stdout
