from __future__ import annotations

import argparse
import asyncio
import csv
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
from types import ModuleType

import pytest
from pytest import MonkeyPatch

import llm_comparison.update_opencode_go as updater

HEADERS = ["Model", "Input", "Output", "Cached Read", "Cached Write", "Usage"]
SCRAPED_AT = "2026-07-17T14:32:05Z"
SOURCE_ROWS = [
    ["Grok 4.5", "$2.00", "$6.00", "$0.50", "-", "$15"],
    ["GLM-5.2", "$1.40", "$4.40", "$0.26", "-", "$60"],
    ["GLM-5.1", "$1.40", "$4.40", "$0.26", "-", "$60"],
    ["GPT 5.6 Luna (≤ 272K tokens)", "$0.20", "$1.20", "$0.02", "$0.25", "$15"],
    ["GPT 5.6 Luna (> 272K tokens)", "$0.40", "$1.80", "$0.04", "$0.50", "$15"],
    ["Kimi K3", "$3.00", "$15.00", "$0.30", "-", "$15"],
    ["Kimi K2.7 Code", "$0.95", "$4.00", "$0.19", "-", "$60"],
    ["Kimi K2.6", "$0.95", "$4.00", "$0.16", "-", "$60"],
    ["MiMo V2.5", "$0.14", "$0.28", "$0.0028", "-", "$60"],
    ["MiMo V2.5 Pro", "$0.435", "$0.87", "$0.003625", "-", "$15"],
    ["MiniMax M3", "$0.30", "$1.20", "$0.06", "-", "$60"],
    ["MiniMax M2.7", "$0.30", "$1.20", "$0.06", "$0.375", "$60"],
    ["MiniMax M2.5", "$0.30", "$1.20", "$0.06", "$0.375", "$60"],
    ["Qwen3.7 Max", "$2.50", "$7.50", "$0.50", "$3.125", "$60"],
    ["Qwen3.7 Plus (≤ 256K tokens)", "$0.40", "$1.60", "$0.04", "$0.50", "$60"],
    ["Qwen3.7 Plus (> 256K tokens)", "$1.20", "$4.80", "$0.12", "$1.50", "$60"],
    ["Qwen3.6 Plus (≤ 256K tokens)", "$0.50", "$3.00", "$0.05", "$0.625", "$60"],
    ["Qwen3.6 Plus (> 256K tokens)", "$2.00", "$6.00", "$0.20", "$2.50", "$60"],
    ["DeepSeek V4 Pro", "$0.435", "$0.87", "$0.003625", "-", "$15"],
    ["DeepSeek V4 Flash", "$0.14", "$0.28", "$0.0028", "-", "$60"],
]
AA_ROWS = [
    {"model": "Grok 4.5 (high)", "artificial_analysis_intelligence_index": "60"},
    {"model": "GLM-5.2", "artificial_analysis_intelligence_index": "45"},
    {"model": "GLM-5.2 (max)", "artificial_analysis_intelligence_index": "50*"},
    {"model": "GLM-5.1", "artificial_analysis_intelligence_index": "41"},
    {"model": "GPT-5.6 Luna (max)", "artificial_analysis_intelligence_index": "51"},
    {"model": "GPT-5.6 Luna (xhigh)", "artificial_analysis_intelligence_index": "49"},
    {"model": "GLM-5.1", "artificial_analysis_intelligence_index": "44"},
    {"model": "Kimi K3", "artificial_analysis_intelligence_index": "55"},
    {"model": "Kimi K2.7 Code", "artificial_analysis_intelligence_index": "38"},
    {"model": "Kimi K2.6", "artificial_analysis_intelligence_index": "36"},
    {"model": "Kimi K2.6", "artificial_analysis_intelligence_index": "39"},
    {"model": "MiMo-V2.5", "artificial_analysis_intelligence_index": "20"},
    {"model": "MiMo-V2.5-Pro", "artificial_analysis_intelligence_index": "31"},
    {"model": "MiMo-V2.5-Pro", "artificial_analysis_intelligence_index": "33"},
    {"model": "MiniMax-M3", "artificial_analysis_intelligence_index": "35"},
    {"model": "MiniMax-M2.7", "artificial_analysis_intelligence_index": "30"},
    {"model": "Qwen3.7 Max", "artificial_analysis_intelligence_index": "52"},
    {"model": "Qwen3.7 Plus", "artificial_analysis_intelligence_index": "42"},
    {"model": "Qwen3.6 Plus", "artificial_analysis_intelligence_index": "40"},
    {"model": "DeepSeek V4 Pro", "artificial_analysis_intelligence_index": "35"},
    {"model": "DeepSeek V4 Pro (high)", "artificial_analysis_intelligence_index": "37"},
    {"model": "DeepSeek V4 Pro (max)", "artificial_analysis_intelligence_index": "39"},
    {"model": "DeepSeek V4 Flash", "artificial_analysis_intelligence_index": "38"},
    {
        "model": "DeepSeek V4 Flash (max)",
        "artificial_analysis_intelligence_index": "40",
    },
    {
        "model": "DeepSeek V4 Flash 0731 (max)",
        "artificial_analysis_intelligence_index": "50",
    },
]


def output_rows() -> list[dict[str, str]]:
    return updater.build_output_rows(
        HEADERS, SOURCE_ROWS, AA_ROWS, scraped_at=SCRAPED_AT
    )


def by_model(rows: list[dict[str, str]], model: str) -> dict[str, str]:
    return next(row for row in rows if row["model"] == model)


def test_exact_table_collapses_tiered_rows_and_calculates_examples() -> None:
    rows = output_rows()
    assert len(rows) == 17
    assert [row["model"] for row in rows[:5]] == [
        "Grok 4.5",
        "GLM-5.2",
        "GLM-5.1",
        "GPT 5.6 Luna",
        "Kimi K3",
    ]
    assert by_model(rows, "Kimi K3")["opencode_go_blended_usd_per_1m_tokens"] == "2.31"

    flash = by_model(rows, "DeepSeek V4 Flash")
    assert flash["artificial_analysis_model"] == "DeepSeek V4 Flash 0731 (max)"
    assert flash["artificial_analysis_intelligence_index"] == "50"
    assert flash["opencode_go_blended_usd_per_1m_tokens"] == "0.05796"
    assert float(flash["value_score"]) == pytest.approx(62.3687162320)

    luna = by_model(rows, "GPT 5.6 Luna")
    assert luna["long_context_threshold_tokens"] == "272000"
    assert luna["artificial_analysis_model"] == "GPT-5.6 Luna (max)"
    assert luna["artificial_analysis_intelligence_index"] == "51"
    assert luna["opencode_go_blended_usd_per_1m_tokens"] == "0.174"
    assert luna["long_context_blended_usd_per_1m_tokens"] == "0.288"

    qwen = by_model(rows, "Qwen3.7 Plus")
    assert qwen["long_context_threshold_tokens"] == "256000"
    assert qwen["opencode_go_blended_usd_per_1m_tokens"] == "0.268"
    assert qwen["long_context_blended_usd_per_1m_tokens"] == "0.804"


def test_unranked_model_and_alias_selection_are_strict() -> None:
    rows = output_rows()
    minimax = by_model(rows, "MiniMax M2.5")
    assert minimax["artificial_analysis_model"] == ""
    assert minimax["artificial_analysis_intelligence_index"] == ""
    assert minimax["value_score"] == ""
    assert by_model(rows, "MiMo V2.5")["artificial_analysis_intelligence_index"] == "20"
    assert (
        by_model(rows, "MiMo V2.5 Pro")["artificial_analysis_intelligence_index"]
        == "33"
    )
    assert by_model(rows, "GLM-5.2")["artificial_analysis_model"] == "GLM-5.2 (max)"
    assert by_model(rows, "GLM-5.1")["artificial_analysis_intelligence_index"] == "44"


def test_equal_index_tie_uses_alias_then_csv_order() -> None:
    rows = [
        {"model": "DeepSeek V4 Pro", "artificial_analysis_intelligence_index": "40"},
        {
            "model": "DeepSeek V4 Pro (high)",
            "artificial_analysis_intelligence_index": "40",
        },
        {
            "model": "DeepSeek V4 Pro (max)",
            "artificial_analysis_intelligence_index": "40",
        },
        {
            "model": "DeepSeek V4 Pro (max)",
            "artificial_analysis_intelligence_index": "40",
        },
    ]
    assert updater.select_aa_candidate("DeepSeek V4 Pro", rows) == (
        "DeepSeek V4 Pro (max)",
        Decimal("40"),
    )


def test_usage_does_not_change_blend_value_or_rank() -> None:
    rows = output_rows()
    changed_source = [row.copy() for row in SOURCE_ROWS]
    changed_source[-1][-1] = "$999"
    changed = updater.build_output_rows(
        HEADERS, changed_source, AA_ROWS, scraped_at=SCRAPED_AT
    )
    original_scores = sorted(
        ((row["model"], row["value_score"]) for row in rows),
        key=lambda item: item[1],
    )
    changed_scores = sorted(
        ((row["model"], row["value_score"]) for row in changed),
        key=lambda item: item[1],
    )
    assert original_scores == changed_scores


@pytest.mark.parametrize(
    ("intelligence", "price", "expected"),
    [
        (Decimal("50"), Decimal("1"), Decimal("50")),
        (Decimal("50"), Decimal("10"), Decimal("40")),
        (Decimal("50"), Decimal("0.1"), Decimal("60")),
        (Decimal("0"), Decimal("1"), Decimal("0")),
    ],
)
def test_cost_adjusted_intelligence_logarithmic_anchors(
    intelligence: Decimal, price: Decimal, expected: Decimal
) -> None:
    assert updater.cost_adjusted_intelligence(intelligence, price) == expected


def test_cost_adjusted_intelligence_has_balanced_exchange_rate() -> None:
    assert updater.cost_adjusted_intelligence(
        Decimal("50"), Decimal("1")
    ) == updater.cost_adjusted_intelligence(Decimal("60"), Decimal("10"))


@pytest.mark.parametrize(
    "intelligence", [Decimal("-1"), Decimal("NaN"), Decimal("Infinity")]
)
def test_invalid_intelligence_is_rejected(intelligence: Decimal) -> None:
    with pytest.raises(
        RuntimeError,
        match="OpenCode Go intelligence must be finite and non-negative",
    ):
        updater.cost_adjusted_intelligence(intelligence, Decimal("1"))


def test_metric_does_not_reward_low_intelligence_for_low_price() -> None:
    kimi_k3 = updater.cost_adjusted_intelligence(Decimal("57"), Decimal("2.31"))
    mimo_v25 = updater.cost_adjusted_intelligence(
        Decimal("37"), Decimal("0.05796")
    )
    assert kimi_k3 > mimo_v25


@pytest.mark.parametrize(
    ("field", "delta", "expected"),
    [
        ("cache", Decimal("1"), Decimal("0.7")),
        ("input", Decimal("1"), Decimal("0.2")),
        ("output", Decimal("1"), Decimal("0.1")),
    ],
)
def test_blend_uses_exact_721_coefficients(
    field: str, delta: Decimal, expected: Decimal
) -> None:
    prices = {"cache": Decimal("1"), "input": Decimal("1"), "output": Decimal("1")}
    baseline = updater.blended_price(prices["cache"], prices["input"], prices["output"])
    prices[field] += delta
    changed = updater.blended_price(prices["cache"], prices["input"], prices["output"])
    assert changed - baseline == expected


@pytest.mark.parametrize("value", [Decimal("0"), Decimal("NaN"), Decimal("Infinity")])
def test_invalid_blended_prices_are_rejected(value: Decimal) -> None:
    with pytest.raises(RuntimeError, match="finite and greater than zero"):
        updater.blended_price(value, Decimal("0"), Decimal("0"))


@pytest.mark.parametrize("value", ["1.00", "$nan", "$-1", "$1x", "", "-"])
def test_malformed_required_currency_is_rejected(value: str) -> None:
    rows = [row.copy() for row in SOURCE_ROWS]
    rows[0][1] = value
    with pytest.raises(RuntimeError, match="Input"):
        updater.parse_source_rows(HEADERS, rows)


def test_blank_cached_write_parses_only_dash() -> None:
    parsed = updater.parse_source_rows(HEADERS, SOURCE_ROWS)
    assert parsed[0]["cache_write_price"] is None
    rows = [row.copy() for row in SOURCE_ROWS]
    rows[0][4] = ""
    with pytest.raises(RuntimeError, match="Cached Write"):
        updater.parse_source_rows(HEADERS, rows)


@pytest.mark.parametrize("missing_index", range(6))
def test_missing_required_source_cells_fail(missing_index: int) -> None:
    rows = [row.copy() for row in SOURCE_ROWS]
    rows[0][missing_index] = ""
    with pytest.raises(RuntimeError):
        updater.parse_source_rows(HEADERS, rows)


def test_duplicate_source_label_and_missing_tier_fail() -> None:
    duplicates = [row.copy() for row in SOURCE_ROWS]
    duplicates.append(SOURCE_ROWS[0].copy())
    with pytest.raises(RuntimeError, match="Duplicate OpenCode Go source label"):
        updater.parse_source_rows(HEADERS, duplicates)

    missing_tier = SOURCE_ROWS[:-5] + SOURCE_ROWS[-4:]
    with pytest.raises(RuntimeError, match="requires both pricing tiers"):
        updater.collapse_price_rows(updater.parse_source_rows(HEADERS, missing_tier))


def test_new_tiered_model_is_collapsed_without_an_allowlist() -> None:
    rows = [row.copy() for row in SOURCE_ROWS]
    rows[0:0] = [
        ["Future Model (≤ 128K tokens)", "$1", "$2", "$0.5", "-", "$60"],
        ["Future Model (> 128K tokens)", "$2", "$4", "$1", "-", "$60"],
    ]
    future = by_model(
        updater.collapse_price_rows(updater.parse_source_rows(HEADERS, rows)),
        "Future Model",
    )
    assert future["long_context_threshold_tokens"] == "128000"
    assert future["input_price_usd_per_1m_tokens"] == "1"
    assert future["long_context_input_price_usd_per_1m_tokens"] == "2"


def test_malformed_or_unpaired_tiered_source_labels_fail() -> None:
    malformed = [row.copy() for row in SOURCE_ROWS]
    malformed.insert(
        0, ["Future Model (up to 128K tokens)", "$1", "$2", "$0.5", "-", "$60"]
    )
    with pytest.raises(RuntimeError, match="Unrecognized OpenCode Go tiered"):
        updater.parse_source_rows(HEADERS, malformed)

    unpaired = [row.copy() for row in SOURCE_ROWS]
    unpaired.insert(
        0, ["Future Model (≤ 128K tokens)", "$1", "$2", "$0.5", "-", "$60"]
    )
    with pytest.raises(RuntimeError, match="requires both pricing tiers"):
        updater.collapse_price_rows(updater.parse_source_rows(HEADERS, unpaired))


def test_required_aa_headers_are_validated(tmp_path: Path) -> None:
    path = tmp_path / "results.csv"
    path.write_text("model,other\nA,1\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="artificial_analysis_intelligence_index"):
        updater.read_aa_rows(path)


def test_csv_columns_and_order_are_deterministic(tmp_path: Path) -> None:
    path = tmp_path / "opencode_go.csv"
    updater.write_csv(output_rows(), path)
    with path.open(newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        csv_rows = list(reader)
        assert reader.fieldnames == updater.CSV_COLUMNS
        assert reader.fieldnames[-1] == "scraped_at"
        assert [row["model"] for row in csv_rows] == [
            row["model"] for row in output_rows()
        ]
        assert {row["scraped_at"] for row in csv_rows} == {SCRAPED_AT}


def test_default_paths_resolve_from_repository_root() -> None:
    args = updater.parse_args([])
    assert args.url == "https://opencode.ai/docs/go/"
    assert args.csv == updater.PROJECT_ROOT / "data/opencode_go.csv"
    assert args.aa_csv == updater.PROJECT_ROOT / "data/results.csv"


@pytest.mark.parametrize("option", ["--skip-publish", "--publish-script"])
def test_publication_options_are_rejected(option: str) -> None:
    with pytest.raises(SystemExit):
        updater.parse_args([option])


@pytest.mark.parametrize(
    "value",
    [
        "",
        "2026-07-17",
        "2026-7-17T14:32:05Z",
        "2026-07-17T14:32:05+00:00",
        "2026-02-30T14:32:05Z",
    ],
)
def test_validate_scraped_at_rejects_noncanonical_or_invalid_values(value: str) -> None:
    with pytest.raises(ValueError):
        updater.validate_scraped_at(value)


def test_build_output_rows_applies_one_scrape_timestamp_to_every_row() -> None:
    rows = output_rows()

    assert updater.validate_scraped_at(SCRAPED_AT) == SCRAPED_AT
    assert {row["scraped_at"] for row in rows} == {SCRAPED_AT}


def test_async_main_writes_only_after_validation(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    aa_path = tmp_path / "results.csv"
    with aa_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(
            output_file, fieldnames=["model", "artificial_analysis_intelligence_index"]
        )
        writer.writeheader()
        writer.writerows(AA_ROWS)
    csv_path = tmp_path / "opencode_go.csv"
    calls: list[str] = []

    async def fake_scrape(
        url: str, *, timeout_ms: int, headed: bool
    ) -> tuple[list[str], list[list[str]]]:
        calls.append("scrape")
        return HEADERS, SOURCE_ROWS

    original_write = updater.write_csv

    def fake_write(rows: list[dict[str, str]], path: Path) -> None:
        calls.append("write")
        original_write(rows, path)

    def fake_current_scraped_at() -> str:
        calls.append("clock")
        return SCRAPED_AT


    monkeypatch.setattr(updater, "scrape_table", fake_scrape)
    monkeypatch.setattr(updater, "current_scraped_at", fake_current_scraped_at)
    monkeypatch.setattr(updater, "write_csv", fake_write)
    args = argparse.Namespace(
        url="example",
        csv=csv_path,
        aa_csv=aa_path,
        headed=False,
        timeout_ms=1,
    )
    asyncio.run(updater.async_main(args))
    assert calls == ["scrape", "clock", "write"]
    assert len(updater.read_aa_rows(csv_path)) == 17


def test_failed_join_preserves_existing_output(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    output = tmp_path / "opencode_go.csv"
    output.write_text("old data\n", encoding="utf-8")
    aa_path = tmp_path / "bad.csv"
    aa_path.write_text("model,wrong\nA,1\n", encoding="utf-8")

    async def fake_scrape(
        url: str, *, timeout_ms: int, headed: bool
    ) -> tuple[list[str], list[list[str]]]:
        return HEADERS, SOURCE_ROWS

    monkeypatch.setattr(updater, "scrape_table", fake_scrape)
    args = argparse.Namespace(
        url="example",
        csv=output,
        aa_csv=aa_path,
        headed=False,
        timeout_ms=1,
    )
    with pytest.raises(RuntimeError):
        asyncio.run(updater.async_main(args))
    assert output.read_text(encoding="utf-8") == "old data\n"

def test_invalid_scraped_at_preserves_existing_output(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    output = tmp_path / "opencode_go.csv"
    output.write_text("old data\n", encoding="utf-8")
    aa_path = tmp_path / "results.csv"
    aa_path.write_text(
        "model,artificial_analysis_intelligence_index\nA,1\n", encoding="utf-8"
    )

    async def fake_scrape(
        url: str, *, timeout_ms: int, headed: bool
    ) -> tuple[list[str], list[list[str]]]:
        return HEADERS, SOURCE_ROWS

    monkeypatch.setattr(updater, "scrape_table", fake_scrape)
    monkeypatch.setattr(updater, "current_scraped_at", lambda: "invalid")
    args = argparse.Namespace(
        url="example",
        csv=output,
        aa_csv=aa_path,
        headed=False,
        timeout_ms=1,
    )

    with pytest.raises(ValueError):
        asyncio.run(updater.async_main(args))

    assert output.read_text(encoding="utf-8") == "old data\n"



def test_direct_script_help_execution() -> None:
    result = subprocess.run(
        [sys.executable, "src/llm_comparison/update_opencode_go.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Update OpenCode Go pricing and value data." in result.stdout


def test_scrape_table_translates_missing_table_timeout_and_closes_browser(
    monkeypatch: MonkeyPatch,
) -> None:
    class SourceTimeoutError(Exception):
        pass

    class FakeLocator:
        @property
        def first(self) -> FakeLocator:
            return self

        async def wait_for(self, *, state: str, timeout: int) -> None:
            raise SourceTimeoutError

    class FakePage:
        async def goto(self, url: str, *, wait_until: str, timeout: int) -> None:
            return None

        def locator(self, selector: str) -> FakeLocator:
            return FakeLocator()

    class FakeBrowser:
        def __init__(self) -> None:
            self.closed = False

        async def new_page(self) -> FakePage:
            return FakePage()

        async def close(self) -> None:
            self.closed = True

    browser = FakeBrowser()

    class FakeChromium:
        async def launch(self, *, headless: bool) -> FakeBrowser:
            return browser

    class FakePlaywright:
        chromium = FakeChromium()

    class FakeContext:
        async def __aenter__(self) -> FakePlaywright:
            return FakePlaywright()

        async def __aexit__(self, *args: object) -> None:
            return None

    async_api = ModuleType("playwright.async_api")
    async_api.TimeoutError = SourceTimeoutError
    async_api.async_playwright = FakeContext
    monkeypatch.setitem(sys.modules, "playwright.async_api", async_api)

    with pytest.raises(RuntimeError, match="Could not find the OpenCode Go pricing"):
        asyncio.run(
            updater.scrape_table("https://example.test", timeout_ms=1, headed=False)
        )
    assert browser.closed


def test_snapshot_selector_rejects_wrong_ambiguous_empty_and_ragged_tables() -> None:
    valid: updater.TableSnapshot = {"headers": HEADERS, "rows": [SOURCE_ROWS[0]]}
    with pytest.raises(RuntimeError, match="Could not find"):
        updater.select_pricing_snapshot(
            [{"headers": ["Model", "Other"], "rows": [["A", "B"]]}]
        )
    with pytest.raises(RuntimeError, match="multiple"):
        updater.select_pricing_snapshot([valid, valid])
    with pytest.raises(RuntimeError, match="no data rows"):
        updater.select_pricing_snapshot([{"headers": HEADERS, "rows": []}])
    with pytest.raises(RuntimeError, match="expected 6"):
        updater.select_pricing_snapshot([{"headers": HEADERS, "rows": [["A", "$1"]]}])


def test_failed_scrape_preserves_existing_output(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    output = tmp_path / "opencode_go.csv"
    output.write_text("old data\n", encoding="utf-8")
    aa_path = tmp_path / "results.csv"
    aa_path.write_text(
        "model,artificial_analysis_intelligence_index\nA,1\n", encoding="utf-8"
    )

    async def failed_scrape(
        url: str, *, timeout_ms: int, headed: bool
    ) -> tuple[list[str], list[list[str]]]:
        raise RuntimeError("source unavailable")

    monkeypatch.setattr(updater, "scrape_table", failed_scrape)
    args = argparse.Namespace(
        url="example",
        csv=output,
        aa_csv=aa_path,
        headed=False,
        timeout_ms=1,
    )
    with pytest.raises(RuntimeError, match="source unavailable"):
        asyncio.run(updater.async_main(args))
    assert output.read_text(encoding="utf-8") == "old data\n"
