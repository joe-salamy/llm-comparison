from __future__ import annotations

HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>LLM Comparison</title>
  <style>
    :root {
      --bg: #f6f7f4;
      --ink: #1c1f1d;
      --muted: #5d655f;
      --line: #d5d9d2;
      --panel: #ffffff;
      --green: #00a854;
      --red: #e03131;
      --blue: #275c8f;
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
      color: #242824;
      font-size: 15px;
      font-weight: 720;
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
      background: #fbfcfa;
      padding: 11px;
    }
    .metric-group.core {
      border-color: #9ab7a6;
      background: #f3faf5;
    }
    .metric-group-title {
      margin: 0 0 8px;
      color: #303630;
      font-size: 12px;
      font-weight: 760;
      text-transform: uppercase;
    }
    .metric-group.core .metric-group-title {
      color: #1e5637;
    }
    .metric-button {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #f7f8f5;
      color: #242824;
      cursor: pointer;
      font: inherit;
      font-size: 12px;
      font-weight: 650;
      padding: 7px 9px;
    }
    .metric-button:hover,
    .metric-button:focus-visible {
      background: #eef0ec;
      outline: none;
    }
    .metric-button[disabled] {
      cursor: default;
      opacity: 0.45;
    }
    .metric-group.core .metric-button {
      border-color: #9ab7a6;
      background: #ffffff;
      font-size: 13px;
      padding: 8px 10px;
    }
    .metric-group.core .metric-button:hover,
    .metric-group.core .metric-button:focus-visible {
      background: #e8f3ec;
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
      background: #fbfcfa;
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
      border: 1px solid #b8c1b8;
      border-radius: 6px;
      background: #ffffff;
      color: #242824;
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
      background: #eef0ec;
      color: #242824;
      cursor: pointer;
      font: inherit;
      font-size: 14px;
      line-height: 1;
      padding: 0;
    }
    .run-button {
      min-height: 42px;
      border: 1px solid #1e5637;
      border-radius: 6px;
      background: #1e5637;
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
    .clear-button {
      min-height: 42px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #f7f8f5;
      color: #303630;
      cursor: pointer;
      font: inherit;
      font-size: 13px;
      font-weight: 720;
      padding: 0 12px;
      white-space: nowrap;
    }
    .run-button:hover,
    .run-button:focus-visible {
      background: #17472d;
      outline: none;
    }
    .clear-button:hover,
    .clear-button:focus-visible {
      background: #eef0ec;
      outline: none;
    }
    .control-note {
      margin-top: 9px;
      color: var(--muted);
      font-size: 12px;
    }
    .info-wrap {
      color: #303630;
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
      color: #1f5d8f;
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
      background: #f7f8f5;
      color: var(--ink);
      cursor: pointer;
      font: inherit;
      font-size: 12px;
      font-weight: 650;
      padding: 5px 9px;
    }
    .chart-button:hover {
      background: #eef0ec;
    }
    .chart-canvas-wrap {
      position: relative;
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
    .chart-wrap:fullscreen .chart-canvas-wrap {
      flex: 1;
      min-height: 0;
    }
    .chart-wrap:fullscreen #chart {
      height: 100%;
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
      border: 1px solid rgba(116, 125, 117, 0.42);
      border-radius: 7px;
      background: rgba(247, 248, 245, 0.90);
      box-shadow: 0 10px 28px rgba(28, 31, 29, 0.12);
      -webkit-backdrop-filter: blur(8px);
      backdrop-filter: blur(8px);
    }
    .view-cube[hidden] {
      display: none;
    }
    .view-cube button {
      min-width: 0;
      border: 1px solid rgba(116, 125, 117, 0.42);
      border-radius: 5px;
      background: #ffffff;
      color: #2f3831;
      cursor: pointer;
      font: inherit;
      font-size: 10px;
      font-weight: 720;
      line-height: 1;
      padding: 0;
    }
    .view-cube button:hover,
    .view-cube button:focus-visible {
      background: #eef0ec;
      border-color: #747d75;
      outline: none;
    }
    .view-cube button.active {
      background: #2f3831;
      color: #ffffff;
      border-color: #2f3831;
    }
    .view-cube button.active:hover,
    .view-cube button.active:focus-visible {
      background: #445047;
      border-color: #445047;
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
      border-top: 3px solid #8a5a00;
    }
    #chart {
      width: 100%;
      height: 560px;
      display: block;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fbfcfa;
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
      border-bottom: 1px solid rgba(0, 0, 0, 0.08);
      text-align: left;
      vertical-align: middle;
      white-space: nowrap;
    }
    th {
      position: sticky;
      top: 0;
      z-index: 2;
      background: #eef0ec;
      color: #242824;
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
      box-shadow: inset 0 0 0 9999px rgba(255, 255, 255, 0.18);
    }
    .tooltip {
      position: fixed;
      pointer-events: none;
      transform: translate(12px, 12px);
      background: rgba(28, 31, 29, 0.94);
      color: #fff;
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
      .selection-actions { display: grid; grid-template-columns: 1fr 1fr; }
      .run-button,
      .clear-button { width: 100%; }
      #chart { height: 440px; }
      th, td { padding: 8px; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>LLM Comparison</h1>
        <div class="meta-stack">
          <div class="meta">Data updated: May 15, 2026</div>
          <div class="meta" id="summary"></div>
        </div>
      </div>
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
          <button class="run-button" id="runComparison" type="button">Run comparison</button>
        </div>
      </div>
      <div class="control-note" id="controlNote"></div>
    </section>
    <section class="chart-wrap" id="chartSection" hidden>
      <div class="chart-title">
        <div id="chartTitle"></div>
        <div class="chart-actions">
          <button class="chart-button" id="fullscreenChart" type="button">Full screen</button>
          <button class="chart-button" id="resetCamera" type="button" hidden>Reset view</button>
          <div class="legend">
            <span><i class="dot green"></i>Pareto optimal</span>
            <span><i class="dot red"></i>Pareto suboptimal</span>
            <span><i class="dot neutral"></i>Other</span>
            <span><i class="line-sample"></i>Linear trend</span>
          </div>
        </div>
      </div>
      <div class="chart-canvas-wrap">
        <canvas id="chart"></canvas>
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
      </div>
    </section>
    <div class="table-wrap">
      <table id="resultsTable"></table>
    </div>
    <section class="info-wrap" aria-labelledby="aboutTitle">
      <h2 class="info-title" id="aboutTitle">About this comparison</h2>
      <div class="info-grid">
        <p>This static report ranks LLMs from the included <code>results.csv</code> data file. The source data was copied from Artificial Analysis, converted locally, and published here so viewers can change comparisons without collecting the data themselves.</p>
        <ul>
          <li>Higher is better for quality, benchmark, context, and speed metrics.</li>
          <li>Lower is better for price, latency, and time metrics.</li>
          <li>The final score is the average of direction-adjusted percentile ranks across the selected metrics.</li>
          <li>Models missing any selected numeric metric are excluded from that run.</li>
        </ul>
        <p>Credit: model benchmark, pricing, and performance data is from <a href="https://artificialanalysis.ai/leaderboards/models" rel="noreferrer">Artificial Analysis</a>. This project is an independent analysis and is not affiliated with Artificial Analysis.</p>
      </div>
    </section>
  </main>
  <div class="tooltip" id="tooltip"></div>
  <script>
    const payload = __PAYLOAD__;
    const dataUpdated = "May 15, 2026";
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
      blended_usd_per_1m_tokens: "Blended (USD/1M Tokens)",
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
    const mainColumnKeys = [
      "model",
      "context_window_tokens",
      "creator",
      "artificial_analysis_intelligence_index",
      "blended_usd_per_1m_tokens",
      "median_tokens_per_second",
      "first_chunk_latency_seconds",
      "total_response_time_seconds",
      "final_score",
    ];
    const lowerIsBetterMarkers = ["price", "usd", "latency", "time"];
    const coreCategoryKeys = [
      "context_window_tokens",
      "artificial_analysis_intelligence_index",
      "blended_usd_per_1m_tokens",
      "median_tokens_per_second",
      "first_chunk_latency_seconds",
      "total_response_time_seconds",
    ];
    const embeddedRows = payload.rows.slice();
    let sourceRows = [];
    let availableCategories = (payload.availableCategories || payload.categories).slice();
    let selectedCategories = payload.categories.map(category => category.key);
    let rows = payload.rows.slice();
    let sortState = { key: "final_score", direction: "desc" };
    let minScore = 0;
    let maxScore = 100;
    let medianScore = 50;
    let chartDisposers = [];
    let chartRender = null;

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

    function applyUrlMetrics() {
      const metrics = metricKeysFromUrl();
      if (metrics.length) selectedCategories = metrics;
    }

    function updateMetricsUrl() {
      const url = new URL(window.location.href);
      if (selectedCategories.length) {
        url.searchParams.set("metrics", selectedCategories.join(","));
      } else {
        url.searchParams.delete("metrics");
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
      if (parsed === null) return value ?? "";
      const general = () => Number.isInteger(parsed) ? String(parsed) : String(parsed);
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

    function percentileScores(values, lowerIsBetter) {
      if (values.length === 1) return [100];
      const sorted = values.map((value, index) => ({ value, index })).sort((a, b) => a.value - b.value);
      const scores = Array(values.length).fill(0);
      let index = 0;
      while (index < sorted.length) {
        let end = index + 1;
        while (end < sorted.length && sorted[end].value === sorted[index].value) end += 1;
        const averageRank = (index + end - 1) / 2;
        const percentile = 100 * averageRank / (values.length - 1);
        for (let itemIndex = index; itemIndex < end; itemIndex += 1) {
          scores[sorted[itemIndex].index] = lowerIsBetter ? 100 - percentile : percentile;
        }
        index = end;
      }
      return scores;
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
      const valuesByCategory = Object.fromEntries(categories.map(category => [category, []]));
      for (const raw of sourceRows) {
        const graph = {};
        let complete = true;
        for (const category of categories) {
          const parsed = parseNumber(raw[category]);
          if (parsed === null) {
            complete = false;
            break;
          }
          graph[category] = parsed;
        }
        if (!complete) continue;
        const row = { raw, graph, score: 0, cells: {}, model: raw.model || "" };
        completeRows.push(row);
        for (const category of categories) valuesByCategory[category].push(graph[category]);
      }

      const scoresByCategory = Object.fromEntries(
        categories.map(category => [category, percentileScores(valuesByCategory[category], isLowerBetter(category))]),
      );
      for (const [rowIndex, row] of completeRows.entries()) {
        const score = categories.reduce((sum, category) => sum + scoresByCategory[category][rowIndex], 0) / categories.length;
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
      const valuesByCategory = Object.fromEntries(categories.map(category => [category, []]));
      for (const original of embeddedRows) {
        const graph = {};
        let complete = true;
        for (const category of categories) {
          const parsed = parseNumber(original.graph[category]);
          if (parsed === null) {
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
        for (const category of categories) valuesByCategory[category].push(graph[category]);
      }

      const scoresByCategory = Object.fromEntries(
        categories.map(category => [category, percentileScores(valuesByCategory[category], isLowerBetter(category))]),
      );
      for (const [rowIndex, row] of completeRows.entries()) {
        const score = categories.reduce((sum, category) => sum + scoresByCategory[category][rowIndex], 0) / categories.length;
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
      const scoreValues = rows.map(row => row.score).sort((a, b) => a - b);
      minScore = scoreValues[0] ?? 0;
      maxScore = scoreValues[scoreValues.length - 1] ?? 100;
      medianScore = scoreValues.length
        ? scoreValues[Math.floor((scoreValues.length - 1) / 2)]
        : 50;
    }

    function updateSummary() {
      document.getElementById("summary").textContent =
        `${rows.length} models ranked by ${payload.categories.map(c => c.label).join(", ")}`;
      document.getElementById("controlNote").textContent =
        "Selected metrics are evaluated in order; the first two or three also define the chart axes.";
    }

    function resetChartCanvas() {
      for (const dispose of chartDisposers) dispose();
      chartDisposers = [];
      chartRender = null;
      const canvas = document.getElementById("chart");
      const replacement = canvas.cloneNode(false);
      canvas.replaceWith(replacement);
      document.getElementById("tooltip").style.display = "none";
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
      if (syncUrl) updateMetricsUrl();
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
      applyUrlMetrics();
      applySelection();
    }

    function interpolate(a, b, t) {
      return Math.round(a + (b - a) * Math.max(0, Math.min(1, t)));
    }

    function rowColor(score) {
      if (Math.abs(maxScore - minScore) < 0.0001) return "rgb(255,255,255)";
      const red = [118, 29, 29];
      const white = [255, 255, 255];
      const green = [11, 93, 42];
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
      return luminance < 0.48 ? "#fff" : "#151815";
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
        tr.style.background = rowColor(row.score);
        tr.style.color = textColor(row.score);
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
      if (row.pareto.optimal) return "#00a854";
      if (row.pareto.suboptimal) return "#e03131";
      return "#275c8f";
    }

    function isChartFullscreen() {
      return document.fullscreenElement === document.getElementById("chartSection");
    }

    function updateFullscreenButton() {
      const button = document.getElementById("fullscreenChart");
      button.textContent = isChartFullscreen() ? "Exit full screen" : "Full screen";
    }

    function chartRenderRatio() {
      const deviceRatio = window.devicePixelRatio || 1;
      const qualityMultiplier = isChartFullscreen() ? 1.75 : 1.5;
      return Math.min(3, Math.max(2, deviceRatio * qualityMultiplier));
    }

    function chartZoomScale() {
      return isChartFullscreen() ? 2 : 1;
    }

    function setupCanvas() {
      const canvas = document.getElementById("chart");
      const ratio = chartRenderRatio();
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

    function metricRange(category) {
      const values = payload.rows.map(row => row.graph[category.key]);
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
          best = { x: labelX, y: labelY, bounds: labelBounds, maxWidth };
          if (overlapCount === 0 && lineCount === 0) break;
        }
      }
      return best;
    }

    function drawContainedLabel(ctx, text, x, y, bounds, options = {}) {
      const label = placedContainedLabel(ctx, text, x, y, bounds, options);
      if (!label) return null;
      if (options.halo) {
        ctx.save();
        ctx.lineJoin = "round";
        ctx.lineWidth = options.haloWidth ?? 2;
        ctx.strokeStyle = options.haloColor ?? "rgba(246, 247, 244, 0.92)";
        ctx.strokeText(text, label.x, label.y, label.maxWidth);
        ctx.restore();
      }
      ctx.fillText(text, label.x, label.y, label.maxWidth);
      return label.bounds;
    }

    function drawLaidOutLabel(ctx, text, x, y, bounds, occupied, options = {}) {
      const labelBounds = drawContainedLabel(ctx, text, x, y, bounds, { ...options, occupied });
      if (labelBounds) occupied.push(labelBounds);
      return labelBounds;
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
      document.getElementById("chartTitle").textContent =
        categories.length === 2 ? "2D category comparison" : "3D category comparison";
      updateFullscreenButton();
      document.getElementById("resetCamera").hidden = categories.length !== 3;
      document.getElementById("viewCube").hidden = categories.length !== 3;
      if (categories.length === 2) draw2D(categories);
      else draw3D(categories);
    }

    function draw2D(categories) {
      const ranges = categories.map(metricRange);
      const trend = fit2DTrend(payload.rows, categories, ranges);
      let hover = null;
      const tooltip = document.getElementById("tooltip");
      const hoverRadius = 18;

      function project(row, width, height) {
        const margins = { top: 54, right: 58, bottom: 74, left: 92 };
        const plotWidth = width - margins.left - margins.right;
        const plotHeight = height - margins.top - margins.bottom;
        const x = margins.left + ((row.graph[categories[0].key] - ranges[0].min) / ranges[0].span) * plotWidth;
        const y = height - margins.bottom - ((row.graph[categories[1].key] - ranges[1].min) / ranges[1].span) * plotHeight;
        return { x, y };
      }

      function render() {
        const { canvas, ctx, width, height } = setupCanvas();
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

        ctx.fillStyle = "#4f5851";

        ctx.strokeStyle = "rgba(207, 212, 204, 0.38)";
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

        ctx.strokeStyle = "rgba(164, 172, 164, 0.68)";
        ctx.lineWidth = 1;
        for (let index = 0; index <= minorTickCount; index += majorTickEvery) {
          const ratio = index / minorTickCount;
          const x = plotLeft + ratio * plotWidth;
          const y = plotBottom - ratio * plotHeight;
          const xValue = ranges[0].min + ratio * ranges[0].span;
          const yValue = ranges[1].min + ratio * ranges[1].span;

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

        ctx.strokeStyle = "#9ea79f";
        ctx.lineWidth = 2.25;
        ctx.beginPath();
        ctx.moveTo(plotLeft, plotTop);
        ctx.lineTo(plotLeft, plotBottom);
        ctx.lineTo(plotRight, plotBottom);
        ctx.stroke();
        ctx.fillStyle = "#2f3831";
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
          const start = { x: plotLeft, y: plotBottom - trend.intercept * plotHeight };
          const end = { x: plotRight, y: plotBottom - (trend.intercept + trend.slope) * plotHeight };
          trendSegment = { start, end };
          ctx.save();
          ctx.beginPath();
          ctx.rect(plotLeft, plotTop, plotWidth, plotHeight);
          ctx.clip();
          ctx.strokeStyle = "#8a5a00";
          ctx.lineWidth = 3;
          ctx.setLineDash([8, 5]);
          ctx.beginPath();
          ctx.moveTo(start.x, start.y);
          ctx.lineTo(end.x, end.y);
          ctx.stroke();
          ctx.restore();
        }

        const projected = payload.rows.map(row => ({ row, ...project(row, width, height) }));
        const modelLabelBounds = {
          left: plotLeft + 4,
          right: plotRight - 4,
          top: plotTop + 4,
          bottom: plotBottom - 4,
        };
        const occupiedLabels = [];
        for (const point of projected) {
          ctx.beginPath();
          ctx.fillStyle = pointColor(point.row);
          ctx.arc(point.x, point.y, point.row.pareto.optimal ? 5.5 : 4, 0, Math.PI * 2);
          ctx.fill();
        }
        if (hover) {
          ctx.save();
          ctx.strokeStyle = "#1c1f1d";
          ctx.lineWidth = 2.5;
          ctx.beginPath();
          ctx.arc(hover.x, hover.y, hover.row.pareto.optimal ? 8.5 : 7, 0, Math.PI * 2);
          ctx.stroke();
          ctx.restore();
        }
        for (const point of projected) {
          if (point.row.pareto.optimal || point.row.pareto.suboptimal) {
            ctx.fillStyle = point.row.pareto.suboptimal ? "#7a1717" : "#12351f";
            ctx.font = "700 12px sans-serif";
            drawLaidOutLabel(
              ctx,
              point.row.model,
              point.x,
              point.y,
              modelLabelBounds,
              occupiedLabels,
              {
                avoidSegments: trendSegment ? [trendSegment] : [],
                halo: true,
                haloWidth: 2,
                labelGap: 4,
                lineGap: 8,
              },
            );
          }
        }
        canvas._points = projected;
      }

      chartRender = render;
      const canvas = document.getElementById("chart");
      trackChartListener(canvas, "mousemove", event => {
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const nearest = (canvas._points || []).reduce((best, point) => {
          const distance = Math.hypot(point.x - x, point.y - y);
          return distance < best.distance ? { point, distance } : best;
        }, { point: null, distance: Infinity });
        hover = nearest.distance < hoverRadius ? nearest.point : null;
        canvas.style.cursor = hover ? "pointer" : "";
        if (hover) {
          tooltip.style.display = "block";
          tooltip.style.left = `${event.clientX}px`;
          tooltip.style.top = `${event.clientY}px`;
          tooltip.innerHTML = tooltipText(hover.row, categories);
        } else {
          tooltip.style.display = "none";
        }
        render();
      });
      trackChartListener(canvas, "mouseleave", () => {
        hover = null;
        canvas.style.cursor = "";
        tooltip.style.display = "none";
        render();
      });
      trackChartListener(window, "resize", render);
      render();
    }

    function draw3D(categories) {
      const ranges = categories.map(metricRange);
      const trend = fit3DTrendLine(payload.rows, categories, ranges);
      const tooltip = document.getElementById("tooltip");
      const initialCamera = { rotationX: 0.62, rotationY: 0.78, zoom: 1.18 };
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
      const hoverRadius = 18;
      const viewCube = document.getElementById("viewCube");

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
        const scale = Math.min(width, height) * 0.28 * zoom * chartZoomScale();
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
        ctx.strokeStyle = "#8a5a00";
        ctx.lineWidth = 3;
        ctx.globalAlpha = 0.82;
        ctx.setLineDash([8, 5]);
        drawSegment(ctx, endpoints.start, endpoints.end, width, height);
        ctx.restore();
      }

      function render() {
        const { canvas, ctx, width, height } = setupCanvas();
        updateViewCubeActiveState();
        ctx.clearRect(0, 0, width, height);
        ctx.fillStyle = "#4f5851";
        ctx.font = "12px sans-serif";
        ctx.lineWidth = 1;

        const minorTickCount = 16;
        const majorTickEvery = 4;

        ctx.strokeStyle = "rgba(207, 212, 204, 0.30)";
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

        ctx.strokeStyle = "rgba(164, 172, 164, 0.60)";
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
        ctx.strokeStyle = "#747d75";
        ctx.lineWidth = 2.6;
        ctx.fillStyle = "#2f3831";
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
          ctx.fillStyle = "#4f5851";
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
          ctx.fillStyle = "#2f3831";
        }

        drawTrendLine(ctx, width, height);

        const projected = payload.rows.map(row => {
          const point = {
            x: norm(row, categories[0], ranges[0]),
            y: norm(row, categories[1], ranges[1]),
            z: norm(row, categories[2], ranges[2]),
          };
          return { row, ...project(rotate(point), width, height) };
        }).sort((a, b) => a.depth - b.depth);

        for (const point of projected) {
          const radius = point.row.pareto.optimal ? 6 : 4.2;
          ctx.globalAlpha = point.row.pareto.suboptimal ? 0.78 : 0.92;
          ctx.beginPath();
          ctx.fillStyle = pointColor(point.row);
          ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
          ctx.fill();
          ctx.globalAlpha = 1;
        }
        if (hover) {
          ctx.save();
          ctx.strokeStyle = "#1c1f1d";
          ctx.lineWidth = 2.5;
          ctx.beginPath();
          ctx.arc(hover.x, hover.y, hover.row.pareto.optimal ? 9 : 7.5, 0, Math.PI * 2);
          ctx.stroke();
          ctx.restore();
        }
        const occupiedLabels = [];
        for (const point of projected) {
          if (!point.row.pareto.optimal && !point.row.pareto.suboptimal) continue;
          ctx.fillStyle = point.row.pareto.suboptimal ? "#7a1717" : "#12351f";
          ctx.font = "700 12px sans-serif";
          drawLaidOutLabel(
            ctx,
            point.row.model,
            point.x,
            point.y,
            { left: 8, right: width - 8, top: 8, bottom: height - 8 },
            occupiedLabels,
            { halo: true, haloWidth: 2, labelGap: 4 },
          );
        }
        canvas._points = projected;
      }

      const canvas = document.getElementById("chart");
      trackChartListener(canvas, "mousedown", event => {
        dragging = true;
        last = { x: event.clientX, y: event.clientY };
      });
      trackChartListener(window, "mouseup", () => {
        dragging = false;
        canvas.style.cursor = hover ? "pointer" : "";
      });
      trackChartListener(window, "mousemove", event => {
        if (dragging) {
          rotationY -= (event.clientX - last.x) * 0.01;
          rotationX += (event.clientY - last.y) * 0.01;
          rotationX = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, rotationX));
          last = { x: event.clientX, y: event.clientY };
          hover = null;
          tooltip.style.display = "none";
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
          hover = null;
          canvas.style.cursor = "";
          tooltip.style.display = "none";
          render();
          return;
        }
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const nearest = (canvas._points || []).reduce((best, point) => {
          const distance = Math.hypot(point.x - x, point.y - y);
          return distance < best.distance ? { point, distance } : best;
        }, { point: null, distance: Infinity });
        hover = nearest.distance < hoverRadius ? nearest.point : null;
        canvas.style.cursor = hover ? "pointer" : "";
        if (hover) {
          tooltip.style.display = "block";
          tooltip.style.left = `${event.clientX}px`;
          tooltip.style.top = `${event.clientY}px`;
          tooltip.innerHTML = tooltipText(hover.row, categories);
        } else {
          tooltip.style.display = "none";
        }
        render();
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
      trackChartListener(document.getElementById("resetCamera"), "click", () => {
        setCamera(initialCamera);
      });
      trackChartListener(viewCube, "click", event => {
        const button = event.target.closest?.("button[data-view]");
        if (!button) return;
        const preset = viewPresets[button.dataset.view];
        if (preset) setCamera(preset, { preserveZoom: true });
      });
      trackChartListener(window, "resize", render);
      chartRender = render;
      render();
    }

    function tooltipText(row, categories) {
      const lines = [`<strong>${escapeHtml(row.model)}</strong>`];
      for (const category of categories) {
        lines.push(`${escapeHtml(category.label)}: ${row.graph[category.key]}`);
      }
      lines.push(`Final Score: ${row.score.toFixed(2)}`);
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
    document.getElementById("fullscreenChart").addEventListener("click", () => {
      const chartSection = document.getElementById("chartSection");
      if (isChartFullscreen()) document.exitFullscreen?.();
      else chartSection.requestFullscreen?.();
    });
    document.addEventListener("fullscreenchange", () => {
      updateFullscreenButton();
      if (chartRender) chartRender();
    });
    applyUrlMetrics();
    renderMetricPicker();
    renderSelectedMetrics();
    updateScoreScale();
    updateSummary();
    renderTable();
    drawGraph();

    fetch("results.csv")
      .then(response => response.ok ? response.text() : Promise.reject(new Error("results.csv not found")))
      .then(text => initializeFromCsv(parseCsv(text)))
      .catch(() => {
        updateScoreScale();
        updateSummary();
      });
  </script>
</body>
</html>
"""
