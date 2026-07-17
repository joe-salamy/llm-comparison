from __future__ import annotations

import argparse
import asyncio
import csv
import re
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import TypedDict, cast

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_URL = "https://opencode.ai/docs/go/"
DEFAULT_CSV = PROJECT_ROOT / "data/opencode_go.csv"
DEFAULT_AA_CSV = PROJECT_ROOT / "data/results.csv"

SOURCE_HEADERS = ["Model", "Input", "Output", "Cached Read", "Cached Write", "Usage"]
CSV_COLUMNS = [
    "model",
    "input_price_usd_per_1m_tokens",
    "output_price_usd_per_1m_tokens",
    "cache_read_usd_per_1m_tokens",
    "cache_write_usd_per_1m_tokens",
    "monthly_usage_usd",
    "long_context_threshold_tokens",
    "long_context_input_price_usd_per_1m_tokens",
    "long_context_output_price_usd_per_1m_tokens",
    "long_context_cache_read_usd_per_1m_tokens",
    "long_context_cache_write_usd_per_1m_tokens",
    "artificial_analysis_model",
    "artificial_analysis_intelligence_index",
    "opencode_go_blended_usd_per_1m_tokens",
    "long_context_blended_usd_per_1m_tokens",
    "value_score",
    "scraped_at",
]

AA_MODEL_ALIASES: dict[str, tuple[str, ...]] = {
    "Grok 4.5": ("Grok 4.5 (high)",),
    "GLM-5.2": ("GLM-5.2 (max)", "GLM-5.2"),
    "GLM-5.1": ("GLM-5.1",),
    "Kimi K3": ("Kimi K3",),
    "Kimi K2.7 Code": ("Kimi K2.7 Code",),
    "Kimi K2.6": ("Kimi K2.6",),
    "MiMo V2.5": ("MiMo-V2.5",),
    "MiMo V2.5 Pro": ("MiMo-V2.5-Pro",),
    "MiniMax M3": ("MiniMax-M3",),
    "MiniMax M2.7": ("MiniMax-M2.7",),
    "MiniMax M2.5": (),
    "Qwen3.7 Max": ("Qwen3.7 Max",),
    "Qwen3.7 Plus": ("Qwen3.7 Plus",),
    "Qwen3.6 Plus": ("Qwen3.6 Plus",),
    "DeepSeek V4 Pro": (
        "DeepSeek V4 Pro (max)",
        "DeepSeek V4 Pro (high)",
        "DeepSeek V4 Pro",
    ),
    "DeepSeek V4 Flash": (
        "DeepSeek V4 Flash (max)",
        "DeepSeek V4 Flash (high)",
        "DeepSeek V4 Flash",
    ),
}

TIERED_LABELS = {
    "Qwen3.7 Plus (≤ 256K tokens)": ("Qwen3.7 Plus", False),
    "Qwen3.7 Plus (> 256K tokens)": ("Qwen3.7 Plus", True),
    "Qwen3.6 Plus (≤ 256K tokens)": ("Qwen3.6 Plus", False),
    "Qwen3.6 Plus (> 256K tokens)": ("Qwen3.6 Plus", True),
}


class PriceRow(TypedDict):
    source_label: str
    model: str
    input_price: Decimal
    output_price: Decimal
    cache_read_price: Decimal
    cache_write_price: Decimal | None
    monthly_usage: Decimal
    long_context: bool


class TableSnapshot(TypedDict):
    headers: list[str]
    rows: list[list[str]]


def normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


def select_pricing_snapshot(
    snapshots: list[TableSnapshot],
) -> tuple[list[str], list[list[str]]]:
    matches = [
        snapshot
        for snapshot in snapshots
        if [normalize_text(header) for header in snapshot["headers"]] == SOURCE_HEADERS
    ]
    if not matches:
        discovered = [
            [normalize_text(header) for header in snapshot["headers"]]
            for snapshot in snapshots
        ]
        raise RuntimeError(
            f"Could not find the OpenCode Go pricing table; found headers: {discovered}"
        )
    if len(matches) != 1:
        raise RuntimeError("Found multiple OpenCode Go pricing tables")
    match = matches[0]
    if not match["rows"]:
        raise RuntimeError("OpenCode Go pricing table has no data rows")
    for row_number, row in enumerate(match["rows"], start=1):
        if len(row) != len(match["headers"]):
            raise RuntimeError(
                f"OpenCode Go pricing row {row_number} has {len(row)} cells; "
                f"expected {len(match['headers'])}"
            )
    return match["headers"], match["rows"]


def parse_currency(
    value: str, *, field: str, source_label: str, allow_blank: bool = False
) -> Decimal | None:
    normalized = normalize_text(value)
    if allow_blank and normalized == "-":
        return None
    if not re.fullmatch(r"\$(?:\d+(?:\.\d*)?|\.\d+)", normalized):
        raise RuntimeError(
            f"Invalid OpenCode Go {field} for {source_label!r}: {value!r}"
        )
    try:
        parsed = Decimal(normalized[1:])
    except InvalidOperation as error:
        raise RuntimeError(
            f"Invalid OpenCode Go {field} for {source_label!r}: {value!r}"
        ) from error
    if not parsed.is_finite() or parsed < 0:
        raise RuntimeError(
            f"Invalid OpenCode Go {field} for {source_label!r}: {value!r}"
        )
    return parsed


def parse_source_rows(headers: list[str], rows: list[list[str]]) -> list[PriceRow]:
    normalized_headers = [normalize_text(header) for header in headers]
    if normalized_headers != SOURCE_HEADERS:
        raise RuntimeError(
            "OpenCode Go pricing table headers did not match the required columns"
        )
    if not rows:
        raise RuntimeError("OpenCode Go pricing table has no data rows")

    parsed_rows: list[PriceRow] = []
    seen_labels: set[str] = set()
    for row_number, cells in enumerate(rows, start=1):
        if len(cells) != len(SOURCE_HEADERS):
            raise RuntimeError(
                f"OpenCode Go pricing row {row_number} has {len(cells)} cells; "
                f"expected {len(SOURCE_HEADERS)}"
            )
        values = [normalize_text(cell) for cell in cells]
        source_label = values[0]
        if not source_label:
            raise RuntimeError(f"OpenCode Go pricing row {row_number} is missing Model")
        if source_label in seen_labels:
            raise RuntimeError(f"Duplicate OpenCode Go source label: {source_label}")
        seen_labels.add(source_label)
        for index, field in (
            (1, "Input"),
            (2, "Output"),
            (3, "Cached Read"),
            (5, "Usage"),
        ):
            if not values[index]:
                raise RuntimeError(f"OpenCode Go {source_label!r} is missing {field}")

        tier = TIERED_LABELS.get(source_label)
        if tier is None and re.search(
            r"\([^)]*\btokens\)$", source_label, re.IGNORECASE
        ):
            raise RuntimeError(
                f"Unrecognized OpenCode Go tiered source label: {source_label}"
            )
        model, long_context = tier if tier is not None else (source_label, False)
        input_price = parse_currency(
            values[1], field="Input", source_label=source_label
        )
        output_price = parse_currency(
            values[2], field="Output", source_label=source_label
        )
        cache_read_price = parse_currency(
            values[3], field="Cached Read", source_label=source_label
        )
        cache_write_price = parse_currency(
            values[4], field="Cached Write", source_label=source_label, allow_blank=True
        )
        monthly_usage = parse_currency(
            values[5], field="Usage", source_label=source_label
        )
        assert input_price is not None
        assert output_price is not None
        assert cache_read_price is not None
        assert monthly_usage is not None
        parsed_rows.append(
            {
                "source_label": source_label,
                "model": model,
                "input_price": input_price,
                "output_price": output_price,
                "cache_read_price": cache_read_price,
                "cache_write_price": cache_write_price,
                "monthly_usage": monthly_usage,
                "long_context": long_context,
            }
        )
    return parsed_rows


def decimal_text(value: Decimal | None) -> str:
    if value is None:
        return ""
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def collapse_price_rows(rows: list[PriceRow]) -> list[dict[str, str]]:
    grouped: dict[str, list[PriceRow]] = {}
    order: list[str] = []
    for row in rows:
        model = row["model"]
        if model not in grouped:
            grouped[model] = []
            order.append(model)
        grouped[model].append(row)

    output: list[dict[str, str]] = []
    for model in order:
        model_rows = grouped[model]
        is_tiered = model in {"Qwen3.7 Plus", "Qwen3.6 Plus"}
        if is_tiered:
            primary = [row for row in model_rows if not row["long_context"]]
            secondary = [row for row in model_rows if row["long_context"]]
            if len(primary) != 1 or len(secondary) != 1:
                labels = ", ".join(row["source_label"] for row in model_rows)
                raise RuntimeError(
                    f"OpenCode Go {model} requires both pricing tiers; found: {labels}"
                )
            primary_row, secondary_row = primary[0], secondary[0]
            if primary_row["monthly_usage"] != secondary_row["monthly_usage"]:
                raise RuntimeError(
                    f"OpenCode Go {model} pricing tiers have different Usage"
                )
        else:
            if len(model_rows) != 1:
                labels = ", ".join(row["source_label"] for row in model_rows)
                raise RuntimeError(f"Duplicate OpenCode Go model {model}: {labels}")
            primary_row = model_rows[0]
            secondary_row = None

        result = {column: "" for column in CSV_COLUMNS}
        result.update(
            {
                "model": model,
                "input_price_usd_per_1m_tokens": decimal_text(
                    primary_row["input_price"]
                ),
                "output_price_usd_per_1m_tokens": decimal_text(
                    primary_row["output_price"]
                ),
                "cache_read_usd_per_1m_tokens": decimal_text(
                    primary_row["cache_read_price"]
                ),
                "cache_write_usd_per_1m_tokens": decimal_text(
                    primary_row["cache_write_price"]
                ),
                "monthly_usage_usd": decimal_text(primary_row["monthly_usage"]),
            }
        )
        if secondary_row is not None:
            result.update(
                {
                    "long_context_threshold_tokens": "256000",
                    "long_context_input_price_usd_per_1m_tokens": decimal_text(
                        secondary_row["input_price"]
                    ),
                    "long_context_output_price_usd_per_1m_tokens": decimal_text(
                        secondary_row["output_price"]
                    ),
                    "long_context_cache_read_usd_per_1m_tokens": decimal_text(
                        secondary_row["cache_read_price"]
                    ),
                    "long_context_cache_write_usd_per_1m_tokens": decimal_text(
                        secondary_row["cache_write_price"]
                    ),
                }
            )
        output.append(result)
    return output


def read_aa_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        headers = reader.fieldnames or []
        required = {"model", "artificial_analysis_intelligence_index"}
        missing = sorted(required - set(headers))
        if missing:
            raise RuntimeError(
                "Artificial Analysis CSV is missing required headers: "
                + ", ".join(missing)
            )
        return list(reader)


def parse_intelligence_index(value: str | None) -> Decimal | None:
    normalized = normalize_text(value or "")
    if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)\*?", normalized):
        return None
    try:
        parsed = Decimal(normalized.removesuffix("*"))
    except InvalidOperation:
        return None
    return parsed if parsed.is_finite() else None


def select_aa_candidate(
    model: str, aa_rows: list[dict[str, str]]
) -> tuple[str, Decimal] | None:
    aliases = AA_MODEL_ALIASES.get(model, ())
    best: tuple[Decimal, int, int, str] | None = None
    for row_index, row in enumerate(aa_rows):
        display_name = row.get("model", "")
        if display_name not in aliases:
            continue
        value = parse_intelligence_index(
            row.get("artificial_analysis_intelligence_index")
        )
        if value is None:
            continue
        alias_index = aliases.index(display_name)
        candidate = (value, -alias_index, -row_index, display_name)
        if best is None or candidate[:3] > best[:3]:
            best = candidate
    return None if best is None else (best[3], best[0])


def blended_price(
    cache_read: Decimal, input_price: Decimal, output_price: Decimal
) -> Decimal:
    result = (
        Decimal(7) * cache_read + Decimal(2) * input_price + output_price
    ) / Decimal(10)
    if not result.is_finite() or result <= 0:
        raise RuntimeError(
            "OpenCode Go blended price must be finite and greater than zero"
        )
    return result


def enrich_rows(
    rows: list[dict[str, str]], aa_rows: list[dict[str, str]]
) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for source in rows:
        row = source.copy()
        primary_blend = blended_price(
            Decimal(row["cache_read_usd_per_1m_tokens"]),
            Decimal(row["input_price_usd_per_1m_tokens"]),
            Decimal(row["output_price_usd_per_1m_tokens"]),
        )
        row["opencode_go_blended_usd_per_1m_tokens"] = decimal_text(primary_blend)

        if row["long_context_threshold_tokens"]:
            long_blend = blended_price(
                Decimal(row["long_context_cache_read_usd_per_1m_tokens"]),
                Decimal(row["long_context_input_price_usd_per_1m_tokens"]),
                Decimal(row["long_context_output_price_usd_per_1m_tokens"]),
            )
            row["long_context_blended_usd_per_1m_tokens"] = decimal_text(long_blend)

        selected = select_aa_candidate(row["model"], aa_rows)
        if selected is not None:
            aa_model, intelligence = selected
            value = intelligence / primary_blend
            if not value.is_finite():
                raise RuntimeError(
                    f"OpenCode Go value score is not finite for {row['model']}"
                )
            row["artificial_analysis_model"] = aa_model
            row["artificial_analysis_intelligence_index"] = decimal_text(intelligence)
            row["value_score"] = decimal_text(value)
        output.append(row)
    return output


def validate_scraped_at(value: str) -> str:
    parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
        raise ValueError(
            "OpenCode Go scraped_at must use canonical YYYY-MM-DDTHH:MM:SSZ format"
        )
    return value


def current_scraped_at() -> str:
    return datetime.now(UTC).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_output_rows(
    headers: list[str],
    source_rows: list[list[str]],
    aa_rows: list[dict[str, str]],
    *,
    scraped_at: str,
) -> list[dict[str, str]]:
    validated_scraped_at = validate_scraped_at(scraped_at)
    rows = enrich_rows(
        collapse_price_rows(parse_source_rows(headers, source_rows)), aa_rows
    )
    for row in rows:
        row["scraped_at"] = validated_scraped_at
    return rows


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(
            output_file, fieldnames=CSV_COLUMNS, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


async def scrape_table(
    url: str, *, timeout_ms: int, headed: bool
) -> tuple[list[str], list[list[str]]]:
    from playwright.async_api import TimeoutError as PlaywrightTimeoutError
    from playwright.async_api import async_playwright

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=not headed)
        try:
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            try:
                await page.locator("table").first.wait_for(
                    state="visible", timeout=timeout_ms
                )
            except PlaywrightTimeoutError as error:
                raise RuntimeError(
                    "Could not find the OpenCode Go pricing table; found headers: []"
                ) from error
            snapshots = cast(
                list[TableSnapshot],
                await page.locator("table").evaluate_all(
                    """
                    (tables) => tables.map(table => ({
                      headers: Array.from(
                        table.querySelectorAll('thead tr:last-child th'),
                        cell => cell.textContent || ''
                      ),
                      rows: Array.from(table.querySelectorAll('tbody tr'), row =>
                        Array.from(row.cells, cell => cell.textContent || '')),
                    }))
                    """
                ),
            )
            return select_pricing_snapshot(snapshots)
        finally:
            await browser.close()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update OpenCode Go pricing and value data."
    )
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--csv", default=DEFAULT_CSV, type=Path)
    parser.add_argument("--aa-csv", default=DEFAULT_AA_CSV, type=Path)
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--timeout-ms", default=30_000, type=int)
    return parser.parse_args(argv)


async def async_main(args: argparse.Namespace) -> None:
    stage_count = 3
    print(f"[1/{stage_count}] Fetching OpenCode Go pricing...", flush=True)
    headers, source_rows = await scrape_table(
        args.url, timeout_ms=args.timeout_ms, headed=args.headed
    )
    scraped_at = current_scraped_at()
    print(f"      Found {len(source_rows)} source price rows.")

    print(f"[2/{stage_count}] Joining Artificial Analysis intelligence...", flush=True)
    aa_rows = read_aa_rows(args.aa_csv)
    output_rows = build_output_rows(
        headers, source_rows, aa_rows, scraped_at=scraped_at
    )

    print(f"[3/{stage_count}] Saving generated data...", flush=True)
    write_csv(output_rows, args.csv)
    print(f"      Wrote {len(output_rows)} canonical rows to {args.csv}.")

    print(f"[{stage_count}/{stage_count}] Update complete.")


def main() -> None:
    asyncio.run(async_main(parse_args()))


if __name__ == "__main__":
    main()
