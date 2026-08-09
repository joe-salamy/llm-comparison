# Artificial Analysis Access Investigation

**Investigation date:** 2026-08-09

## Conclusion

Artificial Analysis has introduced a real paid/gated data-access path, but the repository's current public-leaderboard scraper is not currently broken.

From this environment, the anonymous public leaderboard remained accessible and the installed updater completed successfully. The official API and data-export features are now gated by API keys and subscription tiers.

## Evidence from the current repository

The updater in `src/llm_comparison/update_artificial_analysis.py`:

1. Opens `https://artificialanalysis.ai/leaderboards/models` with Playwright.
2. Expands the public table columns.
3. Extracts the rendered `main table`.
4. Drops the final action-only "Further Analysis" column.
5. Requires `Model` and `Cost per Task` headers before writing data.

The updater has no API fallback. The documented manual fallback in `README.md` copies the rendered public table into `data/input.txt` and runs `convert-results`.

## Live checks

The following checks were performed anonymously:

- `https://artificialanalysis.ai/leaderboards/models` returned HTTP 200.
- The browser had no authenticated session (`/api/auth/get-session` returned `null`).
- The page contained the table and `Expand columns` control.
- After expansion, the table contained 250 rows and 41 raw columns. The updater retained 40 data columns after removing the action column.
- The installed `update-artificial-analysis` command succeeded using temporary output paths:

  ```text
  [1/3] Fetching the Artificial Analysis leaderboard...
        Found 250 rows across 40 columns.
  [2/3] Saving generated data...
        Wrote 250 rows to /tmp/aa-investigation-installed/results.csv.
        Updated the data timestamp in 2 files.
  [3/3] Update complete.
  ```

- The checked-in `data/results.csv` has 261 rows and the same 40-column schema. The row-count difference is upstream data churn, not a parser failure.

## Official API and paywall checks

Without an API key, both official model endpoints returned HTTP 401 with `{"error":"API key is required"}`:

- `https://artificialanalysis.ai/api/v2/language/models/free`
- `https://artificialanalysis.ai/api/v2/language/models`

The official documentation states:

- Every API endpoint requires an `x-api-key`.
- The Free model endpoint exposes only a reduced public subset.
- The Free response excludes fields such as context window, full evaluation data, blended pricing, performance percentiles, licensing, and provider detail.
- The standard language-model endpoint is Pro-only.
- Provider data and performance-over-time endpoints are Commercial-only.
- API usage requires attribution, and redistribution rights require separate terms.

The current pricing page lists Pro at **$417/month per seat** and includes **Data Export** and API access. It also says to contact Artificial Analysis for data redistribution or external use.

Official sources:

- [Public LLM leaderboard](https://artificialanalysis.ai/leaderboards/models)
- [Artificial Analysis pricing](https://artificialanalysis.ai/pricing)
- [Data API documentation](https://artificialanalysis.ai/data-api/docs)
- [Data API OpenAPI specification](https://artificialanalysis.ai/api/v2/openapi)

## Impact

The current scraper still works because it reads the rendered public UI rather than the official API. However:

1. The public table may later require login or expose fewer columns.
2. The scraper is an undocumented UI integration and can break on layout changes.
3. The Free API cannot reproduce the repository's current 40-column CSV.
4. Publicly republishing the scraped dataset may conflict with Artificial Analysis's current export or redistribution terms.

## Recommendation

No source change is justified solely from the current checks. Short term, the existing scraper can continue while the public table remains accessible.

For durable automation, obtain an Artificial Analysis API subscription and key. Pro may cover model-level data; Commercial terms may be required for provider-level data or public redistribution. An API importer would also need pagination, JSON-to-CSV field mapping, null handling, and secret configuration through the environment rather than source control.

## Verification

- `update-artificial-analysis` live scrape: succeeded with 250 rows and 40 columns.
- `uv run --extra dev pytest -q tests/test_update_artificial_analysis.py`: 13 passed.
- Repository source files were not changed during the investigation. Only pre-existing `.omp/` worktree changes remain.
