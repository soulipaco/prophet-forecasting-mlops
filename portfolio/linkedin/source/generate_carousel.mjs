import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const OUT = path.join(REPO, "portfolio/linkedin");
const SLIDES = path.join(OUT, "carousel");
const W = 1080;
const H = 1350;

const C = {
  ink: "#0B1220",
  panel: "#151F32",
  panel2: "#1D2940",
  blue: "#2563EB",
  blueLight: "#93C5FD",
  orange: "#F97316",
  teal: "#14B8A6",
  paper: "#F8FAFC",
  white: "#FFFFFF",
  slate: "#94A3B8",
  line: "#334155",
};

const sans = "Aptos";
const display = "Aptos Display";

async function writeBlob(file, blob) {
  await fs.mkdir(path.dirname(file), { recursive: true });
  await fs.writeFile(file, new Uint8Array(await blob.arrayBuffer()));
}

function shape(slide, left, top, width, height, fill, radius = "rounded-xl", lineFill = "none") {
  return slide.shapes.add({
    geometry: radius === "ellipse" ? "ellipse" : "roundRect",
    position: { left, top, width, height },
    fill,
    line: { style: "solid", fill: lineFill, width: lineFill === "none" ? 0 : 2 },
    borderRadius: radius === "ellipse" ? undefined : radius,
  });
}

function rule(slide, left, top, width, height, fill = C.line) {
  return slide.shapes.add({
    geometry: "rect",
    position: { left, top, width, height },
    fill,
    line: { style: "solid", fill: "none", width: 0 },
  });
}

function text(slide, value, left, top, width, height, size, color = C.white, bold = false, align = "left") {
  const box = slide.shapes.add({
    geometry: "textbox",
    position: { left, top, width, height },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  box.text = value;
  box.text.fontSize = size;
  box.text.color = color;
  box.text.bold = bold;
  box.text.typeface = bold ? display : sans;
  box.text.alignment = align;
  box.text.verticalAlignment = "top";
  box.text.insets = { left: 0, right: 0, top: 0, bottom: 0 };
  return box;
}

function base(presentation, number, eyebrow, light = false) {
  const slide = presentation.slides.add();
  slide.background.fill = light ? C.paper : C.ink;
  text(slide, eyebrow.toUpperCase(), 72, 62, 760, 38, 19, light ? C.blue : C.teal, true);
  text(slide, String(number).padStart(2, "0"), 938, 62, 70, 38, 19, light ? C.slate : C.slate, true, "right");
  rule(slide, 72, 1272, 936, 2, light ? "#CBD5E1" : C.line);
  text(slide, "PROPHET FORECASTING MLOPS", 72, 1290, 600, 28, 14, light ? C.slate : C.slate, true);
  return slide;
}

function title(slide, value, top = 128, color = C.white, size = 58, height = 180) {
  return text(slide, value, 72, top, 936, height, size, color, true);
}

function pill(slide, label, left, top, width, fill = C.panel2, color = C.white) {
  shape(slide, left, top, width, 58, fill, "rounded-full");
  text(slide, label, left, top + 14, width, 30, 20, color, true, "center");
}

function addWave(slide, y, color = C.blue) {
  const xs = [78, 190, 302, 414, 526, 638, 750, 862, 974];
  const ys = [y, y - 74, y + 42, y - 36, y + 70, y - 58, y + 28, y - 78, y + 18];
  for (let i = 0; i < xs.length - 1; i += 1) {
    const x1 = xs[i];
    const y1 = ys[i];
    const x2 = xs[i + 1];
    const y2 = ys[i + 1];
    const length = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
    const angle = (Math.atan2(y2 - y1, x2 - x1) * 180) / Math.PI;
    const segment = rule(slide, x1, y1, length, 8, color);
    segment.rotation = angle;
    shape(slide, x1 - 8, y1 - 8, 16, 16, i % 2 ? C.teal : color, "ellipse");
  }
  shape(slide, xs.at(-1) - 8, ys.at(-1) - 8, 16, 16, C.teal, "ellipse");
}

function addDeckSlides(presentation, chartData) {
  // Slide 1 — the portfolio promise.
  {
    const slide = base(presentation, 1, "Batch forecasting, made inspectable");
    title(slide, "Prophet forecasting,\nengineered for\nrepeatable batch runs", 142, C.white, 62, 310);
    text(slide, "A coordinated model collection with time-aware evaluation, lineage, and stable Delta outputs.", 72, 506, 850, 112, 28, C.slate);
    addWave(slide, 870);
    pill(slide, "OPTUNA", 72, 1058, 190, C.panel2, C.blueLight);
    pill(slide, "MLFLOW", 282, 1058, 190, C.panel2, C.teal);
    pill(slide, "DELTA", 492, 1058, 170, C.panel2, C.white);
  }

  // Slide 2 — make the orchestration problem visible before the solution.
  {
    const slide = base(presentation, 2, "The coordination problem");
    title(slide, "A forecasting pipeline is more than one model", 142, C.white, 56, 160);
    text(slide, "The runtime must coordinate every distinct series with both configured targets.", 72, 338, 880, 92, 28, C.slate);
    text(slide, "N", 90, 500, 240, 190, 138, C.blue, true, "center");
    text(slide, "SERIES", 90, 690, 240, 46, 24, C.slate, true, "center");
    text(slide, "x", 400, 570, 100, 100, 76, C.orange, true, "center");
    text(slide, "2", 555, 500, 240, 190, 138, C.teal, true, "center");
    text(slide, "TARGETS", 555, 690, 240, 46, 24, C.slate, true, "center");
    rule(slide, 155, 825, 610, 4, C.line);
    const labels = ["validate", "tune", "fit", "forecast", "record"];
    labels.forEach((label, i) => {
      const x = 90 + i * 184;
      shape(slide, x, 902, 48, 48, i === 0 || i === 4 ? C.teal : C.blue, "ellipse");
      if (i < 4) rule(slide, x + 48, 923, 136, 6, C.line);
      text(slide, label, x - 20, 972, 100, 32, 18, C.slate, true, "center");
    });
  }

  // Slide 3 — show the boundary, not a generic cloud diagram.
  {
    const slide = base(presentation, 3, "A narrow platform boundary", true);
    title(slide, "Forecasting code stays ordinary Python", 142, C.ink, 56, 150);
    text(slide, "Databricks handles delivery concerns at the edge.", 72, 315, 880, 58, 28, C.slate);
    shape(slide, 72, 430, 936, 650, C.white, "rounded-2xl", "#CBD5E1");
    shape(slide, 675, 430, 333, 650, C.ink, "rounded-2xl");
    text(slide, "ORDINARY PYTHON", 112, 480, 470, 38, 21, C.blue, true);
    const py = ["validated config", "data contracts", "preprocessing", "Prophet + Optuna", "collection orchestration"];
    py.forEach((value, i) => {
      shape(slide, 112, 560 + i * 90, 490, 62, C.paper, "rounded-lg", "#CBD5E1");
      text(slide, value, 138, 577 + i * 90, 440, 30, 21, C.ink, true);
    });
    text(slide, "DATABRICKS", 720, 480, 240, 38, 21, C.teal, true);
    const db = ["Spark / Delta IO", "MLflow lineage", "Asset Bundle job", "dev / acc / prd"];
    db.forEach((value, i) => {
      rule(slide, 720, 578 + i * 112, 10, 10, i === 3 ? C.orange : C.teal);
      text(slide, value, 752, 562 + i * 112, 210, 62, 22, C.white, true);
    });
  }

  // Slide 4 — the per-fit temporal lifecycle.
  {
    const slide = base(presentation, 4, "Time-aware by design");
    title(slide, "Every fit follows the same temporal contract", 142, C.white, 56, 165);
    const steps = [
      ["01", "Prepare daily history", "Expand dates; infer closures; preserve target rules."],
      ["02", "Search with Prophet CV", "Derive initial, period, and horizon from available history."],
      ["03", "Refit selected model", "Use logistic growth, regressors, holidays, and seasonalities."],
      ["04", "Forecast + record", "Emit point/bounds, status, parameters, and backtest rows."],
    ];
    steps.forEach(([n, head, body], i) => {
      const y = 390 + i * 205;
      shape(slide, 72, y, 96, 96, i === 0 || i === 3 ? C.teal : C.blue, "ellipse");
      text(slide, n, 72, y + 27, 96, 44, 30, C.white, true, "center");
      if (i < 3) rule(slide, 117, y + 96, 6, 109, C.line);
      text(slide, head, 210, y + 4, 720, 48, 30, C.white, true);
      text(slide, body, 210, y + 66, 730, 84, 23, C.slate);
    });
  }

  // Slide 5 — reproducibility evidence carried through one run.
  {
    const slide = base(presentation, 5, "Reproducibility is a data product", true);
    title(slide, "A run carries enough evidence to be inspected later", 142, C.ink, 54, 165);
    const items = [
      ["CONFIG", "validated overlay + hash", C.blue],
      ["SOURCE", "Delta table version", C.teal],
      ["CODE", "version + locked dependencies", C.orange],
      ["RESULT", "counts, statuses, metrics, parameters", C.blue],
    ];
    items.forEach(([tag, body, color], i) => {
      const y = 405 + i * 155;
      shape(slide, 72, y, 936, 116, C.white, "rounded-xl", "#CBD5E1");
      rule(slide, 72, y, 14, 116, color);
      text(slide, tag, 118, y + 24, 190, 34, 19, color, true);
      text(slide, body, 310, y + 20, 650, 66, 28, C.ink, true);
    });
    shape(slide, 72, 1065, 936, 94, C.ink, "rounded-xl");
    text(slide, "ONE MLFLOW COLLECTION RUN", 112, 1094, 856, 40, 23, C.teal, true, "center");
  }

  // Slide 6 — native editable chart backed by the repository CSV.
  {
    const slide = base(presentation, 6, "Synthetic execution evidence", true);
    title(slide, "The repository runs the full collection", 142, C.ink, 56, 150);
    text(slide, "Deterministic synthetic data · 3-calendar-month horizon · 80% interval", 72, 312, 900, 60, 25, C.slate);
    shape(slide, 72, 420, 936, 520, C.white, "rounded-2xl", "#CBD5E1");
    slide.charts.add("line", {
      position: { left: 105, top: 475, width: 870, height: 395 },
      categories: chartData.categories,
      series: [
        { name: "Lower", values: chartData.lower, fill: C.blueLight },
        { name: "Forecast", values: chartData.forecast, fill: C.blue },
        { name: "Upper", values: chartData.upper, fill: C.teal },
      ],
      hasLegend: true,
      legend: { position: "bottom" },
      yAxis: { majorGridlines: { style: "solid", fill: "#E2E8F0", width: 1 } },
      xAxis: { labelRotation: -45 },
    });
    const stats = [
      ["4", "fits"],
      ["0", "failed"],
      ["832", "forecast rows"],
      ["84", "backtest rows"],
    ];
    stats.forEach(([value, label], i) => {
      const x = 72 + i * 234;
      text(slide, value, x, 990, 210, 62, 42, i === 1 ? C.teal : C.blue, true, "center");
      text(slide, label, x, 1056, 210, 36, 18, C.slate, true, "center");
    });
    text(slide, "Synthetic demonstration — not production performance", 72, 1150, 936, 36, 18, C.orange, true, "center");
  }

  // Slide 7 — demonstrate judgment through exclusions.
  {
    const slide = base(presentation, 7, "Deliberate scope beats checkbox MLOps");
    title(slide, "Build the operating surface the use case needs", 142, C.white, 54, 160);
    text(slide, "Implemented because batch forecasting needs it", 72, 362, 936, 48, 26, C.teal, true);
    const yes = ["stable Delta contracts", "collection-level lineage", "idempotent retries", "environment overlays"];
    yes.forEach((value, i) => {
      shape(slide, 72, 444 + i * 92, 32, 32, C.teal, "ellipse");
      text(slide, "✓", 72, 444 + i * 92, 32, 32, 20, C.white, true, "center");
      text(slide, value, 128, 440 + i * 92, 700, 46, 25, C.white, true);
    });
    rule(slide, 72, 824, 936, 2, C.line);
    text(slide, "Not invented without a consumer or policy", 72, 872, 936, 48, 26, C.orange, true);
    const no = ["online serving", "model-per-fit registry", "automatic promotion", "unsupported business impact"];
    no.forEach((value, i) => {
      text(slide, "—", 72, 958 + i * 58, 32, 32, 22, C.orange, true, "center");
      text(slide, value, 128, 956 + i * 58, 760, 36, 23, C.slate);
    });
  }

  // Slide 8 — clear invitation and verifiable summary.
  {
    const slide = base(presentation, 8, "Explore the implementation");
    title(slide, "Forecasting MLOps you can inspect, run, and challenge", 142, C.white, 60, 220);
    text(slide, "Python package · Prophet + Optuna · MLflow · Delta · Databricks Asset Bundles", 72, 405, 900, 100, 26, C.slate);
    shape(slide, 72, 570, 936, 300, C.panel, "rounded-2xl", C.line);
    text(slide, "soulipaco/\nprophet-forecasting-mlops", 118, 635, 844, 140, 42, C.white, true, "center");
    rule(slide, 334, 814, 412, 6, C.orange);
    text(slide, "Read the architecture. Run the synthetic demo. Inspect every claim.", 118, 932, 844, 90, 28, C.teal, true, "center");
    pill(slide, "GITHUB PORTFOLIO PROJECT", 260, 1090, 560, C.blue, C.white);
  }
}

async function readChartData() {
  const csv = await fs.readFile(path.join(REPO, "assets/portfolio/synthetic_forecast.csv"), "utf8");
  const rows = csv.trim().split(/\r?\n/).slice(1).map((line) => {
    const [ds, yhat, lower, upper, rowType] = line.split(",");
    return { ds, yhat: Number(yhat), lower: Number(lower), upper: Number(upper), rowType };
  }).filter((row) => row.rowType === "forecast");
  const sampled = rows.filter((_, index) => index % 5 === 0).slice(0, 14);
  return {
    categories: sampled.map((row) => row.ds.slice(5)),
    forecast: sampled.map((row) => Number(row.yhat.toFixed(1))),
    lower: sampled.map((row) => Number(row.lower.toFixed(1))),
    upper: sampled.map((row) => Number(row.upper.toFixed(1))),
  };
}

async function createMainImage() {
  const social = Presentation.create({ slideSize: { width: 1200, height: 627 } });
  const slide = social.slides.add();
  slide.background.fill = C.ink;
  text(slide, "PROPHET FORECASTING MLOPS", 64, 54, 620, 36, 18, C.teal, true);
  text(slide, "Forecast collections,\nengineered for repeatable runs.", 64, 132, 720, 190, 46, C.white, true);
  text(slide, "Optuna · time-aware CV · MLflow · Delta", 64, 365, 660, 54, 22, C.slate);
  addWave(slide, 470);
  rule(slide, 850, 90, 5, 430, C.orange);
  text(slide, "BATCH", 900, 190, 230, 50, 30, C.white, true, "center");
  text(slide, "N × 2", 900, 260, 230, 100, 64, C.blue, true, "center");
  text(slide, "SERIES × TARGETS", 900, 375, 230, 40, 17, C.slate, true, "center");
  await writeBlob(path.join(OUT, "main-image.png"), await social.export({ slide, format: "png", scale: 1 }));
}

async function main() {
  await fs.mkdir(SLIDES, { recursive: true });
  const deck = Presentation.create({ slideSize: { width: W, height: H } });
  addDeckSlides(deck, await readChartData());
  for (const [index, slide] of deck.slides.items.entries()) {
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    await writeBlob(path.join(SLIDES, `${stem}.png`), await deck.export({ slide, format: "png", scale: 1 }));
  }
  await writeBlob(path.join(OUT, "carousel-montage.webp"), await deck.export({ format: "webp", montage: true, scale: 0.3 }));
  const pptx = await PresentationFile.exportPptx(deck);
  const pptxPath = path.join(OUT, "prophet-forecasting-carousel.pptx");
  await pptx.save(pptxPath);
  await fs.rm(`${pptxPath}.inspect.ndjson`, { force: true });
  await createMainImage();
  console.log(`Created ${deck.slides.items.length} slides in ${OUT}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
