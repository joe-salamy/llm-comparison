# 2D chart zoom plan

## Context

Add zoom to the generated 2D chart so clustered model points can be inspected in place. The end state is a static HTML report where the 2D scatter plot supports wheel/trackpad zoom around the pointer, drag pan, touch pinch zoom, one-finger touch pan, the same visible “Reset view” affordance already used by the 3D graph, and the same style zoom number readout as the 3D graph. The default 2D view must remain the full metric range until the user zooms or pans, and metric changes must discard any stale zoom state through the existing chart redraw path.

## Approach

1. In `compare_models_template.py`, rename the existing reset button id from the 3D-specific `resetCamera` to the mode-neutral `resetView`, keeping the literal button text `Reset view`.
   - Edit the chart actions markup at `compare_models_template.py:724-730` from `<button class="chart-button" id="resetCamera" type="button" hidden>Reset view</button>` to `<button class="chart-button" id="resetView" type="button" hidden>Reset view</button>`.
   - Update every template/test callsite of `resetCamera`; the exact current source callsites are:
     - `compare_models_template.py:729` markup id.
     - `compare_models_template.py:1725` visibility toggle.
     - `compare_models_template.py:2311` 3D reset click listener.
     - `tests/test_compare_models.py:274` generated-HTML assertion list.
   - Do not leave a compatibility alias or duplicate reset button. One reset-view button is used by both 2D and 3D, and the mode-specific `trackChartListener(...)` binding is replaced whenever `resetChartCanvas()` clones `#chart` and disposes `chartDisposers`.

2. In `compare_models_template.py:1709-1729`, make `drawGraph()` expose the shared reset button and shared zoom number for both 2D and 3D charts while keeping the view cube 3D-only.
   - Keep `chartSection.classList.toggle("is-3d", categories.length === 3);`.
   - Add `chartSection.classList.toggle("is-2d", categories.length === 2);` so mobile/touch CSS can target 2D without weakening the existing 3D rule.
   - Change reset visibility to the exact logic `document.getElementById("resetView").hidden = ![2, 3].includes(categories.length);`.
   - Keep `document.getElementById("viewCube").hidden = categories.length !== 3;`.
   - Change zoom number visibility to the exact logic `document.getElementById("zoomIndicator").hidden = ![2, 3].includes(categories.length);` so 2D shows `1.00x`, then updates as the user zooms.
   - Keep the dispatch order `if (categories.length === 2) draw2D(categories); else draw3D(categories);`.

3. In the CSS around `compare_models_template.py:672-674`, extend the touch-action rule so 2D touch panning and pinch zoom receive raw touch events.
   - Replace the single selector `.chart-wrap.is-3d #chart { touch-action: none; }` with `.chart-wrap.is-2d #chart, .chart-wrap.is-3d #chart { touch-action: none; }`.
   - Do not change the base `#chart` size rules at `compare_models_template.py:588-590` or fullscreen sizing at `compare_models_template.py:479-488`.

4. In `draw2D(categories)` (`compare_models_template.py:1732-1920`), add local 2D view state and reuse the existing canvas/listener patterns.
   - Add the state immediately after `const hoverRadius = 18;`:
     - `const initial2DView = { minX: ranges[0].min, maxX: ranges[0].max, minY: ranges[1].min, maxY: ranges[1].max, zoom: 1 };`
     - `let view2D = { ...initial2DView };`
     - `let dragging = false;`
     - `let last = { x: 0, y: 0 };`
     - `let pinchDistance = 0;`
   - Add `const zoomIndicator = document.getElementById("zoomIndicator");` beside the other local DOM references in `draw2D(categories)`.
   - Add helper functions near the existing `project(row, width, height)` anchor:
     - `function current2DSpan() { return { x: view2D.maxX - view2D.minX, y: view2D.maxY - view2D.minY }; }`
     - ``function update2DZoomIndicator() { zoomIndicator.textContent = `${view2D.zoom.toFixed(2)}x`; }``
     - `function clamp2DView() { ... }` clamps the visible domain inside the original metric ranges, preserves positive spans, and clamps `view2D.zoom` to the same maximum as 3D zoom: `8`.
     - `function reset2DView() { view2D = { ...initial2DView }; update2DZoomIndicator(); hover = null; tooltip.style.display = "none"; render(); }`
     - `function chartPoint(eventOrTouch) { const rect = canvas.getBoundingClientRect(); return { x: eventOrTouch.clientX - rect.left, y: eventOrTouch.clientY - rect.top }; }`
     - `function zoom2DAt(point, factor, width, height) { ... }` zooms around the pointer by computing the data coordinate under `point` before the zoom, applying a new span divided by `factor`, then choosing `minX/maxX/minY/maxY` so that data coordinate remains under the same relative plot position.
     - `function pan2DBy(deltaX, deltaY, width, height) { ... }` converts pixel deltas to metric-domain deltas using the current visible spans and plot dimensions, then updates `view2D.minX/maxX/minY/maxY`.
     - `function touchPoint(touch) { return { x: touch.clientX, y: touch.clientY }; }` and `function touchDistance(touches) { return Math.hypot(touches[0].clientX - touches[1].clientX, touches[0].clientY - touches[1].clientY); }`, copied in shape from `draw3D()` at `compare_models_template.py:2205-2214`.
   - Implement `clamp2DView()` with these exact edge rules:
     - Let `fullX = ranges[0].span` and `fullY = ranges[1].span`.
     - Let `minSpanX = fullX / 8` and `minSpanY = fullY / 8`; let `maxSpanX = fullX / 0.55` and `maxSpanY = fullY / 0.55`, but when clamping to the original data bounds the visible span must never exceed `fullX`/`fullY` because the 2D chart should not pan into empty space.
     - If a computed span is less than the minimum, expand it around the current center; if greater than the full range, reset that axis to the original `ranges[n].min/max`.
     - If `view2D.minX` falls below `ranges[0].min`, shift both x bounds right; if `view2D.maxX` exceeds `ranges[0].max`, shift both x bounds left. Apply the same rule for y. This preserves zoom level while preventing empty margins.
     - Recompute `view2D.zoom = ranges[0].span / (view2D.maxX - view2D.minX)` after clamping, then clamp that numeric readout to `[1, 8]` for 2D because the no-empty-space rule prevents zooming out beyond the initial view.
   - Change `project(row, width, height)` to map with `view2D.minX/maxX/minY/maxY` instead of `ranges[n].min/span`.
   - In `render()`, keep the existing margins `{ top: 54, right: 58, bottom: 74, left: 92 }` and plot rect calculations. Replace tick values at `compare_models_template.py:1786-1787` with the visible-domain equivalents:
     - `const xValue = view2D.minX + ratio * (view2D.maxX - view2D.minX);`
     - `const yValue = view2D.minY + ratio * (view2D.maxY - view2D.minY);`
   - Keep the grid/tick count constants `minorTickCount = 20` and `majorTickEvery = 4`.
   - At the start of `render()`, call `update2DZoomIndicator()` before drawing so wheel, pinch, pan, reset, resize, and initial render all keep the visible number in sync. The visible text format must be exactly `${view2D.zoom.toFixed(2)}x`, matching the 3D graph’s `${zoom.toFixed(2)}x` format.

5. In the 2D trend rendering block at `compare_models_template.py:1824-1841`, keep the trend line clipped to the plot rectangle but project it through the same visible-domain transform as points.
   - Replace the current full-range pixel endpoints:
     - `start = { x: plotLeft, y: plotBottom - trend.intercept * plotHeight }`
     - `end = { x: plotRight, y: plotBottom - (trend.intercept + trend.slope) * plotHeight }`
   - Compute the trend in data space from the existing normalized trend fields:
     - For any data-space x, `xRatio = (x - ranges[0].min) / ranges[0].span`.
     - `yRatio = trend.intercept + trend.slope * xRatio`.
     - `y = ranges[1].min + yRatio * ranges[1].span`.
   - Build endpoints at `view2D.minX` and `view2D.maxX`, then project them through the same pixel mapping used by points. Keep the existing `ctx.rect(plotLeft, plotTop, plotWidth, plotHeight); ctx.clip();` so off-screen portions are clipped.

6. In the 2D event listener section at `compare_models_template.py:1890-1920`, preserve hover behavior and add pan/zoom/reset listeners using `trackChartListener(...)`.
   - Keep `chartRender = render; const canvas = document.getElementById("chart");`.
   - Change the existing `mousemove` hover listener to a `window` `mousemove` listener like 3D uses at `compare_models_template.py:2224-2260`, because panning must continue if the pointer leaves the canvas while dragging.
   - On `mousedown` over the canvas: set `dragging = true`, `last = { x: event.clientX, y: event.clientY }`, hide the tooltip, and set `canvas.style.cursor = "grabbing"`.
   - On `window` `mouseup`: set `dragging = false` and restore the cursor to `"pointer"` only if `hover` exists, otherwise `""`.
   - On `window` `mousemove`: if `dragging`, run `const rect = canvas.getBoundingClientRect(); pan2DBy(event.clientX - last.x, event.clientY - last.y, rect.width, rect.height);`, update `last`, clear `hover`, hide the tooltip, render, and return. If not dragging, keep the existing nearest-point hover behavior, but first verify the pointer is inside the canvas bounds as the 3D handler does.
   - Add `trackChartListener(canvas, "wheel", event => { event.preventDefault(); const rect = canvas.getBoundingClientRect(); const point = { x: event.clientX - rect.left, y: event.clientY - rect.top }; zoom2DAt(point, event.deltaY < 0 ? 1.08 : 0.92, rect.width, rect.height); render(); }, { passive: false });`.
   - Add touch handlers matching the 3D structure at `compare_models_template.py:2273-2310`:
     - One touch starts panning with `dragging = true` and `last = touchPoint(event.touches[0])`.
     - Two touches stop panning and store `pinchDistance = touchDistance(event.touches)`.
     - One-touch move prevents default, runs `const touch = event.touches[0]; const rect = canvas.getBoundingClientRect();`, pans with `pan2DBy(touch.clientX - last.x, touch.clientY - last.y, rect.width, rect.height)`, updates `last = touchPoint(touch)`, hides tooltip, clears hover, and renders.
     - Two-touch move prevents default, computes `nextDistance / pinchDistance`, reads `const rect = canvas.getBoundingClientRect();`, builds the midpoint as `{ x: ((event.touches[0].clientX + event.touches[1].clientX) / 2) - rect.left, y: ((event.touches[0].clientY + event.touches[1].clientY) / 2) - rect.top }`, calls `zoom2DAt(midpoint, nextDistance / pinchDistance, rect.width, rect.height)`, renders, then stores `pinchDistance = nextDistance`.
     - `touchend` and `touchcancel` reset `dragging`/`pinchDistance` using the same state transitions as 3D.
   - Add `trackChartListener(document.getElementById("resetView"), "click", reset2DView);`.
   - Keep `trackChartListener(window, "resize", render); render();`.

7. In `draw3D(categories)`, update only the renamed reset control and preserve existing 3D camera behavior.
   - Change `trackChartListener(document.getElementById("resetCamera"), "click", () => { setCamera(initialCamera); });` to use `resetView`.
   - Keep `initialCamera = { rotationX: 0.62, rotationY: 0.78, zoom: 1.25 }`, `viewPresets`, `updateZoomIndicator()`, 3D wheel zoom clamp `Math.max(0.55, Math.min(8, zoom))`, and view-cube behavior unchanged.

8. Update `tests/test_compare_models.py` to assert the generated HTML exposes 2D zoom/reset behavior, the renamed reset id, and the shared zoom number.
   - Add a new test after `test_3d_zoom_indicator_is_rendered_and_updated` named `test_2d_chart_supports_zoom_pan_reset_and_zoom_number`.
   - Use the same `write_html(...)` fixture shape as `test_chart_type_uses_active_scoring_categories`: two categories `["quality", "cost"]`, one or two rows with `_raw_values`, `FINAL_SCORE`, and a one-element or matching pareto list.
   - Assert these exact or intentionally equivalent generated strings after implementation:
     - `'id="resetView"' in html`
     - `'id="zoomIndicator"' in html`
     - `'document.getElementById("resetView").hidden = ![2, 3].includes(categories.length)' in html`
     - `'document.getElementById("zoomIndicator").hidden = ![2, 3].includes(categories.length)' in html`
     - `"const initial2DView = { minX: ranges[0].min, maxX: ranges[0].max, minY: ranges[1].min, maxY: ranges[1].max, zoom: 1 }" in html`
     - `"function reset2DView()" in html`
     - `"function update2DZoomIndicator()" in html`
     - `"zoomIndicator.textContent = `${view2D.zoom.toFixed(2)}x`" in html`
     - `"function zoom2DAt(" in html`
     - `"function pan2DBy(" in html`
     - `'trackChartListener(canvas, "wheel"' in html`
     - `'trackChartListener(document.getElementById("resetView"), "click", reset2DView)' in html`
   - Modify `test_mobile_3d_chart_supports_touch_controls_and_fullscreen_fallback` only if the touch-action assertion must include 2D; otherwise add the 2D selector assertion to the new 2D test: `'.chart-wrap.is-2d #chart' in html`.
   - Modify `test_metric_filter_selection_redraws_chart_and_2d_hides_3d_controls`:
     - Rename it to `test_metric_filter_selection_redraws_chart_and_toggles_chart_controls`.
     - Keep `assert "resetChartCanvas();\n      drawGraph();" in html`.
     - Replace `hidden_3d_controls = ["resetCamera", "viewCube", "zoomIndicator"]` with `hidden_3d_controls = ["viewCube"]`.
     - Add the reset visibility assertion from above for `resetView`.
     - Add the zoom number visibility assertion from above for `zoomIndicator`.
     - Keep the existing loop asserting the view cube uses `categories.length !== 3`.

9. Regenerate the tracked report `index.html` from the template after tests pass, because README states generated reports are written to the repository root and the current tracked `index.html` mirrors `compare_models_template.py`.
   - Use the current generated report category set, confirmed from `index.html` payload: `artificial_analysis_intelligence_index`, `blended_usd_per_1m_tokens`, and `median_tokens_per_second`.
   - Run from repo root: `python compare_models.py artificial_analysis_intelligence_index blended_usd_per_1m_tokens median_tokens_per_second`.
   - Do not edit `index.html` by hand; it must be generated from `compare_models_template.py` and `results.csv`.

## Critical files & anchors

- `compare_models_template.py:724-753` — chart actions/canvas markup; rename `resetCamera` to `resetView` and keep one shared button.
- `compare_models_template.py:1709-1729` — `drawGraph()` mode switch; expose reset and zoom number for 2D/3D and keep view cube 3D-only.
- `compare_models_template.py:1732-1920` — `draw2D(categories)`; add 2D view state, coordinate-domain mapping, wheel zoom, drag/touch pan, pinch zoom, reset binding, and zoom number updates.
- `compare_models_template.py:1922-2323` — `draw3D(categories)`; update only the renamed reset button binding while preserving camera behavior.
- `tests/test_compare_models.py:160-282` — generated-HTML chart control tests; add 2D zoom/reset coverage and update reset id/control visibility assertions.

## Verification

1. Run the focused generated-HTML tests from repo root:
   - `python -m pytest tests/test_compare_models.py -k "2d_chart_supports_zoom_pan_reset_and_zoom_number or toggles_chart_controls or 3d_zoom_indicator_is_rendered_and_updated or mobile_3d_chart_supports_touch_controls_and_fullscreen_fallback"`
   - Expected: all selected tests pass, proving the template contains the new 2D reset/zoom/pan handlers, shows the 2D zoom number, keeps 3D zoom indicator behavior, and still redraws after metric selection.
2. Run the full comparison test file from repo root:
   - `python -m pytest tests/test_compare_models.py`
   - Expected: all tests pass; no generated-HTML assertion still expects `resetCamera`.
3. Run static checks from repo root:
   - `python -m ruff check .`
   - `python -m mypy compare_models.py compare_models_core.py convert_results.py update_artificial_analysis.py tests`
   - Expected: both pass. `compare_models_template.py` is excluded from Ruff E501 only, not from syntax/import checks.
4. Regenerate the static report from repo root:
   - `python compare_models.py artificial_analysis_intelligence_index blended_usd_per_1m_tokens median_tokens_per_second`
   - Expected stdout: `Wrote <N> ranked rows to index.html`; exact row count depends on `results.csv`.
5. Manually verify the generated `index.html` in a browser:
   - Open `index.html`.
   - In the metric selector, choose exactly two chart metrics if the default report opens in 3D; use `Artificial Analysis Intelligence Index` and `Blended (USD/1M Tokens)` for a 2D chart.
   - Expected: `Reset view` and the `1.00x` zoom indicator are visible in 2D; `Top/Iso/Back/...` view cube is hidden.
   - Wheel up over a clustered point area: points spread around the pointer, axis tick labels update to a narrower value range, and the zoom number increases above `1.00x`.
   - Drag the zoomed chart: points and grid pan without selecting text or scrolling the page.
   - Click `Reset view`: points, trend line, and axis ticks return to the full original metric ranges.
   - Switch to three metrics: `Reset view`, view cube, and 3D zoom indicator are visible; dragging rotates the 3D chart and `Reset view` restores the initial camera.

## Assumptions & contingencies

- Interaction choice is fixed: wheel/trackpad zoom around pointer, drag pan, touch pinch zoom, and one-finger touch pan. This was selected because it best supports exploring clustered points without repeated mode changes.
- The reset button is renamed to `resetView` instead of adding `reset2DView`; this avoids a second visible reset affordance and removes the now-misleading `resetCamera` id. If an implementer finds external, non-test references to `resetCamera`, update them to `resetView` in the same clean cutover rather than adding an alias.
- The existing `#zoomIndicator` is required for both 2D and 3D. In 2D it displays `view2D.zoom.toFixed(2)x`; in 3D it keeps displaying `zoom.toFixed(2)x`. If the shared overlay position looks too low without the 3D view cube above it, adjust only CSS positioning for 2D via `.chart-wrap.is-2d .zoom-indicator`, not the DOM or text format.
