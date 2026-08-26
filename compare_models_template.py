from __future__ import annotations

HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>LLM Comparison</title>
  <script>
    (() => {
      const storageKey = "llmComparison.theme";
      const stored = (() => {
        try {
          return window.localStorage.getItem(storageKey);
        } catch {
          return null;
        }
      })();
      const systemDark = window.matchMedia?.("(prefers-color-scheme: dark)").matches;
      const theme = stored === "light" || stored === "dark" ? stored : systemDark ? "dark" : "light";
      document.documentElement.dataset.theme = theme;
      document.documentElement.style.colorScheme = theme;
    })();
  </script>
  <style>
    :root {
      --bg: #f6f7f4;
      --ink: #1c1f1d;
      --muted: #5d655f;
      --line: #d5d9d2;
      --panel: #ffffff;
      --panel-soft: #fbfcfa;
      --panel-accent: #f3faf5;
      --heading: #242824;
      --control-ink: #303630;
      --button-bg: #f7f8f5;
      --button-hover: #eef0ec;
      --accent: #1e5637;
      --accent-hover: #17472d;
      --accent-soft: #e8f3ec;
      --accent-line: #9ab7a6;
      --metric-card-line: #b8c1b8;
      --link: #1f5d8f;
      --chart-bg: #fbfcfa;
      --chart-text: #4f5851;
      --chart-title: #2f3831;
      --chart-axis: #9ea79f;
      --chart-axis-strong: #747d75;
      --chart-grid-minor: rgba(207, 212, 204, 0.38);
      --chart-grid-major: rgba(164, 172, 164, 0.68);
      --chart-grid-3d-minor: rgba(207, 212, 204, 0.30);
      --chart-grid-3d-major: rgba(164, 172, 164, 0.60);
      --chart-label-halo: rgba(246, 247, 244, 0.92);
      --chart-hover-ring: #1c1f1d;
      --chart-optimal-label: #12351f;
      --chart-suboptimal-label: #7a1717;
      --trend: #8a5a00;
      --overlay-border: rgba(116, 125, 117, 0.42);
      --overlay-bg: rgba(247, 248, 245, 0.92);
      --shadow: rgba(28, 31, 29, 0.12);
      --table-head: #eef0ec;
      --table-row-border: rgba(0, 0, 0, 0.08);
      --table-hover-wash: rgba(255, 255, 255, 0.18);
      --tooltip-bg: rgba(28, 31, 29, 0.94);
      --tooltip-ink: #ffffff;
      --row-low: 118 29 29;
      --row-mid: 255 255 255;
      --row-high: 11 93 42;
      --row-text-dark: #151815;
      --row-text-light: #ffffff;
      --green: #00a854;
      --red: #e03131;
      --blue: #275c8f;
    }
    html[data-theme="dark"] {
      --bg: #111412;
      --ink: #eef3ee;
      --muted: #a9b4ac;
      --line: #354039;
      --panel: #181d1a;
      --panel-soft: #141916;
      --panel-accent: #17251d;
      --heading: #f3f7f3;
      --control-ink: #dce6df;
      --button-bg: #202720;
      --button-hover: #2a332c;
      --accent: #35b972;
      --accent-hover: #48c983;
      --accent-soft: #1d3426;
      --accent-line: #3d7754;
      --metric-card-line: #4d5b51;
      --link: #8cc7ff;
      --chart-bg: #111613;
      --chart-text: #b7c3ba;
      --chart-title: #eef3ee;
      --chart-axis: #78877d;
      --chart-axis-strong: #94a49a;
      --chart-grid-minor: rgba(105, 120, 110, 0.24);
      --chart-grid-major: rgba(139, 154, 143, 0.46);
      --chart-grid-3d-minor: rgba(105, 120, 110, 0.20);
      --chart-grid-3d-major: rgba(139, 154, 143, 0.40);
      --chart-label-halo: rgba(17, 20, 18, 0.92);
      --chart-hover-ring: #f4f8f4;
      --chart-optimal-label: #93e5b3;
      --chart-suboptimal-label: #ffabab;
      --trend: #d6a64a;
      --overlay-border: rgba(130, 150, 137, 0.45);
      --overlay-bg: rgba(28, 34, 30, 0.92);
      --shadow: rgba(0, 0, 0, 0.34);
      --table-head: #202820;
      --table-row-border: rgba(255, 255, 255, 0.08);
      --table-hover-wash: rgba(255, 255, 255, 0.08);
      --tooltip-bg: rgba(238, 243, 238, 0.96);
      --tooltip-ink: #111412;
      --row-low: 92 22 28;
      --row-mid: 37 43 39;
      --row-high: 13 96 55;
      --row-text-dark: #f4f8f4;
      --row-text-light: #ffffff;
      --green: #29c776;
      --red: #ff5c66;
      --blue: #74a7dc;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 14px;
      line-height: 1.4;
    }
    main {
      width: min(1500px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 24px 0 40px;
    }
    header {
      display: flex;
      justify-content: space-between;
      align-items: end;
      gap: 18px;
      margin-bottom: 16px;
    }
    .view-nav {
      display: flex;
      gap: 16px;
      margin-bottom: 12px;
      border-bottom: 1px solid var(--line);
    }
    .view-nav a {
      padding: 8px 0;
      color: var(--muted);
      text-decoration: none;
    }
    .view-nav a[aria-current="page"] {
      color: var(--heading);
      border-bottom: 2px solid var(--blue);
      font-weight: 700;
    }
    h1 {
      margin: 0 0 4px;
      font-size: 24px;
      font-weight: 720;
      letter-spacing: 0;
    }
    .meta {
      color: var(--muted);
      font-size: 13px;
    }
    .meta-stack {
      display: grid;
      gap: 4px;
    }
    .controls-wrap,
    .info-wrap {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      margin-bottom: 16px;
      padding: 14px;
    }
    .controls-header,
    .info-title {
      margin: 0 0 10px;
      color: var(--heading);
      font-size: 15px;
      font-weight: 720;
    }
    .theme-toggle {
      min-height: 34px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--button-bg);
      color: var(--ink);
      cursor: pointer;
      font: inherit;
      font-size: 12px;
      font-weight: 720;
      padding: 0 10px;
      white-space: nowrap;
    }
    .theme-toggle:hover,
    .theme-toggle:focus-visible {
      background: var(--button-hover);
      outline: none;
    }
    .metric-picker {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .metric-groups {
      display: grid;
      grid-template-columns: minmax(280px, 0.78fr) minmax(320px, 1.22fr);
      gap: 12px;
      margin-bottom: 12px;
    }
    .metric-group {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel-soft);
      padding: 11px;
    }
    .metric-group.core {
      border-color: var(--accent-line);
      background: var(--panel-accent);
    }
    .metric-group-title {
      margin: 0 0 8px;
      color: var(--control-ink);
      font-size: 12px;
      font-weight: 760;
      text-transform: uppercase;
    }
    .metric-group.core .metric-group-title {
      color: var(--accent);
    }
    .metric-button {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--button-bg);
      color: var(--heading);
      cursor: pointer;
      font: inherit;
      font-size: 12px;
      font-weight: 650;
      padding: 7px 9px;
    }
    .metric-button:hover,
    .metric-button:focus-visible {
      background: var(--button-hover);
      outline: none;
    }
    .metric-button[disabled] {
      cursor: default;
      opacity: 0.45;
    }
    .metric-group.core .metric-button {
      border-color: var(--accent-line);
      background: var(--panel);
      font-size: 13px;
      padding: 8px 10px;
    }
    .metric-group.core .metric-button:hover,
    .metric-group.core .metric-button:focus-visible {
      background: var(--accent-soft);
    }
    .selected-line {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      align-items: start;
    }
    .selected-metrics {
      min-height: 42px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
      padding: 7px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel-soft);
    }
    .selected-empty {
      color: var(--muted);
      font-size: 13px;
      padding: 3px 2px;
    }
    .metric-card {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      max-width: 100%;
      border: 1px solid var(--metric-card-line);
      border-radius: 6px;
      background: var(--panel);
      color: var(--heading);
      font-size: 12px;
      font-weight: 650;
      padding: 5px 7px;
    }
    .metric-order {
      color: var(--muted);
      font-weight: 720;
    }
    .remove-metric {
      width: 18px;
      height: 18px;
      display: inline-grid;
      place-items: center;
      border: 0;
      border-radius: 4px;
      background: var(--button-hover);
      color: var(--heading);
      cursor: pointer;
      font: inherit;
      font-size: 14px;
      line-height: 1;
      padding: 0;
    }
    .run-button {
      min-height: 42px;
      border: 1px solid var(--accent);
      border-radius: 6px;
      background: var(--accent);
      color: #ffffff;
      cursor: pointer;
      font: inherit;
      font-size: 13px;
      font-weight: 720;
      padding: 0 14px;
      white-space: nowrap;
    }
    .selection-actions {
      display: flex;
      gap: 8px;
    }
    .filter-line {
      display: flex;
      justify-content: flex-end;
      margin-top: 10px;
    }
    .filter-option {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      padding: 7px 9px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel-soft);
      color: var(--control-ink);
      cursor: pointer;
      font: inherit;
      font-size: 12px;
      font-weight: 650;
    }
    .filter-option input[type="checkbox"] {
      width: 14px;
      height: 14px;
      margin: 0;
      accent-color: var(--accent);
      cursor: pointer;
    }
    .clear-button {
      min-height: 42px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--button-bg);
      color: var(--control-ink);
      cursor: pointer;
      font: inherit;
      font-size: 13px;
      font-weight: 720;
      padding: 0 12px;
      white-space: nowrap;
    }
    .run-button:hover,
    .run-button:focus-visible {
      background: var(--accent-hover);
      outline: none;
    }
    .clear-button:hover,
    .clear-button:focus-visible {
      background: var(--button-hover);
      outline: none;
    }
    .control-note {
      margin-top: 9px;
      color: var(--muted);
      font-size: 12px;
    }
    .info-wrap {
      color: var(--control-ink);
      margin-top: 16px;
    }
    .info-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
    }
    .info-wrap p,
    .info-wrap ul {
      margin: 0;
    }
    .info-wrap ul {
      padding-left: 18px;
    }
    .info-wrap li + li {
      margin-top: 4px;
    }
    .info-wrap a {
      color: var(--link);
      font-weight: 650;
    }
    .chart-wrap {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      margin-bottom: 16px;
      padding: 14px;
    }
    .chart-title {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 10px;
      color: var(--muted);
      font-size: 13px;
    }
    .chart-actions {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-left: auto;
    }
    .chart-button {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--button-bg);
      color: var(--ink);
      cursor: pointer;
      font: inherit;
      font-size: 12px;
      font-weight: 650;
      padding: 5px 9px;
    }
    .chart-button:hover {
      background: var(--button-hover);
    }
    .chart-canvas-wrap {
      position: relative;
    }
    .chart-scroll {
      width: 100%;
      overflow: visible;
    }
    .chart-wrap:fullscreen {
      width: 100vw;
      height: 100vh;
      display: flex;
      flex-direction: column;
      margin: 0;
      padding: 16px;
      border: 0;
      border-radius: 0;
      background: var(--panel);
    }
    .chart-wrap.fullscreen-fallback {
      position: fixed;
      inset: 0;
      z-index: 1000;
      width: 100vw;
      height: 100dvh;
      display: flex;
      flex-direction: column;
      margin: 0;
      padding: 16px;
      border: 0;
      border-radius: 0;
      background: var(--panel);
    }
    body.chart-fullscreen-fallback {
      overflow: hidden;
    }
    .chart-wrap:fullscreen .chart-canvas-wrap {
      flex: 1;
      min-height: 0;
    }
    .chart-wrap.fullscreen-fallback .chart-canvas-wrap {
      flex: 1;
      min-height: 0;
    }
    .chart-wrap:fullscreen .chart-scroll,
    .chart-wrap.fullscreen-fallback .chart-scroll {
      height: 100%;
      overflow: auto;
      -webkit-overflow-scrolling: touch;
    }
    .chart-wrap:fullscreen canvas,
    .chart-wrap.fullscreen-fallback canvas {
      height: 100%;
      min-width: 0;
    }
    .view-cube {
      position: absolute;
      top: 12px;
      right: 12px;
      z-index: 3;
      display: grid;
      grid-template-columns: repeat(3, 42px);
      grid-template-rows: repeat(3, 34px);
      gap: 3px;
      padding: 6px;
      border: 1px solid var(--overlay-border);
      border-radius: 7px;
      background: var(--overlay-bg);
      box-shadow: 0 10px 28px var(--shadow);
      -webkit-backdrop-filter: blur(8px);
      backdrop-filter: blur(8px);
    }
    .view-cube[hidden] {
      display: none;
    }
    .zoom-indicator {
      position: absolute;
      top: 140px;
      right: 12px;
      z-index: 3;
      min-width: 58px;
      padding: 5px 8px;
      border: 1px solid var(--overlay-border);
      border-radius: 6px;
      background: var(--overlay-bg);
      box-shadow: 0 10px 28px var(--shadow);
      color: var(--chart-title);
      font-size: 11px;
      font-weight: 720;
      line-height: 1;
      text-align: center;
      -webkit-backdrop-filter: blur(8px);
      backdrop-filter: blur(8px);
    }
    .chart-wrap.is-2d .zoom-indicator {
      top: 12px;
    }
    .zoom-indicator[hidden] {
      display: none;
    }
    .view-cube button {
      min-width: 0;
      border: 1px solid var(--overlay-border);
      border-radius: 5px;
      background: var(--panel);
      color: var(--chart-title);
      cursor: pointer;
      font: inherit;
      font-size: 10px;
      font-weight: 720;
      line-height: 1;
      padding: 0;
    }
    .view-cube button:hover,
    .view-cube button:focus-visible {
      background: var(--button-hover);
      border-color: var(--chart-axis-strong);
      outline: none;
    }
    .view-cube button.active {
      background: var(--chart-title);
      color: var(--bg);
      border-color: var(--chart-title);
    }
    .view-cube button.active:hover,
    .view-cube button.active:focus-visible {
      background: var(--control-ink);
      border-color: var(--control-ink);
    }
    .legend {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }
    .legend span {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
    }
    .dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      display: inline-block;
    }
    .dot.green { background: var(--green); }
    .dot.red { background: var(--red); }
    .dot.neutral { background: var(--blue); }
    .line-sample {
      width: 22px;
      height: 0;
      display: inline-block;
      border-top: 3px solid var(--trend);
    }
    #chart,
    #paretoChart {
      width: 100%;
      height: 560px;
      display: block;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--chart-bg);
    }
    .table-section {
      margin-bottom: 16px;
    }
    .table-title {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-bottom: 8px;
      color: var(--heading);
      font-size: 15px;
      font-weight: 720;
    }
    .table-wrap {
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      max-height: calc(100vh - 48px);
    }
    table {
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      min-width: 980px;
    }
    th, td {
      padding: 9px 11px;
      border-bottom: 1px solid var(--table-row-border);
      text-align: left;
      vertical-align: middle;
      white-space: nowrap;
    }
    th {
      position: sticky;
      top: 0;
      z-index: 2;
      background: var(--table-head);
      color: var(--heading);
      font-size: 12px;
      font-weight: 720;
      cursor: pointer;
      -webkit-user-select: none;
      user-select: none;
      border-bottom: 1px solid var(--line);
    }
    th.numeric, td.numeric { text-align: right; }
    th.sort-active::after {
      content: attr(data-sort-mark);
      margin-left: 6px;
      color: var(--muted);
    }
    tbody tr:hover td {
      box-shadow: inset 0 0 0 9999px var(--table-hover-wash);
    }
    .tooltip {
      position: fixed;
      pointer-events: none;
      transform: translate(12px, 12px);
      background: var(--tooltip-bg);
      color: var(--tooltip-ink);
      padding: 8px 10px;
      border-radius: 6px;
      font-size: 12px;
      max-width: 300px;
      z-index: 10;
      display: none;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    @media (max-width: 760px) {
      main { width: min(100vw - 18px, 1500px); padding-top: 14px; }
      header { display: block; }
      h1 { font-size: 20px; }
      .selected-line,
      .metric-groups,
      .info-grid { grid-template-columns: 1fr; }
      .chart-wrap {
        padding: 10px;
      }
      .chart-title {
        align-items: flex-start;
        flex-direction: column;
        gap: 8px;
      }
      .chart-actions {
        width: 100%;
        flex-wrap: wrap;
        margin-left: 0;
      }
      .chart-wrap.is-2d #chart,
      .chart-wrap.is-3d #chart {
        touch-action: none;
      }
      .selection-actions { display: grid; grid-template-columns: 1fr 1fr; }
      .run-button,
      .clear-button { width: 100%; }
      .filter-line { justify-content: stretch; }
      .filter-option { width: 100%; }
      #chart, #paretoChart { height: 440px; }
      th, td { padding: 8px; }
    }
  </style>
</head>
<body>
  <main>
    <nav class="view-nav" aria-label="Report views">
      <a id="comparisonViewLink" href="./index.html">Comparison</a>
      <a id="openCodeGoViewLink" href="?view=opencode-go">OpenCode Go value</a>
    </nav>
    <header>
      <div>
        <h1 id="pageTitle">LLM Comparison</h1>
        <div class="meta-stack">
          <div class="meta" id="dataFreshness">Data updated: 2026-08-26T16:08:56Z</div>
          <div class="meta" id="summary"></div>
        </div>
      </div>
      <button class="theme-toggle" id="themeToggle" type="button" aria-label="Toggle dark mode"></button>
    </header>
    <section class="controls-wrap" aria-labelledby="controlsTitle">
      <h2 class="controls-header" id="controlsTitle">Choose scoring metrics</h2>
      <div class="metric-groups">
        <div class="metric-group core">
          <div class="metric-group-title">Core metrics</div>
          <div class="metric-picker" id="coreMetricPicker"></div>
        </div>
        <div class="metric-group">
          <div class="metric-group-title">Additional metrics</div>
          <div class="metric-picker" id="otherMetricPicker"></div>
        </div>
      </div>
      <div class="selected-line">
        <div class="selected-metrics" id="selectedMetrics" aria-live="polite"></div>
        <div class="selection-actions">
          <button class="clear-button" id="clearMetrics" type="button">Clear all</button>
          <button class="clear-button" id="resetMetrics" type="button">Reset</button>
          <button class="run-button" id="runComparison" type="button">Run comparison</button>
        </div>
      </div>
      <div class="filter-line">
        <label class="filter-option">
          <input type="checkbox" id="excludeZeroPrice" checked>
          <span>Exclude free / promo models</span>
        </label>
      </div>
      <div class="control-note" id="controlNote"></div>
    </section>
    <section class="chart-wrap" id="chartSection" hidden>
      <div class="chart-title">
        <div id="chartTitle"></div>
        <div class="chart-actions">
          <button class="chart-button" id="fullscreenChart" type="button">Full screen</button>
          <button class="chart-button" id="saveChart" type="button">Save as image</button>
          <button class="chart-button" id="resetView" type="button" hidden>Reset view</button>
          <div class="legend">
            <span><i class="dot green"></i>Pareto optimal</span>
            <span><i class="dot red"></i>Pareto suboptimal</span>
            <span><i class="dot neutral"></i>Other</span>
            <span><i class="line-sample"></i>Linear trend</span>
          </div>
        </div>
      </div>
      <div class="chart-canvas-wrap">
        <div class="chart-scroll" id="chartScroll">
          <canvas id="chart"></canvas>
        </div>
        <div class="view-cube" id="viewCube" aria-label="3D view controls" hidden>
          <button type="button" data-view="top" title="Top view">Top</button>
          <button type="button" data-view="isometric" title="Isometric view">Iso</button>
          <button type="button" data-view="back" title="Back view">Back</button>
          <button type="button" data-view="left" title="Left view">Left</button>
          <button type="button" data-view="front" title="Front view">Front</button>
          <button type="button" data-view="right" title="Right view">Right</button>
          <span></span>
          <button type="button" data-view="bottom" title="Bottom view">Bottom</button>
          <span></span>
        </div>
        <div class="zoom-indicator" id="zoomIndicator" aria-live="polite" hidden>1.00x</div>
      </div>
      <div class="tooltip" id="tooltip"></div>
    </section>
    <section class="table-section" aria-labelledby="resultsTitle">
      <div class="table-title">
        <span id="resultsTitle">Results</span>
        <button class="chart-button" id="saveTable" type="button">Save as image</button>
      </div>
      <div class="table-wrap">
        <table id="resultsTable"></table>
      </div>
    </section>
    <section class="chart-wrap" id="paretoChartSection" hidden>
      <div class="chart-title">
        <div id="paretoChartTitle">Pareto-optimal models</div>
        <div class="chart-actions">
          <button class="chart-button" id="fullscreenParetoChart" type="button">Full screen</button>
          <button class="chart-button" id="resetParetoView" type="button">Reset view</button>
          <button class="chart-button" id="saveParetoChart" type="button">Save as image</button>
          <div class="legend">
            <span><i class="dot green"></i>Pareto optimal</span>
            <span><i class="line-sample"></i>Linear trend</span>
          </div>
        </div>
      </div>
      <div class="chart-canvas-wrap">
        <div class="chart-scroll" id="paretoChartScroll">
          <canvas id="paretoChart"></canvas>
        </div>
        <div class="view-cube" id="paretoViewCube" aria-label="Pareto 3D view controls" hidden>
          <button type="button" data-view="top" title="Top view">Top</button>
          <button type="button" data-view="isometric" title="Isometric view">Iso</button>
          <button type="button" data-view="back" title="Back view">Back</button>
          <button type="button" data-view="left" title="Left view">Left</button>
          <button type="button" data-view="front" title="Front view">Front</button>
          <button type="button" data-view="right" title="Right view">Right</button>
          <span></span>
          <button type="button" data-view="bottom" title="Bottom view">Bottom</button>
          <span></span>
        </div>
        <div class="zoom-indicator" id="paretoZoomIndicator" aria-live="polite">1.00x</div>
      </div>
      <div class="tooltip" id="paretoTooltip"></div>
    </section>
    <section class="info-wrap" aria-labelledby="aboutTitle">
      <h2 class="info-title" id="aboutTitle">About this comparison</h2>
      <div class="info-grid" id="aboutContent">
        <p>This static report ranks LLMs from the included <code>data/results.csv</code> data file. The source data was copied from Artificial Analysis, converted locally, and published here so viewers can change comparisons without collecting the data themselves.</p>
        <ul>
          <li>Higher is better for quality, benchmark, context, and speed metrics.</li>
          <li>Lower is better for cost, price, latency, and time metrics.</li>
          <li>The final score is the weighted relative geometric mean of actual metric ratios: Artificial Analysis Intelligence counts twice and every other selected metric counts once. A score of 100 matches fixed reference values; higher is better.</li>
          <li>Models missing any selected numeric metric, or containing a nonpositive selected value, are excluded from that run.</li>
        </ul>
        <p>Credit: model benchmark, pricing, and performance data is from <a href="https://artificialanalysis.ai/leaderboards/models" rel="noreferrer">Artificial Analysis</a>. This project is an independent analysis and is not affiliated with Artificial Analysis.</p>
      </div>
    </section>
  </main>
  <script>
    const payload = __PAYLOAD__;
    const dataUpdated = "2026-08-26T16:08:56Z";
    const displayLabels = {
      model: "Model",
      context_window_tokens: "Context Window",
      creator: "Creator",
      providers: "Providers",
      license: "License",
      artificial_analysis_intelligence_index: "Artificial Analysis Intelligence Index",
      artificial_analysis_omniscience_index: "Artificial Analysis Omniscience Index",
      gdpval_aa_pct: "GDPval-AA",
      terminal_bench_hard_pct: "Terminal-Bench Hard",
      tau2_bench_telecom_pct: "Tau2-Bench Telecom",
      aa_lcr_pct: "AA-LCR",
      aa_omniscience_accuracy_pct: "AA-Omniscience Accuracy",
      aa_omniscience_non_hallucination_rate_pct: "AA-Omniscience Non-Hallucination Rate",
      humanitys_last_exam_pct: "Humanity's Last Exam",
      gpqa_diamond_pct: "GPQA Diamond",
      scicode_pct: "SciCode",
      ifbench_pct: "IFBench",
      critpt_pct: "CritPt",
      apex_agents_aa_pct: "APEX-Agents-AA",
      mmmu_pro_pct: "MMMU Pro",
      cost_per_task: "Cost per Task",
      input_price_usd_per_1m_tokens: "Input Price (USD/1M Tokens)",
      output_price_usd_per_1m_tokens: "Output Price (USD/1M Tokens)",
      median_tokens_per_second: "Median (Tokens/s)",
      p5_tokens_per_second: "P5 (Tokens/s)",
      p25_tokens_per_second: "P25 (Tokens/s)",
      p75_tokens_per_second: "P75 (Tokens/s)",
      p95_tokens_per_second: "P95 (Tokens/s)",
      first_chunk_latency_seconds: "First Chunk Latency (s)",
      first_answer_latency_seconds: "First Answer Latency (s)",
      p5_first_chunk_latency_seconds: "P5 First Chunk Latency (s)",
      p25_first_chunk_latency_seconds: "P25 First Chunk Latency (s)",
      p75_first_chunk_latency_seconds: "P75 First Chunk Latency (s)",
      p95_first_chunk_latency_seconds: "P95 First Chunk Latency (s)",
      total_response_time_seconds: "Total Response Time (s)",
      reasoning_time_seconds: "Reasoning Time (s)",
    };
    const isOpenCodeGoView =
      new URLSearchParams(window.location.search).get("view") === "opencode-go";
    if (isOpenCodeGoView) {
      Object.assign(payload, payload.openCodeGo);
      document.getElementById("dataFreshness").textContent =
        `OpenCode Go pricing scraped: ${payload.scrapedAt}`;
    }
    document.getElementById(isOpenCodeGoView ? "openCodeGoViewLink" : "comparisonViewLink")
      .setAttribute("aria-current", "page");
    if (isOpenCodeGoView) {
      document.querySelector(".controls-wrap").hidden = true;
      document.getElementById("pageTitle").textContent = "OpenCode Go value";
      document.getElementById("aboutTitle").textContent = "About OpenCode Go value";
      document.getElementById("aboutContent").innerHTML = `
        <p>This view joins <a href="${payload.sourceUrl}" rel="noreferrer">OpenCode Go</a> token pricing and monthly Usage allowances to the <a href="https://artificialanalysis.ai/leaderboards/models" rel="noreferrer">Artificial Analysis</a> Intelligence Index.</p>
        <ul>
          <li>Cost-adjusted intelligence = Intelligence − 10 × log₁₀(blended price ÷ $1 per 1M tokens).</li>
          <li>A 10-point Intelligence gain offsets a 10× higher blended price.</li>
          <li>Blended price formula: <strong>${payload.formula}</strong>.</li>
          <li>Usage and cached-write prices are displayed but excluded from the score.</li>
          <li>Models without an Intelligence Index remain visible as Unranked.</li>
        </ul>`;
    }
    const goValueKey = "value_score";
    const goIntelligenceKey = "artificial_analysis_intelligence_index";
    const goBlendKey = "opencode_go_blended_usd_per_1m_tokens";
    const embeddedRows = payload.rows.slice();
    let sourceRows = [];
    let availableCategories = (payload.availableCategories || payload.categories).slice();
    const initialSelectedCategories = payload.categories.map(category => category.key);
    let selectedCategories = initialSelectedCategories.slice();
    let excludeZeroPrice = true;
    let rows = payload.rows.slice();
    const lowerIsBetterMarkers = ["cost", "price", "usd", "latency", "time"];
    const mainColumnKeys = [
      "model",
      "context_window_tokens",
      "creator",
      "artificial_analysis_intelligence_index",
      "cost_per_task",
      "median_tokens_per_second",
      "first_chunk_latency_seconds",
      "total_response_time_seconds",
      "final_score",
    ];
    const coreCategoryKeys = [
      "artificial_analysis_intelligence_index",
      "cost_per_task",
      "median_tokens_per_second",
      "first_chunk_latency_seconds",
      "total_response_time_seconds",
    ];
    let sortState = { key: isOpenCodeGoView ? goValueKey : "final_score", direction: "desc" };
    let minScore = 0;
    let maxScore = 100;
    let medianScore = 50;
    let chartDisposers = [];
    let chartRender = null;
    let paretoRender = null;
    const themeStorageKey = "llmComparison.theme";
    const themeMediaQuery = window.matchMedia?.("(prefers-color-scheme: dark)");

    function readStoredTheme() {
      try {
        const stored = window.localStorage.getItem(themeStorageKey);
        return stored === "light" || stored === "dark" ? stored : null;
      } catch {
        return null;
      }
    }

    function writeStoredTheme(theme) {
      try {
        window.localStorage.setItem(themeStorageKey, theme);
      } catch {
        // Theme selection still works for the current page when storage is unavailable.
      }
    }

    function preferredSystemTheme() {
      return themeMediaQuery?.matches ? "dark" : "light";
    }

    function activeTheme() {
      return readStoredTheme() || preferredSystemTheme();
    }

    function updateThemeToggle() {
      const button = document.getElementById("themeToggle");
      if (!button) return;
      const theme = document.documentElement.dataset.theme || activeTheme();
      const nextTheme = theme === "dark" ? "light" : "dark";
      button.textContent = theme === "dark" ? "Dark" : "Light";
      button.title = `Switch to ${nextTheme} mode`;
      button.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
    }

    function applyTheme(theme) {
      document.documentElement.dataset.theme = theme;
      document.documentElement.style.colorScheme = theme;
      updateThemeToggle();
      if (chartRender) chartRender();
      if (paretoRender) paretoRender();
    }

    function toggleTheme() {
      const nextTheme = (document.documentElement.dataset.theme || activeTheme()) === "dark" ? "light" : "dark";
      writeStoredTheme(nextTheme);
      applyTheme(nextTheme);
    }

    function cssColor(name) {
      return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    }

    function cssRgb(name) {
      return cssColor(name).split(/\s+/).map(Number);
    }

    function isLowerBetter(key) {
      return lowerIsBetterMarkers.some(marker => key.includes(marker));
    }

    function labelFor(key) {
      return displayLabels[key] || key.replaceAll("_", " ");
    }

    function orderedValidMetricKeys(keys) {
      const availableKeys = new Set(availableCategories.map(category => category.key));
      const seen = new Set();
      return keys.filter(key => {
        if (!availableKeys.has(key) || seen.has(key)) return false;
        seen.add(key);
        return true;
      });
    }

    function metricKeysFromUrl() {
      const params = new URLSearchParams(window.location.search);
      const rawMetrics = params.get("metrics");
      if (!rawMetrics) return [];
      return orderedValidMetricKeys(
        rawMetrics
          .split(",")
          .map(key => key.trim())
          .filter(Boolean),
      );
    }

    function applyUrlOptions() {
      const params = new URLSearchParams(window.location.search);
      const metrics = metricKeysFromUrl();
      if (metrics.length) selectedCategories = metrics;
      const excludeZeroPriceParam = params.get("excludeZeroPrice");
      excludeZeroPrice = excludeZeroPriceParam === null ? true : excludeZeroPriceParam !== "0";
      syncExcludeZeroPriceCheckbox();
    }

    function syncExcludeZeroPriceCheckbox() {
      const checkbox = document.getElementById("excludeZeroPrice");
      if (checkbox) checkbox.checked = excludeZeroPrice;
    }

    function updateOptionsUrl() {
      const url = new URL(window.location.href);
      if (selectedCategories.length) {
        url.searchParams.set("metrics", selectedCategories.join(","));
      } else {
        url.searchParams.delete("metrics");
      }
      if (excludeZeroPrice) {
        url.searchParams.delete("excludeZeroPrice");
      } else {
        url.searchParams.set("excludeZeroPrice", "0");
      }
      window.history.replaceState({}, "", url);
    }

    function parseNumber(value) {
      if (value === null || value === undefined) return null;
      const text = String(value).trim();
      if (!text) return null;
      const parsed = Number(text.replaceAll(",", ""));
      return Number.isFinite(parsed) ? parsed : null;
    }

    function formatValue(key, value) {
      if (key === "final_score") return Number(value).toFixed(2);
      const parsed = parseNumber(value);
      if (parsed === null) {
        return [goIntelligenceKey, goValueKey].includes(key) ? "Unranked" : (value ?? "");
      }
      const general = () => String(parsed);
      if (key === goValueKey) return parsed.toFixed(2);
      if (key === goIntelligenceKey) return general();
      if (key === "monthly_usage_usd") return `$${general()}`;
      if (key === "cost_per_task") return `$${parsed.toFixed(2)}`;
      if ([
        "input_price_usd_per_1m_tokens",
        "output_price_usd_per_1m_tokens",
        "cache_read_usd_per_1m_tokens",
        "cache_write_usd_per_1m_tokens",
        "long_context_input_price_usd_per_1m_tokens",
        "long_context_output_price_usd_per_1m_tokens",
        "long_context_cache_read_usd_per_1m_tokens",
        "long_context_cache_write_usd_per_1m_tokens",
        goBlendKey,
        "long_context_blended_usd_per_1m_tokens",
      ].includes(key)) {
        return `$${parsed.toFixed(6).replace(/\.?0+$/, "")}`;
      }
      if (key === "context_window_tokens") return Math.round(parsed).toLocaleString();
      if (key.endsWith("_pct") || key.endsWith("_index")) return general();
      if (key.includes("usd") || key.includes("seconds")) return parsed.toFixed(2);
      if (key.includes("tokens_per_second")) return general();
      return general();
    }

    function parseCsv(text) {
      const rows = [];
      let row = [];
      let value = "";
      let quoted = false;
      for (let index = 0; index < text.length; index += 1) {
        const char = text[index];
        const next = text[index + 1];
        if (quoted) {
          if (char === '"' && next === '"') {
            value += '"';
            index += 1;
          } else if (char === '"') {
            quoted = false;
          } else {
            value += char;
          }
          continue;
        }
        if (char === '"') quoted = true;
        else if (char === ",") {
          row.push(value);
          value = "";
        } else if (char === "\n") {
          row.push(value);
          rows.push(row);
          row = [];
          value = "";
        } else if (char !== "\r") {
          value += char;
        }
      }
      if (value || row.length) {
        row.push(value);
        rows.push(row);
      }
      const headers = rows.shift() || [];
      return rows
        .filter(item => item.some(cell => cell.trim()))
        .map(item => Object.fromEntries(headers.map((header, index) => [header, item[index] ?? ""])));
    }

    function fetchCsvFromPaths(paths) {
      return paths.reduce(
        (chain, path) => chain.catch(() => fetch(path)
          .then(response => response.ok ? response.text() : Promise.reject(new Error(`${path} not found`)))),
        Promise.reject()
      );
    }

    function metricReferenceValue(category) {
      if (category === "context_window_tokens") return 100000;
      if (category.endsWith("_pct") || category.endsWith("_index")) return 50;
      if (category.includes("tokens_per_second")) return 100;
      return 1;
    }

    function relativeGeometricScore(graph, categories) {
      const totals = categories.reduce((result, category) => {
        const value = graph[category];
        const reference = metricReferenceValue(category);
        const ratio = isLowerBetter(category) ? reference / value : value / reference;
        const weight = payload.scoringWeights[category] ?? 1;
        result.weightedLogRatios += weight * Math.log(ratio);
        result.weights += weight;
        return result;
      }, { weightedLogRatios: 0, weights: 0 });
      return 100 * Math.exp(totals.weightedLogRatios / totals.weights);
    }

    function dominates(challenger, target, categories, better) {
      let atLeastAll = true;
      let strictOne = false;
      for (const category of categories) {
        const lowerBetter = isLowerBetter(category);
        const challengerValue = challenger.graph[category];
        const targetValue = target.graph[category];
        const atLeast = better
          ? (lowerBetter ? challengerValue <= targetValue : challengerValue >= targetValue)
          : (lowerBetter ? challengerValue >= targetValue : challengerValue <= targetValue);
        const strict = better
          ? (lowerBetter ? challengerValue < targetValue : challengerValue > targetValue)
          : (lowerBetter ? challengerValue > targetValue : challengerValue < targetValue);
        atLeastAll = atLeastAll && atLeast;
        strictOne = strictOne || strict;
      }
      return atLeastAll && strictOne;
    }

    function computePareto(scoredRows, categories) {
      if (![2, 3].includes(categories.length)) {
        return scoredRows.map(() => ({ optimal: false, suboptimal: false }));
      }
      return scoredRows.map(row => {
        let optimal = true;
        let suboptimal = true;
        for (const other of scoredRows) {
          if (other === row) continue;
          if (dominates(other, row, categories, true)) optimal = false;
          if (dominates(other, row, categories, false)) suboptimal = false;
        }
        return { optimal, suboptimal };
      });
    }

    function tableColumns(headers, numericKeys) {
      const keys = mainColumnKeys.filter(key => key === "final_score" || headers.includes(key));
      return keys.map(key => ({ key, label: key === "final_score" ? "Final Score" : labelFor(key), numeric: key === "final_score" || numericKeys.has(key) }));
    }

    function scoreSourceRows(categories) {
      const completeRows = [];
      for (const raw of sourceRows) {
        if (excludeZeroPrice && parseNumber(raw.cost_per_task) === 0) continue;
        const graph = {};
        let complete = true;
        for (const category of categories) {
          const parsed = parseNumber(raw[category]);
          if (parsed === null || parsed <= 0) {
            complete = false;
            break;
          }
          graph[category] = parsed;
        }
        if (!complete) continue;
        const row = { raw, graph, score: 0, cells: {}, model: raw.model || "" };
        completeRows.push(row);
      }

      for (const row of completeRows) {
        const score = relativeGeometricScore(row.graph, categories);
        row.score = Math.round(score * 10000) / 10000;
        row.graph.final_score = row.score;
      }
      completeRows.sort((left, right) => right.score - left.score);
      const pareto = computePareto(completeRows, categories);
      for (const [rowIndex, row] of completeRows.entries()) {
        row.pareto = pareto[rowIndex];
        for (const column of payload.columns) {
          const rawValue = column.key === "final_score" ? row.score : row.raw[column.key];
          const numericValue = column.key === "final_score" ? row.score : parseNumber(rawValue);
          row.cells[column.key] = {
            display: formatValue(column.key, rawValue),
            sort: numericValue ?? String(rawValue || ""),
          };
        }
      }
      return completeRows;
    }

    function scoreEmbeddedRows(categories) {
      const completeRows = [];
      for (const original of embeddedRows) {
        const priceCell = original.cells.cost_per_task;
        const priceValue = priceCell?.sort ?? original.graph.cost_per_task;
        if (excludeZeroPrice && priceValue === 0) continue;
        const graph = {};
        let complete = true;
        for (const category of categories) {
          const parsed = parseNumber(original.graph[category]);
          if (parsed === null || parsed <= 0) {
            complete = false;
            break;
          }
          graph[category] = parsed;
        }
        if (!complete) continue;
        const row = {
          ...original,
          graph: { ...original.graph, ...graph },
          cells: { ...original.cells },
          score: 0,
        };
        completeRows.push(row);
      }

      for (const row of completeRows) {
        const score = relativeGeometricScore(row.graph, categories);
        row.score = Math.round(score * 10000) / 10000;
        row.cells.final_score = {
          display: formatValue("final_score", row.score),
          sort: row.score,
        };
      }
      completeRows.sort((left, right) => right.score - left.score);
      const pareto = computePareto(completeRows, categories);
      for (const [rowIndex, row] of completeRows.entries()) row.pareto = pareto[rowIndex];
      return completeRows;
    }

    function updateScoreScale() {
      const scoreValues = rows
        .map(row => row.score)
        .filter(score => typeof score === "number" && Number.isFinite(score))
        .sort((a, b) => a - b);
      minScore = scoreValues[0] ?? 0;
      maxScore = scoreValues[scoreValues.length - 1] ?? 100;
      medianScore = scoreValues.length
        ? scoreValues[Math.floor((scoreValues.length - 1) / 2)]
        : 50;
    }

    function updateSummary() {
      if (isOpenCodeGoView) {
        const ranked = rows.filter(row => typeof row.score === "number" && Number.isFinite(row.score)).length;
        document.getElementById("summary").textContent =
          `${rows.length} models, ${ranked} ranked by cost-adjusted intelligence`;
        return;
      }
      const filterNote = excludeZeroPrice ? " (excluding free/promo models)" : "";
      document.getElementById("summary").textContent =
        `${rows.length} models ranked by ${payload.categories.map(c => c.label).join(", ")}${filterNote}`;
      document.getElementById("controlNote").textContent =
        "Selected metrics are evaluated in order; the first two or three also define the chart axes.";
    }

    function resetChartCanvas() {
      for (const dispose of chartDisposers) dispose();
      chartDisposers = [];
      chartRender = null;
      paretoRender = null;
      for (const canvasId of ["chart", "paretoChart"]) {
        const canvas = document.getElementById(canvasId);
        canvas.replaceWith(canvas.cloneNode(false));
      }
      for (const tooltipId of ["tooltip", "paretoTooltip"]) {
        document.getElementById(tooltipId).style.display = "none";
      }
    }

    function trackChartListener(target, type, handler, options) {
      target.addEventListener(type, handler, options);
      chartDisposers.push(() => target.removeEventListener(type, handler, options));
    }

    function applySelection({ syncUrl = false } = {}) {
      if (!selectedCategories.length) return;
      payload.categories = selectedCategories.map(key => ({
        key,
        label: labelFor(key),
        lowerIsBetter: isLowerBetter(key),
      }));
      payload.graphCategories = [2, 3].includes(selectedCategories.length) ? selectedCategories.slice() : [];
      if (sourceRows.length) {
        const headers = Object.keys(sourceRows[0] || {});
        const numericKeys = new Set(availableCategories.map(category => category.key));
        payload.columns = tableColumns(headers, numericKeys);
        rows = scoreSourceRows(selectedCategories);
        payload.rows = rows;
      } else {
        rows = scoreEmbeddedRows(selectedCategories);
        payload.rows = rows;
      }
      sortState = { key: "final_score", direction: "desc" };
      updateScoreScale();
      updateSummary();
      renderSelectedMetrics();
      renderMetricPicker();
      renderTable();
      resetChartCanvas();
      drawGraph();
      drawParetoGraph();
      if (syncUrl) updateOptionsUrl();
    }

    function renderSelectedMetrics() {
      const container = document.getElementById("selectedMetrics");
      container.innerHTML = "";
      if (!selectedCategories.length) {
        const empty = document.createElement("span");
        empty.className = "selected-empty";
        empty.textContent = "Select one or more metrics";
        container.appendChild(empty);
        return;
      }
      for (const [index, key] of selectedCategories.entries()) {
        const card = document.createElement("span");
        card.className = "metric-card";
        const order = document.createElement("span");
        order.className = "metric-order";
        order.textContent = `${index + 1}.`;
        const label = document.createElement("span");
        label.textContent = labelFor(key);
        const remove = document.createElement("button");
        remove.className = "remove-metric";
        remove.type = "button";
        remove.title = `Remove ${labelFor(key)}`;
        remove.textContent = "×";
        remove.addEventListener("click", () => {
          selectedCategories = selectedCategories.filter(category => category !== key);
          renderSelectedMetrics();
          renderMetricPicker();
        });
        card.append(order, label, remove);
        container.appendChild(card);
      }
    }

    function renderMetricPicker() {
      const corePicker = document.getElementById("coreMetricPicker");
      const otherPicker = document.getElementById("otherMetricPicker");
      corePicker.innerHTML = "";
      otherPicker.innerHTML = "";

      function addButton(category, container) {
        const button = document.createElement("button");
        button.className = "metric-button";
        button.type = "button";
        button.textContent = `${category.label}${category.lowerIsBetter ? " ↓" : " ↑"}`;
        button.disabled = selectedCategories.includes(category.key);
        button.addEventListener("click", () => {
          selectedCategories.push(category.key);
          renderSelectedMetrics();
          renderMetricPicker();
        });
        container.appendChild(button);
      }

      const categoriesByKey = new Map(availableCategories.map(category => [category.key, category]));
      for (const key of coreCategoryKeys) {
        const category = categoriesByKey.get(key);
        if (category) addButton(category, corePicker);
      }
      for (const category of availableCategories) {
        if (!coreCategoryKeys.includes(category.key)) addButton(category, otherPicker);
      }
    }

    function clearMetrics() {
      selectedCategories = [];
      renderSelectedMetrics();
      renderMetricPicker();
    }

    function resetMetrics() {
      selectedCategories = initialSelectedCategories.slice();
      renderSelectedMetrics();
      renderMetricPicker();
    }

    function initializeFromCsv(csvRows) {
      sourceRows = csvRows;
      const headers = Object.keys(csvRows[0] || {});
      const numericKeys = headers.filter(header => csvRows.some(row => parseNumber(row[header]) !== null));
      const discoveredCategories = numericKeys
        .filter(key => key !== "final_score")
        .map(key => ({ key, label: labelFor(key), lowerIsBetter: isLowerBetter(key) }));
      availableCategories = [
        ...coreCategoryKeys
          .map(key => discoveredCategories.find(category => category.key === key))
          .filter(Boolean),
        ...discoveredCategories.filter(category => !coreCategoryKeys.includes(category.key)),
      ];
      applyUrlOptions();
      applySelection();
    }

    function initializeGoFromCsv(csvRows) {
      const headers = new Set(Object.keys(csvRows[0] || {}));
      const required = [...payload.columns.map(column => column.key), "scraped_at"];
      const missing = required.filter(key => !headers.has(key));
      if (!csvRows.length || missing.length) {
        throw new Error(`OpenCode Go CSV is missing required headers: ${missing.join(", ")}`);
      }
      const scrapedValues = csvRows.map(row => String(row.scraped_at || "").trim());
      const canonicalScrapedAt = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;
      if (scrapedValues.some(value => {
        if (!canonicalScrapedAt.test(value)) return true;
        const parsed = new Date(value);
        return Number.isNaN(parsed.getTime()) ||
          parsed.toISOString().replace(".000Z", "Z") !== value;
      }) || new Set(scrapedValues).size !== 1) {
        throw new Error(
          "OpenCode Go CSV scraped_at values must be identical canonical UTC timestamps"
        );
      }
      const scrapedAt = scrapedValues[0];
      const loadedRows = csvRows.map(raw => {
        const intelligence = parseNumber(raw[goIntelligenceKey]);
        const blend = parseNumber(raw[goBlendKey]);
        const score = parseNumber(raw[goValueKey]);
        const graph = intelligence === null || blend === null
          ? {}
          : { [goIntelligenceKey]: intelligence, [goBlendKey]: blend };
        const cells = Object.fromEntries(payload.columns.map(column => {
          const rawValue = raw[column.key];
          const numericValue = parseNumber(rawValue);
          return [column.key, {
            display: formatValue(column.key, rawValue),
            sort: numericValue ?? String(rawValue || ""),
          }];
        }));
        return {
          model: raw.model || "",
          score,
          cells,
          graph,
          pareto: { optimal: false, suboptimal: false },
        };
      });
      const plottedRows = loadedRows.filter(row =>
        Number.isFinite(row.graph[goIntelligenceKey]) &&
        Number.isFinite(row.graph[goBlendKey])
      );
      const flags = computePareto(plottedRows, payload.graphCategories);
      plottedRows.forEach((row, index) => { row.pareto = flags[index]; });
      loadedRows.sort((left, right) => {
        if (left.score === null) return right.score === null ? 0 : 1;
        if (right.score === null) return -1;
        return right.score - left.score;
      });
      rows = loadedRows;
      payload.rows = loadedRows;
      payload.scrapedAt = scrapedAt;
      document.getElementById("dataFreshness").textContent =
        `OpenCode Go pricing scraped: ${scrapedAt}`;
      sortState = { key: goValueKey, direction: "desc" };
      updateScoreScale();
      updateSummary();
      renderTable();
      resetChartCanvas();
      drawGraph();
      drawParetoGraph();
    }

    function initializeEmbeddedGo() {
      rows = embeddedRows.slice().sort((left, right) => {
        const leftScore = parseNumber(left.cells[goValueKey]?.sort);
        const rightScore = parseNumber(right.cells[goValueKey]?.sort);
        if (leftScore === null) return rightScore === null ? 0 : 1;
        if (rightScore === null) return -1;
        return rightScore - leftScore;
      });
      payload.rows = rows;
      updateScoreScale();
      updateSummary();
      renderTable();
      resetChartCanvas();
      drawGraph();
      drawParetoGraph();
    }

    function interpolate(a, b, t) {
      return Math.round(a + (b - a) * Math.max(0, Math.min(1, t)));
    }

    function rowColor(score) {
      if (Math.abs(maxScore - minScore) < 0.0001) return `rgb(${cssRgb("--row-mid").join(",")})`;
      const red = cssRgb("--row-low");
      const white = cssRgb("--row-mid");
      const green = cssRgb("--row-high");
      const lowSpan = Math.max(0.0001, medianScore - minScore);
      const highSpan = Math.max(0.0001, maxScore - medianScore);
      const t = score <= medianScore
        ? (score - minScore) / lowSpan
        : (score - medianScore) / highSpan;
      const from = score <= medianScore ? red : white;
      const to = score <= medianScore ? white : green;
      const color = [
        interpolate(from[0], to[0], t),
        interpolate(from[1], to[1], t),
        interpolate(from[2], to[2], t),
      ];
      return `rgb(${color.join(",")})`;
    }

    function textColor(score) {
      const color = rowColor(score).match(/\d+/g).map(Number);
      const luminance = (0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]) / 255;
      return luminance < 0.48 ? cssColor("--row-text-light") : cssColor("--row-text-dark");
    }

    function compareValues(a, b, numeric) {
      if (numeric) return Number(a) - Number(b);
      return String(a).localeCompare(String(b), undefined, { numeric: true, sensitivity: "base" });
    }

    function sortRows(key) {
      const column = payload.columns.find(item => item.key === key);
      if (sortState.key === key) {
        sortState.direction = sortState.direction === "desc" ? "asc" : "desc";
      } else {
        sortState = { key, direction: "desc" };
      }
      rows.sort((left, right) => {
        const result = compareValues(left.cells[key].sort, right.cells[key].sort, column.numeric);
        return sortState.direction === "asc" ? result : -result;
      });
      renderTable();
    }

    function renderTable() {
      const table = document.getElementById("resultsTable");
      table.innerHTML = "";

      const thead = document.createElement("thead");
      const headerRow = document.createElement("tr");
      for (const column of payload.columns) {
        const th = document.createElement("th");
        th.textContent = column.label;
        th.className = column.numeric ? "numeric" : "";
        th.dataset.sortMark = sortState.direction === "desc" ? "↓" : "↑";
        if (sortState.key === column.key) th.classList.add("sort-active");
        th.addEventListener("click", () => sortRows(column.key));
        headerRow.appendChild(th);
      }
      thead.appendChild(headerRow);
      table.appendChild(thead);

      const tbody = document.createElement("tbody");
      for (const row of rows) {
        const tr = document.createElement("tr");
        if (typeof row.score === "number" && Number.isFinite(row.score)) {
          tr.style.background = rowColor(row.score);
          tr.style.color = textColor(row.score);
        }
        for (const column of payload.columns) {
          const td = document.createElement("td");
          td.textContent = row.cells[column.key].display;
          if (column.numeric) td.className = "numeric";
          tr.appendChild(td);
        }
        tbody.appendChild(tr);
      }
      table.appendChild(tbody);
    }

    function pointColor(row) {
      if (row.pareto.optimal) return cssColor("--green");
      if (row.pareto.suboptimal) return cssColor("--red");
      return cssColor("--blue");
    }
    function chartSection(sectionId = "chartSection") {
      return document.getElementById(sectionId);
    }

    function isChartFullscreen(sectionId = "chartSection") {
      const section = chartSection(sectionId);
      return document.fullscreenElement === section || section.classList.contains("fullscreen-fallback");
    }

    function chartRenderFor(sectionId) {
      return sectionId === "paretoChartSection" ? paretoRender : chartRender;
    }

    function updateFullscreenButton(sectionId = "chartSection", buttonId = "fullscreenChart") {
      const button = document.getElementById(buttonId);
      button.textContent = isChartFullscreen(sectionId) ? "Exit full screen" : "Full screen";
    }

    function enterFullscreenFallback(sectionId, buttonId) {
      chartSection(sectionId).classList.add("fullscreen-fallback");
      document.body.classList.add("chart-fullscreen-fallback");
      updateFullscreenButton(sectionId, buttonId);
      chartRenderFor(sectionId)?.();
    }

    function exitFullscreenFallback(sectionId, buttonId) {
      chartSection(sectionId).classList.remove("fullscreen-fallback");
      document.body.classList.remove("chart-fullscreen-fallback");
      updateFullscreenButton(sectionId, buttonId);
      chartRenderFor(sectionId)?.();
    }

    function chartRenderRatio(sectionId = "chartSection") {
      const deviceRatio = window.devicePixelRatio || 1;
      const qualityMultiplier = isChartFullscreen(sectionId) ? 1.75 : 1.5;
      return Math.min(3, Math.max(2, deviceRatio * qualityMultiplier));
    }

    function chartZoomScale(sectionId = "chartSection") {
      return isChartFullscreen(sectionId) ? 2 : 1;
    }

    function setupCanvas(canvasId = "chart", sectionId = "chartSection") {
      const canvas = document.getElementById(canvasId);
      const ratio = chartRenderRatio(sectionId);
      const rect = canvas.getBoundingClientRect();
      canvas.width = Math.max(1, Math.floor(rect.width * ratio));
      canvas.height = Math.max(1, Math.floor(rect.height * ratio));
      const ctx = canvas.getContext("2d");
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
      return { canvas, ctx, width: rect.width, height: rect.height };
    }

    function niceNumber(value, round) {
      if (!Number.isFinite(value) || value <= 0) return 1;
      const exponent = Math.floor(Math.log10(value));
      const fraction = value / 10 ** exponent;
      let niceFraction;
      if (round) {
        if (fraction < 1.5) niceFraction = 1;
        else if (fraction < 3) niceFraction = 2;
        else if (fraction < 7) niceFraction = 5;
        else niceFraction = 10;
      } else if (fraction <= 1) niceFraction = 1;
      else if (fraction <= 2) niceFraction = 2;
      else if (fraction <= 5) niceFraction = 5;
      else niceFraction = 10;
      return niceFraction * 10 ** exponent;
    }

    function plottableRows(categories) {
      return payload.rows.filter(row =>
        categories.every(category => Number.isFinite(row.graph[category.key]))
      );
    }

    function metricRange(category) {
      const values = plottableRows([category]).map(row => row.graph[category.key]);
      const min = Math.min(...values);
      const max = Math.max(...values);
      const rawSpan = Math.max(0.0001, max - min);
      const paddedMin = Math.max(0, min - rawSpan * 0.1);
      const paddedMax = max + rawSpan * 0.1;
      const tickStep = niceNumber((paddedMax - paddedMin) / 5, true);
      const rangeMin = Math.max(0, Math.floor(paddedMin / tickStep) * tickStep);
      const rangeMax = Math.max(tickStep, Math.ceil(paddedMax / tickStep) * tickStep);
      return { min: rangeMin, max: rangeMax, span: Math.max(0.0001, rangeMax - rangeMin) };
    }

    function formatTick(value) {
      const absolute = Math.abs(value);
      if (absolute >= 1000) return value.toLocaleString(undefined, { maximumFractionDigits: 0 });
      if (absolute >= 100) return value.toLocaleString(undefined, { maximumFractionDigits: 1 });
      if (absolute >= 10) return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
      return value.toLocaleString(undefined, { maximumFractionDigits: 3 });
    }

    function normalizedMetric(row, category, range) {
      return (row.graph[category.key] - range.min) / range.span;
    }

    function clamped(value, min, max) {
      return Math.max(min, Math.min(max, value));
    }

    function labelBoundsFor(ctx, text, x, y, padding = 3, maxWidth = Infinity) {
      const metrics = ctx.measureText(text);
      const textWidth = Math.min(metrics.width, maxWidth);
      const actualTop = metrics.actualBoundingBoxAscent || 10;
      const actualBottom = metrics.actualBoundingBoxDescent || 3;
      const align = ctx.textAlign || "left";
      let left = x;
      if (align === "center") left = x - textWidth / 2;
      else if (align === "right" || align === "end") left = x - textWidth;
      return {
        left: left - padding,
        right: left + textWidth + padding,
        top: y - actualTop - padding,
        bottom: y + actualBottom + padding,
      };
    }

    function expandedRect(rect, amount) {
      return {
        left: rect.left - amount,
        right: rect.right + amount,
        top: rect.top - amount,
        bottom: rect.bottom + amount,
      };
    }

    function rectsIntersect(a, b) {
      return a.left <= b.right && a.right >= b.left && a.top <= b.bottom && a.bottom >= b.top;
    }

    function pointInRect(point, rect) {
      return point.x >= rect.left && point.x <= rect.right && point.y >= rect.top && point.y <= rect.bottom;
    }

    function orientation(a, b, c) {
      const value = (b.y - a.y) * (c.x - b.x) - (b.x - a.x) * (c.y - b.y);
      if (Math.abs(value) < 0.000001) return 0;
      return value > 0 ? 1 : 2;
    }

    function segmentIntersects(a, b, c, d) {
      const o1 = orientation(a, b, c);
      const o2 = orientation(a, b, d);
      const o3 = orientation(c, d, a);
      const o4 = orientation(c, d, b);
      return o1 !== o2 && o3 !== o4;
    }

    function segmentIntersectsRect(segment, rect) {
      if (pointInRect(segment.start, rect) || pointInRect(segment.end, rect)) return true;
      const corners = [
        { x: rect.left, y: rect.top },
        { x: rect.right, y: rect.top },
        { x: rect.right, y: rect.bottom },
        { x: rect.left, y: rect.bottom },
      ];
      return corners.some((corner, index) => (
        segmentIntersects(segment.start, segment.end, corner, corners[(index + 1) % corners.length])
      ));
    }

    function placedContainedLabel(ctx, text, x, y, bounds, options = {}) {
      const padding = options.padding ?? 3;
      const maxWidth = Math.max(12, (options.maxWidth ?? bounds.right - bounds.left) - padding * 2);
      const labelWidth = Math.min(ctx.measureText(text).width, maxWidth);
      const candidates = options.candidates ?? [
        { dx: 8, dy: -8 },
        { dx: 8, dy: 18 },
        { dx: -labelWidth - 8, dy: -8 },
        { dx: -labelWidth - 8, dy: 18 },
        { dx: -labelWidth / 2, dy: -18 },
        { dx: -labelWidth / 2, dy: 28 },
        { dx: 14, dy: 4 },
        { dx: -labelWidth - 14, dy: 4 },
      ];

      let best = null;
      let bestScore = Infinity;
      for (const candidate of candidates) {
        let labelX = x + candidate.dx;
        let labelY = y + candidate.dy;
        const rawBounds = labelBoundsFor(ctx, text, labelX, labelY, padding, maxWidth);
        labelX += clamped(rawBounds.left, bounds.left, bounds.right) - rawBounds.left;
        labelX += clamped(rawBounds.right, bounds.left, bounds.right) - rawBounds.right;
        labelY += clamped(rawBounds.top, bounds.top, bounds.bottom) - rawBounds.top;
        labelY += clamped(rawBounds.bottom, bounds.top, bounds.bottom) - rawBounds.bottom;
        const labelBounds = labelBoundsFor(ctx, text, labelX, labelY, padding, maxWidth);
        const overlapCount = (options.occupied ?? []).filter(rect => (
          rectsIntersect(expandedRect(labelBounds, options.labelGap ?? 2), rect)
        )).length;
        const lineCount = (options.avoidSegments ?? []).filter(segment => (
          segmentIntersectsRect(segment, expandedRect(labelBounds, options.lineGap ?? 4))
        )).length;
        const displacement = Math.hypot(candidate.dx, candidate.dy);
        const score = overlapCount * 100000 + lineCount * 20000 + displacement;
        if (score < bestScore) {
          bestScore = score;
          best = { x: labelX, y: labelY, bounds: labelBounds, maxWidth, overlapCount, lineCount };
          if (overlapCount === 0 && lineCount === 0) break;
        }
      }
      if (!best || (!options.allowOverlap && (best.overlapCount > 0 || best.lineCount > 0))) return null;
      return best;
    }

    function compareTuple(left, right) {
      for (let index = 0; index < left.length; index += 1) {
        if (left[index] !== right[index]) return left[index] - right[index];
      }
      return 0;
    }

    function circleIntersectsRect(point, rect) {
      const closestX = clamped(point.x, rect.left, rect.right);
      const closestY = clamped(point.y, rect.top, rect.bottom);
      return Math.hypot(point.x - closestX, point.y - closestY) <= point.radius;
    }

    function leaderFor(point, rect) {
      const end = {
        x: clamped(point.x, rect.left, rect.right),
        y: clamped(point.y, rect.top, rect.bottom),
      };
      let dx = end.x - point.x;
      let dy = end.y - point.y;
      let length = Math.hypot(dx, dy);
      if (length < 0.000001) {
        const edges = [
          { x: rect.left, y: point.y },
          { x: rect.right, y: point.y },
          { x: point.x, y: rect.top },
          { x: point.x, y: rect.bottom },
        ].sort((left, right) => (
          Math.hypot(left.x - point.x, left.y - point.y) -
          Math.hypot(right.x - point.x, right.y - point.y)
        ));
        end.x = edges[0].x;
        end.y = edges[0].y;
        dx = end.x - point.x;
        dy = end.y - point.y;
        length = Math.hypot(dx, dy);
      }
      const scale = length > 0 ? point.radius / length : 0;
      return {
        start: { x: point.x + dx * scale, y: point.y + dy * scale },
        end,
      };
    }

    function nearbyLabelCandidates(ctx, point, bounds, occupied, markers, avoidSegments, leaders) {
      const text = point.row.model;
      const maxWidth = Math.max(12, bounds.right - bounds.left - 6);
      const labelWidth = Math.min(ctx.measureText(text).width, maxWidth);
      const offsets = [
        { dx: 8, dy: -8 },
        { dx: 8, dy: 18 },
        { dx: -labelWidth - 8, dy: -8 },
        { dx: -labelWidth - 8, dy: 18 },
        { dx: -labelWidth / 2, dy: -18 },
        { dx: -labelWidth / 2, dy: 28 },
        { dx: 14, dy: 4 },
        { dx: -labelWidth - 14, dy: 4 },
        { dx: 26, dy: -26 },
        { dx: 26, dy: 30 },
        { dx: -labelWidth - 26, dy: -26 },
        { dx: -labelWidth - 26, dy: 30 },
        { dx: -labelWidth / 2, dy: -46 },
        { dx: -labelWidth / 2, dy: 48 },
        { dx: 30, dy: 2 },
        { dx: -labelWidth - 30, dy: 2 },
        { dx: 48, dy: -44 },
        { dx: 48, dy: 48 },
        { dx: -labelWidth - 48, dy: -44 },
        { dx: -labelWidth - 48, dy: 48 },
        { dx: -labelWidth / 2, dy: -66 },
        { dx: -labelWidth / 2, dy: 70 },
        { dx: 52, dy: 0 },
        { dx: -labelWidth - 52, dy: 0 },
        { dx: 90, dy: -80 },
        { dx: 90, dy: 84 },
        { dx: -labelWidth - 90, dy: -80 },
        { dx: -labelWidth - 90, dy: 84 },
        { dx: -labelWidth / 2, dy: -110 },
        { dx: -labelWidth / 2, dy: 112 },
        { dx: 96, dy: -4 },
        { dx: -labelWidth - 96, dy: -4 },
      ];
      return offsets.map((offset, candidateIndex) => {
        let x = point.x + offset.dx;
        let y = point.y + offset.dy;
        const rawBounds = labelBoundsFor(ctx, text, x, y, 3, maxWidth);
        x += clamped(rawBounds.left, bounds.left, bounds.right) - rawBounds.left;
        x += clamped(rawBounds.right, bounds.left, bounds.right) - rawBounds.right;
        y += clamped(rawBounds.top, bounds.top, bounds.bottom) - rawBounds.top;
        y += clamped(rawBounds.bottom, bounds.top, bounds.bottom) - rawBounds.bottom;
        const labelBounds = labelBoundsFor(ctx, text, x, y, 3, maxWidth);
        const leader = candidateIndex < 8 ? null : leaderFor(point, labelBounds);
        const reservedBounds = expandedRect(labelBounds, 4);
        const labelOverlapCount = occupied.filter(rect => rectsIntersect(labelBounds, rect)).length;
        const markerIntersectionCount = markers.filter(marker => (
          marker !== point && circleIntersectsRect(marker, labelBounds)
        )).length;
        const avoidOrLeaderIntersectionCount = [
          ...avoidSegments,
          ...leaders,
        ].filter(segment => (
          segmentIntersectsRect(segment, reservedBounds) ||
          (leader !== null && segmentIntersects(leader.start, leader.end, segment.start, segment.end))
        )).length + (
          leader !== null ? occupied.filter(rect => segmentIntersectsRect(leader, rect)).length : 0
        );
        return {
          point,
          text,
          x,
          y,
          bounds: labelBounds,
          maxWidth,
          leader,
          tuple: [
            labelOverlapCount,
            markerIntersectionCount,
            avoidOrLeaderIntersectionCount,
            leader !== null ? 1 : 0,
            Math.hypot(offset.dx, offset.dy),
            candidateIndex,
          ],
        };
      });
    }

    function laneLabelCandidates(ctx, point, bounds, occupied, markers, avoidSegments, leaders, interval) {
      const text = point.row.model;
      const maxWidth = Math.max(12, bounds.right - bounds.left - 6);
      const metrics = ctx.measureText(text);
      const ascent = metrics.actualBoundingBoxAscent || 10;
      const descent = metrics.actualBoundingBoxDescent || 3;
      const minimumBaseline = bounds.top + 3 + ascent;
      const maximumBaseline = bounds.bottom - 3 - descent;
      const safeMinimum = Math.min(minimumBaseline, maximumBaseline);
      const safeMaximum = Math.max(minimumBaseline, maximumBaseline);
      const preferredBaseline = clamped(point.y, safeMinimum, safeMaximum);
      const baselines = [];
      if (minimumBaseline <= maximumBaseline) {
        for (let baseline = minimumBaseline; baseline <= maximumBaseline; baseline += interval) {
          baselines.push(baseline);
        }
      } else {
        baselines.push((bounds.top + bounds.bottom + ascent - descent) / 2);
      }
      const candidates = [];
      for (const [sideIndex, side] of [
        { x: bounds.left + 3, textAlign: "left" },
        { x: bounds.right - 3, textAlign: "right" },
      ].entries()) {
        for (const baseline of [...baselines, preferredBaseline]) {
          ctx.textAlign = side.textAlign;
          const labelBounds = labelBoundsFor(ctx, text, side.x, baseline, 3, maxWidth);
          const leader = leaderFor(point, labelBounds);
          const reservedBounds = expandedRect(labelBounds, 4);
          const labelOverlapCount = occupied.filter(rect => rectsIntersect(labelBounds, rect)).length;
          const markerIntersectionCount = markers.filter(marker => (
            marker !== point && circleIntersectsRect(marker, labelBounds)
          )).length;
          const avoidOrLeaderIntersectionCount = [
            ...avoidSegments,
            ...leaders,
          ].filter(segment => (
            segmentIntersectsRect(segment, reservedBounds) ||
            segmentIntersects(leader.start, leader.end, segment.start, segment.end)
          )).length + occupied.filter(rect => segmentIntersectsRect(leader, rect)).length;
          const labelCenterY = (labelBounds.top + labelBounds.bottom) / 2;
          candidates.push({
            point,
            text,
            x: side.x,
            y: baseline,
            bounds: labelBounds,
            maxWidth,
            textAlign: side.textAlign,
            leader,
            tuple: [
              labelOverlapCount,
              markerIntersectionCount,
              avoidOrLeaderIntersectionCount,
              Math.abs(labelCenterY - point.y),
              Math.hypot(leader.end.x - leader.start.x, leader.end.y - leader.start.y),
              sideIndex,
              baseline,
            ],
          });
        }
      }
      return candidates;
    }

    function layoutOptimalLabels(ctx, points, bounds, avoidSegments, fontSize, allowLaneOverlap) {
      const font = `700 ${fontSize}px sans-serif`;
      const interval = fontSize === 12 ? 16 : 14;
      const occupied = [];
      const leaders = [];
      const placements = [];
      ctx.font = font;
      ctx.textAlign = "left";
      const ordered = points.map(point => {
        const candidates = nearbyLabelCandidates(ctx, point, bounds, [], points, avoidSegments, []);
        const candidateCount = candidates.filter(candidate => (
          candidate.tuple[1] === 0 && candidate.tuple[2] === 0
        )).length;
        return { point, candidateCount, textWidth: ctx.measureText(point.row.model).width };
      }).sort((left, right) => (
        left.candidateCount - right.candidateCount ||
        right.textWidth - left.textWidth ||
        left.point.row.model.localeCompare(right.point.row.model)
      ));
      const callouts = [];
      for (const { point } of ordered) {
        ctx.textAlign = "left";
        const nearby = nearbyLabelCandidates(ctx, point, bounds, occupied, points, avoidSegments, leaders)
          .filter(candidate => candidate.tuple[0] === 0)
          .sort((left, right) => compareTuple(left.tuple, right.tuple))[0];
        if (nearby) {
          placements.push({ ...nearby, font, fontSize, textAlign: "left" });
          occupied.push(expandedRect(nearby.bounds, 4));
          if (nearby.leader) leaders.push(nearby.leader);
        } else {
          callouts.push(point);
        }
      }
      for (const point of callouts) {
        const candidates = laneLabelCandidates(
          ctx, point, bounds, occupied, points, avoidSegments, leaders, interval,
        ).sort((left, right) => compareTuple(left.tuple, right.tuple));
        const selected = candidates.find(candidate => candidate.tuple[0] === 0) ||
          (allowLaneOverlap ? candidates[0] : null);
        if (!selected) return null;
        placements.push({ ...selected, font, fontSize });
        occupied.push(expandedRect(selected.bounds, 4));
        leaders.push(selected.leader);
      }
      return { placements, occupied, leaders };
    }

    function drawProjectedPoint(ctx, point) {
      ctx.save();
      ctx.globalAlpha = point.alpha;
      ctx.fillStyle = point.fillStyle;
      ctx.beginPath();
      ctx.arc(point.x, point.y, point.radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    function layoutModelLabels(ctx, labelPoints, bounds, options = {}) {
      const avoidSegments = options.avoidSegments ?? [];
      const optimal = labelPoints.filter(point => point.row.pareto.optimal);
      const suboptimal = labelPoints.filter(point => !point.row.pareto.optimal && point.row.pareto.suboptimal);
      let optimalLayout = layoutOptimalLabels(ctx, optimal, bounds, avoidSegments, 12, false);
      if (!optimalLayout) {
        optimalLayout = layoutOptimalLabels(ctx, optimal, bounds, avoidSegments, 10, false) ||
          layoutOptimalLabels(ctx, optimal, bounds, avoidSegments, 10, true);
      }
      const placements = [...optimalLayout.placements];
      const hidden = [];
      ctx.font = "700 12px sans-serif";
      ctx.textAlign = "left";
      for (const point of suboptimal) {
        const selected = nearbyLabelCandidates(
          ctx,
          point,
          bounds,
          optimalLayout.occupied,
          labelPoints,
          avoidSegments,
          optimalLayout.leaders,
        ).filter(candidate => candidate.tuple[0] === 0)
          .sort((left, right) => compareTuple(left.tuple, right.tuple))[0];
        if (!selected) {
          hidden.push(point);
          continue;
        }
        placements.push({
          ...selected,
          font: "700 12px sans-serif",
          fontSize: 12,
          textAlign: "left",
        });
        optimalLayout.occupied.push(expandedRect(selected.bounds, 4));
        if (selected.leader) optimalLayout.leaders.push(selected.leader);
      }
      return { placements, hidden };
    }

    function drawModelLabels(ctx, layout) {
      ctx.save();
      ctx.lineWidth = 1;
      ctx.globalAlpha = 0.55;
      ctx.setLineDash([]);
      ctx.lineCap = "round";
      for (const placement of layout.placements) {
        if (!placement.leader) continue;
        ctx.strokeStyle = placement.point.row.pareto.optimal
          ? cssColor("--chart-optimal-label")
          : cssColor("--chart-suboptimal-label");
        ctx.beginPath();
        ctx.moveTo(placement.leader.start.x, placement.leader.start.y);
        ctx.lineTo(placement.leader.end.x, placement.leader.end.y);
        ctx.stroke();
      }
      ctx.restore();
      for (const placement of layout.placements) drawProjectedPoint(ctx, placement.point);
      for (const placement of layout.placements) {
        ctx.save();
        ctx.font = placement.font;
        ctx.textAlign = placement.textAlign;
        ctx.fillStyle = placement.point.row.pareto.optimal
          ? cssColor("--chart-optimal-label")
          : cssColor("--chart-suboptimal-label");
        ctx.lineJoin = "round";
        ctx.lineWidth = 2;
        ctx.strokeStyle = cssColor("--chart-label-halo");
        ctx.strokeText(placement.text, placement.x, placement.y, placement.maxWidth);
        ctx.fillText(placement.text, placement.x, placement.y, placement.maxWidth);
        ctx.restore();
      }
    }

    function drawFixedContainedLabel(ctx, text, x, y, bounds, options = {}) {
      const padding = options.padding ?? 3;
      const maxWidth = Math.max(12, (options.maxWidth ?? bounds.right - bounds.left) - padding * 2);
      let labelX = x;
      let labelY = y;
      const labelBounds = labelBoundsFor(ctx, text, labelX, labelY, padding, maxWidth);
      labelX += clamped(labelBounds.left, bounds.left, bounds.right) - labelBounds.left;
      labelX += clamped(labelBounds.right, bounds.left, bounds.right) - labelBounds.right;
      labelY += clamped(labelBounds.top, bounds.top, bounds.bottom) - labelBounds.top;
      labelY += clamped(labelBounds.bottom, bounds.top, bounds.bottom) - labelBounds.bottom;
      ctx.fillText(text, labelX, labelY, maxWidth);
    }

    function fit2DTrend(rows, categories, ranges) {
      const points = rows.map(row => ({
        x: normalizedMetric(row, categories[0], ranges[0]),
        y: normalizedMetric(row, categories[1], ranges[1]),
      }));
      const count = points.length;
      if (count < 2) return null;

      const sumX = points.reduce((sum, point) => sum + point.x, 0);
      const sumY = points.reduce((sum, point) => sum + point.y, 0);
      const sumXX = points.reduce((sum, point) => sum + point.x * point.x, 0);
      const sumXY = points.reduce((sum, point) => sum + point.x * point.y, 0);
      const denominator = count * sumXX - sumX * sumX;
      if (Math.abs(denominator) < 0.000001) return null;

      const slope = (count * sumXY - sumX * sumY) / denominator;
      const intercept = (sumY - slope * sumX) / count;
      return { slope, intercept };
    }

    function fit3DTrendLine(rows, categories, ranges) {
      if (rows.length < 3) return null;
      const points = rows.map(row => ({
        x: normalizedMetric(row, categories[0], ranges[0]) * 2 - 1,
        y: normalizedMetric(row, categories[1], ranges[1]) * 2 - 1,
        z: normalizedMetric(row, categories[2], ranges[2]) * 2 - 1,
      }));
      const center = points.reduce((sum, point) => ({
        x: sum.x + point.x / points.length,
        y: sum.y + point.y / points.length,
        z: sum.z + point.z / points.length,
      }), { x: 0, y: 0, z: 0 });

      const covariance = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
      ];
      for (const point of points) {
        const dx = point.x - center.x;
        const dy = point.y - center.y;
        const dz = point.z - center.z;
        covariance[0][0] += dx * dx;
        covariance[0][1] += dx * dy;
        covariance[0][2] += dx * dz;
        covariance[1][0] += dy * dx;
        covariance[1][1] += dy * dy;
        covariance[1][2] += dy * dz;
        covariance[2][0] += dz * dx;
        covariance[2][1] += dz * dy;
        covariance[2][2] += dz * dz;
      }

      let direction = { x: 1, y: 1, z: 1 };
      for (let iteration = 0; iteration < 24; iteration += 1) {
        const next = {
          x: covariance[0][0] * direction.x + covariance[0][1] * direction.y + covariance[0][2] * direction.z,
          y: covariance[1][0] * direction.x + covariance[1][1] * direction.y + covariance[1][2] * direction.z,
          z: covariance[2][0] * direction.x + covariance[2][1] * direction.y + covariance[2][2] * direction.z,
        };
        const length = Math.hypot(next.x, next.y, next.z);
        if (length < 0.000001) return null;
        direction = { x: next.x / length, y: next.y / length, z: next.z / length };
      }
      return { center, direction };
    }

    function chartCategories() {
      return [2, 3].includes(payload.categories.length) ? payload.categories : [];
    }

    function drawGraph() {
      const chartSection = document.getElementById("chartSection");
      const categories = chartCategories();
      if (!categories.length) {
        chartSection.hidden = true;
        return;
      }
      chartSection.hidden = false;
      chartSection.classList.toggle("is-3d", categories.length === 3);
      chartSection.classList.toggle("is-2d", categories.length === 2);
      document.getElementById("chartTitle").textContent =
        categories.length === 2 ? "2D category comparison" : "3D category comparison";
      updateFullscreenButton("chartSection", "fullscreenChart");
      document.getElementById("resetView").hidden = ![2, 3].includes(categories.length);
      document.getElementById("viewCube").hidden = categories.length !== 3;
      document.getElementById("zoomIndicator").hidden = ![2, 3].includes(categories.length);
      const config = {
        rows: plottableRows(categories),
        canvasId: "chart",
        tooltipId: "tooltip",
        zoomIndicatorId: "zoomIndicator",
        resetButtonId: "resetView",
        viewCubeId: "viewCube",
        sectionId: "chartSection",
        setRender: render => { chartRender = render; },
      };
      if (categories.length === 2) draw2D(categories, config);
      else draw3D(categories, config);
    }

    function draw2D(categories, config) {
      const ranges = categories.map(metricRange);
      const trend = fit2DTrend(config.rows, categories, ranges);
      let hover = null;
      const tooltip = document.getElementById(config.tooltipId);
      const zoomIndicator = document.getElementById(config.zoomIndicatorId);
      const hoverRadius = 18;
      const initial2DView = { minX: ranges[0].min, maxX: ranges[0].max, minY: ranges[1].min, maxY: ranges[1].max, zoom: 1 };
      let view2D = { ...initial2DView };
      let dragging = false;
      let last = { x: 0, y: 0 };
      let pinchDistance = 0;
      let touchStart = null;
      let touchMoved = false;
      let lastTouchInteractionAt = 0;
      const tapMoveTolerance = 8;
      const syntheticMouseIgnoreMs = 650;

      function current2DSpan() {
        return { x: view2D.maxX - view2D.minX, y: view2D.maxY - view2D.minY };
      }

      function update2DZoomIndicator() {
        zoomIndicator.textContent = `${view2D.zoom.toFixed(2)}x`;
      }

      function clamp2DView() {
        const fullX = ranges[0].span;
        const fullY = ranges[1].span;
        const minSpanX = fullX / 8;
        const minSpanY = fullY / 8;
        const maxSpanX = fullX / 0.55;
        const maxSpanY = fullY / 0.55;

        function clampAxis(min, max, range, minSpan, maxSpan) {
          const maximumSpan = Math.min(maxSpan, range.span);
          let span = Math.max(0.000001, max - min);
          if (span < minSpan) {
            const center = (min + max) / 2;
            span = minSpan;
            min = center - span / 2;
            max = center + span / 2;
          } else if (span > maximumSpan) {
            min = range.min;
            max = range.max;
            span = range.span;
          }
          if (min < range.min) {
            const offset = range.min - min;
            min += offset;
            max += offset;
          }
          if (max > range.max) {
            const offset = max - range.max;
            min -= offset;
            max -= offset;
          }
          if (min < range.min || max > range.max || max - min > range.span) {
            min = range.min;
            max = range.max;
          }
          return { min, max };
        }

        const xBounds = clampAxis(view2D.minX, view2D.maxX, ranges[0], minSpanX, maxSpanX);
        const yBounds = clampAxis(view2D.minY, view2D.maxY, ranges[1], minSpanY, maxSpanY);
        view2D.minX = xBounds.min;
        view2D.maxX = xBounds.max;
        view2D.minY = yBounds.min;
        view2D.maxY = yBounds.max;
        view2D.zoom = Math.max(1, Math.min(8, ranges[0].span / (view2D.maxX - view2D.minX)));
      }

      function reset2DView() {
        view2D = { ...initial2DView };
        update2DZoomIndicator();
        hover = null;
        tooltip.style.display = "none";
        render();
      }

      function chartPoint(eventOrTouch) {
        const rect = canvas.getBoundingClientRect();
        return { x: eventOrTouch.clientX - rect.left, y: eventOrTouch.clientY - rect.top };
      }

      function projectDataValue(xValue, yValue, width, height) {
        const margins = { top: 54, right: 58, bottom: 74, left: 92 };
        const plotWidth = width - margins.left - margins.right;
        const plotHeight = height - margins.top - margins.bottom;
        const x = margins.left + ((xValue - view2D.minX) / (view2D.maxX - view2D.minX)) * plotWidth;
        const y = height - margins.bottom - ((yValue - view2D.minY) / (view2D.maxY - view2D.minY)) * plotHeight;
        return { x, y };
      }

      function zoom2DAt(point, factor, width, height) {
        const margins = { top: 54, right: 58, bottom: 74, left: 92 };
        const plotLeft = margins.left;
        const plotBottom = height - margins.bottom;
        const plotWidth = width - margins.left - margins.right;
        const plotHeight = height - margins.top - margins.bottom;
        const span = current2DSpan();
        const xRatio = Math.max(0, Math.min(1, (point.x - plotLeft) / plotWidth));
        const yRatio = Math.max(0, Math.min(1, (plotBottom - point.y) / plotHeight));
        const dataX = view2D.minX + xRatio * span.x;
        const dataY = view2D.minY + yRatio * span.y;
        const safeFactor = Math.max(0.01, factor);
        const nextSpanX = span.x / safeFactor;
        const nextSpanY = span.y / safeFactor;
        view2D.minX = dataX - xRatio * nextSpanX;
        view2D.maxX = view2D.minX + nextSpanX;
        view2D.minY = dataY - yRatio * nextSpanY;
        view2D.maxY = view2D.minY + nextSpanY;
        clamp2DView();
      }

      function pan2DBy(deltaX, deltaY, width, height) {
        const margins = { top: 54, right: 58, bottom: 74, left: 92 };
        const plotWidth = width - margins.left - margins.right;
        const plotHeight = height - margins.top - margins.bottom;
        const span = current2DSpan();
        const domainDeltaX = -(deltaX / plotWidth) * span.x;
        const domainDeltaY = (deltaY / plotHeight) * span.y;
        view2D.minX += domainDeltaX;
        view2D.maxX += domainDeltaX;
        view2D.minY += domainDeltaY;
        view2D.maxY += domainDeltaY;
        clamp2DView();
      }

      function touchPoint(touch) {
        return { x: touch.clientX, y: touch.clientY };
      }

      function touchDistance(touches) {
        return Math.hypot(
          touches[0].clientX - touches[1].clientX,
          touches[0].clientY - touches[1].clientY,
        );
      }
      function markTouchInteraction() {
        lastTouchInteractionAt = Date.now();
      }

      function shouldIgnoreSyntheticMouse() {
        return Date.now() - lastTouchInteractionAt < syntheticMouseIgnoreMs;
      }

      function nearest2DPoint(point) {
        return (canvas._points || []).reduce((best, candidate) => {
          const distance = Math.hypot(candidate.x - point.x, candidate.y - point.y);
          return distance < best.distance ? { point: candidate, distance } : best;
        }, { point: null, distance: Infinity });
      }

      function hide2DTooltip() {
        hover = null;
        tooltip.style.display = "none";
      }

      function show2DTooltip(clientPoint) {
        const point = chartPoint(clientPoint);
        const nearest = nearest2DPoint(point);
        hover = nearest.distance < hoverRadius ? nearest.point : null;
        canvas.style.cursor = hover ? "pointer" : "";
        if (hover) {
          tooltip.style.display = "block";
          tooltip.style.left = `${clientPoint.clientX}px`;
          tooltip.style.top = `${clientPoint.clientY}px`;
          tooltip.innerHTML = tooltipText(hover.row, categories);
        } else {
          tooltip.style.display = "none";
        }
        render();
      }

      function project(row, width, height) {
        return projectDataValue(row.graph[categories[0].key], row.graph[categories[1].key], width, height);
      }
      function pointIn2DView(row) {
        const xValue = row.graph[categories[0].key];
        const yValue = row.graph[categories[1].key];
        return (
          xValue >= view2D.minX &&
          xValue <= view2D.maxX &&
          yValue >= view2D.minY &&
          yValue <= view2D.maxY
        );
      }

      function render() {
        update2DZoomIndicator();
        const { canvas, ctx, width, height } = setupCanvas(config.canvasId, config.sectionId);
        ctx.clearRect(0, 0, width, height);
        ctx.lineWidth = 1;
        ctx.font = "12px sans-serif";
        const margins = { top: 54, right: 58, bottom: 74, left: 92 };
        const plotLeft = margins.left;
        const plotRight = width - margins.right;
        const plotTop = margins.top;
        const plotBottom = height - margins.bottom;
        const plotWidth = plotRight - plotLeft;
        const plotHeight = plotBottom - plotTop;
        const minorTickCount = 20;
        const majorTickEvery = 4;

        ctx.fillStyle = cssColor("--chart-text");

        ctx.strokeStyle = cssColor("--chart-grid-minor");
        ctx.lineWidth = 0.75;
        for (let index = 0; index <= minorTickCount; index += 1) {
          if (index % majorTickEvery === 0) continue;
          const ratio = index / minorTickCount;
          const x = plotLeft + ratio * plotWidth;
          const y = plotBottom - ratio * plotHeight;
          ctx.beginPath();
          ctx.moveTo(x, plotTop);
          ctx.lineTo(x, plotBottom);
          ctx.moveTo(plotLeft, y);
          ctx.lineTo(plotRight, y);
          ctx.stroke();
        }

        ctx.strokeStyle = cssColor("--chart-grid-major");
        ctx.lineWidth = 1;
        for (let index = 0; index <= minorTickCount; index += majorTickEvery) {
          const ratio = index / minorTickCount;
          const x = plotLeft + ratio * plotWidth;
          const y = plotBottom - ratio * plotHeight;
          const xValue = view2D.minX + ratio * (view2D.maxX - view2D.minX);
          const yValue = view2D.minY + ratio * (view2D.maxY - view2D.minY);

          ctx.beginPath();
          ctx.moveTo(x, plotTop);
          ctx.lineTo(x, plotBottom);
          ctx.moveTo(plotLeft, y);
          ctx.lineTo(plotRight, y);
          ctx.stroke();

          ctx.fillText(formatTick(xValue), x - 14, plotBottom + 22);
          ctx.textAlign = "right";
          ctx.fillText(formatTick(yValue), plotLeft - 12, y + 4);
          ctx.textAlign = "left";
        }

        ctx.strokeStyle = cssColor("--chart-axis");
        ctx.lineWidth = 2.25;
        ctx.beginPath();
        ctx.moveTo(plotLeft, plotTop);
        ctx.lineTo(plotLeft, plotBottom);
        ctx.lineTo(plotRight, plotBottom);
        ctx.stroke();
        ctx.fillStyle = cssColor("--chart-title");
        ctx.font = "700 16px sans-serif";
        drawFixedContainedLabel(
          ctx,
          `${categories[0].label}${categories[0].lowerIsBetter ? " (lower better)" : " (higher better)"}`,
          plotLeft,
          height - 24,
          { left: 6, right: width - 6, top: 6, bottom: height - 6 },
        );
        ctx.save();
        ctx.translate(24, plotBottom);
        ctx.rotate(-Math.PI / 2);
        ctx.fillText(`${categories[1].label}${categories[1].lowerIsBetter ? " (lower better)" : " (higher better)"}`, 0, 0);
        ctx.restore();

        let trendSegment = null;
        if (trend) {
          const startYRatio = trend.intercept + trend.slope * ((view2D.minX - ranges[0].min) / ranges[0].span);
          const endYRatio = trend.intercept + trend.slope * ((view2D.maxX - ranges[0].min) / ranges[0].span);
          const start = projectDataValue(view2D.minX, ranges[1].min + startYRatio * ranges[1].span, width, height);
          const end = projectDataValue(view2D.maxX, ranges[1].min + endYRatio * ranges[1].span, width, height);
          trendSegment = { start, end };
          ctx.save();
          ctx.beginPath();
          ctx.rect(plotLeft, plotTop, plotWidth, plotHeight);
          ctx.clip();
          ctx.strokeStyle = cssColor("--trend");
          ctx.lineWidth = 3;
          ctx.setLineDash([8, 5]);
          ctx.beginPath();
          ctx.moveTo(start.x, start.y);
          ctx.lineTo(end.x, end.y);
          ctx.stroke();
          ctx.restore();
        }

        const projected = config.rows.filter(pointIn2DView).map(row => ({
          row,
          ...project(row, width, height),
          radius: row.pareto.optimal ? 5.5 : 4,
          fillStyle: pointColor(row),
          alpha: 1,
        }));
        const modelLabelBounds = {
          left: plotLeft + 4,
          right: plotRight - 4,
          top: plotTop + 4,
          bottom: plotBottom - 4,
        };
        ctx.save();
        ctx.beginPath();
        ctx.rect(plotLeft, plotTop, plotWidth, plotHeight);
        ctx.clip();
        for (const point of projected) drawProjectedPoint(ctx, point);
        if (hover) {
          ctx.save();
          ctx.strokeStyle = cssColor("--chart-hover-ring");
          ctx.lineWidth = 2.5;
          ctx.beginPath();
          ctx.arc(hover.x, hover.y, hover.row.pareto.optimal ? 8.5 : 7, 0, Math.PI * 2);
          ctx.stroke();
          ctx.restore();
        }
        const labelPoints = projected.filter(point => (
          point.row.pareto.optimal || point.row.pareto.suboptimal
        ));
        const labelLayout = layoutModelLabels(ctx, labelPoints, modelLabelBounds, {
          avoidSegments: trendSegment ? [trendSegment] : [],
        });
        drawModelLabels(ctx, labelLayout);
        ctx.restore();
        canvas._points = projected;
      }

      config.setRender(render);
      const canvas = document.getElementById(config.canvasId);
      trackChartListener(canvas, "mousedown", event => {
        if (shouldIgnoreSyntheticMouse()) return;
        dragging = true;
        last = { x: event.clientX, y: event.clientY };
        hide2DTooltip();
        canvas.style.cursor = "grabbing";
      });
      trackChartListener(window, "mouseup", () => {
        dragging = false;
        canvas.style.cursor = hover ? "pointer" : "";
      });
      trackChartListener(window, "mousemove", event => {
        if (shouldIgnoreSyntheticMouse()) return;
        if (dragging) {
          const rect = canvas.getBoundingClientRect();
          pan2DBy(event.clientX - last.x, event.clientY - last.y, rect.width, rect.height);
          last = { x: event.clientX, y: event.clientY };
          hide2DTooltip();
          canvas.style.cursor = "grabbing";
          render();
          return;
        }
        const rect = canvas.getBoundingClientRect();
        const inCanvas =
          event.clientX >= rect.left &&
          event.clientX <= rect.right &&
          event.clientY >= rect.top &&
          event.clientY <= rect.bottom;
        if (!inCanvas) {
          hide2DTooltip();
          canvas.style.cursor = "";
          render();
          return;
        }
        show2DTooltip(event);
      });
      trackChartListener(canvas, "wheel", event => {
        event.preventDefault();
        const rect = canvas.getBoundingClientRect();
        const point = { x: event.clientX - rect.left, y: event.clientY - rect.top };
        zoom2DAt(point, event.deltaY < 0 ? 1.08 : 0.92, rect.width, rect.height);
        hover = null;
        tooltip.style.display = "none";
        render();
      }, { passive: false });
      trackChartListener(canvas, "touchstart", event => {
        markTouchInteraction();
        if (event.touches.length === 1) {
          event.preventDefault();
          dragging = true;
          last = touchPoint(event.touches[0]);
          touchStart = last;
          touchMoved = false;
        } else if (event.touches.length === 2) {
          event.preventDefault();
          dragging = false;
          touchStart = null;
          touchMoved = true;
          pinchDistance = touchDistance(event.touches);
          hide2DTooltip();
        }
      }, { passive: false });
      trackChartListener(canvas, "touchmove", event => {
        markTouchInteraction();
        if (event.touches.length === 1 && dragging) {
          event.preventDefault();
          const touch = event.touches[0];
          const next = touchPoint(touch);
          if (touchStart && Math.hypot(next.x - touchStart.x, next.y - touchStart.y) > tapMoveTolerance) {
            touchMoved = true;
          }
          if (!touchMoved) return;
          const rect = canvas.getBoundingClientRect();
          pan2DBy(next.x - last.x, next.y - last.y, rect.width, rect.height);
          last = next;
          hide2DTooltip();
          render();
        } else if (event.touches.length === 2) {
          event.preventDefault();
          const nextDistance = touchDistance(event.touches);
          if (pinchDistance > 0) {
            const rect = canvas.getBoundingClientRect();
            const midpoint = {
              x: ((event.touches[0].clientX + event.touches[1].clientX) / 2) - rect.left,
              y: ((event.touches[0].clientY + event.touches[1].clientY) / 2) - rect.top,
            };
            zoom2DAt(midpoint, nextDistance / pinchDistance, rect.width, rect.height);
            touchMoved = true;
            touchStart = null;
            hide2DTooltip();
            render();
          }
          pinchDistance = nextDistance;
        }
      }, { passive: false });
      trackChartListener(canvas, "touchend", event => {
        markTouchInteraction();
        if (!event.touches.length) {
          const changedTouch = event.changedTouches?.[0];
          const wasTap = changedTouch && touchStart && !touchMoved && pinchDistance === 0;
          dragging = false;
          pinchDistance = 0;
          touchStart = null;
          touchMoved = false;
          if (wasTap) {
            event.preventDefault();
            show2DTooltip(changedTouch);
          }
        } else if (event.touches.length === 1) {
          event.preventDefault();
          dragging = true;
          last = touchPoint(event.touches[0]);
          touchStart = null;
          touchMoved = true;
          pinchDistance = 0;
        }
      }, { passive: false });
      trackChartListener(canvas, "touchcancel", () => {
        markTouchInteraction();
        dragging = false;
        pinchDistance = 0;
        touchStart = null;
        touchMoved = false;
      });
      trackChartListener(document.getElementById(config.resetButtonId), "click", reset2DView);
      trackChartListener(window, "resize", render);
      render();
    }

    function draw3D(categories, config) {
      const ranges = categories.map(metricRange);
      const trend = fit3DTrendLine(config.rows, categories, ranges);
      const tooltip = document.getElementById(config.tooltipId);
      const initialCamera = { rotationX: 0.62, rotationY: 0.78, zoom: 1.25 };
      const viewPresets = {
        front: { rotationX: 0, rotationY: 0, zoom: 1.1 },
        back: { rotationX: 0, rotationY: Math.PI, zoom: 1.1 },
        right: { rotationX: 0, rotationY: Math.PI / 2, zoom: 1.1 },
        left: { rotationX: 0, rotationY: -Math.PI / 2, zoom: 1.1 },
        top: { rotationX: Math.PI / 2, rotationY: 0, zoom: 1.1 },
        bottom: { rotationX: -Math.PI / 2, rotationY: 0, zoom: 1.1 },
        isometric: initialCamera,
      };
      let rotationX = initialCamera.rotationX;
      let rotationY = initialCamera.rotationY;
      let zoom = initialCamera.zoom;
      let dragging = false;
      let hover = null;
      let last = { x: 0, y: 0 };
      let pinchDistance = 0;
      let touchStart = null;
      let touchMoved = false;
      let lastTouchInteractionAt = 0;
      const tapMoveTolerance = 8;
      const syntheticMouseIgnoreMs = 650;
      const hoverRadius = 18;
      const viewCube = document.getElementById(config.viewCubeId);
      const zoomIndicator = document.getElementById(config.zoomIndicatorId);

      function norm(row, category, range) {
        return ((row.graph[category.key] - range.min) / range.span) * 2 - 1;
      }

      function setCamera(camera, { preserveZoom = false } = {}) {
        rotationX = camera.rotationX;
        rotationY = camera.rotationY;
        if (!preserveZoom) zoom = camera.zoom;
        render();
      }

      function normalizedAngleDifference(first, second) {
        return Math.atan2(Math.sin(first - second), Math.cos(first - second));
      }

      function cameraMatches(camera) {
        const tolerance = 0.015;
        return (
          Math.abs(rotationX - camera.rotationX) <= tolerance &&
          Math.abs(normalizedAngleDifference(rotationY, camera.rotationY)) <= tolerance
        );
      }

      function updateViewCubeActiveState() {
        for (const button of viewCube.querySelectorAll("button[data-view]")) {
          const preset = viewPresets[button.dataset.view];
          button.classList.toggle("active", Boolean(preset && cameraMatches(preset)));
        }
      }

      function updateZoomIndicator() {
        zoomIndicator.textContent = `${zoom.toFixed(2)}x`;
      }

      function rotate(point) {
        const cosY = Math.cos(rotationY);
        const sinY = Math.sin(rotationY);
        const cosX = Math.cos(rotationX);
        const sinX = Math.sin(rotationX);
        const x1 = point.x * cosY - point.z * sinY;
        const z1 = point.x * sinY + point.z * cosY;
        const y1 = point.y * cosX - z1 * sinX;
        const z2 = point.y * sinX + z1 * cosX;
        return { x: x1, y: y1, z: z2 };
      }

      function project(rotated, width, height) {
        const scale = Math.min(width, height) * 0.28 * zoom * chartZoomScale(config.sectionId);
        const perspective = 1 / (1 + (2.8 - rotated.z) * 0.12);
        return {
          x: width / 2 + rotated.x * scale * perspective,
          y: height / 2 - rotated.y * scale * perspective,
          depth: rotated.z,
        };
      }

      function drawSegment(ctx, start, end, width, height) {
        const projectedStart = project(rotate(start), width, height);
        const projectedEnd = project(rotate(end), width, height);
        ctx.beginPath();
        ctx.moveTo(projectedStart.x, projectedStart.y);
        ctx.lineTo(projectedEnd.x, projectedEnd.y);
        ctx.stroke();
      }

      function projectPoint(point, width, height) {
        return project(rotate(point), width, height);
      }

      function axisTickPoint(axisIndex, value) {
        const point = { x: -1.05, y: -1.05, z: -1.05 };
        if (axisIndex === 0) point.x = value;
        if (axisIndex === 1) point.y = value;
        if (axisIndex === 2) point.z = value;
        return point;
      }

      function clippedTrendEndpoints() {
        if (!trend) return;
        let minT = -Infinity;
        let maxT = Infinity;
        for (const axis of ["x", "y", "z"]) {
          const centerValue = trend.center[axis];
          const directionValue = trend.direction[axis];
          if (Math.abs(directionValue) < 0.000001) {
            if (centerValue < -1 || centerValue > 1) return null;
            continue;
          }
          const first = (-1 - centerValue) / directionValue;
          const second = (1 - centerValue) / directionValue;
          minT = Math.max(minT, Math.min(first, second));
          maxT = Math.min(maxT, Math.max(first, second));
        }
        if (minT > maxT) return null;
        return {
          start: {
            x: trend.center.x + trend.direction.x * minT,
            y: trend.center.y + trend.direction.y * minT,
            z: trend.center.z + trend.direction.z * minT,
          },
          end: {
            x: trend.center.x + trend.direction.x * maxT,
            y: trend.center.y + trend.direction.y * maxT,
            z: trend.center.z + trend.direction.z * maxT,
          },
        };
      }

      function drawTrendLine(ctx, width, height) {
        const endpoints = clippedTrendEndpoints();
        if (!endpoints) return;
        ctx.save();
        ctx.strokeStyle = cssColor("--trend");
        ctx.lineWidth = 3;
        ctx.globalAlpha = 0.82;
        ctx.setLineDash([8, 5]);
        drawSegment(ctx, endpoints.start, endpoints.end, width, height);
        ctx.restore();
      }

      function render() {
        const { canvas, ctx, width, height } = setupCanvas(config.canvasId, config.sectionId);
        updateViewCubeActiveState();
        updateZoomIndicator();
        ctx.clearRect(0, 0, width, height);
        ctx.fillStyle = cssColor("--chart-text");
        ctx.font = "12px sans-serif";
        ctx.lineWidth = 1;

        const minorTickCount = 16;
        const majorTickEvery = 4;

        ctx.strokeStyle = cssColor("--chart-grid-3d-minor");
        ctx.lineWidth = 0.75;
        for (let index = 0; index <= minorTickCount; index += 1) {
          if (index % majorTickEvery === 0) continue;
          const value = -1.05 + (index / minorTickCount) * 2.1;
          drawSegment(ctx, { x: value, y: -1.05, z: -1.05 }, { x: value, y: 1.05, z: -1.05 }, width, height);
          drawSegment(ctx, { x: value, y: -1.05, z: -1.05 }, { x: value, y: -1.05, z: 1.05 }, width, height);
          drawSegment(ctx, { x: -1.05, y: value, z: -1.05 }, { x: 1.05, y: value, z: -1.05 }, width, height);
          drawSegment(ctx, { x: -1.05, y: value, z: -1.05 }, { x: -1.05, y: value, z: 1.05 }, width, height);
          drawSegment(ctx, { x: -1.05, y: -1.05, z: value }, { x: 1.05, y: -1.05, z: value }, width, height);
          drawSegment(ctx, { x: -1.05, y: -1.05, z: value }, { x: -1.05, y: 1.05, z: value }, width, height);
        }

        ctx.strokeStyle = cssColor("--chart-grid-3d-major");
        ctx.lineWidth = 1;
        for (let index = 0; index <= minorTickCount; index += majorTickEvery) {
          const value = -1.05 + (index / minorTickCount) * 2.1;
          drawSegment(ctx, { x: value, y: -1.05, z: -1.05 }, { x: value, y: 1.05, z: -1.05 }, width, height);
          drawSegment(ctx, { x: value, y: -1.05, z: -1.05 }, { x: value, y: -1.05, z: 1.05 }, width, height);
          drawSegment(ctx, { x: -1.05, y: value, z: -1.05 }, { x: 1.05, y: value, z: -1.05 }, width, height);
          drawSegment(ctx, { x: -1.05, y: value, z: -1.05 }, { x: -1.05, y: value, z: 1.05 }, width, height);
          drawSegment(ctx, { x: -1.05, y: -1.05, z: value }, { x: 1.05, y: -1.05, z: value }, width, height);
          drawSegment(ctx, { x: -1.05, y: -1.05, z: value }, { x: -1.05, y: 1.05, z: value }, width, height);
        }

        const axes = [
          { end: { x: 1.25, y: -1.05, z: -1.05 }, label: categories[0], tickOffset: { x: -12, y: 18 } },
          { end: { x: -1.05, y: 1.25, z: -1.05 }, label: categories[1], tickOffset: { x: 8, y: 16 } },
          { end: { x: -1.05, y: -1.05, z: 1.25 }, label: categories[2], tickOffset: { x: 8, y: -8 } },
        ];
        const origin = projectPoint({ x: -1.05, y: -1.05, z: -1.05 }, width, height);
        ctx.strokeStyle = cssColor("--chart-axis-strong");
        ctx.lineWidth = 2.6;
        ctx.fillStyle = cssColor("--chart-title");
        ctx.font = "700 16px sans-serif";
        for (const [axisIndex, axis] of axes.entries()) {
          const end = projectPoint(axis.end, width, height);
          ctx.beginPath();
          ctx.moveTo(origin.x, origin.y);
          ctx.lineTo(end.x, end.y);
          ctx.stroke();
          drawFixedContainedLabel(
            ctx,
            `${axis.label.label}${axis.label.lowerIsBetter ? " ↓" : " ↑"}`,
            end.x + 6,
            end.y + 4,
            { left: 6, right: width - 6, top: 6, bottom: height - 6 },
          );

          ctx.font = "11px sans-serif";
          ctx.fillStyle = cssColor("--chart-text");
          for (let index = 0; index <= minorTickCount; index += majorTickEvery) {
            const ratio = index / minorTickCount;
            const normalizedValue = -1 + ratio * 2;
            const tick = projectPoint(axisTickPoint(axisIndex, normalizedValue), width, height);
            const tickValue = ranges[axisIndex].min + ratio * ranges[axisIndex].span;
            drawFixedContainedLabel(
              ctx,
              formatTick(tickValue),
              tick.x + axis.tickOffset.x,
              tick.y + axis.tickOffset.y,
              { left: 6, right: width - 6, top: 6, bottom: height - 6 },
            );
          }
          ctx.font = "700 16px sans-serif";
          ctx.fillStyle = cssColor("--chart-title");
        }

        drawTrendLine(ctx, width, height);

        const projected = config.rows.map(row => {
          const point = {
            x: norm(row, categories[0], ranges[0]),
            y: norm(row, categories[1], ranges[1]),
            z: norm(row, categories[2], ranges[2]),
          };
          return {
            row,
            ...project(rotate(point), width, height),
            radius: row.pareto.optimal ? 6 : 4.2,
            fillStyle: pointColor(row),
            alpha: row.pareto.optimal ? 0.92 : row.pareto.suboptimal ? 0.78 : 0.92,
          };
        }).sort((a, b) => a.depth - b.depth);

        for (const point of projected) drawProjectedPoint(ctx, point);
        if (hover) {
          ctx.save();
          ctx.strokeStyle = cssColor("--chart-hover-ring");
          ctx.lineWidth = 2.5;
          ctx.beginPath();
          ctx.arc(hover.x, hover.y, hover.row.pareto.optimal ? 9 : 7.5, 0, Math.PI * 2);
          ctx.stroke();
          ctx.restore();
        }
        const labelPoints = projected.filter(point => (
          (point.row.pareto.optimal || point.row.pareto.suboptimal) &&
          point.x >= -point.radius &&
          point.x <= width + point.radius &&
          point.y >= -point.radius &&
          point.y <= height + point.radius
        ));
        const labelLayout = layoutModelLabels(
          ctx,
          labelPoints,
          { left: 8, right: width - 8, top: 8, bottom: height - 8 },
        );
        drawModelLabels(ctx, labelLayout);
        canvas._points = projected;
      }

      const canvas = document.getElementById(config.canvasId);
      function rotateFromPoint(point) {
        rotationY -= (point.x - last.x) * 0.01;
        rotationX += (point.y - last.y) * 0.01;
        rotationX = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, rotationX));
        last = point;
        hover = null;
        tooltip.style.display = "none";
        render();
      }

      function touchPoint(touch) {
        return { x: touch.clientX, y: touch.clientY };
      }

      function touchDistance(touches) {
        return Math.hypot(
          touches[0].clientX - touches[1].clientX,
          touches[0].clientY - touches[1].clientY,
        );
      }

      function markTouchInteraction() {
        lastTouchInteractionAt = Date.now();
      }

      function shouldIgnoreSyntheticMouse() {
        return Date.now() - lastTouchInteractionAt < syntheticMouseIgnoreMs;
      }

      function show3DTooltip(clientPoint) {
        const rect = canvas.getBoundingClientRect();
        const x = clientPoint.clientX - rect.left;
        const y = clientPoint.clientY - rect.top;
        const nearest = (canvas._points || []).reduce((best, point) => {
          const distance = Math.hypot(point.x - x, point.y - y);
          return distance < best.distance ? { point, distance } : best;
        }, { point: null, distance: Infinity });
        hover = nearest.distance < hoverRadius ? nearest.point : null;
        canvas.style.cursor = hover ? "pointer" : "";
        if (hover) {
          tooltip.style.display = "block";
          tooltip.style.left = `${clientPoint.clientX}px`;
          tooltip.style.top = `${clientPoint.clientY}px`;
          tooltip.innerHTML = tooltipText(hover.row, categories);
        } else {
          tooltip.style.display = "none";
        }
        render();
      }

      trackChartListener(canvas, "mousedown", event => {
        if (shouldIgnoreSyntheticMouse()) return;
        dragging = true;
        last = { x: event.clientX, y: event.clientY };
      });
      trackChartListener(window, "mouseup", () => {
        dragging = false;
        canvas.style.cursor = hover ? "pointer" : "";
      });
      trackChartListener(window, "mousemove", event => {
        if (shouldIgnoreSyntheticMouse()) return;
        if (dragging) {
          rotateFromPoint({ x: event.clientX, y: event.clientY });
          canvas.style.cursor = "grabbing";
          return;
        }
        const rect = canvas.getBoundingClientRect();
        const inCanvas =
          event.clientX >= rect.left &&
          event.clientX <= rect.right &&
          event.clientY >= rect.top &&
          event.clientY <= rect.bottom;
        if (!inCanvas) {
          hover = null;
          canvas.style.cursor = "";
          tooltip.style.display = "none";
          render();
          return;
        }
        show3DTooltip(event);
      });
      trackChartListener(canvas, "mouseleave", () => {
        hover = null;
        canvas.style.cursor = "";
        tooltip.style.display = "none";
        render();
      });
      trackChartListener(canvas, "wheel", event => {
        event.preventDefault();
        zoom *= event.deltaY < 0 ? 1.08 : 0.92;
        zoom = Math.max(0.55, Math.min(8, zoom));
        render();
      }, { passive: false });
      trackChartListener(canvas, "touchstart", event => {
        markTouchInteraction();
        if (event.touches.length === 1) {
          event.preventDefault();
          dragging = true;
          last = touchPoint(event.touches[0]);
          touchStart = last;
          touchMoved = false;
        } else if (event.touches.length === 2) {
          event.preventDefault();
          dragging = false;
          touchStart = null;
          touchMoved = true;
          pinchDistance = touchDistance(event.touches);
        }
      }, { passive: false });
      trackChartListener(canvas, "touchmove", event => {
        markTouchInteraction();
        if (event.touches.length === 1 && dragging) {
          event.preventDefault();
          const next = touchPoint(event.touches[0]);
          if (touchStart && Math.hypot(next.x - touchStart.x, next.y - touchStart.y) > tapMoveTolerance) {
            touchMoved = true;
          }
          if (!touchMoved) return;
          rotateFromPoint(next);
        } else if (event.touches.length === 2) {
          event.preventDefault();
          const nextDistance = touchDistance(event.touches);
          if (pinchDistance > 0) {
            zoom *= nextDistance / pinchDistance;
            zoom = Math.max(0.55, Math.min(8, zoom));
            render();
          }
          pinchDistance = nextDistance;
        }
      }, { passive: false });
      trackChartListener(canvas, "touchend", event => {
        markTouchInteraction();
        if (!event.touches.length) {
          const changedTouch = event.changedTouches?.[0];
          const wasTap = changedTouch && touchStart && !touchMoved && pinchDistance === 0;
          dragging = false;
          pinchDistance = 0;
          touchStart = null;
          touchMoved = false;
          if (wasTap) {
            event.preventDefault();
            show3DTooltip(changedTouch);
          }
        } else if (event.touches.length === 1) {
          event.preventDefault();
          dragging = true;
          last = touchPoint(event.touches[0]);
          touchStart = null;
          touchMoved = true;
          pinchDistance = 0;
        }
      }, { passive: false });
      trackChartListener(canvas, "touchcancel", () => {
        markTouchInteraction();
        dragging = false;
        pinchDistance = 0;
        touchStart = null;
        touchMoved = false;
      });
      trackChartListener(document.getElementById(config.resetButtonId), "click", () => {
        setCamera(initialCamera);
      });
      trackChartListener(viewCube, "click", event => {
        const button = event.target.closest?.("button[data-view]");
        if (!button) return;
        const preset = viewPresets[button.dataset.view];
        if (preset) setCamera(preset, { preserveZoom: true });
      });
      trackChartListener(window, "resize", render);
      config.setRender(render);
      render();
    }

    function drawParetoGraph() {
      const section = document.getElementById("paretoChartSection");
      const categories = chartCategories();
      const optimalRows = plottableRows(categories).filter(row => row.pareto.optimal);
      if (!categories.length || !optimalRows.length) {
        section.hidden = true;
        paretoRender = null;
        return;
      }
      section.hidden = false;
      section.classList.toggle("is-3d", categories.length === 3);
      section.classList.toggle("is-2d", categories.length === 2);
      document.getElementById("paretoChartTitle").textContent =
        `Pareto-optimal models · ${optimalRows.length} model${optimalRows.length === 1 ? "" : "s"}`;
      updateFullscreenButton("paretoChartSection", "fullscreenParetoChart");
      document.getElementById("paretoViewCube").hidden = categories.length !== 3;
      document.getElementById("paretoZoomIndicator").hidden = ![2, 3].includes(categories.length);
      const config = {
        rows: optimalRows,
        canvasId: "paretoChart",
        tooltipId: "paretoTooltip",
        zoomIndicatorId: "paretoZoomIndicator",
        resetButtonId: "resetParetoView",
        viewCubeId: "paretoViewCube",
        sectionId: "paretoChartSection",
        setRender: render => { paretoRender = render; },
      };
      if (categories.length === 2) draw2D(categories, config);
      else draw3D(categories, config);
    }

    function safeFilename(value) {
      return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
    }

    function downloadCanvas(canvas, filename) {
      canvas.toBlob(blob => {
        if (!blob) return;
        const link = document.createElement("a");
        link.download = filename;
        link.href = URL.createObjectURL(blob);
        link.click();
        setTimeout(() => URL.revokeObjectURL(link.href), 0);
      }, "image/png");
    }

    function exportChart(canvasId, title) {
      const source = document.getElementById(canvasId);
      const headerHeight = 96;
      const output = document.createElement("canvas");
      output.width = source.width;
      output.height = source.height + headerHeight;
      const ctx = output.getContext("2d");
      ctx.fillStyle = cssColor("--chart-bg");
      ctx.fillRect(0, 0, output.width, output.height);
      ctx.fillStyle = cssColor("--chart-title");
      ctx.font = "700 30px sans-serif";
      ctx.fillText(title, 32, 42);
      ctx.fillStyle = cssColor("--chart-text");
      ctx.font = "22px sans-serif";
      ctx.fillText(payload.categories.map(category => category.label).join(" · "), 32, 74);
      ctx.drawImage(source, 0, headerHeight);
      downloadCanvas(output, `${safeFilename(title)}.png`);
    }

    function exportTable() {
      const table = document.getElementById("resultsTable");
      const tableWidth = Math.ceil(table.getBoundingClientRect().width);
      const tableHeight = Math.ceil(table.getBoundingClientRect().height);
      const scale = 2;
      const margin = 24;
      const headerHeight = 64;
      const output = document.createElement("canvas");
      output.width = (tableWidth + margin * 2) * scale;
      output.height = (tableHeight + headerHeight + margin * 2) * scale;
      const ctx = output.getContext("2d");
      ctx.scale(scale, scale);
      ctx.fillStyle = cssColor("--panel");
      ctx.fillRect(0, 0, output.width / scale, output.height / scale);
      ctx.fillStyle = cssColor("--heading");
      ctx.font = "700 22px sans-serif";
      ctx.fillText("LLM comparison results", margin, margin + 24);
      ctx.fillStyle = cssColor("--muted");
      ctx.font = "13px sans-serif";
      ctx.fillText(document.getElementById("summary").textContent, margin, margin + 48);
      const originY = margin + headerHeight;
      const headerCells = [...table.tHead.rows[0].cells];
      const columnLefts = headerCells.map(cell => cell.offsetLeft);
      const columnWidths = headerCells.map(cell => cell.offsetWidth);
      for (const [rowIndex, row] of [...table.rows].entries()) {
        const y = originY + row.offsetTop;
        const rowStyle = getComputedStyle(row);
        ctx.fillStyle = rowIndex === 0 ? cssColor("--table-head") :
          (rowStyle.backgroundColor === "rgba(0, 0, 0, 0)" ? cssColor("--panel") : rowStyle.backgroundColor);
        ctx.fillRect(margin, y, tableWidth, row.offsetHeight);
        for (const [columnIndex, cell] of [...row.cells].entries()) {
          const x = margin + columnLefts[columnIndex];
          const width = columnWidths[columnIndex];
          const style = getComputedStyle(cell);
          ctx.save();
          ctx.beginPath();
          ctx.rect(x + 1, y, width - 2, row.offsetHeight);
          ctx.clip();
          ctx.fillStyle = rowIndex === 0 ? cssColor("--heading") : style.color;
          ctx.font = `${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;
          ctx.textBaseline = "middle";
          ctx.textAlign = cell.classList.contains("numeric") ? "right" : "left";
          const text = rowIndex === 0 && cell.classList.contains("sort-active")
            ? `${cell.textContent} ${cell.dataset.sortMark}`
            : cell.textContent;
          const textX = cell.classList.contains("numeric") ? x + width - 11 : x + 11;
          ctx.fillText(text, textX, y + row.offsetHeight / 2);
          ctx.restore();
        }
        ctx.strokeStyle = cssColor("--table-row-border");
        ctx.beginPath();
        ctx.moveTo(margin, y + row.offsetHeight - 0.5);
        ctx.lineTo(margin + tableWidth, y + row.offsetHeight - 0.5);
        ctx.stroke();
      }
      downloadCanvas(output, "llm-comparison-results.png");
    }

    function tooltipText(row, categories) {
      const lines = [`<strong>${escapeHtml(row.model)}</strong>`];
      for (const category of categories) {
        lines.push(`${escapeHtml(category.label)}: ${row.graph[category.key]}`);
      }
      lines.push(`${isOpenCodeGoView ? "Cost-adjusted intelligence" : "Final Score"}: ${row.score.toFixed(2)}`);
      if (row.pareto.optimal) lines.push("Pareto optimal");
      if (row.pareto.suboptimal) lines.push("Pareto suboptimal");
      return lines.join("<br>");
    }

    function escapeHtml(value) {
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    document.getElementById("runComparison").addEventListener("click", () => applySelection({ syncUrl: true }));
    document.getElementById("clearMetrics").addEventListener("click", clearMetrics);
    document.getElementById("resetMetrics").addEventListener("click", resetMetrics);
    document.getElementById("excludeZeroPrice").addEventListener("change", (event) => {
      excludeZeroPrice = event.target.checked;
      applySelection({ syncUrl: true });
    });
    document.getElementById("themeToggle").addEventListener("click", toggleTheme);
    themeMediaQuery?.addEventListener("change", () => {
      if (!readStoredTheme()) applyTheme(preferredSystemTheme());
    });
    document.getElementById("saveChart").addEventListener("click", () => {
      exportChart("chart", document.getElementById("chartTitle").textContent);
    });
    document.getElementById("saveParetoChart").addEventListener("click", () => {
      exportChart("paretoChart", document.getElementById("paretoChartTitle").textContent);
    });
    document.getElementById("saveTable").addEventListener("click", exportTable);
    async function toggleChartFullscreen(sectionId, buttonId) {
      const section = chartSection(sectionId);
      if (section.classList.contains("fullscreen-fallback")) {
        exitFullscreenFallback(sectionId, buttonId);
        return;
      }
      if (document.fullscreenElement === section) {
        await document.exitFullscreen?.();
        return;
      }
      if (!section.requestFullscreen) {
        enterFullscreenFallback(sectionId, buttonId);
        return;
      }
      try {
        await section.requestFullscreen();
      } catch {
        enterFullscreenFallback(sectionId, buttonId);
      }
    }
    document.getElementById("fullscreenChart").addEventListener("click", () => {
      toggleChartFullscreen("chartSection", "fullscreenChart");
    });
    document.getElementById("fullscreenParetoChart").addEventListener("click", () => {
      toggleChartFullscreen("paretoChartSection", "fullscreenParetoChart");
    });
    document.addEventListener("fullscreenchange", () => {
      updateFullscreenButton("chartSection", "fullscreenChart");
      updateFullscreenButton("paretoChartSection", "fullscreenParetoChart");
      chartRender?.();
      paretoRender?.();
    });
    document.addEventListener("keydown", event => {
      if (event.key !== "Escape") return;
      for (const [sectionId, buttonId] of [
        ["chartSection", "fullscreenChart"],
        ["paretoChartSection", "fullscreenParetoChart"],
      ]) {
        if (chartSection(sectionId).classList.contains("fullscreen-fallback")) {
          exitFullscreenFallback(sectionId, buttonId);
        }
      }
    });
    applyTheme(activeTheme());
    if (isOpenCodeGoView) {
      initializeEmbeddedGo();
      if (window.location.protocol !== "file:") {
        fetchCsvFromPaths(["data/opencode_go.csv", "../data/opencode_go.csv"])
          .then(text => initializeGoFromCsv(parseCsv(text)))
          .catch(() => {});
      }
    } else {
      applyUrlOptions();
      applySelection();
      if (window.location.protocol !== "file:") {
        fetchCsvFromPaths(["data/results.csv", "../data/results.csv"])
          .then(text => initializeFromCsv(parseCsv(text)))
          .catch(() => {
            updateScoreScale();
            updateSummary();
          });
      }
    }
  </script>
</body>
</html>
"""
