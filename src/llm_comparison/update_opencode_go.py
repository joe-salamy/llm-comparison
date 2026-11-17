from __future__ import annotations

import argparse
import asyncio
import csv
import re
import sys
from collections.abc import Sequence
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import TypedDict, cast

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_URL = "https://opencode.ai/console/go"
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
    "opencode_go_effective_usd_per_1m_tokens",
    "long_context_effective_usd_per_1m_tokens",
    "value_score",
    "scraped_at",
]

# Artificial Analysis renders variant effort as a trailing word ("... 1017
# Max") while older pages used parentheses; accept both spellings.
DEEPSEEK_V41_ALIASES: tuple[str, ...] = (
    "DeepSeek V4.1 Flash 1017 Max",
    "DeepSeek V4.1 Flash 1017 (max)",
    "DeepSeek V4.1 Flash (max)",
    "DeepSeek V4.1 Flash (high)",
    "DeepSeek V4.1 Flash",
)

AA_MODEL_ALIASES: dict[str, tuple[str, ...]] = {
    "Grok 4.7": (
        "Grok 4.7 High",
        "Grok 4.7 Xhigh",
        "Grok 4.7 (high)",
        "Grok 4.7 (xhigh)",
    ),
    "Grok 4.6": ("Grok 4.6 (high)", "Grok 4.6 (xhigh)"),
    "Grok 4.5": ("Grok 4.5 (high)",),
    "GLM-5.3": ("GLM-5.3 Max", "GLM-5.3 (max)"),
    "GLM-5.2": ("GLM-5.2 (max)", "GLM-5.2"),
    "GLM-5.1": ("GLM-5.1",),
    "GPT 6 Luna": (
        "GPT-6 Luna Max",
        "GPT-6 Luna (max)",
        "GPT-6 Luna (xhigh)",
        "GPT-6 Luna (high)",
        "GPT-6 Luna (medium)",
        "GPT-6 Luna (low)",
        "GPT-6 Luna (Non-reasoning)",
    ),
    "GPT 5.6 Luna": (
        "GPT-5.6 Luna (max)",
        "GPT-5.6 Luna (xhigh)",
        "GPT-5.6 Luna (high)",
        "GPT-5.6 Luna (medium)",
        "GPT-5.6 Luna (low)",
        "GPT-5.6 Luna (Non-reasoning)",
    ),
    "Kimi K3": ("Kimi K3 (max)", "Kimi K3 (low)"),
    "Kimi K2.7 Code": ("Kimi K2.7 Code",),
    "Kimi K2.6": ("Kimi K2.6",),
    "MiMo V2.5": ("MiMo-V2.5",),
    "MiMo V2.5 Pro": ("MiMo-V2.5-Pro",),
    "MiniMax M3": ("MiniMax-M3",),
    "MiniMax M2.7": ("MiniMax-M2.7",),
    "MiniMax M2.5": (),
    "Muse Spark 1.3 Contributor": ("Muse Spark 1.3 (xhigh)",),
    "Muse Spark 1.2 Contributor": ("Muse Spark 1.2 (xhigh)",),
    "Qwen3.8 Max": ("Qwen3.8 Max (0902)", "Qwen3.8 Max"),
    "Qwen3.8 Flash": ("Qwen3.8-Flash-Next",),
    "Qwen3.7 Max": ("Qwen3.7 Max",),
    "Qwen3.7 Plus": ("Qwen3.7 Plus",),
    "Qwen3.6 Plus": ("Qwen3.6 Plus",),
    "DeepSeek V4 Pro": (
        "DeepSeek V4 Pro 0813 Max",
        "DeepSeek V4 Pro 0813 (max)",
        "DeepSeek V4 Pro (max)",
        "DeepSeek V4 Pro (high)",
        "DeepSeek V4 Pro",
    ),
    "DeepSeek V4 Flash": (
        "DeepSeek V4 Flash 0731 (max)",
        "DeepSeek V4 Flash (max)",
        "DeepSeek V4 Flash (high)",
        "DeepSeek V4 Flash",
    ),
    "DeepSeek V4 Pro (Off-Peak)": (
        "DeepSeek V4 Pro 0813 Max",
        "DeepSeek V4 Pro 0813 (max)",
        "DeepSeek V4 Pro (max)",
        "DeepSeek V4 Pro (high)",
        "DeepSeek V4 Pro",
    ),
    "DeepSeek V4 Pro (Peak)": (
        "DeepSeek V4 Pro 0813 Max",
        "DeepSeek V4 Pro 0813 (max)",
        "DeepSeek V4 Pro (max)",
        "DeepSeek V4 Pro (high)",
        "DeepSeek V4 Pro",
    ),
    "DeepSeek V4 Flash (Off-Peak)": (
        "DeepSeek V4 Flash 0731 (max)",
        "DeepSeek V4 Flash (max)",
        "DeepSeek V4 Flash (high)",
        "DeepSeek V4 Flash",
    ),
    "DeepSeek V4 Flash (Peak)": (
        "DeepSeek V4 Flash 0731 (max)",
        "DeepSeek V4 Flash (max)",
        "DeepSeek V4 Flash (high)",
        "DeepSeek V4 Flash",
    ),
    "DeepSeek V4.1 Flash 1017 (Off-Peak)": DEEPSEEK_V41_ALIASES,
    "DeepSeek V4.1 Flash 1017 (Peak)": DEEPSEEK_V41_ALIASES,
    "DeepSeek V4.1 Flash (Off-Peak)": DEEPSEEK_V41_ALIASES,
    "DeepSeek V4.1 Flash (Peak)": DEEPSEEK_V41_ALIASES,
    "DeepSeek V4 Flash Vision Exp (Off-Peak)": (
        "DeepSeek V4 Flash Vision (max)",
        "DeepSeek V4 Flash 0731 (max)",
        "DeepSeek V4 Flash (max)",
        "DeepSeek V4 Flash (high)",
        "DeepSeek V4 Flash",
    ),
    "DeepSeek V4 Flash Vision Exp (Peak)": (
        "DeepSeek V4 Flash Vision (max)",
        "DeepSeek V4 Flash 0731 (max)",
        "DeepSeek V4 Flash (max)",
        "DeepSeek V4 Flash (high)",
        "DeepSeek V4 Flash",
    ),
    "MiniMax M3.1 Flash": ("MiniMax-M3.1-Flash",),
    "Gemini 4 Argon": (
        "Gemini 4 Argon High",
        "Gemini 4 Argon (high)",
        "Gemini 4 Argon (medium)",
        "Gemini 4 Argon (low)",
    ),
    "Gemini 4 Argon Contributor": (
        "Gemini 4 Argon High",
        "Gemini 4 Argon (high)",
        "Gemini 4 Argon (medium)",
        "Gemini 4 Argon (low)",
    ),
    "Hy4": ("Tencent Hy4",),
    "Hy4 preview": ("Tencent Hy4",),
    "Hy3": ("Hy3",),
    "Beam Free": (),
    "Crouton Alpha Free": (),
    "Iceman Contributor Free": (),
    "LongCat 2.5 Preview Free": (),
    "Space Bunny Free": (),
    "Ox Alpha Free": (),
}

TIER_LABEL_PATTERN = re.compile(
    r"(?P<model>.+) \((?P<operator>≤|>) (?P<threshold>[1-9]\d*)K tokens\)"
)
CURRENCY_PATTERN = re.compile(r"\$(?:\d+(?:\.\d*)?|\.\d+)")
CURRENCY_AMOUNT_PATTERN = re.compile(r"\$(\d+(?:\.\d*)?|\.\d+)")
PROMO_MODEL_SUFFIX = re.compile(
    r"\s*\(\s*\d+(?:\.\d+)?%\s*off\s*\)$", re.IGNORECASE
)


class PriceRow(TypedDict):
    source_label: str
    model: str
    input_price: Decimal
    output_price: Decimal
    cache_read_price: Decimal
    cache_write_price: Decimal | None
    monthly_usage: Decimal | None
    long_context: bool
    tier_threshold_tokens: int | None


class ConsolePriceRow(TypedDict):
    """One row of the console Pricing view, with its variant annotation.

    The console repeats a model for long-context tiers ("Over 512K tokens"),
    peak-hour windows ("Peak hours, ..."), and scheduled price changes
    ("From Dec 1, 2026"); ``annotation`` holds that trailing label.
    """

    model: str
    annotation: str
    cells: list[str]


class ConsoleLimitRow(TypedDict):
    model: str
    quota: str


TIER_ANNOTATION_PATTERN = re.compile(r"Over (?P<threshold>[1-9]\d*)K tokens\b")
FUTURE_PRICE_ANNOTATION_PATTERN = re.compile(
    r"From (?P<date>[A-Z][a-z]{2} \d{1,2}, \d{4})"
)
PEAK_ANNOTATION_PREFIX = "Peak hours"
GO_QUOTA_PATTERN = re.compile(r"Go:\s*(?P<quota>[^;]+)")
UNLIMITED_QUOTA_VALUES = frozenset({"∞", "Unlimited"})


def normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


def is_pricing_headers(normalized_headers: list[str]) -> bool:
    return normalized_headers == SOURCE_HEADERS


def normalize_annotation(value: str) -> str:
    return normalize_text(value).replace(" ,", ",")


def parse_go_quota(value: str, *, model: str) -> str:
    """Turn the console's "Go: $15; Go Plus: $60" text into a Usage cell."""
    match = GO_QUOTA_PATTERN.search(normalize_text(value))
    if match is None:
        raise RuntimeError(
            f"OpenCode Go monthly limit for {model!r} did not match: {value!r}"
        )
    quota = normalize_text(match.group("quota"))
    return "-" if quota in UNLIMITED_QUOTA_VALUES else quota


def classify_price_row(
    row: ConsolePriceRow, *, today: date
) -> tuple[str, str | None]:
    """Classify a Pricing view row as base, tier, peak, or future.

    Returns the kind and its detail: the tier threshold in tokens or the
    scheduled price date. Future rows whose date has arrived are treated as
    the current base price.
    """
    model = normalize_text(row["model"])
    annotation = normalize_annotation(row["annotation"])
    if not annotation:
        return "base", None
    tier_match = TIER_ANNOTATION_PATTERN.search(annotation)
    if tier_match is not None:
        return "tier", tier_match.group("threshold") + "000"
    if annotation.startswith(PEAK_ANNOTATION_PREFIX):
        return "peak", None
    future_match = FUTURE_PRICE_ANNOTATION_PATTERN.search(annotation)
    if future_match is not None:
        scheduled = datetime.strptime(future_match.group("date"), "%b %d, %Y")
        if scheduled.date() > today:
            return "future", future_match.group("date")
        return "base", None
    raise RuntimeError(
        f"Unrecognized OpenCode Go price annotation for {model!r}: {annotation!r}"
    )


def build_source_rows(
    price_rows: Sequence[ConsolePriceRow],
    limit_rows: Sequence[ConsoleLimitRow],
    *,
    today: date,
) -> list[list[str]]:
    """Merge the console Pricing and Limits views into SOURCE_HEADERS rows."""
    quotas: dict[str, str] = {}
    for row in limit_rows:
        model = normalize_text(row["model"])
        if not model:
            raise RuntimeError(
                "Could not read OpenCode Go monthly limits; a row has no model name"
            )
        if model in quotas:
            raise RuntimeError(f"Duplicate OpenCode Go monthly limit: {model!r}")
        quotas[model] = parse_go_quota(row["quota"], model=model)

    grouped: dict[str, list[tuple[str, str | None, ConsolePriceRow]]] = {}
    for row in price_rows:
        model = normalize_text(row["model"])
        if not model:
            raise RuntimeError("OpenCode Go pricing row has no model name")
        kind, detail = classify_price_row(row, today=today)
        grouped.setdefault(model, []).append((kind, detail, row))

    output: list[list[str]] = []
    seen_labels: set[str] = set()

    def emit(label: str, row: ConsolePriceRow, model: str) -> None:
        if label in seen_labels:
            raise RuntimeError(f"Duplicate OpenCode Go source label: {label!r}")
        seen_labels.add(label)
        cells = row["cells"]
        if len(cells) != len(SOURCE_HEADERS) - 2:
            raise RuntimeError(
                f"OpenCode Go pricing row for {label!r} has {len(cells)} price "
                f"cells; expected {len(SOURCE_HEADERS) - 2}"
            )
        if model not in quotas:
            raise RuntimeError(f"OpenCode Go has no monthly limit for {model!r}")
        output.append([label, *cells, quotas[model]])

    for model, entries in grouped.items():
        kinds = [kind for kind, _, _ in entries]
        base_entries = [entry for entry in entries if entry[0] == "base"]
        tier_entries = [entry for entry in entries if entry[0] == "tier"]
        peak_entries = [entry for entry in entries if entry[0] == "peak"]
        future_entries = [entry for entry in entries if entry[0] == "future"]
        if len(base_entries) != 1:
            raise RuntimeError(
                f"OpenCode Go {model!r} needs exactly one base price row; "
                f"found kinds: {kinds}"
            )
        if len(tier_entries) > 1 or (tier_entries and peak_entries):
            raise RuntimeError(
                f"OpenCode Go {model!r} combines unsupported price variants: "
                f"found kinds: {kinds}"
            )
        for _, detail, _ in future_entries:
            print(
                f"warning: OpenCode Go {model!r} has a scheduled price from "
                f"{detail}; keeping the current price",
                file=sys.stderr,
                flush=True,
            )
        base_row = base_entries[0][2]
        if tier_entries:
            _, threshold, tier_row = tier_entries[0]
            tier_k = int(threshold) // 1_000
            emit(f"{model} (≤ {tier_k}K tokens)", base_row, model)
            emit(f"{model} (> {tier_k}K tokens)", tier_row, model)
        elif peak_entries:
            emit(f"{model} (Off-Peak)", base_row, model)
            emit(f"{model} (Peak)", peak_entries[0][2], model)
        else:
            emit(model, base_row, model)
    return output


def parse_currency(
    value: str, *, field: str, source_label: str, allow_blank: bool = False
) -> Decimal | None:
    """Parse a token price, tolerating strikethrough promo cells.

    Promo cells render as "<del>$4.00</del> $2.00" and innerText keeps both
    amounts, so the last price is the current one (matching parse_usage).
    """
    normalized = normalize_text(value)
    if allow_blank and normalized in {"", "-"}:
        return None
    if normalized.lower() == "free":
        return Decimal(0)
    if CURRENCY_PATTERN.fullmatch(normalized):
        text = normalized[1:]
    else:
        amounts = CURRENCY_AMOUNT_PATTERN.findall(normalized)
        if len(amounts) < 2:
            raise RuntimeError(
                f"Invalid OpenCode Go {field} for {source_label!r}: {value!r}"
            )
        text = amounts[-1]
        print(
            f"warning: OpenCode Go {field} for {source_label!r} carries promo "
            f"text; using current price ${text} from {value!r}",
            file=sys.stderr,
            flush=True,
        )
    try:
        parsed = Decimal(text)
    except InvalidOperation as error:
        raise RuntimeError(
            f"Invalid OpenCode Go {field} for {source_label!r}: {value!r}"
        ) from error
    if not parsed.is_finite() or parsed < 0:
        raise RuntimeError(
            f"Invalid OpenCode Go {field} for {source_label!r}: {value!r}"
        )
    return parsed


PROMO_USAGE_MARKERS = re.compile(r"(?i)\bends\b|\bpromo\b|[·•]|\dx\b")


def parse_usage(value: str, *, source_label: str) -> Decimal | None:
    """Parse the Usage quota, tolerating promo annotations.

    Promo cells render as "<del>$15</del> <strong>$60</strong> 4x · Ends ...";
    the last price is the current quota. A glued "<dollar><digits>x" token
    (textContent scraping without a <br> separator) is ambiguous, so it fails
    loudly instead of writing a wrong quota.
    """
    normalized = normalize_text(value)
    if normalized == "-":
        return None
    if normalized.lower().startswith("unlimited"):
        return None
    if re.fullmatch(r"\$(?:\d+(?:\.\d*)?|\.\d+)", normalized):
        return Decimal(normalized[1:])
    if re.search(r"\$\d[\d.]*x\b", normalized):
        raise RuntimeError(
            f"Ambiguous OpenCode Go Usage for {source_label!r}: {value!r}"
        )
    amounts = re.findall(r"\$(\d+(?:\.\d*)?|\.\d+)\b", normalized)
    if amounts and PROMO_USAGE_MARKERS.search(normalized):
        current = amounts[-1]
        print(
            f"warning: OpenCode Go Usage for {source_label!r} carries promo "
            f"text; using current quota ${current} from {value!r}",
            file=sys.stderr,
            flush=True,
        )
        return Decimal(current)
    raise RuntimeError(f"Invalid OpenCode Go Usage for {source_label!r}: {value!r}")


def parse_source_rows(headers: list[str], rows: list[list[str]]) -> list[PriceRow]:
    normalized_headers = [normalize_text(header) for header in headers]
    if not is_pricing_headers(normalized_headers):
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
        ):
            if not values[index]:
                raise RuntimeError(f"OpenCode Go {source_label!r} is missing {field}")
        # Usage may be "-" for free models (Ox Alpha Free) -> blank
        if not values[5] and normalize_text(cells[5]) != "-":
            raise RuntimeError(f"OpenCode Go {source_label!r} is missing Usage")

        tier_match = TIER_LABEL_PATTERN.fullmatch(source_label)
        if tier_match is not None:
            model = tier_match.group("model")
            long_context = tier_match.group("operator") == ">"
            tier_threshold_tokens = int(tier_match.group("threshold")) * 1_000
        elif re.search(r"\([^)]*\btokens\)$", source_label, re.IGNORECASE):
            raise RuntimeError(
                f"Unrecognized OpenCode Go tiered source label: {source_label}"
            )
        else:
            model = source_label
            long_context = False
            tier_threshold_tokens = None
        # A discount renders in the label ("Gemini 4 Argon (50% off)"); the
        # model identity is the part before it, so Artificial Analysis joins.
        model = PROMO_MODEL_SUFFIX.sub("", model).strip()
        if not model:
            raise RuntimeError(
                f"OpenCode Go source label has no model name: {source_label!r}"
            )

        if normalize_text(values[1]) == "-":
            input_price = Decimal(0)
        else:
            parsed = parse_currency(
                values[1], field="Input", source_label=source_label
            )
            assert parsed is not None
            input_price = parsed
        if normalize_text(values[2]) == "-":
            output_price = Decimal(0)
        else:
            parsed = parse_currency(
                values[2], field="Output", source_label=source_label
            )
            assert parsed is not None
            output_price = parsed
        if normalize_text(values[3]) == "-":
            cache_read_price = Decimal(0)
        else:
            parsed = parse_currency(
                values[3], field="Cached Read", source_label=source_label
            )
            assert parsed is not None
            cache_read_price = parsed
        cache_write_price = parse_currency(
            values[4], field="Cached Write", source_label=source_label, allow_blank=True
        )
        monthly_usage = parse_usage(values[5], source_label=source_label)
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
                "tier_threshold_tokens": tier_threshold_tokens,
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
        is_tiered = any(
            row["tier_threshold_tokens"] is not None for row in model_rows
        )
        if is_tiered:
            primary = [row for row in model_rows if not row["long_context"]]
            secondary = [row for row in model_rows if row["long_context"]]
            if len(primary) != 1 or len(secondary) != 1:
                labels = ", ".join(row["source_label"] for row in model_rows)
                raise RuntimeError(
                    f"OpenCode Go {model} requires both pricing tiers; found: {labels}"
                )
            primary_row, secondary_row = primary[0], secondary[0]
            primary_threshold = primary_row["tier_threshold_tokens"]
            secondary_threshold = secondary_row["tier_threshold_tokens"]
            if (
                primary_threshold is None
                or secondary_threshold is None
                or primary_threshold != secondary_threshold
            ):
                raise RuntimeError(
                    f"OpenCode Go {model} pricing tiers have different thresholds"
                )
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
            primary_threshold = None

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
                    "long_context_threshold_tokens": str(primary_threshold),
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


def _normalize_model_name(value: str) -> str:
    normalized = normalize_text(value).lower()
    normalized = normalized.replace("_", " ").replace("-", " ")
    return " ".join(normalized.split())


def select_aa_candidate(
    model: str, aa_rows: list[dict[str, str]]
) -> tuple[str, Decimal] | None:
    aliases = AA_MODEL_ALIASES.get(model)
    if aliases is not None and len(aliases) == 0:
        return None
    best: tuple[Decimal, int, int, str] | None = None
    if aliases is not None:
        normalized_aliases = [_normalize_model_name(alias) for alias in aliases]
        alias_lookup = {norm: idx for idx, norm in enumerate(normalized_aliases)}
        for row_index, row in enumerate(aa_rows):
            display_name = row.get("model", "")
            normalized_display = _normalize_model_name(display_name)
            alias_index = alias_lookup.get(normalized_display)
            if alias_index is None:
                continue
            value = parse_intelligence_index(
                row.get("artificial_analysis_intelligence_index")
            )
            if value is None:
                continue
            candidate = (value, -alias_index, -row_index, display_name)
            if best is None or candidate[:3] > best[:3]:
                best = candidate
        if best is not None:
            return (best[3], best[0])
    # Generic fallback for models not in AA_MODEL_ALIASES: try normalized
    # exact or prefix match (e.g., "GLM-5.3" -> "GLM-5.3 (max)") so new
    # OpenCode Go models with slight convention differences don't get skipped
    # even without an explicit alias entry.
    if aliases is None:
        normalized_model = _normalize_model_name(model)
        generic_best: tuple[Decimal, int, int, str] | None = None
        for row_index, row in enumerate(aa_rows):
            display_name = row.get("model", "")
            normalized_display = _normalize_model_name(display_name)
            if not (
                normalized_display == normalized_model
                or normalized_display.startswith(normalized_model + " ")
                or normalized_display.startswith(normalized_model + " (")
            ):
                continue
            value = parse_intelligence_index(
                row.get("artificial_analysis_intelligence_index")
            )
            if value is None:
                continue
            # Prefer shorter suffix when intelligence ties, then earlier row
            suffix_len = len(normalized_display) - len(normalized_model)
            candidate = (value, -suffix_len, -row_index, display_name)
            if generic_best is None or candidate[:3] > generic_best[:3]:
                generic_best = candidate
        if generic_best is not None:
            return (generic_best[3], generic_best[0])
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


def effective_price(blended: Decimal, quota: Decimal) -> Decimal:
    if not blended.is_finite() or blended <= 0:
        raise RuntimeError(
            "OpenCode Go blended price must be finite and greater than zero"
        )
    if not quota.is_finite() or quota <= 0:
        raise RuntimeError(
            "OpenCode Go monthly quota must be finite and greater than zero"
        )
    result = blended / quota
    if not result.is_finite() or result <= 0:
        raise RuntimeError(
            "OpenCode Go effective price must be finite and greater than zero"
        )
    return result


def cost_adjusted_intelligence(
    intelligence: Decimal, effective_blended_price: Decimal
) -> Decimal:
    if not intelligence.is_finite() or intelligence < 0:
        raise RuntimeError("OpenCode Go intelligence must be finite and non-negative")
    if not effective_blended_price.is_finite() or effective_blended_price <= 0:
        raise RuntimeError(
            "OpenCode Go effective price must be finite and greater than zero"
        )
    return intelligence - Decimal(10) * effective_blended_price.log10()


def parse_quota(value: str | None) -> Decimal | None:
    normalized = normalize_text(value or "")
    if not normalized:
        return None
    # Stored values are plain decimals (e.g., "15") but accept "$15" for robustness.
    if normalized.startswith("$"):
        normalized = normalized[1:].strip()
        if not normalized:
            return None
    try:
        parsed = Decimal(normalized)
    except InvalidOperation:
        return None
    if not parsed.is_finite() or parsed <= 0:
        return None
    return parsed

def enrich_rows(
    rows: list[dict[str, str]], aa_rows: list[dict[str, str]]
) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for source in rows:
        row = source.copy()
        cache_read = Decimal(row["cache_read_usd_per_1m_tokens"] or "0")
        input_price = Decimal(row["input_price_usd_per_1m_tokens"] or "0")
        output_price = Decimal(row["output_price_usd_per_1m_tokens"] or "0")
        is_free = cache_read == 0 and input_price == 0 and output_price == 0
        if is_free:
            row["opencode_go_blended_usd_per_1m_tokens"] = "0"
            row["opencode_go_effective_usd_per_1m_tokens"] = ""
            # Long-context free not expected, but handle if present and zero.
            if row["long_context_threshold_tokens"]:
                lc_cache = Decimal(
                    row["long_context_cache_read_usd_per_1m_tokens"] or "0"
                )
                lc_input = Decimal(
                    row["long_context_input_price_usd_per_1m_tokens"] or "0"
                )
                lc_output = Decimal(
                    row["long_context_output_price_usd_per_1m_tokens"] or "0"
                )
                if lc_cache == 0 and lc_input == 0 and lc_output == 0:
                    row["long_context_blended_usd_per_1m_tokens"] = "0"
                    row["long_context_effective_usd_per_1m_tokens"] = ""
                else:
                    long_blend = blended_price(lc_cache, lc_input, lc_output)
                    row["long_context_blended_usd_per_1m_tokens"] = decimal_text(
                        long_blend
                    )
                    quota = parse_quota(
                        row.get("monthly_usage_usd") or row.get("monthly_quota_usd")
                    )
                    if quota is not None:
                        long_effective = effective_price(long_blend, quota)
                        row["long_context_effective_usd_per_1m_tokens"] = decimal_text(
                            long_effective
                        )
                    else:
                        row["long_context_effective_usd_per_1m_tokens"] = ""
            else:
                row["long_context_effective_usd_per_1m_tokens"] = ""
            # Free tier has no cost-adjusted intelligence;
            # leave value_score blank even if alias exists.
            # Alias is empty for Ox Alpha Free.
            output.append(row)
            continue

        primary_blend = blended_price(cache_read, input_price, output_price)
        row["opencode_go_blended_usd_per_1m_tokens"] = decimal_text(primary_blend)

        quota = parse_quota(
            row.get("monthly_usage_usd") or row.get("monthly_quota_usd")
        )
        if quota is not None:
            primary_effective = effective_price(primary_blend, quota)
            row["opencode_go_effective_usd_per_1m_tokens"] = decimal_text(
                primary_effective
            )
        else:
            row["opencode_go_effective_usd_per_1m_tokens"] = ""

        if row["long_context_threshold_tokens"]:
            long_blend = blended_price(
                Decimal(row["long_context_cache_read_usd_per_1m_tokens"]),
                Decimal(row["long_context_input_price_usd_per_1m_tokens"]),
                Decimal(row["long_context_output_price_usd_per_1m_tokens"]),
            )
            row["long_context_blended_usd_per_1m_tokens"] = decimal_text(long_blend)
            if quota is not None:
                long_effective = effective_price(long_blend, quota)
                row["long_context_effective_usd_per_1m_tokens"] = decimal_text(
                    long_effective
                )
            else:
                row["long_context_effective_usd_per_1m_tokens"] = ""
        else:
            row["long_context_effective_usd_per_1m_tokens"] = ""

        selected = select_aa_candidate(row["model"], aa_rows)
        if selected is not None and quota is not None:
            aa_model, intelligence = selected
            # Use quota-adjusted effective price for scoring.
            effective = effective_price(primary_blend, quota)
            value = cost_adjusted_intelligence(intelligence, effective)
            row["artificial_analysis_model"] = aa_model
            row["artificial_analysis_intelligence_index"] = decimal_text(intelligence)
            row["value_score"] = decimal_text(value)
        elif selected is not None and quota is None:
            # Quota missing but intelligence exists: leave value blank (cannot score).
            aa_model, intelligence = selected
            row["artificial_analysis_model"] = aa_model
            row["artificial_analysis_intelligence_index"] = decimal_text(intelligence)
            row["value_score"] = ""
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


LIMIT_ROWS_SCRIPT = """
(table) => Array.from(table.querySelectorAll('tbody tr'), row => {
  const header = row.querySelector('th');
  const usage = row.querySelector('td[data-allowance-type="usage"]');
  return {
    model: (
      header?.querySelector('[data-layer="model-name"]')?.getAttribute('title') ||
      header?.innerText ||
      ''
    ).trim(),
    quota: (usage?.querySelector('.sr-only')?.textContent || '').trim(),
  };
})
"""

PRICE_ROWS_SCRIPT = """
(table) => Array.from(table.querySelectorAll('tbody tr'), row => {
  const header = row.querySelector('th');
  const nameCell = header?.querySelector('[data-layer="model-name"]');
  // Variant rows (tiers, peak windows, scheduled prices) have no model-name
  // span: their name sits in an sr-only prefix before the annotation.
  const name = (
    nameCell?.getAttribute('title') ||
    header?.querySelector('.sr-only')?.textContent ||
    ''
  ).replace(/,\\s*$/, '').trim();
  const text = (header?.innerText || '').trim();
  const annotation = nameCell
    ? ''
    : text.slice(text.indexOf(name) + name.length).replace(/^[,\\s]+/, '').trim();
  return {
    model: name,
    annotation,
    cells: Array.from(row.cells, cell => cell.innerText || '').slice(1),
  };
})
"""


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
                    "Could not find the OpenCode Go pricing table; the console "
                    "page rendered no tables"
                ) from error
            limit_rows = cast(
                list[ConsoleLimitRow],
                await page.locator("table").first.evaluate(LIMIT_ROWS_SCRIPT),
            )
            try:
                await page.get_by_role("button", name="Pricing", exact=True).click(
                    timeout=timeout_ms
                )
                await page.locator('table[aria-label="Pricing"]').wait_for(
                    state="visible", timeout=timeout_ms
                )
            except PlaywrightTimeoutError as error:
                raise RuntimeError(
                    "Could not open the OpenCode Go Pricing view on the console page"
                ) from error
            price_rows = cast(
                list[ConsolePriceRow],
                await page.locator('table[aria-label="Pricing"]').evaluate(
                    PRICE_ROWS_SCRIPT
                ),
            )
        finally:
            await browser.close()
    return SOURCE_HEADERS, build_source_rows(
        price_rows, limit_rows, today=datetime.now(UTC).date()
    )


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
