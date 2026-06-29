# LLM Comparison

Tools for converting and comparing Artificial Analysis LLM data.

## Installation

This project uses only the Python standard library at runtime. Python 3.11 or
newer is required.

For development checks, install the optional tools and updater dependency used
by the documented type-check command:

```powershell
python -m pip install -e ".[dev,update]"
```

For the automated Artificial Analysis updater, install Playwright and its
Chromium browser:

```powershell
python -m pip install -e ".[update]"
python -m playwright install chromium
```

## Data

The comparison script uses `data/results.csv` as its source of truth. Generated
reports are written to `public/index.html` by default.

Manual raw-copy source text lives in `data/input.txt`. Converted CSV output lives
in `data/results.csv`.

## Update and Publish

Fetch the latest Artificial Analysis table, update `data/results.csv`, refresh
the generated report date with today's date, commit generated outputs, and
publish GitHub Pages:

```powershell
update-artificial-analysis
```

Use `--skip-publish` when you only want to refresh local data files.


## Compare Models

Use the installed `compare-models` command, or run the module with
`python -m llm_comparison.compare_models`, to rank models across one or more
numeric categories:

```powershell
compare-models price intelligence
compare-models price intelligence latency
compare-models price intelligence speed latency --all-columns
```

By default, the command writes `public/index.html`. Use `--output` to choose a
different report path:

```powershell
compare-models price intelligence --output quality_vs_price.html
```

The report includes a sortable HTML table with the original selected columns plus `Final Score`. With exactly two categories, it adds a 2D Pareto scatter plot. With exactly three categories, it adds a rotatable 3D Pareto scatter plot.

## Scoring

Models are scored with direction-adjusted percentile ranks:

- Higher is better for quality, benchmark, context, and speed metrics.
- Lower is better for price, latency, and time metrics.
- `Final Score` is the average percentile score across the requested categories.
- Models missing any requested scoring category are excluded from that run.

List available categories and aliases:

```powershell
compare-models --list-categories
```

Common aliases include `intelligence`, `price`, `speed`, `latency`, and `response-time`.

## Convert Raw Results

Use the installed `update-artificial-analysis` command, or run
`python -m llm_comparison.update_artificial_analysis`, to refresh Artificial
Analysis data without manual clipboard selection. The upload date defaults to
today:

```powershell
update-artificial-analysis
```

The updater opens the Artificial Analysis leaderboard, expands columns, reads
the table DOM, writes `data/results.csv`, updates the displayed data date in
`src/llm_comparison/compare_models_template.py` and `public/index.html` when
those files are present, then runs `scripts/update-gh-pages.py` to commit the
generated outputs and republish the GitHub Pages branch. Pass `--skip-publish`
to only refresh the local data files.

If the automated updater is unavailable, use the installed `convert-results`
command, or run `python -m llm_comparison.convert_results`, as a manual fallback
for copied Artificial Analysis source text:

1. Go to https://artificialanalysis.ai/leaderboards/models
2. Expand all columns
3. Copy from "Features" through last "Model, Providers"
4. Paste into `data/input.txt`
5. Run `convert-results`

By default, both converters write `data/results.csv`.

## Development

Run the validation checks before publishing changes:

```powershell
python -m ruff check .
python -m mypy src tests
python -m pytest
```

`llm_comparison.compare_models` is the CLI entry point. Ranking and data-shaping
logic lives in `llm_comparison.compare_models_core`; the generated report
template lives in `llm_comparison.compare_models_template`.

## License

MIT. See `LICENSE`.
