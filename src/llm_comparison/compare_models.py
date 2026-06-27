from __future__ import annotations

import argparse
from pathlib import Path

from .compare_models_core import (
    DEFAULT_INPUT,
    DEFAULT_OUTPUT,
    FINAL_SCORE,
    exclude_zero_price_rows,
    list_categories,
    numeric_columns,
    pareto_flags,
    read_rows,
    resolve_category,
    score_rows,
    table_columns,
    write_html,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Rank LLMs from data/results.csv across one or more categories and "
            "write an interactive HTML comparison report to public/index.html."
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
        "--exclude-zero-price",
        action="store_true",
        help=(
            "Exclude models whose blended price is 0 (promo/free tiers) "
            "from scoring and output."
        ),
    )
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="List available numeric scoring categories and aliases, then exit.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    headers, rows = read_rows(args.input)

    if args.list_categories:
        list_categories(headers, rows)
        return

    if not args.categories:
        raise SystemExit("At least one scoring category is required.")

    if args.exclude_zero_price:
        rows = exclude_zero_price_rows(rows)
    numeric = numeric_columns(headers, rows)
    categories = [resolve_category(category, headers) for category in args.categories]
    invalid = [category for category in categories if category not in numeric]
    if invalid:
        invalid_list = ", ".join(invalid)
        raise SystemExit(f"Scoring categories must be numeric: {invalid_list}")

    scored_rows = score_rows(rows, categories)
    pareto = pareto_flags(scored_rows, categories) if len(categories) in {2, 3} else []
    columns = table_columns(headers, numeric | {FINAL_SCORE}, args.all_columns)
    available_categories = [header for header in headers if header in numeric]
    write_html(
        args.output,
        scored_rows,
        columns,
        categories,
        pareto,
        available_categories,
    )

    print(f"Wrote {len(scored_rows)} ranked rows to {args.output}")


if __name__ == "__main__":
    main()
