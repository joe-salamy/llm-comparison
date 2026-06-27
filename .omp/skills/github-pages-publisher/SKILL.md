---
name: github-pages-publisher
description: "Publish this llm-comparison repo to GitHub Pages by refreshing the gh-pages branch with only the public static-site subset."
---

# GitHub Pages Publisher

Use this skill when asked to update or refresh the GitHub Pages publishing branch for this repository.

The script is the source of truth for the published file list and workflow.
Run it from the repository root:

```powershell
python .\scripts\update-gh-pages.py
```

For later updates, run the script again from the source branch after regenerating `public/index.html` and `data/results.csv`.

