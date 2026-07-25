# Implementation Summary

## Plan

- Approved plan: `.omp/worktree-flow/20260725-133922-intelligence-weighted-rankings-and-persistent-pareto/plan.md`
- Worktree: `/mnt/c/Users/joesa/code/llm-comparison-intelligence-weighted-rankings-and-persistent-pareto`
- Branch: `feature/intelligence-weighted-rankings-and-persistent-pareto`
- Commit: `72c0c4c6d4e2ae81b97e8793a8560ffd2267c616` (`Implement intelligence-weighted rankings and Pareto callouts`)

## Changed Files

- `README.md`
- `public/index.html`
- `src/llm_comparison/compare_models_core.py`
- `src/llm_comparison/compare_models_template.py`
- `tests/test_compare_models.py`
- `tests/test_compare_models_browser.py` (new)

`.omp/handoff/` and `.omp/worktree-flow/` remain untracked workflow artifacts and were not committed.

## Behavior Changes

### Intelligence-weighted scoring

- Added the policy constant `SCORING_WEIGHTS = {"artificial_analysis_intelligence_index": 2.0}`.
- Python scoring now computes a weighted relative geometric mean. Intelligence receives weight 2; every unlisted selected metric defaults to weight 1.
- Serialized the policy as `payload.scoringWeights`; browser reranking consumes that payload map through the existing shared `relativeGeometricScore` path.
- Left Pareto dominance and the OpenCode Go `value_score` pipeline unchanged.
- Updated the About panel and README scoring explanation.
- Regenerated `public/index.html` from the canonical template for `price intelligence`.
- Local `file://` comparison reports now use embedded data without attempting unsupported CSV fetches; non-file reports retain CSV refresh behavior.

### Persistent Pareto labels

- Added shared `drawProjectedPoint`, `layoutModelLabels`, and `drawModelLabels` helpers used by both 2D and 3D charts, including the Pareto-only chart through its existing renderer routing.
- Label layout is computed before painting and orders optimal models deterministically by available nearby candidates, measured name width, then model name.
- Nearby placements use the existing eight positions and score label, marker, trend/leader collisions in deterministic tuples.
- Optimal labels that cannot use nearby positions move to contained left/right callout lanes with solid leaders. Layout retries all optimal names uniformly at 10px if 12px cannot place every name.
- The pathological 10px fallback chooses the least-colliding callout rather than hiding an optimal name. Suboptimal labels may still be hidden when no collision-free nearby placement exists.
- Leaders render below redrawn markers and haloed text. 3D label layout excludes projected points outside the viewport by more than their marker radius.
- Layout recomputes through the existing render callbacks on resize, pan/zoom, reset, rotation, metric changes, theme/fullscreen redraws, and exports.

### Contracts

- Updated weighted score examples and added tie-breaking, equal-default-weight, and payload serialization tests.
- Replaced the old collision-drop source assertion with shared helper and style-precedence assertions.
- Added byte-for-byte canonical-template/generated-report synchronization coverage.
- Added real Chromium contracts for direct coincident-point geometry, 2D/3D desktop/mobile rendering, zoom/reset redraws, weighted browser reranking, current generated-report labels, and distinct coordinates for the two current coincident models.
- Chromium itself is session-scoped through a CDP process; each test uses a function-scoped Playwright client. This avoids leaving Playwright's sync asyncio loop active during unrelated existing `asyncio.run` tests.

## Tests and Checks

Passed:

- Focused scoring contracts:
  - `python -m pytest tests/test_compare_models.py::test_relative_geometric_score_uses_actual_metric_ratios tests/test_compare_models.py::test_intelligence_weight_breaks_unweighted_tie tests/test_compare_models.py::test_unlisted_metrics_keep_equal_geometric_weights tests/test_compare_models.py::test_write_html_serializes_scoring_weights -q`
  - Result: 4 passed.
- Focused browser contracts:
  - `python -m pytest tests/test_compare_models_browser.py::test_layout_model_labels_uses_callouts_without_overlap tests/test_compare_models_browser.py::test_weighted_ranking_and_pareto_labels_render_in_2d_and_3d -q`
  - Result: 2 passed.
- Generated report contracts:
  - `python -m pytest tests/test_compare_models.py::test_generated_public_html_matches_canonical_template tests/test_compare_models_browser.py::test_generated_public_report_shows_every_current_pareto_label -q`
  - Result: 2 passed.
- Complete browser module after fixture isolation:
  - `python -m pytest tests/test_compare_models_browser.py -q`
  - Result: 3 passed.
- Current-data assertion from the plan:
  - Verified `scoringWeights` is exactly the Intelligence 2x map and the first row with Intelligence >= 50 is rank 19.
- Full suite:
  - `python -m pytest`
  - Result: 119 passed.
- Lint:
  - `python -m ruff check .`
  - Result: clean.
- Generated report command:
  - `python -m llm_comparison.compare_models price intelligence`
  - Result: wrote 89 ranked rows to `public/index.html`.

The commands were run with `.venv/bin/python` because the workstation has no `python` executable and its system `python3` environment is PEP 668 externally managed.

## Skipped or Non-Clean Checks

- `python -m mypy src tests` is not clean: 26 errors in existing `tests/test_update_all_data.py`, `tests/test_compare_models.py`, and `tests/test_update_opencode_go.py` involving explicit re-exports, `dict[str, object]` indexing/`Any`, and mocked Playwright module attributes.
- The same command against the untouched primary checkout reports the same 26 errors. No error is reported for new `tests/test_compare_models_browser.py`; the implementation did not introduce a new mypy diagnostic.
- Workspace Pyright reported `playwright.sync_api` unresolved because the language server does not use the newly provisioned `.venv`. Runtime import and all Playwright tests passed in that environment.

## Decisions, Assumptions, and Risks

- Kept the weight policy fixed and payload-driven, with no CLI/URL control and no browser-only duplicate coefficient.
- Preserved the existing full model string and canvas `maxWidth` behavior rather than truncating names.
- Used rectangle expansion for the required label gap and collision tuples for deterministic placement.
- Kept the planned pathological fallback: if even 10px callout lanes cannot avoid every collision, every visible optimal name is still drawn at its least-colliding candidate. Dense future datasets may therefore contain overlap, but optimal labels will not disappear.
- Raw Pareto geometry remains unweighted; only table ordering and Final Score changed.
- No blockers or follow-up implementation work remain within the approved plan.
