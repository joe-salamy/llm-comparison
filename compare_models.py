from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_INPUT = Path("data/results.csv")
DEFAULT_OUTPUT = Path("model_comparison.html")

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
    "aa_omniscience_non_hallucination_rate_pct": "AA-Omniscience Non-Hallucination Rate",
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Rank LLMs from data/results.csv across one or more categories and "
            "write an interactive HTML comparison report to the repository root."
        )
    )
    parser.add_argument(
        "categories",
        nargs="*",
        help=(
            "Scoring categories. Use CSV column names or aliases such as "
            "intelligence, price, speed, latency, and response-time."
        ),
    )
    parser.add_argument("--input", default=DEFAULT_INPUT, type=Path)
    parser.add_argument("--output", default=DEFAULT_OUTPUT, type=Path)
    parser.add_argument(
        "--all-columns",
        action="store_true",
        help="Include all CSV columns in the final table instead of the main columns.",
    )
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="List available numeric scoring categories and aliases, then exit.",
    )
    return parser.parse_args()


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        if reader.fieldnames is None:
            raise ValueError(f"{path} does not contain a header row.")
        return reader.fieldnames, list(reader)


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
        while end < len(sorted_pairs) and sorted_pairs[end][1] == sorted_pairs[index][1]:
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
) -> tuple[list[dict[str, Any]], dict[str, dict[str, float]]]:
    complete_rows: list[dict[str, Any]] = []
    parsed_values: dict[str, list[float]] = {category: [] for category in categories}

    for row in rows:
        parsed_row = {category: parse_float(row.get(category)) for category in categories}
        if any(value is None for value in parsed_row.values()):
            continue

        output_row: dict[str, Any] = dict(row)
        output_row["_raw_values"] = parsed_row
        complete_rows.append(output_row)
        for category, value in parsed_row.items():
            parsed_values[category].append(float(value))

    if not complete_rows:
        category_list = ", ".join(categories)
        raise ValueError(f"No rows have complete numeric data for: {category_list}")

    per_category_scores: dict[str, list[float]] = {}
    for category, values in parsed_values.items():
        per_category_scores[category] = percentile_scores(values, is_lower_better(category))

    row_category_scores: dict[str, dict[str, float]] = {}
    for row_index, row in enumerate(complete_rows):
        category_scores = {
            category: per_category_scores[category][row_index] for category in categories
        }
        row[FINAL_SCORE] = round(statistics.fmean(category_scores.values()), 4)
        row_category_scores[row["model"]] = category_scores

    complete_rows.sort(key=lambda row: row[FINAL_SCORE], reverse=True)
    return complete_rows, row_category_scores


def pareto_flags(
    rows: list[dict[str, Any]], categories: list[str]
) -> dict[str, dict[str, bool]]:
    flags = {}
    for row in rows:
        row_values = row["_raw_values"]
        optimal = True
        suboptimal = True

        for other in rows:
            if other is row:
                continue
            other_values = other["_raw_values"]
            if dominates(other_values, row_values, categories, better=True):
                optimal = False
            if dominates(other_values, row_values, categories, better=False):
                suboptimal = False

        flags[row["model"]] = {"optimal": optimal, "suboptimal": suboptimal}
    return flags


def dominates(
    challenger: dict[str, float | None],
    target: dict[str, float | None],
    categories: list[str],
    *,
    better: bool,
) -> bool:
    at_least_all = True
    strict_one = False
    for category in categories:
        challenger_value = float(challenger[category])
        target_value = float(target[category])
        lower_better = is_lower_better(category)

        if better:
            at_least = challenger_value <= target_value if lower_better else challenger_value >= target_value
            strict = challenger_value < target_value if lower_better else challenger_value > target_value
        else:
            at_least = challenger_value >= target_value if lower_better else challenger_value <= target_value
            strict = challenger_value > target_value if lower_better else challenger_value < target_value

        at_least_all = at_least_all and at_least
        strict_one = strict_one or strict

    return at_least_all and strict_one


def table_columns(headers: list[str], numeric: set[str], all_columns: bool) -> list[Column]:
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
    pareto: dict[str, dict[str, bool]],
) -> list[dict[str, Any]]:
    output = []
    for row in rows:
        cells = {}
        for column in columns:
            raw_value = row.get(column.key)
            numeric_value = float(raw_value) if column.key == FINAL_SCORE else parse_float(str(raw_value))
            cells[column.key] = {
                "display": format_value(column.key, raw_value),
                "sort": numeric_value if numeric_value is not None else str(raw_value or ""),
            }

        output.append(
            {
                "model": row["model"],
                "score": row[FINAL_SCORE],
                "cells": cells,
                "graph": {category: row["_raw_values"][category] for category in graph_categories},
                "pareto": pareto.get(row["model"], {"optimal": False, "suboptimal": False}),
            }
        )
    return output


def write_html(
    output_path: Path,
    rows: list[dict[str, Any]],
    columns: list[Column],
    categories: list[str],
    pareto: dict[str, dict[str, bool]],
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

    html = HTML_TEMPLATE.replace("__PAYLOAD__", json.dumps(payload, ensure_ascii=False))
    output_path.write_text(html, encoding="utf-8", newline="\n")


def list_categories(headers: list[str], rows: list[dict[str, str]]) -> None:
    numeric = numeric_columns(headers, rows)
    print("Numeric scoring categories:")
    for header in headers:
        if header in numeric:
            direction = "lower is better" if is_lower_better(header) else "higher is better"
            print(f"  {header} ({direction})")
    print("\nAliases:")
    for alias, header in sorted(ALIASES.items()):
        if header in headers:
            print(f"  {alias} -> {header}")


def main() -> None:
    args = parse_args()
    headers, rows = read_rows(args.input)

    if args.list_categories:
        list_categories(headers, rows)
        return

    if not args.categories:
        raise SystemExit("At least one scoring category is required.")

    numeric = numeric_columns(headers, rows)
    categories = [resolve_category(category, headers) for category in args.categories]
    invalid = [category for category in categories if category not in numeric]
    if invalid:
        invalid_list = ", ".join(invalid)
        raise SystemExit(f"Scoring categories must be numeric: {invalid_list}")

    scored_rows, _category_scores = score_rows(rows, categories)
    pareto = pareto_flags(scored_rows, categories) if len(categories) in {2, 3} else {}
    columns = table_columns(headers, numeric | {FINAL_SCORE}, args.all_columns)
    write_html(args.output, scored_rows, columns, categories, pareto)

    print(f"Wrote {len(scored_rows)} ranked rows to {args.output}")


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>LLM Comparison</title>
  <style>
    :root {
      --bg: #f6f7f4;
      --ink: #1c1f1d;
      --muted: #5d655f;
      --line: #d5d9d2;
      --panel: #ffffff;
      --green: #00a854;
      --red: #e03131;
      --blue: #275c8f;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 14px;
      line-height: 1.4;
    }
    main {
      width: min(1500px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 24px 0 40px;
    }
    header {
      display: flex;
      justify-content: space-between;
      align-items: end;
      gap: 18px;
      margin-bottom: 16px;
    }
    h1 {
      margin: 0 0 4px;
      font-size: 24px;
      font-weight: 720;
      letter-spacing: 0;
    }
    .meta {
      color: var(--muted);
      font-size: 13px;
    }
    .chart-wrap {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      margin-bottom: 16px;
      padding: 14px;
    }
    .chart-title {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 10px;
      color: var(--muted);
      font-size: 13px;
    }
    .chart-actions {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-left: auto;
    }
    .chart-button {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #f7f8f5;
      color: var(--text);
      cursor: pointer;
      font: inherit;
      font-size: 12px;
      font-weight: 650;
      padding: 5px 9px;
    }
    .chart-button:hover {
      background: #eef0ec;
    }
    .chart-canvas-wrap {
      position: relative;
    }
    .view-cube {
      position: absolute;
      top: 12px;
      right: 12px;
      z-index: 3;
      display: grid;
      grid-template-columns: repeat(3, 42px);
      grid-template-rows: repeat(3, 34px);
      gap: 3px;
      padding: 6px;
      border: 1px solid rgba(116, 125, 117, 0.42);
      border-radius: 7px;
      background: rgba(247, 248, 245, 0.90);
      box-shadow: 0 10px 28px rgba(28, 31, 29, 0.12);
      -webkit-backdrop-filter: blur(8px);
      backdrop-filter: blur(8px);
    }
    .view-cube[hidden] {
      display: none;
    }
    .view-cube button {
      min-width: 0;
      border: 1px solid rgba(116, 125, 117, 0.42);
      border-radius: 5px;
      background: #ffffff;
      color: #2f3831;
      cursor: pointer;
      font: inherit;
      font-size: 10px;
      font-weight: 720;
      line-height: 1;
      padding: 0;
    }
    .view-cube button:hover,
    .view-cube button:focus-visible {
      background: #eef0ec;
      border-color: #747d75;
      outline: none;
    }
    .view-cube button.active {
      background: #2f3831;
      color: #ffffff;
      border-color: #2f3831;
    }
    .view-cube button.active:hover,
    .view-cube button.active:focus-visible {
      background: #445047;
      border-color: #445047;
    }
    .legend {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }
    .legend span {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
    }
    .dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      display: inline-block;
    }
    .dot.green { background: var(--green); }
    .dot.red { background: var(--red); }
    .dot.neutral { background: var(--blue); }
    .line-sample {
      width: 22px;
      height: 0;
      display: inline-block;
      border-top: 3px solid #8a5a00;
    }
    #chart {
      width: 100%;
      height: 560px;
      display: block;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fbfcfa;
    }
    .table-wrap {
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      max-height: calc(100vh - 48px);
    }
    table {
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      min-width: 980px;
    }
    th, td {
      padding: 9px 11px;
      border-bottom: 1px solid rgba(0, 0, 0, 0.08);
      text-align: left;
      vertical-align: middle;
      white-space: nowrap;
    }
    th {
      position: sticky;
      top: 0;
      z-index: 2;
      background: #eef0ec;
      color: #242824;
      font-size: 12px;
      font-weight: 720;
      cursor: pointer;
      -webkit-user-select: none;
      user-select: none;
      border-bottom: 1px solid var(--line);
    }
    th.numeric, td.numeric { text-align: right; }
    th.sort-active::after {
      content: attr(data-sort-mark);
      margin-left: 6px;
      color: var(--muted);
    }
    tbody tr:hover td {
      box-shadow: inset 0 0 0 9999px rgba(255, 255, 255, 0.18);
    }
    .tooltip {
      position: fixed;
      pointer-events: none;
      transform: translate(12px, 12px);
      background: rgba(28, 31, 29, 0.94);
      color: #fff;
      padding: 8px 10px;
      border-radius: 6px;
      font-size: 12px;
      max-width: 300px;
      z-index: 10;
      display: none;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    @media (max-width: 760px) {
      main { width: min(100vw - 18px, 1500px); padding-top: 14px; }
      header { display: block; }
      h1 { font-size: 20px; }
      #chart { height: 440px; }
      th, td { padding: 8px; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>LLM Comparison</h1>
        <div class="meta" id="summary"></div>
      </div>
      <div class="meta">Click column headers to sort.</div>
    </header>
    <section class="chart-wrap" id="chartSection" hidden>
      <div class="chart-title">
        <div id="chartTitle"></div>
        <div class="chart-actions">
          <button class="chart-button" id="resetCamera" type="button" hidden>Reset view</button>
          <div class="legend">
            <span><i class="dot green"></i>Pareto optimal</span>
            <span><i class="dot red"></i>Pareto suboptimal</span>
            <span><i class="dot neutral"></i>Other</span>
            <span><i class="line-sample"></i>Linear trend</span>
          </div>
        </div>
      </div>
      <div class="chart-canvas-wrap">
        <canvas id="chart"></canvas>
        <div class="view-cube" id="viewCube" aria-label="3D view controls" hidden>
          <button type="button" data-view="top" title="Top view">Top</button>
          <button type="button" data-view="isometric" title="Isometric view">Iso</button>
          <button type="button" data-view="back" title="Back view">Back</button>
          <button type="button" data-view="left" title="Left view">Left</button>
          <button type="button" data-view="front" title="Front view">Front</button>
          <button type="button" data-view="right" title="Right view">Right</button>
          <span></span>
          <button type="button" data-view="bottom" title="Bottom view">Bottom</button>
          <span></span>
        </div>
      </div>
    </section>
    <div class="table-wrap">
      <table id="resultsTable"></table>
    </div>
  </main>
  <div class="tooltip" id="tooltip"></div>
  <script>
    const payload = __PAYLOAD__;
    let rows = payload.rows.slice();
    let sortState = { key: "final_score", direction: "desc" };

    const scoreValues = rows.map(row => row.score).sort((a, b) => a - b);
    const minScore = scoreValues[0] ?? 0;
    const maxScore = scoreValues[scoreValues.length - 1] ?? 100;
    const medianScore = scoreValues.length
      ? scoreValues[Math.floor((scoreValues.length - 1) / 2)]
      : 50;

    document.getElementById("summary").textContent =
      `${rows.length} models ranked by ${payload.categories.map(c => c.label).join(", ")}`;

    function interpolate(a, b, t) {
      return Math.round(a + (b - a) * Math.max(0, Math.min(1, t)));
    }

    function rowColor(score) {
      if (Math.abs(maxScore - minScore) < 0.0001) return "rgb(255,255,255)";
      const red = [118, 29, 29];
      const white = [255, 255, 255];
      const green = [11, 93, 42];
      const lowSpan = Math.max(0.0001, medianScore - minScore);
      const highSpan = Math.max(0.0001, maxScore - medianScore);
      const t = score <= medianScore
        ? (score - minScore) / lowSpan
        : (score - medianScore) / highSpan;
      const from = score <= medianScore ? red : white;
      const to = score <= medianScore ? white : green;
      const color = [
        interpolate(from[0], to[0], t),
        interpolate(from[1], to[1], t),
        interpolate(from[2], to[2], t),
      ];
      return `rgb(${color.join(",")})`;
    }

    function textColor(score) {
      const color = rowColor(score).match(/\d+/g).map(Number);
      const luminance = (0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]) / 255;
      return luminance < 0.48 ? "#fff" : "#151815";
    }

    function compareValues(a, b, numeric) {
      if (numeric) return Number(a) - Number(b);
      return String(a).localeCompare(String(b), undefined, { numeric: true, sensitivity: "base" });
    }

    function sortRows(key) {
      const column = payload.columns.find(item => item.key === key);
      if (sortState.key === key) {
        sortState.direction = sortState.direction === "desc" ? "asc" : "desc";
      } else {
        sortState = { key, direction: "desc" };
      }
      rows.sort((left, right) => {
        const result = compareValues(left.cells[key].sort, right.cells[key].sort, column.numeric);
        return sortState.direction === "asc" ? result : -result;
      });
      renderTable();
    }

    function renderTable() {
      const table = document.getElementById("resultsTable");
      table.innerHTML = "";

      const thead = document.createElement("thead");
      const headerRow = document.createElement("tr");
      for (const column of payload.columns) {
        const th = document.createElement("th");
        th.textContent = column.label;
        th.className = column.numeric ? "numeric" : "";
        th.dataset.sortMark = sortState.direction === "desc" ? "↓" : "↑";
        if (sortState.key === column.key) th.classList.add("sort-active");
        th.addEventListener("click", () => sortRows(column.key));
        headerRow.appendChild(th);
      }
      thead.appendChild(headerRow);
      table.appendChild(thead);

      const tbody = document.createElement("tbody");
      for (const row of rows) {
        const tr = document.createElement("tr");
        tr.style.background = rowColor(row.score);
        tr.style.color = textColor(row.score);
        for (const column of payload.columns) {
          const td = document.createElement("td");
          td.textContent = row.cells[column.key].display;
          if (column.numeric) td.className = "numeric";
          tr.appendChild(td);
        }
        tbody.appendChild(tr);
      }
      table.appendChild(tbody);
    }

    function pointColor(row) {
      if (row.pareto.optimal) return "#00a854";
      if (row.pareto.suboptimal) return "#e03131";
      return "#275c8f";
    }

    function setupCanvas() {
      const canvas = document.getElementById("chart");
      const ratio = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = Math.max(1, Math.floor(rect.width * ratio));
      canvas.height = Math.max(1, Math.floor(rect.height * ratio));
      const ctx = canvas.getContext("2d");
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
      return { canvas, ctx, width: rect.width, height: rect.height };
    }

    function niceNumber(value, round) {
      if (!Number.isFinite(value) || value <= 0) return 1;
      const exponent = Math.floor(Math.log10(value));
      const fraction = value / 10 ** exponent;
      let niceFraction;
      if (round) {
        if (fraction < 1.5) niceFraction = 1;
        else if (fraction < 3) niceFraction = 2;
        else if (fraction < 7) niceFraction = 5;
        else niceFraction = 10;
      } else if (fraction <= 1) niceFraction = 1;
      else if (fraction <= 2) niceFraction = 2;
      else if (fraction <= 5) niceFraction = 5;
      else niceFraction = 10;
      return niceFraction * 10 ** exponent;
    }

    function metricRange(category) {
      const values = payload.rows.map(row => row.graph[category.key]);
      const min = Math.min(...values);
      const max = Math.max(...values);
      const rawSpan = Math.max(0.0001, max - min);
      const paddedMin = min - rawSpan * 0.1;
      const paddedMax = max + rawSpan * 0.1;
      const tickStep = niceNumber((paddedMax - paddedMin) / 5, true);
      const rangeMin = Math.floor(paddedMin / tickStep) * tickStep;
      const rangeMax = Math.ceil(paddedMax / tickStep) * tickStep;
      return { min: rangeMin, max: rangeMax, span: Math.max(0.0001, rangeMax - rangeMin) };
    }

    function formatTick(value) {
      const absolute = Math.abs(value);
      if (absolute >= 1000) return value.toLocaleString(undefined, { maximumFractionDigits: 0 });
      if (absolute >= 100) return value.toLocaleString(undefined, { maximumFractionDigits: 1 });
      if (absolute >= 10) return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
      return value.toLocaleString(undefined, { maximumFractionDigits: 3 });
    }

    function normalizedMetric(row, category, range) {
      return (row.graph[category.key] - range.min) / range.span;
    }

    function clamped(value, min, max) {
      return Math.max(min, Math.min(max, value));
    }

    function labelBoundsFor(ctx, text, x, y, padding = 3, maxWidth = Infinity) {
      const metrics = ctx.measureText(text);
      const textWidth = Math.min(metrics.width, maxWidth);
      const actualTop = metrics.actualBoundingBoxAscent || 10;
      const actualBottom = metrics.actualBoundingBoxDescent || 3;
      const align = ctx.textAlign || "left";
      let left = x;
      if (align === "center") left = x - textWidth / 2;
      else if (align === "right" || align === "end") left = x - textWidth;
      return {
        left: left - padding,
        right: left + textWidth + padding,
        top: y - actualTop - padding,
        bottom: y + actualBottom + padding,
      };
    }

    function expandedRect(rect, amount) {
      return {
        left: rect.left - amount,
        right: rect.right + amount,
        top: rect.top - amount,
        bottom: rect.bottom + amount,
      };
    }

    function rectsIntersect(a, b) {
      return a.left <= b.right && a.right >= b.left && a.top <= b.bottom && a.bottom >= b.top;
    }

    function pointInRect(point, rect) {
      return point.x >= rect.left && point.x <= rect.right && point.y >= rect.top && point.y <= rect.bottom;
    }

    function orientation(a, b, c) {
      const value = (b.y - a.y) * (c.x - b.x) - (b.x - a.x) * (c.y - b.y);
      if (Math.abs(value) < 0.000001) return 0;
      return value > 0 ? 1 : 2;
    }

    function segmentIntersects(a, b, c, d) {
      const o1 = orientation(a, b, c);
      const o2 = orientation(a, b, d);
      const o3 = orientation(c, d, a);
      const o4 = orientation(c, d, b);
      return o1 !== o2 && o3 !== o4;
    }

    function segmentIntersectsRect(segment, rect) {
      if (pointInRect(segment.start, rect) || pointInRect(segment.end, rect)) return true;
      const corners = [
        { x: rect.left, y: rect.top },
        { x: rect.right, y: rect.top },
        { x: rect.right, y: rect.bottom },
        { x: rect.left, y: rect.bottom },
      ];
      return corners.some((corner, index) => (
        segmentIntersects(segment.start, segment.end, corner, corners[(index + 1) % corners.length])
      ));
    }

    function placedContainedLabel(ctx, text, x, y, bounds, options = {}) {
      const padding = options.padding ?? 3;
      const maxWidth = Math.max(12, (options.maxWidth ?? bounds.right - bounds.left) - padding * 2);
      const labelWidth = Math.min(ctx.measureText(text).width, maxWidth);
      const candidates = options.candidates ?? [
        { dx: 8, dy: -8 },
        { dx: 8, dy: 18 },
        { dx: -labelWidth - 8, dy: -8 },
        { dx: -labelWidth - 8, dy: 18 },
        { dx: -labelWidth / 2, dy: -18 },
        { dx: -labelWidth / 2, dy: 28 },
        { dx: 14, dy: 4 },
        { dx: -labelWidth - 14, dy: 4 },
      ];

      let best = null;
      let bestScore = Infinity;
      for (const candidate of candidates) {
        let labelX = x + candidate.dx;
        let labelY = y + candidate.dy;
        const rawBounds = labelBoundsFor(ctx, text, labelX, labelY, padding, maxWidth);
        labelX += clamped(rawBounds.left, bounds.left, bounds.right) - rawBounds.left;
        labelX += clamped(rawBounds.right, bounds.left, bounds.right) - rawBounds.right;
        labelY += clamped(rawBounds.top, bounds.top, bounds.bottom) - rawBounds.top;
        labelY += clamped(rawBounds.bottom, bounds.top, bounds.bottom) - rawBounds.bottom;
        const labelBounds = labelBoundsFor(ctx, text, labelX, labelY, padding, maxWidth);
        const overlapCount = (options.occupied ?? []).filter(rect => (
          rectsIntersect(expandedRect(labelBounds, options.labelGap ?? 2), rect)
        )).length;
        const lineCount = (options.avoidSegments ?? []).filter(segment => (
          segmentIntersectsRect(segment, expandedRect(labelBounds, options.lineGap ?? 4))
        )).length;
        const displacement = Math.hypot(candidate.dx, candidate.dy);
        const score = overlapCount * 100000 + lineCount * 20000 + displacement;
        if (score < bestScore) {
          bestScore = score;
          best = { x: labelX, y: labelY, bounds: labelBounds, maxWidth };
          if (overlapCount === 0 && lineCount === 0) break;
        }
      }
      return best;
    }

    function drawContainedLabel(ctx, text, x, y, bounds, options = {}) {
      const label = placedContainedLabel(ctx, text, x, y, bounds, options);
      if (!label) return null;
      if (options.halo) {
        ctx.save();
        ctx.lineJoin = "round";
        ctx.lineWidth = options.haloWidth ?? 2;
        ctx.strokeStyle = options.haloColor ?? "rgba(246, 247, 244, 0.92)";
        ctx.strokeText(text, label.x, label.y, label.maxWidth);
        ctx.restore();
      }
      ctx.fillText(text, label.x, label.y, label.maxWidth);
      return label.bounds;
    }

    function drawLaidOutLabel(ctx, text, x, y, bounds, occupied, options = {}) {
      const labelBounds = drawContainedLabel(ctx, text, x, y, bounds, { ...options, occupied });
      if (labelBounds) occupied.push(labelBounds);
      return labelBounds;
    }

    function drawFixedContainedLabel(ctx, text, x, y, bounds, options = {}) {
      const padding = options.padding ?? 3;
      const maxWidth = Math.max(12, (options.maxWidth ?? bounds.right - bounds.left) - padding * 2);
      let labelX = x;
      let labelY = y;
      const labelBounds = labelBoundsFor(ctx, text, labelX, labelY, padding, maxWidth);
      labelX += clamped(labelBounds.left, bounds.left, bounds.right) - labelBounds.left;
      labelX += clamped(labelBounds.right, bounds.left, bounds.right) - labelBounds.right;
      labelY += clamped(labelBounds.top, bounds.top, bounds.bottom) - labelBounds.top;
      labelY += clamped(labelBounds.bottom, bounds.top, bounds.bottom) - labelBounds.bottom;
      ctx.fillText(text, labelX, labelY, maxWidth);
    }

    function fit2DTrend(rows, categories, ranges) {
      const points = rows.map(row => ({
        x: normalizedMetric(row, categories[0], ranges[0]),
        y: normalizedMetric(row, categories[1], ranges[1]),
      }));
      const count = points.length;
      if (count < 2) return null;

      const sumX = points.reduce((sum, point) => sum + point.x, 0);
      const sumY = points.reduce((sum, point) => sum + point.y, 0);
      const sumXX = points.reduce((sum, point) => sum + point.x * point.x, 0);
      const sumXY = points.reduce((sum, point) => sum + point.x * point.y, 0);
      const denominator = count * sumXX - sumX * sumX;
      if (Math.abs(denominator) < 0.000001) return null;

      const slope = (count * sumXY - sumX * sumY) / denominator;
      const intercept = (sumY - slope * sumX) / count;
      return { slope, intercept };
    }

    function solve3By3(matrix, vector) {
      const augmented = matrix.map((row, index) => [...row, vector[index]]);
      for (let pivot = 0; pivot < 3; pivot += 1) {
        let bestRow = pivot;
        for (let row = pivot + 1; row < 3; row += 1) {
          if (Math.abs(augmented[row][pivot]) > Math.abs(augmented[bestRow][pivot])) {
            bestRow = row;
          }
        }
        if (Math.abs(augmented[bestRow][pivot]) < 0.000001) return null;
        [augmented[pivot], augmented[bestRow]] = [augmented[bestRow], augmented[pivot]];

        const pivotValue = augmented[pivot][pivot];
        for (let column = pivot; column < 4; column += 1) {
          augmented[pivot][column] /= pivotValue;
        }
        for (let row = 0; row < 3; row += 1) {
          if (row === pivot) continue;
          const factor = augmented[row][pivot];
          for (let column = pivot; column < 4; column += 1) {
            augmented[row][column] -= factor * augmented[pivot][column];
          }
        }
      }
      return augmented.map(row => row[3]);
    }

    function fit3DTrend(rows, categories, ranges) {
      if (rows.length < 3) return null;
      let sumX = 0;
      let sumY = 0;
      let sumZ = 0;
      let sumXX = 0;
      let sumYY = 0;
      let sumXY = 0;
      let sumXZ = 0;
      let sumYZ = 0;

      for (const row of rows) {
        const x = normalizedMetric(row, categories[0], ranges[0]) * 2 - 1;
        const y = normalizedMetric(row, categories[1], ranges[1]) * 2 - 1;
        const z = normalizedMetric(row, categories[2], ranges[2]) * 2 - 1;
        sumX += x;
        sumY += y;
        sumZ += z;
        sumXX += x * x;
        sumYY += y * y;
        sumXY += x * y;
        sumXZ += x * z;
        sumYZ += y * z;
      }

      const coefficients = solve3By3(
        [
          [rows.length, sumX, sumY],
          [sumX, sumXX, sumXY],
          [sumY, sumXY, sumYY],
        ],
        [sumZ, sumXZ, sumYZ],
      );
      if (!coefficients) return null;
      const [intercept, xSlope, ySlope] = coefficients;
      return { intercept, xSlope, ySlope };
    }

    function drawGraph() {
      if (![2, 3].includes(payload.graphCategories.length)) return;
      document.getElementById("chartSection").hidden = false;
      document.getElementById("chartTitle").textContent =
        payload.graphCategories.length === 2 ? "2D category comparison" : "3D category comparison";
      document.getElementById("resetCamera").hidden = payload.graphCategories.length !== 3;
      document.getElementById("viewCube").hidden = payload.graphCategories.length !== 3;
      if (payload.graphCategories.length === 2) draw2D();
      else draw3D();
    }

    function draw2D() {
      const categories = payload.categories.slice(0, 2);
      const ranges = categories.map(metricRange);
      const trend = fit2DTrend(payload.rows, categories, ranges);
      let hover = null;
      const tooltip = document.getElementById("tooltip");

      function project(row, width, height) {
        const margins = { top: 54, right: 58, bottom: 74, left: 92 };
        const plotWidth = width - margins.left - margins.right;
        const plotHeight = height - margins.top - margins.bottom;
        const x = margins.left + ((row.graph[categories[0].key] - ranges[0].min) / ranges[0].span) * plotWidth;
        const y = height - margins.bottom - ((row.graph[categories[1].key] - ranges[1].min) / ranges[1].span) * plotHeight;
        return { x, y };
      }

      function render() {
        const { canvas, ctx, width, height } = setupCanvas();
        ctx.clearRect(0, 0, width, height);
        ctx.lineWidth = 1;
        ctx.font = "12px sans-serif";
        const margins = { top: 54, right: 58, bottom: 74, left: 92 };
        const plotLeft = margins.left;
        const plotRight = width - margins.right;
        const plotTop = margins.top;
        const plotBottom = height - margins.bottom;
        const plotWidth = plotRight - plotLeft;
        const plotHeight = plotBottom - plotTop;
        const minorTickCount = 20;
        const majorTickEvery = 4;

        ctx.fillStyle = "#4f5851";

        ctx.strokeStyle = "rgba(207, 212, 204, 0.38)";
        ctx.lineWidth = 0.75;
        for (let index = 0; index <= minorTickCount; index += 1) {
          if (index % majorTickEvery === 0) continue;
          const ratio = index / minorTickCount;
          const x = plotLeft + ratio * plotWidth;
          const y = plotBottom - ratio * plotHeight;
          ctx.beginPath();
          ctx.moveTo(x, plotTop);
          ctx.lineTo(x, plotBottom);
          ctx.moveTo(plotLeft, y);
          ctx.lineTo(plotRight, y);
          ctx.stroke();
        }

        ctx.strokeStyle = "rgba(164, 172, 164, 0.68)";
        ctx.lineWidth = 1;
        for (let index = 0; index <= minorTickCount; index += majorTickEvery) {
          const ratio = index / minorTickCount;
          const x = plotLeft + ratio * plotWidth;
          const y = plotBottom - ratio * plotHeight;
          const xValue = ranges[0].min + ratio * ranges[0].span;
          const yValue = ranges[1].min + ratio * ranges[1].span;

          ctx.beginPath();
          ctx.moveTo(x, plotTop);
          ctx.lineTo(x, plotBottom);
          ctx.moveTo(plotLeft, y);
          ctx.lineTo(plotRight, y);
          ctx.stroke();

          ctx.fillText(formatTick(xValue), x - 14, plotBottom + 22);
          ctx.textAlign = "right";
          ctx.fillText(formatTick(yValue), plotLeft - 12, y + 4);
          ctx.textAlign = "left";
        }

        ctx.strokeStyle = "#9ea79f";
        ctx.lineWidth = 2.25;
        ctx.beginPath();
        ctx.moveTo(plotLeft, plotTop);
        ctx.lineTo(plotLeft, plotBottom);
        ctx.lineTo(plotRight, plotBottom);
        ctx.stroke();
        ctx.fillStyle = "#2f3831";
        ctx.font = "700 16px sans-serif";
        drawFixedContainedLabel(
          ctx,
          `${categories[0].label}${categories[0].lowerIsBetter ? " (lower better)" : " (higher better)"}`,
          plotLeft,
          height - 24,
          { left: 6, right: width - 6, top: 6, bottom: height - 6 },
        );
        ctx.save();
        ctx.translate(24, plotBottom);
        ctx.rotate(-Math.PI / 2);
        ctx.fillText(`${categories[1].label}${categories[1].lowerIsBetter ? " (lower better)" : " (higher better)"}`, 0, 0);
        ctx.restore();

        let trendSegment = null;
        if (trend) {
          const start = { x: plotLeft, y: plotBottom - trend.intercept * plotHeight };
          const end = { x: plotRight, y: plotBottom - (trend.intercept + trend.slope) * plotHeight };
          trendSegment = { start, end };
          ctx.save();
          ctx.beginPath();
          ctx.rect(plotLeft, plotTop, plotWidth, plotHeight);
          ctx.clip();
          ctx.strokeStyle = "#8a5a00";
          ctx.lineWidth = 3;
          ctx.setLineDash([8, 5]);
          ctx.beginPath();
          ctx.moveTo(start.x, start.y);
          ctx.lineTo(end.x, end.y);
          ctx.stroke();
          ctx.restore();
        }

        const projected = payload.rows.map(row => ({ row, ...project(row, width, height) }));
        const modelLabelBounds = {
          left: plotLeft + 4,
          right: plotRight - 4,
          top: plotTop + 4,
          bottom: plotBottom - 4,
        };
        const occupiedLabels = [];
        for (const point of projected) {
          ctx.beginPath();
          ctx.fillStyle = pointColor(point.row);
          ctx.arc(point.x, point.y, point.row.pareto.optimal ? 5.5 : 4, 0, Math.PI * 2);
          ctx.fill();
        }
        for (const point of projected) {
          if (point.row.pareto.optimal || point.row.pareto.suboptimal) {
            ctx.fillStyle = point.row.pareto.suboptimal ? "#7a1717" : "#12351f";
            ctx.font = "700 12px sans-serif";
            drawLaidOutLabel(
              ctx,
              point.row.model,
              point.x,
              point.y,
              modelLabelBounds,
              occupiedLabels,
              {
                avoidSegments: trendSegment ? [trendSegment] : [],
                halo: true,
                haloWidth: 2,
                labelGap: 4,
                lineGap: 8,
              },
            );
          }
        }
        canvas._points = projected;
      }

      const canvas = document.getElementById("chart");
      canvas.addEventListener("mousemove", event => {
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const nearest = (canvas._points || []).reduce((best, point) => {
          const distance = Math.hypot(point.x - x, point.y - y);
          return distance < best.distance ? { point, distance } : best;
        }, { point: null, distance: Infinity });
        hover = nearest.distance < 12 ? nearest.point : null;
        if (hover) {
          tooltip.style.display = "block";
          tooltip.style.left = `${event.clientX}px`;
          tooltip.style.top = `${event.clientY}px`;
          tooltip.innerHTML = tooltipText(hover.row, categories);
        } else {
          tooltip.style.display = "none";
        }
      });
      canvas.addEventListener("mouseleave", () => {
        hover = null;
        tooltip.style.display = "none";
      });
      window.addEventListener("resize", render);
      render();
    }

    function draw3D() {
      const categories = payload.categories.slice(0, 3);
      const ranges = categories.map(metricRange);
      const trend = fit3DTrend(payload.rows, categories, ranges);
      const tooltip = document.getElementById("tooltip");
      const initialCamera = { rotationX: -0.62, rotationY: -2.36, zoom: 1 };
      const viewPresets = {
        front: { rotationX: 0, rotationY: 0, zoom: 1.1 },
        back: { rotationX: 0, rotationY: Math.PI, zoom: 1.1 },
        right: { rotationX: 0, rotationY: -Math.PI / 2, zoom: 1.1 },
        left: { rotationX: 0, rotationY: Math.PI / 2, zoom: 1.1 },
        top: { rotationX: -Math.PI / 2, rotationY: 0, zoom: 1.1 },
        bottom: { rotationX: Math.PI / 2, rotationY: 0, zoom: 1.1 },
        isometric: initialCamera,
      };
      let rotationX = initialCamera.rotationX;
      let rotationY = initialCamera.rotationY;
      let zoom = initialCamera.zoom;
      let dragging = false;
      let last = { x: 0, y: 0 };
      const viewCube = document.getElementById("viewCube");

      function norm(row, category, range) {
        return ((row.graph[category.key] - range.min) / range.span) * 2 - 1;
      }

      function setCamera(camera) {
        rotationX = camera.rotationX;
        rotationY = camera.rotationY;
        zoom = camera.zoom;
        render();
      }

      function normalizedAngleDifference(first, second) {
        return Math.atan2(Math.sin(first - second), Math.cos(first - second));
      }

      function cameraMatches(camera) {
        const tolerance = 0.015;
        return (
          Math.abs(rotationX - camera.rotationX) <= tolerance &&
          Math.abs(normalizedAngleDifference(rotationY, camera.rotationY)) <= tolerance
        );
      }

      function updateViewCubeActiveState() {
        for (const button of viewCube.querySelectorAll("button[data-view]")) {
          const preset = viewPresets[button.dataset.view];
          button.classList.toggle("active", Boolean(preset && cameraMatches(preset)));
        }
      }

      function rotate(point) {
        const cosY = Math.cos(rotationY);
        const sinY = Math.sin(rotationY);
        const cosX = Math.cos(rotationX);
        const sinX = Math.sin(rotationX);
        const x1 = point.x * cosY - point.z * sinY;
        const z1 = point.x * sinY + point.z * cosY;
        const y1 = point.y * cosX - z1 * sinX;
        const z2 = point.y * sinX + z1 * cosX;
        return { x: x1, y: y1, z: z2 };
      }

      function project(rotated, width, height) {
        const scale = Math.min(width, height) * 0.28 * zoom;
        const perspective = 1 / (1 + (rotated.z + 2.8) * 0.12);
        return {
          x: width / 2 + rotated.x * scale * perspective,
          y: height / 2 - rotated.y * scale * perspective,
          depth: rotated.z,
        };
      }

      function drawSegment(ctx, start, end, width, height) {
        const projectedStart = project(rotate(start), width, height);
        const projectedEnd = project(rotate(end), width, height);
        ctx.beginPath();
        ctx.moveTo(projectedStart.x, projectedStart.y);
        ctx.lineTo(projectedEnd.x, projectedEnd.y);
        ctx.stroke();
      }

      function projectPoint(point, width, height) {
        return project(rotate(point), width, height);
      }

      function axisTickPoint(axisIndex, value) {
        const point = { x: -1.05, y: -1.05, z: -1.05 };
        if (axisIndex === 0) point.x = value;
        if (axisIndex === 1) point.y = value;
        if (axisIndex === 2) point.z = value;
        return point;
      }

      function trendZ(x, y) {
        return trend.intercept + trend.xSlope * x + trend.ySlope * y;
      }

      function drawTrendPlane(ctx, width, height) {
        if (!trend) return;
        const gridCount = 8;
        const sampleCount = 28;
        const min = -1;
        const max = 1;

        ctx.save();
        ctx.strokeStyle = "#8a5a00";
        ctx.lineWidth = 2.25;
        ctx.globalAlpha = 0.72;
        ctx.setLineDash([8, 5]);

        function drawTrendPolyline(points) {
          let drawing = false;
          for (const point of points) {
            if (point.z < -1.12 || point.z > 1.12) {
              drawing = false;
              continue;
            }
            const projected = projectPoint(point, width, height);
            if (!drawing) {
              ctx.beginPath();
              ctx.moveTo(projected.x, projected.y);
              drawing = true;
            } else {
              ctx.lineTo(projected.x, projected.y);
            }
          }
          if (drawing) ctx.stroke();
        }

        for (let gridIndex = 0; gridIndex <= gridCount; gridIndex += 1) {
          const fixed = min + (gridIndex / gridCount) * (max - min);
          const xLine = [];
          const yLine = [];
          for (let sampleIndex = 0; sampleIndex <= sampleCount; sampleIndex += 1) {
            const moving = min + (sampleIndex / sampleCount) * (max - min);
            xLine.push({ x: fixed, y: moving, z: trendZ(fixed, moving) });
            yLine.push({ x: moving, y: fixed, z: trendZ(moving, fixed) });
          }
          drawTrendPolyline(xLine);
          drawTrendPolyline(yLine);
        }
        ctx.restore();
      }

      function render() {
        const { canvas, ctx, width, height } = setupCanvas();
        updateViewCubeActiveState();
        ctx.clearRect(0, 0, width, height);
        ctx.fillStyle = "#4f5851";
        ctx.font = "12px sans-serif";
        ctx.lineWidth = 1;

        const minorTickCount = 16;
        const majorTickEvery = 4;

        ctx.strokeStyle = "rgba(207, 212, 204, 0.30)";
        ctx.lineWidth = 0.75;
        for (let index = 0; index <= minorTickCount; index += 1) {
          if (index % majorTickEvery === 0) continue;
          const value = -1.05 + (index / minorTickCount) * 2.1;
          drawSegment(ctx, { x: value, y: -1.05, z: -1.05 }, { x: value, y: 1.05, z: -1.05 }, width, height);
          drawSegment(ctx, { x: value, y: -1.05, z: -1.05 }, { x: value, y: -1.05, z: 1.05 }, width, height);
          drawSegment(ctx, { x: -1.05, y: value, z: -1.05 }, { x: 1.05, y: value, z: -1.05 }, width, height);
          drawSegment(ctx, { x: -1.05, y: value, z: -1.05 }, { x: -1.05, y: value, z: 1.05 }, width, height);
          drawSegment(ctx, { x: -1.05, y: -1.05, z: value }, { x: 1.05, y: -1.05, z: value }, width, height);
          drawSegment(ctx, { x: -1.05, y: -1.05, z: value }, { x: -1.05, y: 1.05, z: value }, width, height);
        }

        ctx.strokeStyle = "rgba(164, 172, 164, 0.60)";
        ctx.lineWidth = 1;
        for (let index = 0; index <= minorTickCount; index += majorTickEvery) {
          const value = -1.05 + (index / minorTickCount) * 2.1;
          drawSegment(ctx, { x: value, y: -1.05, z: -1.05 }, { x: value, y: 1.05, z: -1.05 }, width, height);
          drawSegment(ctx, { x: value, y: -1.05, z: -1.05 }, { x: value, y: -1.05, z: 1.05 }, width, height);
          drawSegment(ctx, { x: -1.05, y: value, z: -1.05 }, { x: 1.05, y: value, z: -1.05 }, width, height);
          drawSegment(ctx, { x: -1.05, y: value, z: -1.05 }, { x: -1.05, y: value, z: 1.05 }, width, height);
          drawSegment(ctx, { x: -1.05, y: -1.05, z: value }, { x: 1.05, y: -1.05, z: value }, width, height);
          drawSegment(ctx, { x: -1.05, y: -1.05, z: value }, { x: -1.05, y: 1.05, z: value }, width, height);
        }

        const axes = [
          { end: { x: 1.25, y: -1.05, z: -1.05 }, label: categories[0], tickOffset: { x: -12, y: 18 } },
          { end: { x: -1.05, y: 1.25, z: -1.05 }, label: categories[1], tickOffset: { x: 8, y: 16 } },
          { end: { x: -1.05, y: -1.05, z: 1.25 }, label: categories[2], tickOffset: { x: 8, y: -8 } },
        ];
        const origin = projectPoint({ x: -1.05, y: -1.05, z: -1.05 }, width, height);
        ctx.strokeStyle = "#747d75";
        ctx.lineWidth = 2.6;
        ctx.fillStyle = "#2f3831";
        ctx.font = "700 16px sans-serif";
        for (const [axisIndex, axis] of axes.entries()) {
          const end = projectPoint(axis.end, width, height);
          ctx.beginPath();
          ctx.moveTo(origin.x, origin.y);
          ctx.lineTo(end.x, end.y);
          ctx.stroke();
          drawFixedContainedLabel(
            ctx,
            `${axis.label.label}${axis.label.lowerIsBetter ? " ↓" : " ↑"}`,
            end.x + 6,
            end.y + 4,
            { left: 6, right: width - 6, top: 6, bottom: height - 6 },
          );

          ctx.font = "11px sans-serif";
          ctx.fillStyle = "#4f5851";
          for (let index = 0; index <= minorTickCount; index += majorTickEvery) {
            const ratio = index / minorTickCount;
            const normalizedValue = -1 + ratio * 2;
            const tick = projectPoint(axisTickPoint(axisIndex, normalizedValue), width, height);
            const tickValue = ranges[axisIndex].min + ratio * ranges[axisIndex].span;
            drawFixedContainedLabel(
              ctx,
              formatTick(tickValue),
              tick.x + axis.tickOffset.x,
              tick.y + axis.tickOffset.y,
              { left: 6, right: width - 6, top: 6, bottom: height - 6 },
            );
          }
          ctx.font = "700 16px sans-serif";
          ctx.fillStyle = "#2f3831";
        }

        drawTrendPlane(ctx, width, height);

        const projected = payload.rows.map(row => {
          const point = {
            x: norm(row, categories[0], ranges[0]),
            y: norm(row, categories[1], ranges[1]),
            z: norm(row, categories[2], ranges[2]),
          };
          return { row, ...project(rotate(point), width, height) };
        }).sort((a, b) => a.depth - b.depth);

        for (const point of projected) {
          const radius = point.row.pareto.optimal ? 6 : 4.2;
          ctx.globalAlpha = point.row.pareto.suboptimal ? 0.78 : 0.92;
          ctx.beginPath();
          ctx.fillStyle = pointColor(point.row);
          ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
          ctx.fill();
          ctx.globalAlpha = 1;
        }
        const occupiedLabels = [];
        for (const point of projected) {
          if (!point.row.pareto.optimal && !point.row.pareto.suboptimal) continue;
          ctx.fillStyle = point.row.pareto.suboptimal ? "#7a1717" : "#12351f";
          ctx.font = "700 12px sans-serif";
          drawLaidOutLabel(
            ctx,
            point.row.model,
            point.x,
            point.y,
            { left: 8, right: width - 8, top: 8, bottom: height - 8 },
            occupiedLabels,
            { halo: true, haloWidth: 2, labelGap: 4 },
          );
        }
        canvas._points = projected;
      }

      const canvas = document.getElementById("chart");
      canvas.addEventListener("mousedown", event => {
        dragging = true;
        last = { x: event.clientX, y: event.clientY };
      });
      window.addEventListener("mouseup", () => dragging = false);
      window.addEventListener("mousemove", event => {
        if (dragging) {
          rotationY += (event.clientX - last.x) * 0.01;
          rotationX -= (event.clientY - last.y) * 0.01;
          rotationX = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, rotationX));
          last = { x: event.clientX, y: event.clientY };
          render();
          return;
        }
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const nearest = (canvas._points || []).reduce((best, point) => {
          const distance = Math.hypot(point.x - x, point.y - y);
          return distance < best.distance ? { point, distance } : best;
        }, { point: null, distance: Infinity });
        if (nearest.distance < 13) {
          tooltip.style.display = "block";
          tooltip.style.left = `${event.clientX}px`;
          tooltip.style.top = `${event.clientY}px`;
          tooltip.innerHTML = tooltipText(nearest.point.row, categories);
        } else {
          tooltip.style.display = "none";
        }
      });
      canvas.addEventListener("mouseleave", () => {
        tooltip.style.display = "none";
      });
      canvas.addEventListener("wheel", event => {
        event.preventDefault();
        zoom *= event.deltaY < 0 ? 1.08 : 0.92;
        zoom = Math.max(0.55, Math.min(8, zoom));
        render();
      }, { passive: false });
      document.getElementById("resetCamera").addEventListener("click", () => {
        setCamera(initialCamera);
      });
      viewCube.addEventListener("click", event => {
        const button = event.target.closest?.("button[data-view]");
        if (!button) return;
        const preset = viewPresets[button.dataset.view];
        if (preset) setCamera(preset);
      });
      window.addEventListener("resize", render);
      render();
    }

    function tooltipText(row, categories) {
      const lines = [`<strong>${escapeHtml(row.model)}</strong>`];
      for (const category of categories) {
        lines.push(`${escapeHtml(category.label)}: ${row.graph[category.key]}`);
      }
      lines.push(`Final Score: ${row.score.toFixed(2)}`);
      if (row.pareto.optimal) lines.push("Pareto optimal");
      if (row.pareto.suboptimal) lines.push("Pareto suboptimal");
      return lines.join("<br>");
    }

    function escapeHtml(value) {
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    renderTable();
    drawGraph();
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
