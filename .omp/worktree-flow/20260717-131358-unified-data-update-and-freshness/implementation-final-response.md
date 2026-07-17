Implemented and committed the approved unified data update plan.

- **Commit:** `112ab34ca4c2869812ce7c7f8edaba9e2182bc22`
- **Branch:** `feature/unified-data-update-and-freshness`
- **Handoff:** `.omp/handoff/implementation-summary.md` — untracked as required

Key changes:
- Added `update-all-data` orchestration command.
- Made source-specific updaters local-only.
- Added canonical UTC `scraped_at` provenance to OpenCode Go data.
- Added freshness metadata and fetched-data fallback behavior to the Go report.
- Refreshed both datasets and regenerated `public/index.html`.
- Updated tests and README workflow documentation.

Verification:
- Focused tests: **88 passed**
- Ruff: **OK**
- Mypy: **OK**
- Live `update-all-data --skip-publish`: succeeded
- Generated inline JavaScript: `node --check` passed
- Browser smoke: Go and Comparison views passed, including valid fetched freshness and malformed-CSV fallback

Worktree has no staged or unstaged changes. Only `.omp/handoff/` and `.omp/worktree-flow/` remain untracked workflow artifacts.
