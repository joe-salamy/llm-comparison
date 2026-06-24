---
name: github-pages-publisher
description: "Publish this llm-comparison repo to GitHub Pages by refreshing the gh-pages branch with only the public static-site subset."
---

# GitHub Pages Publisher

Use this skill when asked to update or refresh the GitHub Pages publishing branch for this repository.

## Public Files

The `gh-pages` branch should contain only:

- `index.html`
- `results.csv`
- `compare_models.py`
- `compare_models_core.py`
- `compare_models_template.py`
- `README.md`
- `.gitignore`

Do not publish `input.txt`, tests, caches, `.codex/`, `AGENTS.md`, build metadata, or other source/workspace files.

## Workflow

Run the bundled script from the repository root:

```powershell
.\update-gh-pages.ps1
```

The script:

1. Detects the current source branch.
2. If only `.omp/skill-usage.json`, `compare_models_template.py`, `index.html`, and/or `results.csv` are dirty, commits them first.
3. Verifies the working tree is clean.
4. Switches to `gh-pages`, creating an orphan branch if needed.
5. Replaces the branch contents with only the public files listed above.
6. Commits the update when there are changes.
7. Leaves the working tree on `gh-pages`.

After reviewing, push the branch:

```powershell
git push -u origin gh-pages
```

For later updates, run the script again from the source branch after regenerating `index.html` and `results.csv`, then push `gh-pages`.

