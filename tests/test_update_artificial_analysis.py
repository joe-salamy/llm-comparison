from __future__ import annotations

import argparse
import asyncio
import subprocess
import sys
from datetime import date
from pathlib import Path

from pytest import MonkeyPatch

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


def test_async_main_runs_publish_after_data_update(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    calls: list[str] = []
    csv_path = tmp_path / "results.csv"
    html_path = tmp_path / "index.html"
    template_path = tmp_path / "template.py"
    publish_script = tmp_path / "scripts/update-gh-pages.py"
    uploaded_date = date(2026, 6, 27)

    async def fake_scrape_table(
        url: str, *, timeout_ms: int, headed: bool
    ) -> tuple[list[str], list[list[str]]]:
        assert url == "https://example.com"
        assert timeout_ms == 123
        assert headed is True
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

    def fake_run_publish_script(path: Path) -> None:
        assert path == publish_script
        calls.append("publish")

    monkeypatch.setattr(updater, "scrape_table", fake_scrape_table)
    monkeypatch.setattr(updater, "write_table_csv", fake_write_table_csv)
    monkeypatch.setattr(updater, "update_upload_dates", fake_update_upload_dates)
    monkeypatch.setattr(updater, "run_publish_script", fake_run_publish_script)

    args = argparse.Namespace(
        url="https://example.com",
        timeout_ms=123,
        headed=True,
        csv=csv_path,
        template=template_path,
        html=html_path,
        uploaded_date=uploaded_date,
        skip_publish=False,
        publish_script=publish_script,
    )

    asyncio.run(updater.async_main(args))

    assert calls == ["scrape", "write", "date", "publish"]

def test_async_main_defaults_missing_uploaded_date_to_today(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    csv_path = tmp_path / "results.csv"
    html_path = tmp_path / "index.html"
    template_path = tmp_path / "template.py"
    expected_date = date(2026, 6, 29)

    class FixedDate(date):
        @classmethod
        def today(cls) -> FixedDate:
            return cls(2026, 6, 29)

    async def fake_scrape_table(
        url: str, *, timeout_ms: int, headed: bool
    ) -> tuple[list[str], list[list[str]]]:
        return ["Model"], [["Claude"]]

    def fake_write_table_csv(
        display_headers: list[str], rows: list[list[str]], path: Path
    ) -> list[str]:
        return ["model"]

    def fake_update_upload_dates(paths: list[Path], value: date) -> int:
        assert paths == [template_path, html_path]
        assert value == expected_date
        return len(paths)

    monkeypatch.setattr(updater, "date", FixedDate)
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
        skip_publish=True,
        publish_script=Path("scripts/update-gh-pages.py"),
    )

    asyncio.run(updater.async_main(args))


def test_run_publish_script_resolves_relative_path_from_git_root(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    repo_root = tmp_path / "repo"
    calls: list[tuple[list[str], Path | None]] = []

    def fake_run(
        command: list[str],
        *,
        check: bool,
        encoding: str | None = None,
        stdout: int | None = None,
        cwd: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        assert check is True
        calls.append((command, cwd))
        if command == ["git", "rev-parse", "--show-toplevel"]:
            assert encoding == "utf-8"
            assert stdout == subprocess.PIPE
            return subprocess.CompletedProcess(command, 0, stdout=f"{repo_root}\n")
        return subprocess.CompletedProcess(command, 0, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    updater.run_publish_script(Path("scripts/update-gh-pages.py"))

    assert calls == [
        (["git", "rev-parse", "--show-toplevel"], None),
        ([sys.executable, str(repo_root / "scripts/update-gh-pages.py")], repo_root),
    ]


def test_direct_script_execution_imports_package() -> None:
    script_path = Path("src/llm_comparison/update_artificial_analysis.py")

    result = subprocess.run(
        [sys.executable, str(script_path), "--help"],
        check=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
    )

    assert "Update Artificial Analysis leaderboard data automatically." in result.stdout
