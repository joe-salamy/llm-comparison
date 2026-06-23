# LLM Comparison

Tools for converting and comparing Artificial Analysis LLM data.

## Installation

This project uses only the Python standard library at runtime. Python 3.11 or
newer is required.

For development checks, install the optional tools:

```powershell
python -m pip install -e ".[dev]"
```

For the automated Artificial Analysis updater, install Playwright and its
Chromium browser:

```powershell
python -m pip install -e ".[update]"
python -m playwright install chromium
```

## Data

The comparison script uses `results.csv` as its source of truth. Generated
reports are written to the repository root.

Manual raw-copy source text lives in `input.txt`. Converted CSV output lives in
`results.csv`.

## Compare Models

Use `compare_models.py` to rank models across one or more numeric categories:

```powershell
python compare_models.py price intelligence
python compare_models.py price intelligence latency
python compare_models.py price intelligence speed latency --all-columns
```

By default, the script writes `index.html`. Use `--output` to choose a different report path:

```powershell
python compare_models.py price intelligence --output quality_vs_price.html
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
python compare_models.py --list-categories
```

Common aliases include `intelligence`, `price`, `speed`, `latency`, and `response-time`.

## Convert Raw Results

Use `update_artificial_analysis.py` to refresh Artificial Analysis data without
manual clipboard selection:

```powershell
python update_artificial_analysis.py --uploaded-date YYYY-MM-DD
```

The updater opens the Artificial Analysis leaderboard, expands columns, reads
the table DOM, writes `results.csv`, and updates the displayed data date in
`compare_models_template.py` and `index.html` when those files are present.

If the automated updater is unavailable, use `convert_results.py` as a manual
fallback for copied Artificial Analysis source text:

1. Go to https://artificialanalysis.ai/leaderboards/models
2. Expand all columns
3. Copy from "Features" through last "Model, Providers"
4. Paste into `input.txt`
5. Run `python convert_results.py`

By default, both converters write `results.csv`.

## Development

Run the validation checks before publishing changes:

```powershell
python -m ruff check .
python -m mypy compare_models.py compare_models_core.py convert_results.py update_artificial_analysis.py tests
python -m pytest
```

`compare_models.py` is the CLI entry point. Ranking and data-shaping logic lives
in `compare_models_core.py`; the generated report template lives in
`compare_models_template.py`.

## License

MIT. See `LICENSE`.
