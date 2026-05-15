# LLM Comparison

Tools for converting and comparing Artificial Analysis LLM data.

## Data

The comparison script uses `data/results.csv` as its source of truth. Generated reports are written to the repository root.

## Compare Models

Use `compare_models.py` to rank models across one or more numeric categories:

```powershell
python compare_models.py price intelligence
python compare_models.py price intelligence latency
python compare_models.py price intelligence speed latency --all-columns
```

By default, the script writes `model_comparison.html`. Use `--output` to choose a different report path:

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

Use `convert_results.py` to convert copied Artificial Analysis source text into Markdown and CSV outputs.

1. Go to https://artificialanalysis.ai/leaderboards/models
2. Expand all columns
3. Copy from "Features" through last "Model, Providers"
4. Paste into input.txt
5. Run `python convert_results.py`
