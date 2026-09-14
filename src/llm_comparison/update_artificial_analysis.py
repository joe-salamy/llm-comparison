from __future__ import annotations

import argparse
import asyncio
import contextlib
import re
import sys
import time
from collections.abc import Sequence
from datetime import UTC, date, datetime
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


def validate_scraped_table(
    display_headers: list[str], rows: list[list[str]]
) -> None:
    required_headers = {"Model", "Cost per Task"}
    missing_headers = sorted(required_headers - set(display_headers))
    if missing_headers:
        raise RuntimeError(
            "Artificial Analysis table is missing required headers: "
            + ", ".join(missing_headers)
        )

    cost_index = display_headers.index("Cost per Task")
    invalid_costs = [
        value
        for row in rows
        if (value := normalize_text(row[cost_index])) not in {"", "--"}
        and re.fullmatch(r"\$[0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?", value) is None
    ]
    if invalid_costs:
        examples = ", ".join(invalid_costs[:5])
        raise RuntimeError(
            f"Artificial Analysis Cost per Task values are malformed: {examples}"
        )


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


async def _locator_visible(locator: Any) -> bool:
    try:
        return bool(await locator.is_visible())
    except Exception:
        return False


async def _leaf_header_count(page: Any) -> int:
    try:
        table = page.locator("main table").first
        leaf_cells = table.locator("thead tr").last.locator("th, td")
        return int(await leaf_cells.count())
    except Exception:
        return 0


async def expand_columns(page: Any, timeout_ms: int) -> None:
    expand_by_name = page.get_by_role("button", name=re.compile("Expand columns", re.I))
    collapse_by_name = page.get_by_role(
        "button", name=re.compile("Collapse columns", re.I)
    )
    # Narrow viewports hide the label span, leaving an icon-only button with
    # an empty accessible name that the role locators above cannot match.
    expand_by_icon = page.locator("button:has(svg.lucide-arrow-right-from-line)")
    collapse_by_icon = page.locator("button:has(svg.lucide-arrow-left-from-line)")
    deadline = time.monotonic() + (timeout_ms / 1000)
    baseline = await _leaf_header_count(page)
    while time.monotonic() < deadline:
        remaining_ms = int((deadline - time.monotonic()) * 1000)
        if remaining_ms <= 0:
            break
        if await _locator_visible(collapse_by_name.first) or await _locator_visible(
            collapse_by_icon.first
        ):
            return
        current = await _leaf_header_count(page)
        if baseline > 0 and current > baseline:
            return
        if baseline == 0 and current > 0:
            baseline = current
        if await _locator_visible(expand_by_name.first):
            expand_target = expand_by_name.first
        elif await _locator_visible(expand_by_icon.first):
            expand_target = expand_by_icon.first
        else:
            await page.wait_for_timeout(min(250, remaining_ms))
            continue
        # The button renders before React hydration attaches its handler, so a
        # single click can land without expanding. Click, then poll for the
        # transition and retry until the deadline instead of waiting once.
        with contextlib.suppress(Exception):
            await expand_target.scroll_into_view_if_needed(timeout=remaining_ms)
        with contextlib.suppress(Exception):
            await expand_target.click(timeout=remaining_ms)
        settle_until = min(deadline, time.monotonic() + 5)
        while time.monotonic() < settle_until:
            if await _locator_visible(collapse_by_name.first) or await _locator_visible(
                collapse_by_icon.first
            ):
                return
            expanded = await _leaf_header_count(page)
            if baseline > 0 and expanded > baseline:
                return
            settle_remaining_ms = int((deadline - time.monotonic()) * 1000)
            if settle_remaining_ms <= 0:
                break
            await page.wait_for_timeout(min(250, settle_remaining_ms))
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
            display_headers, rows = extract_table(snapshot)
            validate_scraped_table(display_headers, rows)
            return display_headers, rows
        finally:
            await browser.close()




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
    return parser.parse_args(argv)


async def async_main(args: argparse.Namespace) -> None:
    stage_count = 3

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
    uploaded_at = args.uploaded_date or datetime.now(UTC)
    write_table_csv(display_headers, rows, args.csv)
    updated_files = update_upload_dates([args.template, args.html], uploaded_at)
    print(f"      Wrote {row_count} {row_label} to {args.csv}.")
    print(f"      Updated the data timestamp in {updated_files} files.")


    print(f"[{stage_count}/{stage_count}] Update complete.")


def main() -> None:
    asyncio.run(async_main(parse_args()))


if __name__ == "__main__":
    main()
