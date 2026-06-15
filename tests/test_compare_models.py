from pathlib import Path

from compare_models_core import (
    FINAL_SCORE,
    Column,
    exclude_zero_price_rows,
    json_ready_rows,
    pareto_flags,
    score_rows,
    write_html,
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

def test_metric_filter_selection_redraws_chart_and_2d_hides_3d_controls(
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
    hidden_3d_controls = [
        "resetCamera",
        "viewCube",
        "zoomIndicator",
    ]
    for element_id in hidden_3d_controls:
        assert (
            f'document.getElementById("{element_id}").hidden = '
            "categories.length !== 3"
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


def test_exclude_zero_price_rows_removes_zero_price_models() -> None:
    rows = [
        {"model": "free", "blended_usd_per_1m_tokens": "0.00"},
        {"model": "paid", "blended_usd_per_1m_tokens": "1.50"},
        {"model": "empty", "blended_usd_per_1m_tokens": ""},
    ]

    filtered = exclude_zero_price_rows(rows)

    assert [row["model"] for row in filtered] == ["paid", "empty"]


def test_exclude_zero_price_changes_percentile_scores(tmp_path: Path) -> None:
    rows = [
        {"model": "free", "quality": "50", "blended_usd_per_1m_tokens": "0.00"},
        {"model": "mid", "quality": "60", "blended_usd_per_1m_tokens": "1.00"},
        {"model": "top", "quality": "100", "blended_usd_per_1m_tokens": "2.00"},
    ]

    scored_with_free = score_rows(rows, ["quality"])
    scored_without_free = score_rows(exclude_zero_price_rows(rows), ["quality"])

    with_free_scores = {
        row["model"]: row[FINAL_SCORE] for row in scored_with_free
    }
    without_free_scores = {
        row["model"]: row[FINAL_SCORE] for row in scored_without_free
    }
    assert "free" not in without_free_scores
    assert with_free_scores["mid"] != without_free_scores["mid"]
    assert without_free_scores["top"] == 100.0
