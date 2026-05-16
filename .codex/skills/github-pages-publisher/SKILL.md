---
name: github-pages-publisher
description: Publish this llm-comparison repo to GitHub Pages by refreshing the gh-pages branch with only the public static-site subset: index.html, results.csv, compare_models.py, compare_models_core.py, compare_models_template.py, README.md, and .gitignore.
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
.\.codex\skills\github-pages-publisher\scripts\update-gh-pages.ps1
```

The script:

1. Verifies the working tree is clean.
2. Detects the current source branch.
3. Switches to `gh-pages`, creating an orphan branch if needed.
4. Replaces the branch contents with only the public files listed above.
5. Commits the update when there are changes.
6. Leaves the working tree on `gh-pages`.

After reviewing, push the branch:

```powershell
git push -u origin gh-pages
```

For later updates, run the script again from the source branch after regenerating `index.html` and `results.csv`, then push `gh-pages`.

