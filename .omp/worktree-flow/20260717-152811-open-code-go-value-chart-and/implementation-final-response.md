Implemented and committed the approved plan.

- **Commit:** `0af56f3f801e3146a26a8605851d73ddfb00d330`
- **Branch:** `feature/open-code-go-value-chart-and`
- **Handoff:** `.omp/handoff/implementation-summary.md`

Changed:
- Added logarithmic cost-adjusted Intelligence metric.
- Reversed OpenCode Go chart axes to cost X / Intelligence Y.
- Updated labels, formula, summary, and tooltip copy.
- Preserved Unranked behavior and `value_score` storage key.
- Regenerated `data/opencode_go.csv` and `public/index.html`.
- Prevented `file://` reports from attempting unsupported live CSV fetches.

Verification:
- Updater tests: **52 passed**
- Report tests: **25 passed**
- All 15 ranked CSV scores exactly validated against the new Decimal formula.
- Temporary `file://` report loaded with no console/page errors.
- Served UI verified axis titles, default sorting, About copy, tooltip order, and Unranked chart exclusion.

Only `.omp/handoff/` and `.omp/worktree-flow/` remain untracked; neither was committed.
