from pathlib import Path

from compare_models_core import (
    FINAL_SCORE,
    Column,
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
