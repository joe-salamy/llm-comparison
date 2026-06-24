Implemented and committed the approved plan.

- Commit: `a75b5355e34cc6da7b064da2de83bffe2bc955a1`
- Branch: `feature/2d-chart-zoom-plan`
- Handoff: `.omp/handoff/implementation-summary.md` written and left untracked.
- Final status: clean except untracked workflow artifacts:
  - `.omp/handoff/`
  - `.omp/worktree-flow/2d-chart-zoom-plan/`

Changed:
- `compare_models_template.py`
- `tests/test_compare_models.py`
- `index.html`
- `.omp/skill-usage.json`

Verification:
- Focused pytest: `4 passed, 10 deselected`
- Full `tests/test_compare_models.py`: `14 passed`
- Scoped Ruff: `OK`
- mypy: `OK`
- Report regeneration: `Wrote 45 ranked rows to index.html`
- Manual Chromium smoke: 2D zoom/pan/reset passed; 3D reset still restores `1.25x`.

Notes:
- `python -m ruff check .` still fails on pre-existing `.omp/scripts/*.py` E501 diagnostics outside plan scope.
- Loaded `github-pages-publisher` per repo instruction, but did not run it: its workflow switches/creates `gh-pages`, conflicting with the explicit no worktree/branch operations constraint.
