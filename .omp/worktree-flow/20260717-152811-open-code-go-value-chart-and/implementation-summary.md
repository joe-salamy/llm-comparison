# Open Code Go Value Chart and Nonlinear Value Metric Implementation

## Plan

- Approved plan: `.omp/worktree-flow/20260717-152811-open-code-go-value-chart-and/plan.md`
- Worktree: `/mnt/c/Users/joesa/code/llm-comparison-open-code-go-value-chart-and`
- Branch: `feature/open-code-go-value-chart-and`
- Commit: `0af56f3f801e3146a26a8605851d73ddfb00d330` (`Update OpenCode Go value metric`)

## Changed Files

- `src/llm_comparison/update_opencode_go.py`
- `src/llm_comparison/compare_models_core.py`
- `src/llm_comparison/compare_models_template.py`
- `tests/test_update_opencode_go.py`
- `tests/test_compare_models.py`
- `data/opencode_go.csv`
- `public/index.html`

## Behavior Changes

- Added pure `cost_adjusted_intelligence(intelligence, blended_price)` Decimal calculation: `intelligence - 10 * log10(blended_price)`.
- The helper rejects non-finite or negative Intelligence with `OpenCode Go intelligence must be finite and non-negative`; zero Intelligence remains valid. Strictly positive finite blended prices remain required.
- `enrich_rows` now stores the full-precision logarithmic score under the existing `value_score` CSV key. Missing Intelligence still leaves the score blank.
- OpenCode Go chart categories and graph categories now order blended cost first (X/lower better), then Intelligence (Y/higher better). Pareto behavior and the generic renderer remain unchanged.
- The score column, About formula and exchange-rate explanation, summary, and tooltip now use `Cost-adjusted intelligence` terminology.
- OpenCode Go live CSV refresh is skipped for `file://` reports, which use the embedded fallback directly. HTTP(S) reports retain the existing live CSV refresh attempt. This avoids browser Fetch console errors during the required local-file smoke test.
- Regenerated `data/opencode_go.csv` through the live updater. It contains 16 current rows, 15 formula-validated ranked scores, one blank unranked score, and scrape timestamp `2026-07-17T22:32:15Z`.
- Regenerated `public/index.html` from the updated CSV and report implementation.

## Tests and Checks Run

- `/usr/bin/pytest tests/test_update_opencode_go.py -q` — 52 passed.
- `/usr/bin/pytest tests/test_compare_models.py -q` — 25 passed after the final template/test update.
- `PYTHONPATH=src python -m llm_comparison.update_opencode_go` — succeeded; fetched 18 source price rows and wrote 16 canonical rows inside this worktree.
- Decimal CSV invariant check — all 15 ranked rows exactly equal `cost_adjusted_intelligence(Intelligence, primary blended price)`; the single unranked score is blank.
- `PYTHONPATH=src python -m llm_comparison.compare_models price intelligence --opencode-go-input data/opencode_go.csv --output /tmp/opencode-go-value-report.html` — succeeded, 103 comparison rows written.
- Playwright file smoke at `file:///tmp/opencode-go-value-report.html?view=opencode-go` — page title loaded as `OpenCode Go value`; zero console/page errors after the file-protocol guard.
- `PYTHONPATH=src python -m llm_comparison.compare_models price intelligence --opencode-go-input data/opencode_go.csv --output public/index.html` — succeeded, 103 comparison rows written.
- Served `public` at `http://127.0.0.1:8000/?view=opencode-go` and exercised it with project Playwright Chromium. Verified:
  - summary: `16 models, 15 ranked by cost-adjusted intelligence`;
  - default active sort column: `Cost-adjusted intelligence`;
  - horizontal canvas title: `OpenCode Go blended price ($/1M tokens) (lower better)`;
  - vertical canvas title: `Artificial Analysis Intelligence Index (higher better)`;
  - exact formula and 10-point/10× About copy;
  - tooltip lists cost before Intelligence and labels the score `Cost-adjusted intelligence`;
  - the Unranked row remains in the table and `MiniMax M2.5` is absent from plotted models.
- Confirmed the accidental first updater invocation against the primary editable install was restored; the primary checkout's `data/opencode_go.csv` returned to clean status before worktree regeneration.
- Post-commit worktree status contains only untracked `.omp/handoff/` and `.omp/worktree-flow/20260717-152811-open-code-go-value-chart-and/` workflow artifacts.

## Skipped or Unavailable Checks

- Initial `python -m pytest ...` attempts could not run because the active editable virtual environment has no `pytest`; reran both suites successfully with `/usr/bin/pytest`.
- `ruff` and `mypy` were not installed on `PATH`, so those checks were not run.
- The harness browser device could not install its configured Puppeteer Chromium because the cached executable was missing. Browser verification used the project's working Playwright Chromium installation instead.

## Decisions and Tradeoffs

- Kept `value_score`, descending sort, score coloring, primary blended-price input, two-decimal presentation, live CSV parser, embedded fallback, and generic `draw2D` implementation.
- Kept the cost chart axis linear as required; logarithmic treatment applies only to the ranking metric.
- Added explicit positive/finite blended-price validation in the new helper as well as retaining `blended_price` validation, so direct helper calls fail with the established cost error instead of a Decimal logarithm exception.
- Added a file-protocol live-refresh guard only for the OpenCode Go view. This is the minimum change that satisfies clean local-file loading without altering served live-refresh behavior.

## Assumptions and Known Risks

- The calibration remains fixed at 10 Intelligence points per 10× price with a `$1/1M tokens` reference.
- The live scrape succeeded and current source values were accepted rather than pinning the prior snapshot.
- When served with `python -m http.server 8000 --directory public`, the two configured live CSV paths return 404 because `public` contains only `index.html`; the embedded payload still initializes and every requested UI behavior passed. This is pre-existing deployment-layout behavior and was not expanded into copying data under `public`, which the approved plan did not request.
- No blockers or follow-up implementation work remain for the approved plan.
