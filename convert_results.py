from __future__ import annotations

import argparse
import csv
import re
from datetime import date
from pathlib import Path

DEFAULT_INPUT = Path("input.txt")
DEFAULT_CSV = Path("results.csv")
DEFAULT_HTML = Path("index.html")
DEFAULT_TEMPLATE = Path("compare_models_template.py")

DISPLAY_TO_CSV: dict[str, str] = {
    "Model": "model",
    "Context Window": "context_window_tokens",
    "Creator": "creator",
    "Providers": "providers",
    "License": "license",
    "Artificial Analysis Intelligence Index": "artificial_analysis_intelligence_index",
    "Artificial Analysis Omniscience Index": "artificial_analysis_omniscience_index",
    "GDPval-AA": "gdpval_aa_pct",
    "Terminal-Bench Hard": "terminal_bench_hard_pct",
    "τ²-Bench Telecom": "tau2_bench_telecom_pct",
    "AA-LCR": "aa_lcr_pct",
    "AA-Omniscience Accuracy": "aa_omniscience_accuracy_pct",
    "AA-Omniscience Non-Hallucination Rate": (
        "aa_omniscience_non_hallucination_rate_pct"
    ),
    "Humanity's Last Exam": "humanitys_last_exam_pct",
    "GPQA Diamond": "gpqa_diamond_pct",
    "SciCode": "scicode_pct",
    "IFBench": "ifbench_pct",
    "CritPt": "critpt_pct",
    "APEX-Agents-AA": "apex_agents_aa_pct",
    "MMMU Pro": "mmmu_pro_pct",
    "Blended (USD/1M Tokens)": "blended_usd_per_1m_tokens",
    "Input Price (USD/1M Tokens)": "input_price_usd_per_1m_tokens",
    "Output Price (USD/1M Tokens)": "output_price_usd_per_1m_tokens",
    "Median (Tokens/s)": "median_tokens_per_second",
    "P5 (Tokens/s)": "p5_tokens_per_second",
    "P25 (Tokens/s)": "p25_tokens_per_second",
    "P75 (Tokens/s)": "p75_tokens_per_second",
    "P95 (Tokens/s)": "p95_tokens_per_second",
    "First Chunk Latency (s)": "first_chunk_latency_seconds",
    "First Answer Latency (s)": "first_answer_latency_seconds",
    "P5 First Chunk Latency (s)": "p5_first_chunk_latency_seconds",
    "P25 First Chunk Latency (s)": "p25_first_chunk_latency_seconds",
    "P75 First Chunk Latency (s)": "p75_first_chunk_latency_seconds",
    "P95 First Chunk Latency (s)": "p95_first_chunk_latency_seconds",
    "Total Response Time (s)": "total_response_time_seconds",
    "Reasoning Time (s)": "reasoning_time_seconds",
}


def parse_header_pairs(lines: list[str]) -> list[tuple[str, str]]:
    """Return (primary, secondary) header pairs from the input header block.

    The header block runs from the start of the file up to (but not including)
    the 'Further Analysis' marker. Column headers are entries of one or two
    non-empty lines separated by blank lines.
    """
    try:
        end = lines.index("Further Analysis")
    except ValueError as exc:
        raise ValueError(
            "Could not find the 'Further Analysis' marker before data rows."
        ) from exc

    header_block = lines[:end]
    try:
        start = header_block.index("Model")
    except ValueError as exc:
        raise ValueError(
            "Could not find the 'Model' column header in the header block."
        ) from exc

    entries: list[list[str]] = []
    current: list[str] = []
    for line in header_block[start:]:
        if line == "":
            if current:
                entries.append(current)
                current = []
            continue
        current.append(line)
    if current:
        entries.append(current)

    pairs: list[tuple[str, str]] = []
    for entry in entries:
        primary = entry[0]
        secondary = entry[1] if len(entry) > 1 else ""
        pairs.append((primary, secondary))

    return pairs


def build_display_header(primary: str, secondary: str) -> str:
    """Build a human-readable display header from an input header pair."""
    if primary == "Latency" and secondary == "First Chunk (s)":
        return "First Chunk Latency (s)"
    if primary in {"First Answer", "P5", "P25", "P75", "P95"}:
        if secondary == "First Chunk (s)":
            return f"{primary} First Chunk Latency (s)"
        if secondary == "(s)":
            return f"{primary} Latency (s)"
    if primary == "Total" and secondary == "Response (s)":
        return "Total Response Time (s)"
    if primary == "Reasoning" and secondary == "Time (s)":
        return "Reasoning Time (s)"
    if secondary in {"USD/1M Tokens", "Tokens/s"}:
        return f"{primary} ({secondary})"
    return primary


def to_csv_key(display_header: str) -> str:
    """Convert a display header to a CSV column key."""
    if display_header in DISPLAY_TO_CSV:
        return DISPLAY_TO_CSV[display_header]
    key = display_header.lower()
    key = re.sub(r"[^a-z0-9]+", "_", key)
    return key.strip("_")


def csv_headers_from_display_headers(display_headers: list[str]) -> list[str]:
    return [to_csv_key(header) for header in display_headers]


def dedupe_csv_headers(csv_headers: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    deduped: list[str] = []
    for header in csv_headers:
        count = seen.get(header, 0) + 1
        seen[header] = count
        deduped.append(header if count == 1 else f"{header}_{count}")
    return deduped


def parse_headers(lines: list[str]) -> tuple[list[str], list[str]]:
    pairs = parse_header_pairs(lines)
    display_headers = [
        build_display_header(primary, secondary)
        for primary, secondary in pairs
    ]
    csv_headers = csv_headers_from_display_headers(display_headers)
    return display_headers, csv_headers


def parse_input(path: Path) -> tuple[list[str], list[str], list[list[str]]]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    display_headers, csv_headers = parse_headers(lines)

    non_empty_lines = [line for line in lines if line]
    try:
        start = non_empty_lines.index("Further Analysis") + 1
    except ValueError as exc:
        raise ValueError(
            "Could not find the 'Further Analysis' marker before data rows."
        ) from exc

    rows: list[list[str]] = []
    current: list[str] = []
    index = start

    while index < len(non_empty_lines):
        if (
            index + 1 < len(non_empty_lines)
            and non_empty_lines[index] == "Model"
            and non_empty_lines[index + 1] == "Providers"
        ):
            if current:
                rows.append(current)
                current = []
            index += 2
            continue

        current.append(non_empty_lines[index])
        index += 1

    if current:
        rows.append(current)

    row_widths = [len(row) for row in rows]
    base_width = len(display_headers)
    if rows and all(width == base_width for width in row_widths):
        expected_width = base_width
    elif (
        rows
        and "Creator" in display_headers
        and all(width == base_width + 1 for width in row_widths)
    ):
        insert_at = display_headers.index("Creator") + 1
        display_headers.insert(insert_at, "Providers")
        csv_headers = csv_headers_from_display_headers(display_headers)
        expected_width = len(display_headers)
    else:
        bad_rows = [
            (row[0] if row else "<empty>", len(row))
            for row in rows
            if len(row) != base_width
        ]
        examples = ", ".join(f"{name}: {width}" for name, width in bad_rows[:5])
        raise ValueError(
            f"Expected {base_width} columns per row; mismatches: {examples}"
        )

    bad_rows = [
        (row[0] if row else "<empty>", len(row))
        for row in rows
        if len(row) != expected_width
    ]
    if bad_rows:
        examples = ", ".join(f"{name}: {width}" for name, width in bad_rows[:5])
        raise ValueError(
            f"Expected {expected_width} columns per row; mismatches: {examples}"
        )

    return display_headers, csv_headers, rows


def parse_context_window(value: str) -> str:
    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)([kKmM])", value)
    if not match:
        return value

    number = float(match.group(1))
    multiplier = 1_000 if match.group(2).lower() == "k" else 1_000_000
    return str(int(number * multiplier))


def clean_csv_cell(value: str, csv_header: str) -> str:
    value = value.strip().replace("−", "-")
    if value == "--":
        return ""

    if csv_header == "context_window_tokens":
        return parse_context_window(value)

    if value.startswith("$"):
        return value[1:].replace(",", "")

    if value.endswith("%"):
        return value[:-1]

    return (
        value.replace(",", "")
        if re.fullmatch(r"-?[0-9]+(?:\.[0-9]+)?", value.replace(",", ""))
        else value
    )


def write_csv(rows: list[list[str]], csv_headers: list[str], path: Path) -> None:
    final_headers = dedupe_csv_headers(csv_headers)
    expected_width = len(final_headers)
    bad_rows = [
        (index, len(row))
        for index, row in enumerate(rows, start=1)
        if len(row) != expected_width
    ]
    if bad_rows:
        examples = ", ".join(f"row {index}: {width}" for index, width in bad_rows[:5])
        raise ValueError(
            f"Expected {expected_width} columns per row before writing CSV; "
            f"mismatches: {examples}"
        )

    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(final_headers)
        for row in rows:
            writer.writerow(
                [
                    clean_csv_cell(cell, csv_header)
                    for cell, csv_header in zip(row, final_headers, strict=True)
                ]
            )


def write_table_csv(
    display_headers: list[str], rows: list[list[str]], path: Path
) -> list[str]:
    csv_headers = csv_headers_from_display_headers(display_headers)
    final_headers = dedupe_csv_headers(csv_headers)
    write_csv(rows, csv_headers, path)
    return final_headers


def format_display_date(uploaded_date: date) -> str:
    return f"{uploaded_date.strftime('%B')} {uploaded_date.day}, {uploaded_date.year}"


def update_upload_dates(paths: list[Path], uploaded_date: date) -> int:
    display_date = format_display_date(uploaded_date)
    replacements = (
        (
            re.compile(r"Data updated: [A-Z][a-z]+ [0-9]{1,2}, [0-9]{4}"),
            f"Data updated: {display_date}",
        ),
        (
            re.compile(r'const dataUpdated = "[A-Z][a-z]+ [0-9]{1,2}, [0-9]{4}"'),
            f'const dataUpdated = "{display_date}"',
        ),
    )

    updated_files = 0
    for path in paths:
        if not path.exists():
            continue

        original = path.read_text(encoding="utf-8")
        updated = original
        for pattern, replacement in replacements:
            updated = pattern.sub(replacement, updated)

        if updated != original:
            path.write_text(updated, encoding="utf-8", newline="\n")
            updated_files += 1

    return updated_files


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert copied Artificial Analysis leaderboard data into CSV."
    )
    parser.add_argument("--input", default=DEFAULT_INPUT, type=Path)
    parser.add_argument("--csv", default=DEFAULT_CSV, type=Path)
    parser.add_argument("--html", default=DEFAULT_HTML, type=Path)
    parser.add_argument("--template", default=DEFAULT_TEMPLATE, type=Path)
    parser.add_argument(
        "--uploaded-date",
        default=date.today(),
        type=date.fromisoformat,
        help="Data upload date in YYYY-MM-DD format. Defaults to today.",
    )
    args = parser.parse_args()

    _display_headers, csv_headers, rows = parse_input(args.input)
    write_csv(rows, csv_headers, args.csv)
    updated_files = update_upload_dates([args.template, args.html], args.uploaded_date)
    print(f"Wrote {len(rows)} rows to {args.csv}")
    print(f"Updated upload date in {updated_files} files")


if __name__ == "__main__":
    main()
