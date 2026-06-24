from __future__ import annotations

import argparse
import asyncio
import re
import time
from datetime import date
from pathlib import Path
from typing import Any, TypedDict, cast

from convert_results import build_display_header, update_upload_dates, write_table_csv

DEFAULT_URL = "https://artificialanalysis.ai/leaderboards/models"
DEFAULT_CSV = Path("results.csv")
DEFAULT_HTML = Path("index.html")
DEFAULT_TEMPLATE = Path("compare_models_template.py")


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
        examples = ", ".join(
            f"row {index}: {width}" for index, width in bad_rows[:5]
        )
        raise ValueError(
            f"Expected {expected_width} retained columns per row; "
            f"mismatches: {examples}"
        )

    return retained_headers, retained_rows


async def expand_columns(page: Any, timeout_ms: int) -> None:
    expand_button = page.get_by_role(
        "button", name=re.compile("Expand columns", re.I)
    )
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update Artificial Analysis leaderboard data automatically."
    )
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--csv", default=DEFAULT_CSV, type=Path)
    parser.add_argument("--html", default=DEFAULT_HTML, type=Path)
    parser.add_argument("--template", default=DEFAULT_TEMPLATE, type=Path)
    parser.add_argument(
        "--uploaded-date",
        default=date.today(),
        type=date.fromisoformat,
        help="Data upload date in YYYY-MM-DD format. Defaults to today.",
    )
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--timeout-ms", default=30_000, type=int)
    return parser.parse_args()


async def async_main(args: argparse.Namespace) -> None:
    display_headers, rows = await scrape_table(
        args.url, timeout_ms=args.timeout_ms, headed=args.headed
    )
    csv_headers = write_table_csv(display_headers, rows, args.csv)
    updated_files = update_upload_dates([args.template, args.html], args.uploaded_date)

    row_count = len(rows)
    column_count = len(csv_headers)
    print(f"Scraped {row_count} rows and {column_count} columns from {args.url}")
    print(f"Wrote {row_count} rows to {args.csv}")
    print(f"Updated upload date in {updated_files} files")


def main() -> None:
    asyncio.run(async_main(parse_args()))


if __name__ == "__main__":
    main()
