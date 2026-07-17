# OpenCode Go Value Comparison Implementation Summary

## Plan
- Approved plan: `.omp/worktree-flow/20260717-113552-opencode-go-value-comparison/plan.md`

## Worktree and branch
- Worktree: `/mnt/c/Users/joesa/code/llm-comparison-opencode-go-value-comparison`
- Branch: `feature/opencode-go-value-comparison`
- Commit: `3e1c596f2a781605f4428b2e834c53b52b2970c0` (`Add OpenCode Go value comparison`)

## Changed files
- `pyproject.toml`
- `scripts/update-gh-pages.py`
- `src/llm_comparison/update_opencode_go.py` (new)
- `src/llm_comparison/compare_models.py`
- `src/llm_comparison/compare_models_core.py`
- `src/llm_comparison/compare_models_template.py`
- `tests/test_update_opencode_go.py` (new)
- `tests/test_compare_models.py`
- `tests/test_update_gh_pages.py`
- `data/opencode_go.csv` (new generated data)
- `public/index.html` (regenerated)

## Behavior changes
- Added the `update-opencode-go` console entry point and direct module/script execution path.
- Added strict Playwright scraping for the unique OpenCode Go pricing table. The scraper validates normalized six-column headers, uniqueness, non-empty rows, and row widths, and closes Chromium in `finally`.
- Added strict currency parsing, Qwen ≤256K/>256K tier collapse, deterministic source-order CSV output, explicit Artificial Analysis aliases, highest-index selection with deterministic tie handling, the Artificial Analysis 7:2:1 cached-read/input/output blend, and intelligence-per-blended-dollar value calculation.
- Validation and joining complete before `data/opencode_go.csv` is opened, preserving an existing generated file on scrape or join failure.
- Added `--opencode-go-input` to report generation. Production report generation now requires and embeds the Go CSV.
- Added `payload.openCodeGo` while retaining the comparison payload. Ranked rows use precomputed `value_score`; unranked rows retain neutral score/Pareto/color state and are excluded from plotted points.
- Added `?view=opencode-go`, semantic Comparison/OpenCode Go navigation, source/formula disclosure, Go-specific formatting, direct value sorting, view-gated CSV loading/fallback, and reuse of the existing table and 2D chart shell without percentile rescoring.
- Added `data/opencode_go.csv` to generated/public Pages manifests while retaining one `index.html`.
- Regenerated the current 16-row Go CSV and the single combined `public/index.html`. Current live data selects `DeepSeek V4 Flash (max)` at index 40 and leaves `MiniMax M2.5` unranked.

## Tests and checks run
- `python3 -m pytest tests/test_update_opencode_go.py tests/test_compare_models.py tests/test_update_gh_pages.py tests/test_update_artificial_analysis.py`
  - Result: 63 passed.
- `/tmp/llm-comparison-playwright/bin/ruff check ...` over all changed Python source/test files.
  - Result: OK.
- `PYTHONPATH=src /tmp/llm-comparison-playwright/bin/mypy src/llm_comparison/update_opencode_go.py src/llm_comparison/compare_models.py src/llm_comparison/compare_models_core.py`
  - Result: OK.
- `/tmp/llm-comparison-playwright/bin/python -m llm_comparison.update_opencode_go --skip-publish` with `PYTHONPATH=src`.
  - Result: selected the live six-column table, found 18 source rows, and wrote 16 canonical rows.
- `python3 -m llm_comparison.compare_models price intelligence --opencode-go-input data/opencode_go.csv --output public/index.html` with `PYTHONPATH=src`.
  - Result: wrote 103 comparison rows and embedded both report views.
- `node --check /tmp/llm-comparison-inline.js` after extracting the two inline scripts from regenerated `public/index.html`.
  - Result: no syntax errors.
- Served the repository root with `python3 -m http.server 8000`; the generated report was reachable at the requested local URL.

## Skipped checks
- The requested interactive Edge verification was attempted twice against the exact existing endpoint `http://172.18.176.1:9222`. Both attempts timed out before CDP attachment. No alternate browser/profile was launched or substituted. Runtime query switching, visual chart/table behavior, Usage-header sorting, and Comparison-link interaction therefore remain unobserved in Edge. Static payload/structure tests and generated JavaScript syntax checks passed.
- The live Pages publisher was not run, per plan. The synthetic publisher integration test passed and verified the exact public tree includes both CSV files and the single HTML document.

## Implementation decisions and tradeoffs
- Table selection was factored into pure `select_pricing_snapshot` validation so zero/multiple/empty/ragged snapshot behavior is testable without a browser.
- Artificial Analysis matching is exact and allowlisted. Unknown future OpenCode models remain visible and unranked until an alias is intentionally added.
- Full Decimal precision is retained during calculation and CSV writing; HTML display formatting is separate from numeric sort values.
- Go CSV refresh uses the live source but does not invoke the Artificial Analysis updater, avoiding intermediate two-source publication.
- A temporary environment under `/tmp/llm-comparison-playwright` supplied Playwright, Chromium, Ruff, and mypy because the system Python is externally managed. No environment files were added to the worktree.

## Assumptions and residual risks
- The approved alias list, Qwen 256K threshold, primary-tier ranking, and 7:2:1 formula are treated as fixed product rules.
- Current live OpenCode/Artificial Analysis values may drift; fixture tests pin the approved examples while the generated CSV reflects the live 2026-07-17 sources.
- Residual risk: interactive Edge behavior could not be directly observed until the dedicated `OMP-Automation` Edge instance/WSL port proxy is restored. The implementation has focused DOM/payload tests and JavaScript syntax validation but no substitute browser verification was performed.
- No blockers remain for code integration. `.omp/handoff/implementation-summary.md` is intentionally untracked and not included in the commit.
