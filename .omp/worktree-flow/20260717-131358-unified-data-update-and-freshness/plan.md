# Unified data update and freshness

## Context

Replace the two independently publishing source refreshes with one installed `update-all-data` workflow. It must refresh Artificial Analysis first, refresh OpenCode Go against that newly written intelligence data, and invoke the existing GitHub Pages publisher once so both generated datasets enter one source-branch commit; the publisher’s separate `gh-pages` deployment commit remains required. The OpenCode Go CSV must record one UTC scrape timestamp and the OpenCode Go report view must display that provenance.

## Approach

### 1. Make both source-specific updaters local-only

- In `src/llm_comparison/update_artificial_analysis.py`, keep `parse_args()`, `async_main(args)`, `main()`, scraping, `data/results.csv` writing, and report-date replacement intact, but remove `--skip-publish`, `--publish-script`, the publication branch in `async_main`, and `run_publish_script()`. The `update-artificial-analysis` command becomes an explicitly local source refresh and never commits or publishes.
- In `src/llm_comparison/update_opencode_go.py`, remove its conditional import of `run_publish_script`, remove the same two publication CLI options and publication branch, and keep scraping, joining, validation, and CSV writing unchanged apart from the freshness work below. The `update-opencode-go` command also becomes local-only.
- Update every direct `argparse.Namespace` caller in `tests/test_update_artificial_analysis.py` and `tests/test_update_opencode_go.py` to remove the deleted fields. Replace publication-order assertions with local write-order assertions, and move the existing subprocess-resolution contract for `run_publish_script()` to the new unified updater tests. Do not leave ignored CLI flags or compatibility aliases: passing either removed publication option to a source-specific command must be an argparse error.

### 2. Add the single publishing orchestrator

- Create `src/llm_comparison/update_all_data.py`; no equivalent orchestrator exists. Register exactly `update-all-data = "llm_comparison.update_all_data:main"` in `[project.scripts]` in `pyproject.toml`, and support `python -m llm_comparison.update_all_data` through the module’s `main()`.
- Implement `parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace` with unambiguous unified options and existing defaults:
  - `--artificial-analysis-url` from `update_artificial_analysis.DEFAULT_URL`.
  - `--opencode-go-url` from `update_opencode_go.DEFAULT_URL`.
  - `--artificial-analysis-csv` from `update_artificial_analysis.DEFAULT_CSV`; wire this same path to the Go child’s `aa_csv`.
  - `--opencode-go-csv` from `update_opencode_go.DEFAULT_CSV`.
  - `--html`, `--template`, and `--uploaded-date` with the same types/defaults as the Artificial Analysis parser.
  - Shared `--headed` and `--timeout-ms` values passed to both children.
  - Outer-only `--skip-publish` and `--publish-script`, defaulting the latter to `scripts/update-gh-pages.py` under the repository root.
- Move the existing publisher subprocess behavior into `update_all_data.run_publish_script(script_path: Path) -> None`: resolve relative paths against the repository root, run `[sys.executable, resolved_script]` from that root, capture output, and preserve the existing `RuntimeError("GitHub Pages publishing failed: ...")` failure shape. This module is the only updater allowed to invoke it.
- Implement `async_main(args: argparse.Namespace) -> None` in strict order:
  1. Construct an Artificial Analysis child namespace and `await update_artificial_analysis.async_main(...)`.
  2. Only after that succeeds, construct an OpenCode Go child namespace with `aa_csv=args.artificial_analysis_csv` and `await update_opencode_go.async_main(...)`.
  3. Only after both succeed, call `run_publish_script(args.publish_script)` once unless the outer `--skip-publish` is set.
- Implement `main() -> None` as `asyncio.run(async_main(parse_args()))`. Import and call the two modules directly rather than assembling subprocess CLI arguments; this reuses their exact update paths while making order and the single publication call testable.
- Failure policy is fail-fast with no retry: an Artificial Analysis failure skips Go and publishing; a Go scrape/join/write failure leaves Artificial Analysis changes local and skips publishing; a publisher failure is terminal and is never followed by another publisher call. The existing Go invariant that validation finishes before opening its output file remains intact.
- Keep `scripts/update-gh-pages.py` orchestration unchanged. Its existing `GENERATED_FILES` already stages both CSVs plus the generated template/report in one source-data commit, while its separate `gh-pages` commit and single push remain the deployment mechanism.

### 3. Add deterministic OpenCode Go scrape provenance

- In `src/llm_comparison/update_opencode_go.py`, append the exact final CSV column `scraped_at` to `CSV_COLUMNS`; do not add freshness metadata to the dynamically sourced Artificial Analysis schema.
- Add `validate_scraped_at(value: str) -> str`, accepting only a semantically valid UTC instant whose canonical text exactly matches `YYYY-MM-DDTHH:MM:SSZ`; implement it with `datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")` and return the unchanged value. Add `current_scraped_at() -> str`, returning the current aware UTC instant at whole-second precision in that format; this function is the clock-injection seam for deterministic tests.
- Change the pure join signature to `build_output_rows(headers: list[str], source_rows: list[list[str]], aa_rows: list[dict[str, str]], *, scraped_at: str) -> list[dict[str, str]]`. Validate the timestamp before building rows, then populate the identical non-empty `scraped_at` value on every canonical row. Capture it exactly once, immediately after `scrape_table(...)` returns successfully, and pass it through the join; never call the clock once per row.
- Preserve the prior Go CSV if scraping, AA joining, timestamp validation, or row validation fails.
- Regenerate `data/opencode_go.csv` through the updater after implementation; do not hand-edit it. The tracked CSV must have `scraped_at` as its last header and the same freshly captured value on all rows.

### 4. Carry freshness into the OpenCode Go report view

- In `src/llm_comparison/compare_models.py`, extend `validate_opencode_go_headers(headers)` so `scraped_at` is required in addition to the displayed `OPENCODE_GO_COLUMNS`; keep it out of `OPENCODE_GO_COLUMNS` so it never becomes a sortable per-model table column.
- In `src/llm_comparison/compare_models_core.py`, extend `opencode_go_payload(rows)` with the exact payload property `scrapedAt`. For non-empty input, require every row’s stripped `scraped_at` to be non-empty, identical, and canonical `YYYY-MM-DDTHH:MM:SSZ`, then use that single value; malformed, inconsistent, or missing provenance raises `ValueError`. Empty optional Go input may serialize `scrapedAt` as an empty string.
- In `src/llm_comparison/compare_models_template.py`, give the existing first header metadata element the exact id `dataFreshness` and, in the Go view only, replace its comparison-wide `Data updated` text with `OpenCode Go pricing scraped: <RFC3339 timestamp>`. Initialize from `payload.scrapedAt` so the embedded fallback is complete.
- Extend `initializeGoFromCsv(csvRows)` to require `scraped_at`, accept only the canonical `YYYY-MM-DDTHH:MM:SSZ` form, reject blank or inconsistent row values, update `payload.scrapedAt`, and refresh `#dataFreshness` before rendering the fetched rows. Any malformed/failing fetched CSV must continue through the existing rejected-promise path and leave the already rendered embedded Go payload and timestamp intact. Keep the Comparison view’s existing human-readable `Data updated: Month D, YYYY` behavior unchanged.
- Regenerate `public/index.html` through `llm_comparison.compare_models` after refreshing both CSVs so the checked-in fallback payload, template JavaScript, and visible embedded timestamp agree.

### 5. Document the one-command workflow

- In `README.md`, replace the Artificial-Analysis-only primary Update and Publish command with `update-all-data` and the module alternative `python -m llm_comparison.update_all_data`.
- State the exact sequence: Artificial Analysis scrape/write/date update, OpenCode Go live pricing scrape joined to the newly written AA CSV, then one publisher invocation producing one combined source-data commit plus the required `gh-pages` deployment commit.
- Document unified `--skip-publish` as the way to refresh both datasets locally. Document `update-artificial-analysis` and `update-opencode-go` as local-only diagnostic/source-specific commands that never commit or publish; neither alone is the complete refresh workflow.
- Document `data/opencode_go.csv.scraped_at` as the OpenCode Go pricing scrape completion time, repeated on every row in UTC RFC 3339 whole-second form, and note that the same value appears in the `?view=opencode-go` report metadata. Keep the manual `convert-results` fallback and the separate report-wide Artificial Analysis display date accurate.
- Include the direct view URL shape `?view=opencode-go` and the “OpenCode Go value” navigation label so users can find the new view.

## Critical files & anchors

- `src/llm_comparison/update_all_data.py` — new `parse_args`, `async_main`, `run_publish_script`, and `main` ownership boundary for the only publishing command.
- `src/llm_comparison/update_opencode_go.py` — `CSV_COLUMNS`, `build_output_rows`, and `async_main`; owns one-time scrape provenance and the fresh-AA join.
- `src/llm_comparison/compare_models_core.py` — `OPENCODE_GO_COLUMNS` and `opencode_go_payload`; keeps provenance dataset-level rather than a table metric.
- `src/llm_comparison/compare_models_template.py` — header metadata plus `initializeGoFromCsv`; must update freshness for both embedded and fetched Go data.
- `scripts/update-gh-pages.py` — `GENERATED_FILES`, `require_clean_or_commit_generated`, and `publish`; confirms one publisher call already yields one combined source-data commit.

## Verification

1. From the repository root, run the focused behavior tests:
   ```bash
   python -m pytest tests/test_update_all_data.py tests/test_update_artificial_analysis.py tests/test_update_opencode_go.py tests/test_compare_models.py tests/test_update_gh_pages.py
   ```
   New orchestration tests must assert exact call order `AA -> Go -> publish`, exactly one publisher call, `Go.aa_csv == AA.csv`, both children still run under outer `--skip-publish`, AA failure skips Go/publish, and Go failure skips publish. Source-updater parser tests must assert removed publication flags are rejected.
2. In `tests/test_update_opencode_go.py`, use a fixed `current_scraped_at` result and assert the literal last header is `scraped_at`, every output row receives the same `2026-07-17T14:32:05Z`, malformed timestamps fail before output replacement, and the existing failed-scrape/failed-join preservation contracts still pass.
3. In `tests/test_compare_models.py`, assert `scrapedAt` is present in the embedded Go payload, malformed/inconsistent row timestamps fail, `scraped_at` is absent from displayed columns, the generated Go bootstrap requires and applies fetched freshness, and Comparison still retains `Data updated`. Exercise actual fetched-versus-embedded behavior in the browser smoke below rather than testing JavaScript source text as a substitute.
4. Run static checks over the affected code:
   ```bash
   python -m ruff check src/llm_comparison/update_all_data.py src/llm_comparison/update_artificial_analysis.py src/llm_comparison/update_opencode_go.py src/llm_comparison/compare_models.py src/llm_comparison/compare_models_core.py tests
   python -m mypy src/llm_comparison/update_all_data.py src/llm_comparison/update_artificial_analysis.py src/llm_comparison/update_opencode_go.py src/llm_comparison/compare_models.py src/llm_comparison/compare_models_core.py
   ```
5. Exercise the real two-source path without committing or publishing:
   ```bash
   PYTHONPATH=src python -m llm_comparison.update_all_data --skip-publish
   ```
   Expected: Artificial Analysis completes before OpenCode Go starts; both `data/results.csv` and `data/opencode_go.csv` refresh; no publisher runs; the Go CSV has one parseable UTC `scraped_at` value shared by every row.
6. Regenerate the checked-in report from the refreshed data:
   ```bash
   PYTHONPATH=src python -m llm_comparison.compare_models price intelligence --opencode-go-input data/opencode_go.csv --output public/index.html
   ```
   Expected: report generation succeeds, the embedded `openCodeGo.scrapedAt` matches the CSV, and the generated JavaScript remains syntactically valid under the existing inline-script `node --check` procedure.
7. Serve `public/` locally and open `http://127.0.0.1:8000/?view=opencode-go`:
   ```bash
   python -m http.server 8000 --directory public
   ```
   Verify the “OpenCode Go value” navigation item is active, the metadata shows the CSV’s exact UTC scrape timestamp, the Go table/chart render, and the default Comparison view still shows its existing human-readable data date.

## Assumptions & contingencies

- “One total git commit” means one combined generated-data commit on the source branch. The separate `gh-pages` deployment commit remains because the current Pages publisher deploys through that branch.
- The source-specific commands are a clean-cutover local-only interface; existing automation using their removed publication flags must switch to `update-all-data` rather than receive a compatibility shim.
- OpenCode Go freshness is a true UTC instant, not the existing report-wide calendar date, and is displayed as the exact RFC 3339 value to avoid locale/timezone ambiguity.
- If the live source changes before implementation and the strict OpenCode table selector rejects it, update that source-specific parser and its fixture first; do not weaken table/header validation or publish partial data.
