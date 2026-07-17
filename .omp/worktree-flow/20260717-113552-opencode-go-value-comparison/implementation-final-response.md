Implemented and committed the approved OpenCode Go value comparison plan.

- **Commit:** `3e1c596f2a781605f4428b2e834c53b52b2970c0`
- **Branch:** `feature/opencode-go-value-comparison`
- **Handoff:** `.omp/handoff/implementation-summary.md` — untracked as required
- **Verification:** 63 focused tests passed; Ruff and mypy passed; live scrape produced 18 source rows / 16 canonical rows; report regenerated; generated JavaScript passed `node --check`.
- **Skipped:** Interactive Edge verification. Attachment to `http://172.18.176.1:9222` timed out twice. No alternate browser/profile was used.
- **Worktree state:** implementation clean; only `.omp/handoff/` and the workflow plan directory remain untracked.
