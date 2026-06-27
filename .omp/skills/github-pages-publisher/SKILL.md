---
name: github-pages-publisher
description: "Publish this llm-comparison repo to GitHub Pages by refreshing the gh-pages branch with only the public static-site subset."
---

# GitHub Pages Publisher

Use this skill when asked to update or refresh the GitHub Pages publishing branch for this repository.

## Public Files

The `gh-pages` branch should contain only these root-level published files:

- `index.html` from `public/index.html`
- `results.csv` from `data/results.csv`
- `compare_models.py` from `src/llm_comparison/compare_models.py`
- `compare_models_core.py` from `src/llm_comparison/compare_models_core.py`
- `compare_models_template.py` from `src/llm_comparison/compare_models_template.py`
- `README.md`
- `.gitignore`

Do not publish `data/input.txt`, `src/`, `data/`, `public/`, tests, caches,
`.codex/`, `AGENTS.md`, build metadata, or other source/workspace files.

## Workflow

Run the bundled script from the repository root:

```powershell
.\update-gh-pages.ps1
```

The script:

1. Detects the current source branch.
2. If only `src/llm_comparison/compare_models_template.py`, `public/index.html`, and/or `data/results.csv` are dirty, commits them first.
3. Verifies the working tree is clean.
4. Switches to `gh-pages`, creating an orphan branch if needed.
5. Replaces the branch contents with only the public files listed above.
6. Commits the update when there are changes.
7. Pushes `gh-pages` to `origin` with upstream tracking.
8. Switches back to the original source branch as the final step.

For later updates, run the script again from the source branch after regenerating `public/index.html` and `data/results.csv`.

