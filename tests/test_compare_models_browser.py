from __future__ import annotations

import json
import socket
import subprocess
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast

import pytest
from playwright.sync_api import Browser, Page, sync_playwright

from llm_comparison.compare_models_core import (
    DISPLAY_LABELS,
    FINAL_SCORE,
    Column,
    pareto_flags,
    score_rows,
    write_html,
)

INTELLIGENCE = "artificial_analysis_intelligence_index"
COST = "cost_per_task"
SPEED = "median_tokens_per_second"
FIXTURE_NAMES = [
    "Reference",
    "Higher intelligence",
    *[f"Crowded Pareto {index:02d}" for index in range(1, 13)],
]


@pytest.fixture(scope="session")
def chromium_server(tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    with sync_playwright() as playwright:
        executable = playwright.chromium.executable_path
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = cast(int, listener.getsockname()[1])
    user_data = tmp_path_factory.mktemp("chromium-profile")
    process = subprocess.Popen(
        [
            executable,
            "--headless",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            f"--remote-debugging-port={port}",
            f"--user-data-dir={user_data}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    endpoint = f"http://127.0.0.1:{port}"
    try:
        for _ in range(100):
            try:
                with urllib.request.urlopen(f"{endpoint}/json/version", timeout=0.2):
                    break
            except urllib.error.URLError as error:
                if process.poll() is not None:
                    raise RuntimeError(
                        "Session Chromium exited before CDP was ready"
                    ) from error
                time.sleep(0.05)
        else:
            raise RuntimeError("Session Chromium CDP endpoint did not become ready")
        yield endpoint
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


@pytest.fixture
def chromium_browser(chromium_server: str) -> Iterator[Browser]:
    with sync_playwright() as playwright:
        yield playwright.chromium.connect_over_cdp(chromium_server)


@pytest.fixture(scope="session")
def comparison_report(tmp_path_factory: pytest.TempPathFactory) -> Path:
    source_rows = [
        {
            "model": "Reference",
            INTELLIGENCE: "50",
            COST: "1",
            SPEED: "50",
        },
        {
            "model": "Higher intelligence",
            INTELLIGENCE: "100",
            COST: "2",
            SPEED: "100",
        },
        *[
            {
                "model": f"Crowded Pareto {index:02d}",
                INTELLIGENCE: "50",
                COST: "1",
                SPEED: "50",
            }
            for index in range(1, 13)
        ],
    ]
    rows = score_rows(source_rows, [INTELLIGENCE, COST])
    for row in rows:
        cast(dict[str, float], row["_raw_values"])[SPEED] = float(row[SPEED])
    flags = pareto_flags(rows, [INTELLIGENCE, COST])
    output = tmp_path_factory.mktemp("browser-report") / "index.html"
    write_html(
        output,
        rows,
        [
            Column("model", "Model", False),
            Column(INTELLIGENCE, DISPLAY_LABELS[INTELLIGENCE], True),
            Column(COST, DISPLAY_LABELS[COST], True),
            Column(FINAL_SCORE, "Final Score", True),
        ],
        [INTELLIGENCE, COST],
        flags,
        [INTELLIGENCE, COST, SPEED],
    )
    return output


def _instrument_model_labels(page: Page, model_names: set[str]) -> list[str]:
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"page: {error}"))
    page.on(
        "console",
        lambda message: errors.append(f"console: {message.text}")
        if message.type == "error"
        else None,
    )
    encoded_names = json.dumps(sorted(model_names))
    page.add_init_script(
        script=f"""
          (() => {{
            const modelNames = new Set({encoded_names});
            window.__modelLabelLog = [];
            const originalFillText = CanvasRenderingContext2D.prototype.fillText;
            CanvasRenderingContext2D.prototype.fillText =
              function(text, x, y, maxWidth) {{
              if (modelNames.has(String(text))) {{
                window.__modelLabelLog.push({{
                  canvasId: this.canvas.id,
                  text: String(text),
                  x,
                  y,
                  font: this.font,
                }});
              }}
              return originalFillText.call(this, text, x, y, maxWidth);
            }};
          }})();
        """
    )
    return errors


def _open_report(page: Page, report: Path) -> None:
    page.goto(report.resolve().as_uri(), wait_until="load")
    page.locator("#resultsTable tbody tr").first.wait_for()
    page.wait_for_function(
        "typeof chartRender === 'function' && "
        "typeof paretoRender === 'function'"
    )


def _painted_names(page: Page) -> dict[str, set[str]]:
    entries = cast(list[dict[str, Any]], page.evaluate("window.__modelLabelLog"))
    return {
        canvas_id: {
            cast(str, entry["text"])
            for entry in entries
            if entry["canvasId"] == canvas_id
        }
        for canvas_id in ("chart", "paretoChart")
    }


def _clear_and_render(page: Page) -> None:
    page.evaluate(
        """() => {
          window.__modelLabelLog = [];
          chartRender();
          paretoRender();
        }"""
    )


def _assert_all_names_painted(page: Page, expected: set[str]) -> None:
    painted = _painted_names(page)
    assert painted["chart"] == expected
    assert painted["paretoChart"] == expected


def _assert_no_browser_errors(errors: list[str]) -> None:
    assert errors == []


def test_layout_model_labels_uses_callouts_without_overlap(
    chromium_browser: Browser,
    comparison_report: Path,
) -> None:
    page = chromium_browser.new_page(viewport={"width": 800, "height": 500})
    errors = _instrument_model_labels(page, set(FIXTURE_NAMES))
    _open_report(page, comparison_report)

    result = cast(
        dict[str, Any],
        page.evaluate(
            """() => {
              const canvas = document.createElement('canvas');
              canvas.width = 640;
              canvas.height = 320;
              const ctx = canvas.getContext('2d');
              const points = Array.from({ length: 9 }, (_, index) => ({
                row: {
                  model: `Coincident optimal ${String(index + 1).padStart(2, '0')}`,
                  pareto: { optimal: true, suboptimal: false },
                },
                x: 320,
                y: 160,
                radius: 5.5,
                fillStyle: '#000',
                alpha: 1,
              }));
              const layout = layoutModelLabels(
                ctx,
                points,
                { left: 8, right: 632, top: 8, bottom: 312 },
              );
              return {
                hidden: layout.hidden.length,
                placements: layout.placements.map(placement => ({
                  bounds: placement.bounds,
                  fontSize: placement.fontSize,
                  leader: placement.leader,
                })),
              };
            }"""
        ),
    )

    placements = cast(list[dict[str, Any]], result["placements"])
    assert result["hidden"] == 0
    assert len(placements) == 9
    assert {placement["fontSize"] for placement in placements} in ({12}, {10})
    assert min(cast(int, placement["fontSize"]) for placement in placements) >= 10
    assert any(placement["leader"] is not None for placement in placements)
    for placement in placements:
        bounds = cast(dict[str, float], placement["bounds"])
        assert bounds["left"] >= 8
        assert bounds["right"] <= 632
        assert bounds["top"] >= 8
        assert bounds["bottom"] <= 312
    for index, left_placement in enumerate(placements):
        left = cast(dict[str, float], left_placement["bounds"])
        for right_placement in placements[index + 1 :]:
            right = cast(dict[str, float], right_placement["bounds"])
            separated = (
                left["right"] + 4 < right["left"]
                or right["right"] + 4 < left["left"]
                or left["bottom"] + 4 < right["top"]
                or right["bottom"] + 4 < left["top"]
            )
            assert separated
    _assert_no_browser_errors(errors)
    page.close()


def test_weighted_ranking_and_pareto_labels_render_in_2d_and_3d(
    chromium_browser: Browser,
    comparison_report: Path,
) -> None:
    expected = set(FIXTURE_NAMES)
    page = chromium_browser.new_page(viewport={"width": 1280, "height": 900})
    errors = _instrument_model_labels(page, expected)
    _open_report(page, comparison_report)

    first_row_cells = page.locator("#resultsTable tbody tr").first.locator("td")
    assert first_row_cells.first.inner_text() == "Higher intelligence"
    assert first_row_cells.last.inner_text() == "125.99"

    for width in (1280, 390):
        page.set_viewport_size({"width": width, "height": 900})
        _clear_and_render(page)
        _assert_all_names_painted(page, expected)
        for canvas_id, reset_id in (
            ("chart", "resetView"),
            ("paretoChart", "resetParetoView"),
        ):
            page.evaluate("window.__modelLabelLog = []")
            page.locator(f"#{canvas_id}").dispatch_event("wheel", {"deltaY": -120})
            _clear_and_render(page)
            _assert_all_names_painted(page, expected)
            page.evaluate("window.__modelLabelLog = []")
            page.locator(f"#{reset_id}").click()
            _clear_and_render(page)
            _assert_all_names_painted(page, expected)

    page.get_by_role("button", name="Median (Tokens/s) ↑", exact=True).click()
    page.locator("#runComparison").click()
    page.locator("#chartSection.is-3d").wait_for()
    _clear_and_render(page)
    _assert_all_names_painted(page, expected)
    _assert_no_browser_errors(errors)
    page.close()


def _embedded_payload(path: Path) -> dict[str, Any]:
    html = path.read_text(encoding="utf-8")
    start = html.index("const payload = ") + len("const payload = ")
    end = html.index(";\n    const dataUpdated", start)
    return cast(dict[str, Any], json.loads(html[start:end]))


def test_generated_public_report_shows_every_current_pareto_label(
    chromium_browser: Browser,
) -> None:
    report = Path(__file__).parents[1] / "public" / "index.html"
    payload = _embedded_payload(report)
    expected = {
        cast(str, row["model"])
        for row in cast(list[dict[str, Any]], payload["rows"])
        if cast(dict[str, bool], row["pareto"])["optimal"]
    }
    page = chromium_browser.new_page(viewport={"width": 1440, "height": 900})
    errors = _instrument_model_labels(page, expected)

    for width in (1440, 390):
        page.set_viewport_size({"width": width, "height": 900})
        _open_report(page, report)
        _clear_and_render(page)
        _assert_all_names_painted(page, expected)
        entries = cast(list[dict[str, Any]], page.evaluate("window.__modelLabelLog"))
        for canvas_id in ("chart", "paretoChart"):
            coordinates = {
                cast(str, entry["text"]): (entry["x"], entry["y"])
                for entry in entries
                if entry["canvasId"] == canvas_id
                and entry["text"]
                in {"Grok 4.5 (high)", "GPT-5.6 Sol (medium)"}
            }
            assert coordinates["Grok 4.5 (high)"] != coordinates[
                "GPT-5.6 Sol (medium)"
            ]

    _assert_no_browser_errors(errors)
    page.close()
