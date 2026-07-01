# Auto-update Artificial Analysis data plan

## Context

The repo currently updates Artificial Analysis data manually: README lines 61-69 say to expand all columns on `https://artificialanalysis.ai/leaderboards/models`, copy from `Features` through the last `Model, Providers`, paste into `input.txt`, and run `python convert_results.py` to write `results.csv`. The requested end state is a Python script that updates Artificial Analysis model data automatically without hard-coding model names, row count, or column headers, and without using clipboard selection. Use Python Playwright for browser automation, per user selection. The automated path must be truly header-agnostic: it reads actual table headers/cells from the DOM and does not use the manual-copy provider convention where `convert_results.py` inserts a `Providers` header after `Creator`.

Verified facts:
- `pyproject.toml` currently has `dependencies = []` and `dev = [pytest, ruff, mypy]`; Playwright must be optional so the core runtime remains standard-library-only.
- `convert_results.py:126-140` currently inserts `Providers` after `Creator` whenever the copied header omitted it. Keep that only for the legacy manual parser; the new automated path must not call that parser.
- `convert_results.py:224-231` writes CSV through `clean_csv_cell(cell, index)`. Change this to header-key-aware cleaning for shared structured writes so context-window normalization is not tied to a fragile column index.
- Live expanded page inspection found `main table`, two `thead tr` rows, 41 visible `tbody td` cells per row, and 219 `tbody tr` rows at inspection time. The row count and column count are runtime facts only and must not be hard-coded.
- The live creator cell contains visible text and `img[alt]` with the same label. The updater must extract one value per actual data cell: use visible text first, fall back to image alt text only when visible text is empty.

## Approach

1. Refactor CSV writing utilities in `convert_results.py` without changing the legacy CLI behavior.
   - Add `def csv_headers_from_display_headers(display_headers: list[str]) -> list[str]:` returning `[to_csv_key(header) for header in display_headers]`.
   - Add `def dedupe_csv_headers(csv_headers: list[str]) -> list[str]:` that preserves first occurrences and appends `_2`, `_3`, ... to later duplicates in encounter order. Use it in all structured CSV writes. This avoids decisions when the site exposes duplicate or renamed headers.
   - Change `clean_csv_cell` to `def clean_csv_cell(value: str, csv_header: str) -> str:`. Preserve current behavior except context-window conversion triggers when `csv_header == "context_window_tokens"`, not when the column index is `1`. Dollar, percent, dash, and numeric-comma normalization stay unchanged.
   - Add `def write_csv(rows: list[list[str]], csv_headers: list[str], path: Path) -> None:` with the same public name but update its implementation to call `dedupe_csv_headers(csv_headers)`, create `path.parent` when it is not `Path('.')`, and clean each cell with its header key. If a row width differs from the header width, raise `ValueError(f"Expected {len(csv_headers)} columns per row before writing CSV; mismatches: {examples}")` where `examples` names up to five 1-based row indexes and widths.
   - Add `def write_table_csv(display_headers: list[str], rows: list[list[str]], path: Path) -> list[str]:` that converts display headers with `csv_headers_from_display_headers`, calls `write_csv`, and returns the final deduped CSV headers. The new updater uses this function directly, bypassing `parse_input` and the provider insertion path.
   - Update existing callsites in `convert_results.py:284-285` so the manual CLI still does `_display_headers, csv_headers, rows = parse_input(args.input)` then `write_csv(rows, csv_headers, args.csv)`.

2. Make the legacy manual-copy provider insertion data-shape based, not unconditional.
   - In `parse_headers`, remove the unconditional `Providers` insertion at `convert_results.py:133-138`; it should only parse header pairs and return base display/csv headers.
   - In `parse_input`, after raw rows are collected and before width validation, compare each row width to `len(display_headers)`.
   - If every row width equals `len(display_headers)`, keep headers unchanged.
   - Else if every row width equals `len(display_headers) + 1` and `"Creator" in display_headers`, insert display header `"Providers"` immediately after `"Creator"`, recompute `csv_headers`, and then validate widths. This preserves existing copied `input.txt` behavior without affecting the automated path.
   - Else raise the existing mismatch `ValueError`, updated to report the expected base width and examples. Do not add any compatibility alias or deprecated path.
   - Keep `DISPLAY_TO_CSV` for stable known report keys; unknown or changed site headers continue to fall through to generic slug generation via `to_csv_key`.

3. Add a new script `update_artificial_analysis.py` that scrapes the live table and writes `results.csv` directly.
   - Add the module to `pyproject.toml [tool.setuptools].py-modules` as `"update_artificial_analysis"`.
   - Do not import Playwright at module import time. Import `async_playwright` inside the async browser function so tests can import pure helpers without installing browsers.
   - Define constants only for behavior and defaults, not data: `DEFAULT_URL = "https://artificialanalysis.ai/leaderboards/models"`, `DEFAULT_CSV = Path("results.csv")`, `DEFAULT_HTML = Path("index.html")`, `DEFAULT_TEMPLATE = Path("compare_models_template.py")`.
   - CLI signature:
     - `--url`, default `DEFAULT_URL`
     - `--csv`, default `DEFAULT_CSV`
     - `--html`, default `DEFAULT_HTML`
     - `--template`, default `DEFAULT_TEMPLATE`
     - `--uploaded-date`, default `date.today()`, parsed by `date.fromisoformat`
     - `--headed`, `store_true`, for manual debugging
     - `--timeout-ms`, default `30000`
   - `main()` runs `asyncio.run(async_main(args))`, writes CSV through `convert_results.write_table_csv`, updates dates through `convert_results.update_upload_dates([args.template, args.html], args.uploaded_date)`, and prints exactly:
     - `Scraped {row_count} rows and {column_count} columns from {url}`
     - `Wrote {row_count} rows to {csv_path}`
     - `Updated upload date in {updated_files} files`

4. Implement DOM extraction in `update_artificial_analysis.py` with no model/header hard-coding.
   - Navigate with Playwright Chromium to `args.url` using `wait_until="networkidle"` and timeout `args.timeout_ms`.
   - Find the column toggle by role/name, not a brittle CSS path: if a button whose accessible name matches `/Expand columns/i` is visible, click its first match; then wait for a button matching `/Collapse columns/i` to be visible. If no expand button exists but collapse is visible, proceed. If neither is visible before timeout, raise `RuntimeError("Could not find Artificial Analysis column expansion control")`.
   - Locate the table with `page.locator("main table").first`. Wait for `thead tr` and `tbody tr` under that table. Do not use the class-heavy selectors from DevTools.
   - Evaluate the table into JSON with one snapshot per header/cell. Each header snapshot includes `text = element.innerText`. Each cell snapshot includes: `text = element.innerText`, `linkText = joined innerText from all descendant links`, `hasLink = whether descendant links exist`, and `imageAlts = all non-empty descendant img alt values`.
   - Use only the last `thead tr` as leaf headers. Convert each header text to display text with `header_lines = [non-empty stripped lines from text.splitlines()]`; if there are two or more lines, call existing `convert_results.build_display_header(header_lines[0], header_lines[1])`, otherwise use the single line. Empty leaf headers are kept only if their column is not dropped; their CSV key becomes the generic slug from `to_csv_key`, then deduped.
   - Drop action-only columns generically. A column is action-only when every row's cell at that index has at least one link, has non-empty normalized text, and normalized full cell text equals normalized concatenated link text. This drops the live trailing links column without checking for the text `Further Analysis`, `Model`, or `Providers`.
   - For retained cells, normalize value as: strip `cell.text`; if it is non-empty, collapse internal whitespace/newlines to a single space and use it; otherwise join non-empty `imageAlts` with `; `; if both are empty, use `""`. This prevents the duplicated image-alt provider value from becoming an extra column.
   - Validate before writing: at least one retained column, at least one row, every retained row width equals retained header width. Raise `ValueError` with row indexes and widths on mismatch. Do not silently pad or truncate.

5. Add tests for converter refactors and updater pure helpers.
   - Update `tests/test_convert_results.py::test_parse_headers_derives_columns_from_input` so `parse_headers(lines)` returns no synthetic `Providers` header by itself.
   - Add `test_parse_input_preserves_legacy_provider_insertion_when_rows_have_extra_value`: use the current copied-text shape with headers `Model`, `Context Window`, `Creator`, `License`, marker `Further Analysis`, row delimiter `Model`, `Providers`, and a row containing model/context/creator/provider/license. Assert `parse_input` inserts `Providers` after `Creator` and row width matches.
   - Add `test_parse_input_does_not_insert_provider_for_structured_width`: same headers but row contains model/context/creator/license only. Assert no `providers` CSV header exists.
   - Update `test_clean_csv_cell_normalizes_numeric_values` to pass header keys, including `clean_csv_cell("1.05M", "context_window_tokens") == "1050000"` and a non-context header leaves non-numeric text unchanged.
   - Add `test_write_table_csv_dedupes_dynamic_headers`: write two identical display headers to a temp CSV and assert output header suffixes `_2` and rows are cleaned under those final keys.
   - Add `tests/test_update_artificial_analysis.py` for pure helpers only, importing the new module without requiring Playwright browsers:
     - `test_action_only_column_is_dropped_without_header_name`: create two columns where the second has cells with `hasLink=True`, `text="Model Providers"`, `linkText="Model Providers"`; assert extraction returns only the first column and does not inspect header names.
     - `test_cell_text_preferred_over_duplicate_image_alt`: a cell with `text="Anthropic"` and `imageAlts=("Anthropic",)` returns one value `"Anthropic"`.
     - `test_image_alt_fallback_when_text_empty`: a cell with empty text and image alt `"Provider X"` returns `"Provider X"`.

6. Update documentation and optional dependency configuration.
   - In `pyproject.toml`, add optional dependency group `update = ["playwright>=1.49"]`. Keep `[project].dependencies = []`.
   - In README Installation, keep the core standard-library runtime sentence and add an update-script install block:
     - `python -m pip install -e ".[update]"`
     - `python -m playwright install chromium`
   - In README Convert Raw Results, add an automated path before the manual path:
     - `python update_artificial_analysis.py --uploaded-date YYYY-MM-DD`
     - State it opens the leaderboard, expands columns, reads the table DOM, writes `results.csv`, and updates the displayed data date in `compare_models_template.py`/`index.html` when present.
   - Keep the manual `convert_results.py` copy/paste path as a fallback, but update wording so `input.txt` is described as the manual raw-copy input, not the source for the automated updater.
   - In README Development mypy command, add `update_artificial_analysis.py` to the checked files.

## Critical files & anchors

- `convert_results.py:126-190` — legacy copied-input header and row parsing; move provider insertion out of `parse_headers` and into `parse_input` based on row width.
- `convert_results.py:203-231` — cell cleaning and CSV writing; change cleaning from column-index-aware to csv-header-aware and add structured table writer.
- `update_artificial_analysis.py` — new Playwright updater script; keep Playwright imports lazy and header/model extraction data-driven.
- `tests/test_convert_results.py:15-104` — existing parser and cleaner expectations that must change with provider insertion and header-aware cleaning.
- `pyproject.toml:8-23` — preserve empty required dependencies, add optional `update`, and include the new module in `py-modules`.

## Verification

Run from `C:/Users/joesa/Code/llm-comparison`.

0. Install verification dependencies before running checks:
   ```powershell
   python -m pip install -e ".[dev,update]"
   python -m playwright install chromium
   ```

1. Unit tests for changed behavior:
   ```powershell
   python -m pytest tests/test_convert_results.py tests/test_update_artificial_analysis.py
   ```
   Required observable checks: structured-width parsed input has no `providers` header; legacy extra-width copied input still gets `providers`; action-only link column is dropped without checking its header text; duplicate image alt does not create an extra provider value.

2. Lint and type checks:
   ```powershell
   python -m ruff check .
   python -m mypy compare_models.py compare_models_core.py convert_results.py update_artificial_analysis.py tests
   ```

3. Live end-to-end smoke test without overwriting repo data:
   ```powershell
   python update_artificial_analysis.py --csv .tmp/aa-results.csv --html .tmp/index.html --template .tmp/compare_models_template.py --uploaded-date 2026-06-23
   ```
   Expected observable output: `Scraped N rows and M columns from https://artificialanalysis.ai/leaderboards/models`, `Wrote N rows to .tmp/aa-results.csv`, and no row-width exception. Open `.tmp/aa-results.csv` or read its first line and verify it contains dynamically generated headers from the live expanded table and no synthetic provider column unless the live table itself exposes a retained provider column.

4. Existing report still works from the generated smoke CSV:
   ```powershell
   python compare_models.py price intelligence --input .tmp/aa-results.csv --output .tmp/aa-index.html
   ```
   Expected observable output: command exits successfully and `.tmp/aa-index.html` is created. This proves the automated CSV preserves the scoring columns needed by the current report path.

5. Cleanup temporary smoke artifacts after verification:
   ```powershell
   Remove-Item -Recurse -Force .tmp
   ```

## Assumptions & contingencies

- Use Python Playwright rather than Selenium; the user selected Playwright. If Playwright is unavailable in the execution environment, implement the script and tests anyway, and mark only the live smoke test blocked with the exact install/browser error.
- The script may hard-code the page URL and the expand/collapse control labels because those are UI behavior selectors, not data columns. It must not hard-code model names, benchmark names, metric headers, row count, or column count.
- If the site changes so rows are virtualized, the first live smoke test will show fewer DOM rows than expected by visual count. Pre-decided fallback: add a scrolling collector that repeatedly scrolls the table container, records rows by their full normalized cell tuple in insertion order, and stops after two consecutive scroll positions add no new rows. Keep the same downstream structured table writer.
- If the site removes the expand/collapse control entirely but the table already exposes all columns, proceed only when `tbody tr` exists and the second header row has more than one retained data column; otherwise raise the explicit expansion-control error above.
