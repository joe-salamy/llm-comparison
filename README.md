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

Run the installed unified updater, or its module equivalent:

```powershell
update-all-data
python -m llm_comparison.update_all_data
```

This is the complete refresh workflow. It scrapes and writes Artificial Analysis
data and updates the report-wide UTC timestamp first, then scrapes OpenCode Go
live pricing and joins it to the newly written Artificial Analysis CSV. Finally,
it invokes the GitHub Pages publisher once. The publisher creates one combined
source-data commit containing both generated datasets and report artifacts, plus
the required separate deployment commit on `gh-pages`.

Use `update-all-data --skip-publish` to refresh both datasets locally without
committing or publishing.

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

The report includes a sortable HTML table with the original selected columns plus
`Final Score`. With exactly two categories, it adds a 2D Pareto scatter plot.
With exactly three categories, it adds a rotatable 3D Pareto scatter plot. A
second chart shows only the Pareto-optimal models for the active metrics and
filters. Each chart and the full filtered table can be saved as a PNG.

## Scoring

Models are scored from their actual metric values using a relative geometric mean:

- Each higher-is-better metric contributes `value / reference`; cost, price, latency, and time metrics contribute `reference / value`.
- Fixed references are 50 for percentage/index metrics, 100,000 for context windows, 100 for token-speed metrics, and 1 otherwise.
- `Final Score` is 100 times the weighted geometric mean of those ratios. Artificial Analysis Intelligence counts twice; every other selected metric counts once. A score of 100 matches the fixed references for the selected metrics.
- Adding or removing other models does not change an existing model's score or rank.
- Models missing a requested scoring category, or containing a nonpositive selected value, are excluded from that run.

List available categories and aliases:

```powershell
compare-models --list-categories
```

The `price`, `cost`, and `cost-per-task` aliases select Artificial Analysis Cost per Task. Other common aliases include `intelligence`, `speed`, `latency`, and `response-time`.

## Convert Raw Results

The source-specific commands are local-only diagnostic tools:

```powershell
update-artificial-analysis
python -m llm_comparison.update_artificial_analysis
update-opencode-go
python -m llm_comparison.update_opencode_go
```

`update-artificial-analysis` scrapes the Artificial Analysis leaderboard, writes
`data/results.csv`, and updates the report-wide UTC scrape timestamp in
`src/llm_comparison/compare_models_template.py` and `public/index.html`.
`update-opencode-go` scrapes live OpenCode Go pricing and joins it to the current
`data/results.csv`. These commands never commit or publish, and neither alone is
the complete refresh workflow.

The final `data/opencode_go.csv` column, `scraped_at`, records the OpenCode Go
pricing scrape completion time. One value is repeated on every row in UTC RFC
3339 whole-second form (`YYYY-MM-DDTHH:MM:SSZ`). The exact same value appears in
the report metadata at `?view=opencode-go`; select the **OpenCode Go value**
navigation item or open `https://<site>/index.html?view=opencode-go` directly.
The default Comparison view shows the separate Artificial Analysis scrape time
in the same UTC RFC 3339 whole-second format.

If the automated Artificial Analysis updater is unavailable, use the installed
`convert-results` command, or run `python -m llm_comparison.convert_results`, as
a manual fallback for copied Artificial Analysis source text:

1. Go to https://artificialanalysis.ai/leaderboards/models
2. Expand all columns
3. Copy from "Features" through last "Model, Providers"
4. Paste into `data/input.txt`
5. Run `convert-results`

The manual converter writes `data/results.csv`.

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
