from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

DISPLAY_HEADERS = [
    "Model",
    "Context Window",
    "Creator",
    "Providers",
    "License",
    "Artificial Analysis Intelligence Index",
    "Artificial Analysis Omniscience Index",
    "GDPval-AA",
    "Terminal-Bench Hard",
    "Tau2-Bench Telecom",
    "AA-LCR",
    "AA-Omniscience Accuracy",
    "AA-Omniscience Non-Hallucination Rate",
    "Humanity's Last Exam",
    "GPQA Diamond",
    "SciCode",
    "IFBench",
    "CritPt",
    "APEX-Agents-AA",
    "MMMU Pro",
    "Blended (USD/1M Tokens)",
    "Input Price (USD/1M Tokens)",
    "Output Price (USD/1M Tokens)",
    "Median (Tokens/s)",
    "P5 (Tokens/s)",
    "P25 (Tokens/s)",
    "P75 (Tokens/s)",
    "P95 (Tokens/s)",
    "First Chunk Latency (s)",
    "First Answer Latency (s)",
    "P5 First Chunk Latency (s)",
    "P25 First Chunk Latency (s)",
    "P75 First Chunk Latency (s)",
    "P95 First Chunk Latency (s)",
    "Total Response Time (s)",
    "Reasoning Time (s)",
]

MAIN_DISPLAY_HEADERS = {
    "Model",
    "Context Window",
    "Creator",
    "Artificial Analysis Intelligence Index",
    "Blended (USD/1M Tokens)",
    "Median (Tokens/s)",
    "First Chunk Latency (s)",
    "Total Response Time (s)",
}

CSV_HEADERS = [
    "model",
    "context_window_tokens",
    "creator",
    "providers",
    "license",
    "artificial_analysis_intelligence_index",
    "artificial_analysis_omniscience_index",
    "gdpval_aa_pct",
    "terminal_bench_hard_pct",
    "tau2_bench_telecom_pct",
    "aa_lcr_pct",
    "aa_omniscience_accuracy_pct",
    "aa_omniscience_non_hallucination_rate_pct",
    "humanitys_last_exam_pct",
    "gpqa_diamond_pct",
    "scicode_pct",
    "ifbench_pct",
    "critpt_pct",
    "apex_agents_aa_pct",
    "mmmu_pro_pct",
    "blended_usd_per_1m_tokens",
    "input_price_usd_per_1m_tokens",
    "output_price_usd_per_1m_tokens",
    "median_tokens_per_second",
    "p5_tokens_per_second",
    "p25_tokens_per_second",
    "p75_tokens_per_second",
    "p95_tokens_per_second",
    "first_chunk_latency_seconds",
    "first_answer_latency_seconds",
    "p5_first_chunk_latency_seconds",
    "p25_first_chunk_latency_seconds",
    "p75_first_chunk_latency_seconds",
    "p95_first_chunk_latency_seconds",
    "total_response_time_seconds",
    "reasoning_time_seconds",
]


def parse_input(path: Path) -> list[list[str]]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    lines = [line for line in lines if line]

    try:
        start = lines.index("Further Analysis") + 1
    except ValueError as exc:
        raise ValueError(
            "Could not find the 'Further Analysis' marker before data rows."
        ) from exc

    rows: list[list[str]] = []
    current: list[str] = []
    index = start

    while index < len(lines):
        if (
            index + 1 < len(lines)
            and lines[index] == "Model"
            and lines[index + 1] == "Providers"
        ):
            if current:
                rows.append(current)
                current = []
            index += 2
            continue

        current.append(lines[index])
        index += 1

    if current:
        rows.append(current)

    expected_width = len(DISPLAY_HEADERS)
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

    return rows


def markdown_escape(value: str) -> str:
    return value.replace("|", "\\|")


def markdown_header(value: str) -> str:
    escaped = markdown_escape(value)
    return f"**{escaped}**" if value in MAIN_DISPLAY_HEADERS else escaped


def write_markdown(rows: list[list[str]], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as output:
        output.write("# LLM Comparison Results\n\n")
        output.write(
            "| "
            + " | ".join(markdown_header(header) for header in DISPLAY_HEADERS)
            + " |\n"
        )
        output.write("| " + " | ".join("---" for _ in DISPLAY_HEADERS) + " |\n")

        for row in rows:
            output.write(
                "| " + " | ".join(markdown_escape(cell) for cell in row) + " |\n"
            )


def parse_context_window(value: str) -> str:
    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)([kKmM])", value)
    if not match:
        return value

    number = float(match.group(1))
    multiplier = 1_000 if match.group(2).lower() == "k" else 1_000_000
    return str(int(number * multiplier))


def clean_csv_cell(value: str, column_index: int) -> str:
    value = value.strip().replace("−", "-")
    if value == "--":
        return ""

    if column_index == 1:
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


def write_csv(rows: list[list[str]], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(CSV_HEADERS)
        for row in rows:
            writer.writerow(
                [clean_csv_cell(cell, index) for index, cell in enumerate(row)]
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert copied Artificial Analysis leaderboard data into Markdown and CSV."
    )
    parser.add_argument("--input", default="input.txt", type=Path)
    parser.add_argument("--markdown", default="results.md", type=Path)
    parser.add_argument("--csv", default="results.csv", type=Path)
    args = parser.parse_args()

    rows = parse_input(args.input)
    write_markdown(rows, args.markdown)
    write_csv(rows, args.csv)
    print(f"Wrote {len(rows)} rows to {args.markdown} and {args.csv}")


if __name__ == "__main__":
    main()
