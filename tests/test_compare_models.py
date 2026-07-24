import json
from pathlib import Path

import pytest

from llm_comparison.compare_models import validate_opencode_go_headers
from llm_comparison.compare_models_core import (
    FINAL_SCORE,
    Column,
    exclude_zero_price_rows,
    is_lower_better,
    json_ready_rows,
    opencode_go_payload,
    pareto_flags,
    resolve_category,
    score_rows,
    write_html,
)


def test_opencode_go_header_validation_requires_every_displayed_field() -> None:
    with pytest.raises(SystemExit, match="monthly_usage_usd"):
        validate_opencode_go_headers(
            [
                "model",
                "artificial_analysis_intelligence_index",
                "opencode_go_blended_usd_per_1m_tokens",
                "value_score",
            ]
        )


def test_opencode_go_header_validation_requires_scraped_at() -> None:
    with pytest.raises(SystemExit, match="scraped_at"):
        validate_opencode_go_headers(
            [
                "model",
                "artificial_analysis_intelligence_index",
                "input_price_usd_per_1m_tokens",
                "output_price_usd_per_1m_tokens",
                "cache_read_usd_per_1m_tokens",
                "cache_write_usd_per_1m_tokens",
                "opencode_go_blended_usd_per_1m_tokens",
                "long_context_blended_usd_per_1m_tokens",
                "monthly_usage_usd",
                "value_score",
            ]
        )


def test_pareto_flags_stay_aligned_for_duplicate_model_names() -> None:
    rows = [
        {"model": "duplicate", "quality": "10", "cost": "10"},
        {"model": "duplicate", "quality": "20", "cost": "20"},
        {"model": "winner", "quality": "30", "cost": "5"},
    ]

    scored = score_rows(rows, ["quality", "cost"])
    flags = pareto_flags(scored, ["quality", "cost"])
    ready = json_ready_rows(
        scored,
        [Column("model", "Model", False), Column(FINAL_SCORE, "Final Score", True)],
        ["quality", "cost"],
        flags,
    )

    assert len(ready) == 3
    assert [row["pareto"] for row in ready] == flags


def test_write_html_escapes_script_closing_tags(tmp_path: Path) -> None:
    output = tmp_path / "report.html"
    rows = [
        {
            "model": "</script><script>alert(1)</script>",
            "quality": "1",
            "_raw_values": {"quality": 1.0},
            FINAL_SCORE: 100.0,
        }
    ]

    write_html(
        output,
        rows,
        [Column("model", "Model", False), Column(FINAL_SCORE, "Final Score", True)],
        ["quality"],
        [],
    )

    html = output.read_text(encoding="utf-8")
    assert "</script><script>alert" not in html
    assert "<\\/script>" in html


def test_chart_type_uses_active_scoring_categories(tmp_path: Path) -> None:
    output = tmp_path / "report.html"
    rows = [
        {
            "model": "one",
            "quality": "1",
            "cost": "2",
            "_raw_values": {"quality": 1.0, "cost": 2.0, "speed": 3.0},
            FINAL_SCORE: 100.0,
        }
    ]

    write_html(
        output,
        rows,
        [Column("model", "Model", False), Column(FINAL_SCORE, "Final Score", True)],
        ["quality", "cost"],
        [{"optimal": True, "suboptimal": False}],
        ["quality", "cost", "speed"],
    )

    html = output.read_text(encoding="utf-8")
    assert '"categories": [{"key": "quality"' in html
    assert '"graphCategories": ["quality", "cost"]' in html
    assert "function chartCategories()" in html
    stale_chart_branch = (
        'payload.graphCategories.length === 2 ? "2D category comparison"'
    )
    assert stale_chart_branch not in html


def test_initial_bootstrap_applies_default_zero_price_filter(tmp_path: Path) -> None:
    output = tmp_path / "report.html"
    rows = [
        {
            "model": "free",
            "quality": "50",
            "cost_per_task": "0.00",
            "_raw_values": {"quality": 50.0, "cost_per_task": 0.0},
            FINAL_SCORE: 50.0,
        },
        {
            "model": "paid",
            "quality": "100",
            "cost_per_task": "1.00",
            "_raw_values": {"quality": 100.0, "cost_per_task": 1.0},
            FINAL_SCORE: 100.0,
        },
    ]

    write_html(
        output,
        rows,
        [
            Column("model", "Model", False),
            Column("cost_per_task", "Cost per Task", True),
            Column(FINAL_SCORE, "Final Score", True),
        ],
        ["quality"],
        [],
        ["quality", "cost_per_task"],
    )

    html = output.read_text(encoding="utf-8")
    initial_render = html[
        html.index("applyTheme(activeTheme());") : html.index(
            'fetchCsvFromPaths(["data/results.csv", "../data/results.csv"])'
        )
    ]

    assert "let excludeZeroPrice = true;" in html
    assert "applySelection();" in initial_render
    assert "renderTable();" not in initial_render
    assert "drawGraph();" not in initial_render


def test_3d_trend_renders_as_line_not_plane(tmp_path: Path) -> None:
    output = tmp_path / "report.html"
    rows = [
        {
            "model": "one",
            "quality": "1",
            "cost": "3",
            "speed": "2",
            "_raw_values": {"quality": 1.0, "cost": 3.0, "speed": 2.0},
            FINAL_SCORE: 10.0,
        },
        {
            "model": "two",
            "quality": "2",
            "cost": "2",
            "speed": "3",
            "_raw_values": {"quality": 2.0, "cost": 2.0, "speed": 3.0},
            FINAL_SCORE: 20.0,
        },
        {
            "model": "three",
            "quality": "3",
            "cost": "1",
            "speed": "4",
            "_raw_values": {"quality": 3.0, "cost": 1.0, "speed": 4.0},
            FINAL_SCORE: 30.0,
        },
    ]

    write_html(
        output,
        rows,
        [Column("model", "Model", False), Column(FINAL_SCORE, "Final Score", True)],
        ["quality", "cost", "speed"],
        [{"optimal": False, "suboptimal": False}] * 3,
    )

    html = output.read_text(encoding="utf-8")
    assert "function fit3DTrendLine(" in html
    assert "function drawTrendLine(" in html
    assert "function drawTrendPlane(" not in html


def test_3d_default_camera_starts_slightly_zoomed_in(tmp_path: Path) -> None:
    output = tmp_path / "report.html"
    rows = [
        {
            "model": "one",
            "quality": "1",
            "cost": "3",
            "speed": "2",
            "_raw_values": {"quality": 1.0, "cost": 3.0, "speed": 2.0},
            FINAL_SCORE: 10.0,
        }
    ]

    write_html(
        output,
        rows,
        [Column("model", "Model", False), Column(FINAL_SCORE, "Final Score", True)],
        ["quality", "cost", "speed"],
        [{"optimal": True, "suboptimal": False}],
    )

    html = output.read_text(encoding="utf-8")
    expected_camera = (
        "const initialCamera = { rotationX: 0.62, rotationY: 0.78, zoom: 1.25 }"
    )
    assert expected_camera in html


def test_3d_zoom_indicator_is_rendered_and_updated(tmp_path: Path) -> None:
    output = tmp_path / "report.html"
    rows = [
        {
            "model": "one",
            "quality": "1",
            "cost": "3",
            "speed": "2",
            "_raw_values": {"quality": 1.0, "cost": 3.0, "speed": 2.0},
            FINAL_SCORE: 10.0,
        }
    ]

    write_html(
        output,
        rows,
        [Column("model", "Model", False), Column(FINAL_SCORE, "Final Score", True)],
        ["quality", "cost", "speed"],
        [{"optimal": True, "suboptimal": False}],
    )

    html = output.read_text(encoding="utf-8")
    assert 'id="zoomIndicator"' in html
    assert "top: 140px;" in html
    assert "function updateZoomIndicator()" in html
    assert "zoomIndicator.textContent = `${zoom.toFixed(2)}x`" in html


def test_2d_chart_supports_zoom_pan_reset_and_zoom_number(tmp_path: Path) -> None:
    output = tmp_path / "report.html"
    rows = [
        {
            "model": "one",
            "quality": "1",
            "cost": "3",
            "_raw_values": {"quality": 1.0, "cost": 3.0},
            FINAL_SCORE: 10.0,
        },
        {
            "model": "two",
            "quality": "2",
            "cost": "1",
            "_raw_values": {"quality": 2.0, "cost": 1.0},
            FINAL_SCORE: 9.0,
        },
    ]

    write_html(
        output,
        rows,
        [Column("model", "Model", False), Column(FINAL_SCORE, "Final Score", True)],
        ["quality", "cost"],
        [
            {"optimal": True, "suboptimal": False},
            {"optimal": False, "suboptimal": True},
        ],
    )

    html = output.read_text(encoding="utf-8")
    assert 'id="resetView"' in html
    assert 'id="zoomIndicator"' in html
    reset_view_visibility = (
        'document.getElementById("resetView").hidden = '
        "![2, 3].includes(categories.length)"
    )
    zoom_indicator_visibility = (
        'document.getElementById("zoomIndicator").hidden = '
        "![2, 3].includes(categories.length)"
    )
    assert reset_view_visibility in html
    assert zoom_indicator_visibility in html
    assert ".chart-wrap.is-2d #chart" in html
    assert ".chart-wrap.is-2d .zoom-indicator {\n      top: 12px;\n    }" in html
    assert (
        "const initial2DView = { minX: ranges[0].min, maxX: ranges[0].max, "
        "minY: ranges[1].min, maxY: ranges[1].max, zoom: 1 }" in html
    )
    assert "function reset2DView()" in html
    assert "function update2DZoomIndicator()" in html
    assert "zoomIndicator.textContent = `${view2D.zoom.toFixed(2)}x`" in html
    assert "function zoom2DAt(" in html
    assert "function pan2DBy(" in html
    assert "function pointIn2DView(row)" in html
    assert "plottableRows(categories).filter(pointIn2DView).map" in html
    hover_clear = (
        'hover = null;\n        tooltip.style.display = "none";\n        render();'
    )
    assert hover_clear in html
    assert "const tapMoveTolerance = 8" in html
    assert "function show2DTooltip(clientPoint)" in html
    assert "if (shouldIgnoreSyntheticMouse()) return;" in html
    assert "const wasTap = changedTouch && touchStart && !touchMoved" in html
    assert 'trackChartListener(canvas, "wheel"' in html
    assert (
        'trackChartListener(document.getElementById("resetView"), "click", reset2DView)'
        in html
    )


def test_pareto_chart_styles_prioritize_optimal_when_flags_overlap(
    tmp_path: Path,
) -> None:
    output = tmp_path / "report.html"
    rows = [
        {
            "model": "overlap",
            "quality": "10",
            "cost": "1",
            "speed": "5",
            "_raw_values": {"quality": 10.0, "cost": 1.0, "speed": 5.0},
            FINAL_SCORE: 100.0,
        }
    ]

    write_html(
        output,
        rows,
        [Column("model", "Model", False), Column(FINAL_SCORE, "Final Score", True)],
        ["quality", "cost", "speed"],
        [{"optimal": True, "suboptimal": True}],
    )

    html = output.read_text(encoding="utf-8")
    optimal_label_priority = (
        'ctx.fillStyle = point.row.pareto.optimal ? cssColor("--chart-optimal-label") '
        ': cssColor("--chart-suboptimal-label");'
    )
    optimal_opacity_priority = (
        "ctx.globalAlpha = point.row.pareto.optimal ? 0.92 : "
        "point.row.pareto.suboptimal ? 0.78 : 0.92;"
    )

    assert '"pareto": {"optimal": true, "suboptimal": true}' in html
    assert html.count(optimal_label_priority) == 2
    assert optimal_opacity_priority in html


def test_report_exports_images_and_renders_separate_pareto_chart(
    tmp_path: Path,
) -> None:
    output = tmp_path / "report.html"
    rows = [
        {
            "model": "winner",
            "quality": "10",
            "cost": "1",
            "_raw_values": {"quality": 10.0, "cost": 1.0},
            FINAL_SCORE: 100.0,
        },
        {
            "model": "other",
            "quality": "5",
            "cost": "2",
            "_raw_values": {"quality": 5.0, "cost": 2.0},
            FINAL_SCORE: 50.0,
        },
    ]

    write_html(
        output,
        rows,
        [Column("model", "Model", False), Column(FINAL_SCORE, "Final Score", True)],
        ["quality", "cost"],
        [
            {"optimal": True, "suboptimal": False},
            {"optimal": False, "suboptimal": True},
        ],
    )

    html = output.read_text(encoding="utf-8")
    table_index = html.index('class="table-section"')
    pareto_index = html.index('id="paretoChartSection"')
    about_index = html.index('id="aboutTitle"')

    assert table_index < pareto_index < about_index
    assert 'id="saveChart"' in html
    assert 'id="saveTable"' in html
    assert 'id="saveParetoChart"' in html
    assert 'id="paretoChart"' in html
    assert "plottableRows(categories).filter(row => row.pareto.optimal)" in html
    assert "function exportChart(canvasId, title)" in html
    assert "function exportTable()" in html
    assert "for (const [rowIndex, row] of [...table.rows].entries())" in html
    assert "downloadCanvas(output, \"llm-comparison-results.png\")" in html
    assert ".table-section {\n      margin-bottom: 16px;" in html
    info_spacing = (
        ".info-wrap {\n"
        "      color: var(--control-ink);\n"
        "      margin-top: 16px;"
    )
    assert info_spacing in html


def test_mobile_3d_chart_supports_touch_controls_and_fullscreen_fallback(
    tmp_path: Path,
) -> None:
    output = tmp_path / "report.html"
    rows = [
        {
            "model": "one",
            "quality": "1",
            "cost": "3",
            "speed": "2",
            "_raw_values": {"quality": 1.0, "cost": 3.0, "speed": 2.0},
            FINAL_SCORE: 10.0,
        }
    ]

    write_html(
        output,
        rows,
        [Column("model", "Model", False), Column(FINAL_SCORE, "Final Score", True)],
        ["quality", "cost", "speed"],
        [{"optimal": True, "suboptimal": False}],
    )

    html = output.read_text(encoding="utf-8")
    assert 'class="chart-scroll" id="chartScroll"' in html
    assert ".chart-wrap.is-3d #chart" in html
    assert "touch-action: none;" in html
    assert 'trackChartListener(canvas, "touchmove"' in html
    assert "pinchDistance" in html
    assert "function enterFullscreenFallback()" in html
    assert "section.requestFullscreen" in html
    chart_section_start = html.index('<section class="chart-wrap" id="chartSection"')
    chart_section = html[
        chart_section_start : html.index("</section>", chart_section_start)
    ]
    assert '<div class="tooltip" id="tooltip"></div>' in chart_section


def test_report_supports_shareable_ordered_metric_urls(tmp_path: Path) -> None:
    output = tmp_path / "report.html"
    rows = [
        {
            "model": "one",
            "quality": "1",
            "cost": "2",
            "_raw_values": {"quality": 1.0, "cost": 2.0},
            FINAL_SCORE: 100.0,
        }
    ]

    write_html(
        output,
        rows,
        [Column("model", "Model", False), Column(FINAL_SCORE, "Final Score", True)],
        ["quality"],
        [{"optimal": True, "suboptimal": False}],
        ["quality", "cost"],
    )

    html = output.read_text(encoding="utf-8")
    assert 'params.get("metrics")' in html
    assert "function orderedValidMetricKeys(keys)" in html
    assert 'url.searchParams.set("metrics", selectedCategories.join(","))' in html
    assert "applySelection({ syncUrl: true })" in html


def test_report_can_reset_to_original_metric_selection(tmp_path: Path) -> None:
    output = tmp_path / "report.html"
    rows = [
        {
            "model": "one",
            "quality": "1",
            "cost": "2",
            "speed": "3",
            "_raw_values": {"quality": 1.0, "cost": 2.0, "speed": 3.0},
            FINAL_SCORE: 100.0,
        }
    ]

    write_html(
        output,
        rows,
        [Column("model", "Model", False), Column(FINAL_SCORE, "Final Score", True)],
        ["cost", "quality", "speed"],
        [{"optimal": True, "suboptimal": False}],
        ["quality", "cost", "speed"],
    )

    reset_listener = (
        'document.getElementById("resetMetrics").addEventListener('
        '"click", resetMetrics)'
    )
    html = output.read_text(encoding="utf-8")
    assert 'id="resetMetrics"' in html
    assert "const initialSelectedCategories = payload.categories.map" in html
    assert "let selectedCategories = initialSelectedCategories.slice();" in html
    assert "function resetMetrics()" in html
    assert reset_listener in html


def test_metric_filter_selection_redraws_chart_and_toggles_chart_controls(
    tmp_path: Path,
) -> None:
    output = tmp_path / "report.html"
    rows = [
        {
            "model": "one",
            "quality": "1",
            "cost": "2",
            "_raw_values": {"quality": 1.0, "cost": 2.0, "speed": 3.0},
            FINAL_SCORE: 100.0,
        }
    ]

    write_html(
        output,
        rows,
        [Column("model", "Model", False), Column(FINAL_SCORE, "Final Score", True)],
        ["quality", "cost"],
        [{"optimal": True, "suboptimal": False}],
        ["quality", "cost", "speed"],
    )

    html = output.read_text(encoding="utf-8")
    assert "resetChartCanvas();\n      drawGraph();" in html
    reset_view_visibility = (
        'document.getElementById("resetView").hidden = '
        "![2, 3].includes(categories.length)"
    )
    zoom_indicator_visibility = (
        'document.getElementById("zoomIndicator").hidden = '
        "![2, 3].includes(categories.length)"
    )
    assert reset_view_visibility in html
    assert zoom_indicator_visibility in html
    hidden_3d_controls = [
        "viewCube",
    ]
    for element_id in hidden_3d_controls:
        assert (
            f'document.getElementById("{element_id}").hidden = categories.length !== 3'
        ) in html


def test_report_supports_persisted_theme_preference(tmp_path: Path) -> None:
    output = tmp_path / "report.html"
    rows = [
        {
            "model": "one",
            "quality": "1",
            "_raw_values": {"quality": 1.0},
            FINAL_SCORE: 100.0,
        }
    ]

    write_html(
        output,
        rows,
        [Column("model", "Model", False), Column(FINAL_SCORE, "Final Score", True)],
        ["quality"],
        [{"optimal": True, "suboptimal": False}],
    )

    html = output.read_text(encoding="utf-8")
    assert 'id="themeToggle"' in html
    assert "llmComparison.theme" in html
    assert "window.localStorage.getItem(themeStorageKey)" in html
    assert "window.localStorage.setItem(themeStorageKey, theme)" in html
    assert "prefers-color-scheme: dark" in html
    assert 'html[data-theme="dark"]' in html
    assert (
        'document.getElementById("themeToggle").addEventListener("click", toggleTheme)'
        in html
    )


def test_context_window_is_not_a_core_metric(tmp_path: Path) -> None:
    output = tmp_path / "report.html"
    rows = [
        {
            "model": "one",
            "context_window_tokens": "128000",
            "quality": "1",
            "_raw_values": {"context_window_tokens": 128000.0, "quality": 1.0},
            FINAL_SCORE: 100.0,
        }
    ]

    write_html(
        output,
        rows,
        [Column("model", "Model", False), Column(FINAL_SCORE, "Final Score", True)],
        ["quality"],
        [{"optimal": True, "suboptimal": False}],
        ["context_window_tokens", "quality"],
    )

    html = output.read_text(encoding="utf-8")
    core_keys_start = html.index("const coreCategoryKeys = [")
    core_keys_end = html.index("];", core_keys_start)
    core_keys = html[core_keys_start:core_keys_end]

    assert '"context_window_tokens"' not in core_keys


def test_price_alias_resolves_to_lower_is_better_task_cost() -> None:
    headers = ["model", "cost_per_task"]

    resolved = resolve_category("price", headers)

    assert resolved == "cost_per_task"
    assert is_lower_better(resolved)


def test_exclude_zero_price_rows_removes_zero_price_models() -> None:
    rows = [
        {"model": "free", "cost_per_task": "0.00"},
        {"model": "paid", "cost_per_task": "1.50"},
        {"model": "empty", "cost_per_task": ""},
    ]

    filtered = exclude_zero_price_rows(rows)

    assert [row["model"] for row in filtered] == ["paid", "empty"]


def test_low_quality_model_does_not_change_existing_scores() -> None:
    rows = [
        {"model": "mid", "quality": "60"},
        {"model": "top", "quality": "100"},
    ]
    rows_with_trash = [{"model": "trash", "quality": "1"}, *rows]

    base_scores = {
        row["model"]: row[FINAL_SCORE] for row in score_rows(rows, ["quality"])
    }
    expanded_scores = {
        row["model"]: row[FINAL_SCORE]
        for row in score_rows(rows_with_trash, ["quality"])
    }

    assert expanded_scores["mid"] == base_scores["mid"]
    assert expanded_scores["top"] == base_scores["top"]


def test_relative_geometric_score_uses_actual_metric_ratios() -> None:
    rows = [
        {
            "model": "balanced",
            "artificial_analysis_intelligence_index": "50",
            "cost_per_task": "1",
        },
        {
            "model": "expensive",
            "artificial_analysis_intelligence_index": "100",
            "cost_per_task": "4",
        },
        {
            "model": "efficient",
            "artificial_analysis_intelligence_index": "25",
            "cost_per_task": "0.25",
        },
    ]

    scored = score_rows(
        rows,
        [
            "artificial_analysis_intelligence_index",
            "cost_per_task",
        ],
    )

    assert [row["model"] for row in scored] == ["efficient", "balanced", "expensive"]
    assert scored[0][FINAL_SCORE] == pytest.approx(141.4214)
    assert scored[1][FINAL_SCORE] == 100.0
    assert scored[2][FINAL_SCORE] == pytest.approx(70.7107)


def test_nonpositive_selected_metric_is_excluded() -> None:
    rows = [
        {"model": "free", "cost_per_task": "0"},
        {"model": "paid", "cost_per_task": "1"},
    ]

    scored = score_rows(rows, ["cost_per_task"])

    assert [row["model"] for row in scored] == ["paid"]
    assert scored[0][FINAL_SCORE] == 100.0


def embedded_payload(html: str) -> dict[str, object]:
    start = html.index("const payload = ") + len("const payload = ")
    end = html.index(";\n    const dataUpdated", start)
    return json.loads(html[start:end])


def test_write_html_embeds_dedicated_opencode_go_payload(tmp_path: Path) -> None:
    output = tmp_path / "report.html"
    comparison_rows = [
        {
            "model": "comparison",
            "quality": "1",
            "_raw_values": {"quality": 1.0},
            FINAL_SCORE: 100.0,
        }
    ]
    go_rows = [
        {
            "model": "Ranked </script>",
            "artificial_analysis_intelligence_index": "40",
            "input_price_usd_per_1m_tokens": "0.14",
            "output_price_usd_per_1m_tokens": "0.28",
            "cache_read_usd_per_1m_tokens": "0.0028",
            "cache_write_usd_per_1m_tokens": "",
            "opencode_go_blended_usd_per_1m_tokens": "0.05796",
            "long_context_blended_usd_per_1m_tokens": "",
            "monthly_usage_usd": "60",
            "value_score": "52.36871623200863025402473033",
            "scraped_at": "2026-07-17T14:32:05Z",
        },
        {
            "model": "Unranked",
            "artificial_analysis_intelligence_index": "",
            "input_price_usd_per_1m_tokens": "0.30",
            "output_price_usd_per_1m_tokens": "1.20",
            "cache_read_usd_per_1m_tokens": "0.06",
            "cache_write_usd_per_1m_tokens": "0.375",
            "opencode_go_blended_usd_per_1m_tokens": "0.222",
            "long_context_blended_usd_per_1m_tokens": "",
            "monthly_usage_usd": "60",
            "value_score": "",
            "scraped_at": "2026-07-17T14:32:05Z",
        },
    ]
    write_html(
        output,
        comparison_rows,
        [Column("model", "Model", False), Column(FINAL_SCORE, "Final Score", True)],
        ["quality"],
        [],
        opencode_go_rows=go_rows,
    )

    html = output.read_text(encoding="utf-8")
    payload = embedded_payload(html)
    go = payload["openCodeGo"]
    assert set(go) == {
        "columns",
        "rows",
        "categories",
        "graphCategories",
        "sourceUrl",
        "formula",
        "scrapedAt",
    }
    assert [column["label"] for column in go["columns"]] == [
        "Model",
        "Artificial Analysis Intelligence Index",
        "Input",
        "Output",
        "Cached Read",
        "Cached Write",
        "Blended Price",
        ">256K Blended Price",
        "Usage",
        "Cost-adjusted intelligence",
    ]
    assert all(column["key"] != "scraped_at" for column in go["columns"])
    ranked, unranked = go["rows"]
    assert ranked["score"] == 52.36871623200863
    assert ranked["cells"]["value_score"] == {
        "display": "52.37",
        "sort": 52.36871623200863,
    }
    assert (
        ranked["cells"]["opencode_go_blended_usd_per_1m_tokens"]["display"]
        == "$0.05796"
    )
    assert ranked["cells"]["monthly_usage_usd"]["display"] == "$60"
    assert unranked["score"] is None
    assert (
        unranked["cells"]["artificial_analysis_intelligence_index"]["display"]
        == "Unranked"
    )
    assert unranked["cells"]["value_score"]["display"] == "Unranked"
    assert unranked["graph"] == {}
    assert unranked["pareto"] == {"optimal": False, "suboptimal": False}
    assert go["categories"] == [
        {
            "key": "opencode_go_blended_usd_per_1m_tokens",
            "label": "OpenCode Go blended price ($/1M tokens)",
            "lowerIsBetter": True,
        },
        {
            "key": "artificial_analysis_intelligence_index",
            "label": "Artificial Analysis Intelligence Index",
            "lowerIsBetter": False,
        },
    ]
    assert go["graphCategories"] == [
        "opencode_go_blended_usd_per_1m_tokens",
        "artificial_analysis_intelligence_index",
    ]
    assert go["sourceUrl"] == "https://opencode.ai/docs/go/"
    assert go["formula"] == "(7 × cached read + 2 × input + output) ÷ 10"
    assert go["scrapedAt"] == "2026-07-17T14:32:05Z"
    assert "Ranked <\\/script>" in html
    assert "<\\/script>" in html


@pytest.mark.parametrize(
    "rows",
    [
        [{"scraped_at": ""}],
        [{"scraped_at": "2026-7-17T14:32:05Z"}],
        [{"scraped_at": "2026-02-30T14:32:05Z"}],
        [
            {"scraped_at": "2026-07-17T14:32:05Z"},
            {"scraped_at": "2026-07-17T14:32:06Z"},
        ],
    ],
)
def test_opencode_go_payload_rejects_invalid_freshness(
    rows: list[dict[str, str]],
) -> None:
    with pytest.raises(ValueError):
        opencode_go_payload(rows)


def test_report_contains_semantic_navigation_and_go_bootstrap(tmp_path: Path) -> None:
    output = tmp_path / "report.html"
    rows = [
        {
            "model": "one",
            "quality": "1",
            "_raw_values": {"quality": 1.0},
            FINAL_SCORE: 100.0,
        }
    ]
    write_html(
        output,
        rows,
        [Column("model", "Model", False), Column(FINAL_SCORE, "Final Score", True)],
        ["quality"],
        [],
    )
    html = output.read_text(encoding="utf-8")
    assert '<nav class="view-nav" aria-label="Report views">' in html
    assert 'href="./index.html">Comparison</a>' in html
    assert 'href="?view=opencode-go">OpenCode Go value</a>' in html
    assert 'get("view") === "opencode-go"' in html
    assert (
        'fetchCsvFromPaths(["data/opencode_go.csv", "../data/opencode_go.csv"])' in html
    )
    assert "initializeGoFromCsv(parseCsv(text))" in html
    assert 'window.location.protocol !== "file:"' in html
    assert 'id="dataFreshness">Data updated: ' in html
    assert "`OpenCode Go pricing scraped: ${payload.scrapedAt}`" in html
    assert '[...payload.columns.map(column => column.key), "scraped_at"]' in html
    assert "payload.scrapedAt = scrapedAt;" in html
    assert (
        "Usage and cached-write prices are displayed but excluded from the score."
        in html
    )
    assert (
        "Cost-adjusted intelligence = Intelligence − 10 × log₁₀"
        "(blended price ÷ $1 per 1M tokens)." in html
    )
    assert "A 10-point Intelligence gain offsets a 10× higher blended price." in html
    assert "ranked by cost-adjusted intelligence" in html
    assert '"Cost-adjusted intelligence" : "Final Score"' in html
    go_bootstrap = html[
        html.index(
            "if (isOpenCodeGoView) {", html.index("applyTheme(activeTheme());")
        ) :
    ]
    assert "initializeEmbeddedGo();" in go_bootstrap
    assert "applySelection();" not in go_bootstrap.split("} else {", 1)[0]
