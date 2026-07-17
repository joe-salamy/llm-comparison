from __future__ import annotations

import argparse
import asyncio
import re
import subprocess
import sys
import time
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Any, TypedDict, cast

if __package__:
    from .convert_results import (
        build_display_header,
        update_upload_dates,
        write_table_csv,
    )
else:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from llm_comparison.convert_results import (
        build_display_header,
        update_upload_dates,
        write_table_csv,
    )

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_URL = "https://artificialanalysis.ai/leaderboards/models"
DEFAULT_CSV = PROJECT_ROOT / "data/results.csv"
DEFAULT_HTML = PROJECT_ROOT / "public/index.html"
DEFAULT_TEMPLATE = PROJECT_ROOT / "src/llm_comparison/compare_models_template.py"
DEFAULT_PUBLISH_SCRIPT = PROJECT_ROOT / "scripts/update-gh-pages.py"


class HeaderSnapshot(TypedDict):
    text: str


class CellSnapshot(TypedDict):
    text: str
    linkText: str
    hasLink: bool
    imageAlts: list[str]


class TableSnapshot(TypedDict):
    headers: list[HeaderSnapshot]
    rows: list[list[CellSnapshot]]


def normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


def display_header_from_snapshot(header: HeaderSnapshot) -> str:
    header_lines = [
        line.strip() for line in header["text"].splitlines() if line.strip()
    ]
    if len(header_lines) >= 2:
        return build_display_header(header_lines[0], header_lines[1])
    if header_lines:
        return header_lines[0]
    return ""


def cell_value_from_snapshot(cell: CellSnapshot) -> str:
    text = normalize_text(cell["text"])
    if text:
        return text
    image_alts = [normalize_text(alt) for alt in cell["imageAlts"]]
    return "; ".join(alt for alt in image_alts if alt)


def is_action_only_column(rows: list[list[CellSnapshot]], column_index: int) -> bool:
    if not rows:
        return False

    for row in rows:
        if column_index >= len(row):
            return False
        cell = row[column_index]
        text = normalize_text(cell["text"])
        link_text = normalize_text(cell["linkText"])
        if not cell["hasLink"] or not text or text != link_text:
            return False

    return True


def extract_table(snapshot: TableSnapshot) -> tuple[list[str], list[list[str]]]:
    display_headers = [
        display_header_from_snapshot(header) for header in snapshot["headers"]
    ]
    rows = snapshot["rows"]
    raw_bad_rows = [
        (index, len(row))
        for index, row in enumerate(rows, start=1)
        if len(row) != len(display_headers)
    ]
    if raw_bad_rows:
        examples = ", ".join(
            f"row {index}: {width}" for index, width in raw_bad_rows[:5]
        )
        raise ValueError(
            f"Expected {len(display_headers)} raw columns per row; "
            f"mismatches: {examples}"
        )
    retained_indexes = [
        index
        for index in range(len(display_headers))
        if not is_action_only_column(rows, index)
    ]
    retained_headers = [display_headers[index] for index in retained_indexes]
    retained_rows = [
        [
            cell_value_from_snapshot(row[index])
            for index in retained_indexes
            if index < len(row)
        ]
        for row in rows
    ]

    if not retained_headers:
        raise ValueError("Expected at least one retained table column")
    if not retained_rows:
        raise ValueError("Expected at least one table row")

    expected_width = len(retained_headers)
    bad_rows = [
        (index, len(row))
        for index, row in enumerate(retained_rows, start=1)
        if len(row) != expected_width
    ]
    if bad_rows:
        examples = ", ".join(f"row {index}: {width}" for index, width in bad_rows[:5])
        raise ValueError(
            f"Expected {expected_width} retained columns per row; "
            f"mismatches: {examples}"
        )

    return retained_headers, retained_rows


async def expand_columns(page: Any, timeout_ms: int) -> None:
    expand_button = page.get_by_role("button", name=re.compile("Expand columns", re.I))
    collapse_button = page.get_by_role(
        "button", name=re.compile("Collapse columns", re.I)
    )
    deadline = time.monotonic() + (timeout_ms / 1000)

    while time.monotonic() < deadline:
        if await expand_button.first.is_visible():
            await expand_button.first.click(timeout=timeout_ms)
            await collapse_button.first.wait_for(state="visible", timeout=timeout_ms)
            return
        if await collapse_button.first.is_visible():
            return
        await page.wait_for_timeout(250)

    raise RuntimeError("Could not find Artificial Analysis column expansion control")


async def scrape_table(
    url: str, *, timeout_ms: int, headed: bool
) -> tuple[list[str], list[list[str]]]:
    from playwright.async_api import async_playwright

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=not headed)
        try:
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            await expand_columns(page, timeout_ms)

            table = page.locator("main table").first
            await table.locator("thead tr").last.wait_for(
                state="visible", timeout=timeout_ms
            )
            await table.locator("tbody tr").first.wait_for(
                state="visible", timeout=timeout_ms
            )
            snapshot = cast(
                TableSnapshot,
                await table.evaluate(
                    """
                    (table) => {
                        const headerRows = Array.from(
                            table.querySelectorAll('thead tr')
                        );
                        const leafHeaderRow = headerRows.at(-1);
                        const headers = leafHeaderRow
                            ? Array.from(leafHeaderRow.cells, (cell) => ({
                                text: cell.innerText || '',
                            }))
                            : [];
                        const rows = Array.from(
                            table.querySelectorAll('tbody tr'),
                            (row) => Array.from(row.cells, (cell) => {
                                const links = Array.from(cell.querySelectorAll('a'));
                                const imageAlts = Array.from(
                                    cell.querySelectorAll('img')
                                )
                                    .map((image) => image.getAttribute('alt') || '')
                                    .map((alt) => alt.trim())
                                    .filter(Boolean);
                                return {
                                    text: cell.innerText || '',
                                    linkText: links
                                        .map((link) => link.innerText || '')
                                        .join(' '),
                                    hasLink: links.length > 0,
                                    imageAlts,
                                };
                            })
                        );
                        return { headers, rows };
                    }
                    """
                ),
            )
            return extract_table(snapshot)
        finally:
            await browser.close()


def run_publish_script(script_path: Path) -> None:
    resolved_script = (
        script_path if script_path.is_absolute() else PROJECT_ROOT / script_path
    )
    publish_result = subprocess.run(
        [sys.executable, str(resolved_script)],
        cwd=PROJECT_ROOT,
        check=False,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if publish_result.returncode != 0:
        output = publish_result.stderr or publish_result.stdout
        detail = " ".join(output.splitlines()[-3:])
        message = "GitHub Pages publishing failed"
        if detail:
            message = f"{message}: {detail}"
        raise RuntimeError(message)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update Artificial Analysis leaderboard data automatically."
    )
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--csv", default=DEFAULT_CSV, type=Path)
    parser.add_argument("--html", default=DEFAULT_HTML, type=Path)
    parser.add_argument("--template", default=DEFAULT_TEMPLATE, type=Path)
    parser.add_argument(
        "--uploaded-date",
        default=None,
        type=date.fromisoformat,
        help="Data upload date in YYYY-MM-DD format. Defaults to today.",
    )
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--timeout-ms", default=30_000, type=int)
    parser.add_argument(
        "--skip-publish",
        action="store_true",
        help="Update local data files without running scripts/update-gh-pages.py.",
    )
    parser.add_argument(
        "--publish-script",
        default=DEFAULT_PUBLISH_SCRIPT,
        type=Path,
        help="Path to the GitHub Pages update script, relative to the repository root.",
    )
    return parser.parse_args(argv)


async def async_main(args: argparse.Namespace) -> None:
    stage_count = 3 if args.skip_publish else 4

    print(
        f"[1/{stage_count}] Fetching the Artificial Analysis leaderboard...",
        flush=True,
    )
    display_headers, rows = await scrape_table(
        args.url, timeout_ms=args.timeout_ms, headed=args.headed
    )
    row_count = len(rows)
    row_label = "row" if row_count == 1 else "rows"
    column_count = len(display_headers)
    column_label = "column" if column_count == 1 else "columns"
    print(
        f"      Found {row_count} {row_label} across "
        f"{column_count} {column_label}."
    )

    print(f"[2/{stage_count}] Saving generated data...", flush=True)
    uploaded_date = args.uploaded_date or date.today()
    write_table_csv(display_headers, rows, args.csv)
    updated_files = update_upload_dates([args.template, args.html], uploaded_date)
    print(f"      Wrote {row_count} {row_label} to {args.csv}.")
    print(f"      Updated the data date in {updated_files} files.")

    if not args.skip_publish:
        print(f"[3/{stage_count}] Publishing GitHub Pages...", flush=True)
        run_publish_script(args.publish_script)
        print("      Published GitHub Pages.")

    print(f"[{stage_count}/{stage_count}] Update complete.")


def main() -> None:
    asyncio.run(async_main(parse_args()))


if __name__ == "__main__":
    main()
