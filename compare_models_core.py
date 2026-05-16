from __future__ import annotations

import csv
import json
import math
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from compare_models_template import HTML_TEMPLATE

DEFAULT_INPUT = Path("results.csv")
DEFAULT_OUTPUT = Path("index.html")
ParetoFlag = dict[str, bool]

DISPLAY_LABELS = {
    "model": "Model",
    "context_window_tokens": "Context Window",
    "creator": "Creator",
    "providers": "Providers",
    "license": "License",
    "artificial_analysis_intelligence_index": "Artificial Analysis Intelligence Index",
    "artificial_analysis_omniscience_index": "Artificial Analysis Omniscience Index",
    "gdpval_aa_pct": "GDPval-AA",
    "terminal_bench_hard_pct": "Terminal-Bench Hard",
    "tau2_bench_telecom_pct": "Tau2-Bench Telecom",
    "aa_lcr_pct": "AA-LCR",
    "aa_omniscience_accuracy_pct": "AA-Omniscience Accuracy",
    "aa_omniscience_non_hallucination_rate_pct": (
        "AA-Omniscience Non-Hallucination Rate"
    ),
    "humanitys_last_exam_pct": "Humanity's Last Exam",
    "gpqa_diamond_pct": "GPQA Diamond",
    "scicode_pct": "SciCode",
    "ifbench_pct": "IFBench",
    "critpt_pct": "CritPt",
    "apex_agents_aa_pct": "APEX-Agents-AA",
    "mmmu_pro_pct": "MMMU Pro",
    "blended_usd_per_1m_tokens": "Blended (USD/1M Tokens)",
    "input_price_usd_per_1m_tokens": "Input Price (USD/1M Tokens)",
    "output_price_usd_per_1m_tokens": "Output Price (USD/1M Tokens)",
    "median_tokens_per_second": "Median (Tokens/s)",
    "p5_tokens_per_second": "P5 (Tokens/s)",
    "p25_tokens_per_second": "P25 (Tokens/s)",
    "p75_tokens_per_second": "P75 (Tokens/s)",
    "p95_tokens_per_second": "P95 (Tokens/s)",
    "first_chunk_latency_seconds": "First Chunk Latency (s)",
    "first_answer_latency_seconds": "First Answer Latency (s)",
    "p5_first_chunk_latency_seconds": "P5 First Chunk Latency (s)",
    "p25_first_chunk_latency_seconds": "P25 First Chunk Latency (s)",
    "p75_first_chunk_latency_seconds": "P75 First Chunk Latency (s)",
    "p95_first_chunk_latency_seconds": "P95 First Chunk Latency (s)",
    "total_response_time_seconds": "Total Response Time (s)",
    "reasoning_time_seconds": "Reasoning Time (s)",
}

MAIN_COLUMNS = [
    ("model", "Model"),
    ("context_window_tokens", "Context Window"),
    ("creator", "Creator"),
    ("artificial_analysis_intelligence_index", "Intelligence"),
    ("blended_usd_per_1m_tokens", "Price"),
    ("median_tokens_per_second", "Speed"),
    ("first_chunk_latency_seconds", "Latency"),
    ("total_response_time_seconds", "End-to-End Response Time"),
]

ALIASES = {
    "model": "model",
    "context-window": "context_window_tokens",
    "context_window": "context_window_tokens",
    "creator": "creator",
    "intelligence": "artificial_analysis_intelligence_index",
    "aa-intelligence": "artificial_analysis_intelligence_index",
    "price": "blended_usd_per_1m_tokens",
    "blended-price": "blended_usd_per_1m_tokens",
    "speed": "median_tokens_per_second",
    "tokens-per-second": "median_tokens_per_second",
    "latency": "first_chunk_latency_seconds",
    "first-chunk-latency": "first_chunk_latency_seconds",
    "response-time": "total_response_time_seconds",
    "end-to-end-response-time": "total_response_time_seconds",
    "total-response-time": "total_response_time_seconds",
}

LOWER_IS_BETTER_MARKERS = ("price", "usd", "latency", "time")
FINAL_SCORE = "final_score"


@dataclass(frozen=True)
class Column:
    key: str
    label: str
    numeric: bool


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        if reader.fieldnames is None:
            raise ValueError(f"{path} does not contain a header row.")
        return list(reader.fieldnames), list(reader)


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        parsed = float(value)
    except ValueError:
        return None
    return parsed if math.isfinite(parsed) else None


def numeric_columns(headers: list[str], rows: list[dict[str, str]]) -> set[str]:
    numeric: set[str] = set()
    for header in headers:
        values = [parse_float(row.get(header)) for row in rows]
        if any(value is not None for value in values):
            numeric.add(header)
    return numeric


def normalize_name(name: str) -> str:
    return name.strip().lower().replace("_", "-").replace(" ", "-")


def resolve_category(category: str, headers: list[str]) -> str:
    stripped = category.strip()
    if stripped in headers:
        return stripped

    normalized = normalize_name(stripped)
    if normalized in ALIASES:
        return ALIASES[normalized]

    normalized_headers = {normalize_name(header): header for header in headers}
    if normalized in normalized_headers:
        return normalized_headers[normalized]

    raise ValueError(f"Unknown category: {category}")


def is_lower_better(column: str) -> bool:
    return any(marker in column for marker in LOWER_IS_BETTER_MARKERS)


def percentile_scores(values: list[float], lower_is_better: bool) -> list[float]:
    if len(values) == 1:
        return [100.0]

    sorted_pairs = sorted(enumerate(values), key=lambda item: item[1])
    raw_scores = [0.0] * len(values)
    index = 0
    while index < len(sorted_pairs):
        end = index + 1
        while (
            end < len(sorted_pairs)
            and sorted_pairs[end][1] == sorted_pairs[index][1]
        ):
            end += 1

        average_rank = (index + end - 1) / 2
        percentile = 100 * average_rank / (len(values) - 1)
        for original_index, _value in sorted_pairs[index:end]:
            raw_scores[original_index] = percentile
        index = end

    if lower_is_better:
        return [100 - score for score in raw_scores]
    return raw_scores


def score_rows(
    rows: list[dict[str, str]], categories: list[str]
) -> list[dict[str, Any]]:
    complete_rows: list[dict[str, Any]] = []
    parsed_values: dict[str, list[float]] = {category: [] for category in categories}

    for row in rows:
        parsed_row: dict[str, float] = {}
        for category in categories:
            value = parse_float(row.get(category))
            if value is None:
                break
            parsed_row[category] = value
        else:
            output_row: dict[str, Any] = dict(row)
            output_row["_raw_values"] = parsed_row
            complete_rows.append(output_row)

            for category, value in parsed_row.items():
                parsed_values[category].append(value)

    if not complete_rows:
        category_list = ", ".join(categories)
        raise ValueError(f"No rows have complete numeric data for: {category_list}")

    per_category_scores: dict[str, list[float]] = {}
    for category, values in parsed_values.items():
        per_category_scores[category] = percentile_scores(
            values, is_lower_better(category)
        )

    for row_index, row in enumerate(complete_rows):
        category_scores = {
            category: per_category_scores[category][row_index]
            for category in categories
        }
        scored_row = cast(dict[str, Any], row)
        scored_row[FINAL_SCORE] = round(statistics.fmean(category_scores.values()), 4)

    complete_rows.sort(key=lambda row: row[FINAL_SCORE], reverse=True)
    return complete_rows


def pareto_flags(rows: list[dict[str, Any]], categories: list[str]) -> list[ParetoFlag]:
    flags: list[ParetoFlag] = []
    for row in rows:
        row_values = cast(dict[str, float], row["_raw_values"])
        optimal = True
        suboptimal = True

        for other in rows:
            if other is row:
                continue
            other_values = cast(dict[str, float], other["_raw_values"])
            if dominates(other_values, row_values, categories, better=True):
                optimal = False
            if dominates(other_values, row_values, categories, better=False):
                suboptimal = False

        flags.append({"optimal": optimal, "suboptimal": suboptimal})
    return flags


def dominates(
    challenger: dict[str, float],
    target: dict[str, float],
    categories: list[str],
    *,
    better: bool,
) -> bool:
    at_least_all = True
    strict_one = False
    for category in categories:
        challenger_value = challenger[category]
        target_value = target[category]
        lower_better = is_lower_better(category)

        if better:
            at_least = (
                challenger_value <= target_value
                if lower_better
                else challenger_value >= target_value
            )
            strict = (
                challenger_value < target_value
                if lower_better
                else challenger_value > target_value
            )
        else:
            at_least = (
                challenger_value >= target_value
                if lower_better
                else challenger_value <= target_value
            )
            strict = (
                challenger_value > target_value
                if lower_better
                else challenger_value < target_value
            )

        at_least_all = at_least_all and at_least
        strict_one = strict_one or strict

    return at_least_all and strict_one


def table_columns(
    headers: list[str], numeric: set[str], all_columns: bool
) -> list[Column]:
    columns = (
        [(header, DISPLAY_LABELS.get(header, header)) for header in headers]
        if all_columns
        else MAIN_COLUMNS
    )
    result = [Column(key, label, key in numeric) for key, label in columns]
    result.append(Column(FINAL_SCORE, "Final Score", True))
    return result


def format_value(key: str, value: Any) -> str:
    if key == FINAL_SCORE:
        return f"{float(value):.2f}"

    parsed = parse_float(str(value)) if value is not None else None
    if parsed is None:
        return "" if value is None else str(value)

    if key == "context_window_tokens":
        return f"{int(parsed):,}"
    if key.endswith("_pct") or key.endswith("_index"):
        return f"{parsed:g}"
    if "usd" in key:
        return f"{parsed:.2f}"
    if "seconds" in key:
        return f"{parsed:.2f}"
    if "tokens_per_second" in key:
        return f"{parsed:g}"
    return f"{parsed:g}"


def json_ready_rows(
    rows: list[dict[str, Any]],
    columns: list[Column],
    graph_categories: list[str],
    pareto: list[ParetoFlag],
) -> list[dict[str, Any]]:
    output = []
    default_flag = {"optimal": False, "suboptimal": False}
    for row_index, row in enumerate(rows):
        cells = {}
        for column in columns:
            raw_value = row.get(column.key)
            numeric_value = (
                float(raw_value)
                if column.key == FINAL_SCORE and raw_value is not None
                else parse_float(str(raw_value))
            )
            cells[column.key] = {
                "display": format_value(column.key, raw_value),
                "sort": (
                    numeric_value
                    if numeric_value is not None
                    else str(raw_value or "")
                ),
            }

        raw_values = cast(dict[str, float], row["_raw_values"])
        output.append(
            {
                "model": row["model"],
                "score": row[FINAL_SCORE],
                "cells": cells,
                "graph": {
                    category: raw_values[category] for category in graph_categories
                },
                "pareto": (
                    pareto[row_index] if row_index < len(pareto) else default_flag
                ),
            }
        )
    return output


def write_html(
    output_path: Path,
    rows: list[dict[str, Any]],
    columns: list[Column],
    categories: list[str],
    pareto: list[ParetoFlag],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    graph_categories = categories if len(categories) in {2, 3} else []
    payload = {
        "columns": [
            {"key": column.key, "label": column.label, "numeric": column.numeric}
            for column in columns
        ],
        "rows": json_ready_rows(rows, columns, graph_categories, pareto),
        "categories": [
            {
                "key": category,
                "label": DISPLAY_LABELS.get(category, category),
                "lowerIsBetter": is_lower_better(category),
            }
            for category in categories
        ],
        "graphCategories": graph_categories,
    }

    payload_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    html = HTML_TEMPLATE.replace("__PAYLOAD__", payload_json)
    output_path.write_text(html, encoding="utf-8", newline="\n")


def list_categories(headers: list[str], rows: list[dict[str, str]]) -> None:
    numeric = numeric_columns(headers, rows)
    print("Numeric scoring categories:")
    for header in headers:
        if header in numeric:
            direction = (
                "lower is better" if is_lower_better(header) else "higher is better"
            )
            print(f"  {header} ({direction})")
    print("\nAliases:")
    for alias, header in sorted(ALIASES.items()):
        if header in headers:
            print(f"  {alias} -> {header}")
