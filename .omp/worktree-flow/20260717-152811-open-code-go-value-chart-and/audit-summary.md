# Open Code Go Value Chart and Nonlinear Value Metric Audit

## Audit Context

- Worktree: `/mnt/c/Users/joesa/code/llm-comparison-open-code-go-value-chart-and`
- Branch: `feature/open-code-go-value-chart-and`
- Base ref: local `master` after `git fetch --all --prune`
- Merge base: `80000708e2f1f69567c77a4501c46e5184351b2e`
- Implementation commit audited: `0af56f3f801e3146a26a8605851d73ddfb00d330` (`Update OpenCode Go value metric`)

## Implementation Intent Received

The prior implementation replaced the linear Intelligence-per-dollar score with `intelligence - 10 * log10(blended_price)`, reversed the OpenCode Go chart to cost on X and Intelligence on Y, updated user-facing terminology and explanations, preserved missing-Intelligence behavior, regenerated the CSV and published report, and added focused tests. It also guarded the OpenCode Go live-CSV refresh on `file://` so the required local-file smoke test remains console-error-free.

## Skills Loaded

- `audit-worktree`: required audit procedure, worktree safety, diff review, verification, commit, and reporting rules.
- No additional repository-local audit skill was loaded: `.agent-harness/skills` is not present in this worktree. The changed Python, embedded JavaScript, tests, CSV, and generated HTML were reviewed directly.

## Diff Audited

Compared the complete branch diff against `master`, excluding prohibited scratchpad paths. The diff contains seven files:

- `src/llm_comparison/update_opencode_go.py`
- `src/llm_comparison/compare_models_core.py`
- `src/llm_comparison/compare_models_template.py`
- `tests/test_update_opencode_go.py`
- `tests/test_compare_models.py`
- `data/opencode_go.csv`
- `public/index.html`

Reviewed the metric validation and Decimal calculation, enrichment path, missing-Intelligence behavior, ordered payload categories, Pareto inputs, generic 2D axis mapping, report copy/bootstrap/tooltip behavior, focused test contracts, generated score values, and generated HTML parity.

## Findings and Fixes

- Confirmed issues: none.
- Audit fixes applied: none.
- Files changed by the audit: none outside this workflow summary.
- Audit commit: none created because no product changes were needed.

The implementation satisfies the approved plan. The logarithmic helper rejects invalid Intelligence and price inputs with the required messages, uses the primary 7:2:1 blended price, preserves full Decimal output in CSV, leaves the unranked model blank and unplotted, emits cost before Intelligence in both ordered payload contracts, and retains the generic renderer.

## Verification

- `/usr/bin/pytest tests/test_update_opencode_go.py -q` — 52 passed.
- `/usr/bin/pytest tests/test_compare_models.py -q` — 25 passed.
- `PYTHONPATH=src python -m llm_comparison.compare_models price intelligence --opencode-go-input data/opencode_go.csv --output /tmp/opencode-go-audit-report.html` — succeeded; wrote 103 ranked comparison rows.
- `cmp -s public/index.html /tmp/opencode-go-audit-report.html` — exact match; tracked report is reproducible from current sources and CSV.
- Decimal CSV invariant check — 16 rows, 15 ranked rows, one blank unranked score, and zero formula mismatches.
- Chromium file smoke at `file:///tmp/opencode-go-audit-report.html?view=opencode-go` — zero console errors and zero page errors; verified the OpenCode Go heading, `16 models, 15 ranked by cost-adjusted intelligence` summary, exact formula/tradeoff/disclosure copy, descending displayed score order, and final Unranked row.
- Interactive chart tooltip — verified cost appears before Intelligence and the score label is `Cost-adjusted intelligence`; the unranked model was absent from plotted chart labels.

## Skipped Checks and Residual Risk

- The harness-managed default Puppeteer Chromium was unavailable because its configured executable is missing. Browser verification instead used the installed Playwright Chromium at `/home/joesa/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome` through the browser device.
- No live OpenCode Go network scrape was rerun during audit. The checked-in generated CSV was validated against the metric formula, and the report was regenerated from that CSV exactly. External pricing may change after the recorded scrape timestamp; this is normal live-source drift, not an implementation defect.
- No confirmed residual code risk or follow-up work remains.
