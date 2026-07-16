"""Generate public portfolio visuals from deterministic synthetic forecasts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch
from PIL import Image

from forecasting_project.config import ProjectConfig
from forecasting_project.orchestration import run_collection

ROOT = Path(__file__).parents[1]
OUTPUT = ROOT / "assets" / "portfolio"
CUTOFF = pd.Timestamp("2024-05-01")
SEED = 314159

INK = "#0B1220"
SLATE = "#475569"
MUTED = "#94A3B8"
PAPER = "#F8FAFC"
WHITE = "#FFFFFF"
BLUE = "#2563EB"
BLUE_LIGHT = "#DBEAFE"
ORANGE = "#F97316"
TEAL = "#14B8A6"


def synthetic_source() -> pd.DataFrame:
    """Mirror the safe Databricks demonstration at pandas grain."""
    rng = np.random.default_rng(SEED)
    rows: list[dict[str, object]] = []
    for index, language in enumerate(["Segment_A", "Segment_B"]):
        dates = pd.date_range(CUTOFF - pd.Timedelta(days=200), CUTOFF + pd.Timedelta(days=100), freq="D")
        for day_number, day in enumerate(dates):
            if day.dayofweek in (5, 6):
                continue
            trend = 80 + index * 15 + day_number * 0.05
            volume = max(1.0, trend + 12 * np.sin(day_number * 2 * np.pi / 7) + rng.normal(0, 2))
            rows.append(
                {
                    "Date": day,
                    "Business_Category_001": "Operations_A",
                    "Business_Category_002": f"KPI_Group_{index + 1}",
                    "Language": language,
                    "Country": "GR",
                    "Business_Category_003": float(volume) if day < CUTOFF else None,
                    "Business_Category_004": float(day.dayofweek),
                    "Business_Category_005": float(100 + day_number),
                    "Business_Category_006": float(index + 1 + 0.1 * np.cos(day_number * 2 * np.pi / 7)),
                    "Business_Category_007": 1.0,
                    "Business_Category_008": (
                        float(50 + 5 * np.sin(day_number * 2 * np.pi / 7)) if day < CUTOFF else None
                    ),
                }
            )
    return pd.DataFrame(rows)


def _canvas(width: int, height: int, background: str = PAPER):
    fig = plt.figure(figsize=(width / 100, height / 100), dpi=100, facecolor=background)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("off")
    ax.set_facecolor(background)
    return fig, ax


def _round_rect(ax, x, y, width, height, fill, edge="none", radius=24, linewidth=1):
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=fill,
        edgecolor=edge,
        linewidth=linewidth,
    )
    ax.add_patch(patch)
    return patch


def _save(fig, stem: str, width: int, height: int) -> None:
    svg = OUTPUT / f"{stem}.svg"
    png = OUTPUT / f"{stem}.png"
    fig.savefig(svg, format="svg", facecolor=fig.get_facecolor(), bbox_inches=None, pad_inches=0)
    fig.savefig(png, format="png", facecolor=fig.get_facecolor(), bbox_inches=None, pad_inches=0, dpi=100)
    plt.close(fig)
    with Image.open(png) as image:
        if image.size != (width, height):
            raise RuntimeError(f"unexpected dimensions for {png}: {image.size}")
        clean = image.convert("RGB")
        clean.save(png, optimize=True)


def hero() -> None:
    width, height = 1600, 560
    fig, ax = _canvas(width, height, INK)
    x = np.linspace(780, 1550, 220)
    y = 280 + 90 * np.sin(np.linspace(0, 7 * np.pi, 220)) * np.linspace(0.25, 1.0, 220)
    ax.fill_between(x, y - 42, y + 42, color=BLUE, alpha=0.08)
    ax.plot(x, y, color=BLUE, linewidth=5)
    ax.plot(x[::20], y[::20], "o", color=TEAL, markersize=7, markeredgecolor=INK, markeredgewidth=2)
    ax.axvline(1185, ymin=0.22, ymax=0.78, color=ORANGE, linewidth=3, linestyle=(0, (4, 4)))
    ax.text(
        90,
        52,
        "PROPHET FORECASTING MLOPS",
        color=TEAL,
        fontsize=18,
        weight="bold",
        family="DejaVu Sans",
        va="top",
    )
    ax.text(
        90,
        112,
        "Forecast collections,\nengineered for repeatable runs.",
        color=WHITE,
        fontsize=48,
        weight="bold",
        va="top",
    )
    ax.text(
        90,
        332,
        "Optuna tuning  |  time-aware CV  |  MLflow lineage  |  Delta outputs",
        color=MUTED,
        fontsize=21,
        va="top",
    )
    ax.text(90, 462, "PYTHON DOMAIN LOGIC", color=WHITE, fontsize=15, weight="bold", va="top")
    ax.text(420, 462, "DATABRICKS BATCH DELIVERY", color=WHITE, fontsize=15, weight="bold", va="top")
    ax.plot([382, 402], [473, 473], color=ORANGE, linewidth=4)
    _save(fig, "hero", width, height)


def architecture() -> None:
    width, height = 1600, 900
    fig, ax = _canvas(width, height)
    ax.text(80, 70, "Implemented architecture", color=INK, fontsize=38, weight="bold")
    ax.text(80, 112, "Forecasting stays testable; platform concerns stay at the boundary.", color=SLATE, fontsize=19)
    _round_rect(ax, 70, 160, 1010, 650, WHITE, edge="#CBD5E1", radius=30, linewidth=1.5)
    _round_rect(ax, 1110, 160, 420, 650, INK, radius=30)
    ax.text(110, 210, "ORDINARY PYTHON", color=BLUE, fontsize=18, weight="bold")
    ax.text(1150, 210, "DATABRICKS BOUNDARY", color=TEAL, fontsize=18, weight="bold")
    nodes = [
        (110, 260, 245, 92, "Validated config", "base + env overlays"),
        (385, 260, 245, 92, "Input contract", "schema + date grain"),
        (660, 260, 360, 92, "Series preparation", "daily expansion + closures"),
        (110, 405, 245, 92, "Holiday calendar", "native + binary regressor"),
        (385, 405, 245, 92, "Series x target", "collection orchestration"),
        (660, 405, 360, 92, "Optuna + Prophet CV", "shared builder + adaptive window"),
        (110, 550, 245, 92, "Final fit", "logistic growth"),
        (385, 550, 245, 92, "Forecast contract", "point + 80% interval"),
        (660, 550, 360, 92, "Run evidence", "metrics + parameters + status"),
    ]
    for x, y, w, h, title, subtitle in nodes:
        _round_rect(ax, x, y, w, h, PAPER, edge="#CBD5E1", radius=16)
        ax.text(x + 20, y + 34, title, color=INK, fontsize=17, weight="bold")
        ax.text(x + 20, y + 64, subtitle, color=SLATE, fontsize=13)
    connectors = [
        ((355, 306), (385, 306)),
        ((630, 306), (660, 306)),
        ((355, 451), (385, 451)),
        ((630, 451), (660, 451)),
        ((355, 596), (385, 596)),
        ((630, 596), (660, 596)),
    ]
    for start, end in connectors:
        ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "color": MUTED, "lw": 2})
    platform = [
        (1150, 260, "Spark / Delta input"),
        (1150, 370, "Managed Delta outputs"),
        (1150, 480, "MLflow collection run"),
        (1150, 590, "Asset Bundle job"),
        (1150, 700, "dev / acc / prd targets"),
    ]
    for x, y, label in platform:
        _round_rect(ax, x, y, 340, 70, "#172033", edge="#334155", radius=14)
        ax.text(x + 24, y + 43, label, color=WHITE, fontsize=16, weight="bold")
    ax.annotate("", xy=(1110, 475), xytext=(1020, 475), arrowprops={"arrowstyle": "->", "color": ORANGE, "lw": 3})
    ax.text(1040, 450, "IO", color=ORANGE, fontsize=13, weight="bold")
    _save(fig, "architecture", width, height)


def lifecycle() -> None:
    width, height = 1600, 600
    fig, ax = _canvas(width, height, INK)
    ax.text(80, 72, "One batch run, end to end", color=WHITE, fontsize=38, weight="bold")
    ax.text(80, 112, "The collection coordinates every series and both configured targets.", color=MUTED, fontsize=19)
    steps = [
        ("01", "Validate", "required columns\nunique series/date"),
        ("02", "Prepare", "daily expansion\ncalendar rules"),
        ("03", "Enumerate", "series keys\nx 2 targets"),
        ("04", "Tune", "Optuna search\nProphet CV"),
        ("05", "Fit", "selected params\nlogistic model"),
        ("06", "Forecast", "3 calendar months\n80% interval"),
        ("07", "Persist", "Delta tables\nMLflow lineage"),
    ]
    x_positions = np.linspace(80, 1370, len(steps))
    ax.plot([x_positions[0] + 56, x_positions[-1] + 56], [285, 285], color="#334155", linewidth=4)
    for index, (x, (number, title, subtitle)) in enumerate(zip(x_positions, steps, strict=True)):
        color = TEAL if index in (0, 6) else BLUE
        ax.scatter([x + 56], [285], s=900, color=color, edgecolor=INK, linewidth=4, zorder=3)
        ax.text(x + 56, 291, number, ha="center", va="center", color=WHITE, fontsize=16, weight="bold", zorder=4)
        ax.text(x, 350, title, color=WHITE, fontsize=20, weight="bold", va="top")
        ax.text(x, 414, subtitle, color=MUTED, fontsize=14, linespacing=1.5, va="top")
    _save(fig, "lifecycle", width, height)


def forecast_chart(source: pd.DataFrame, forecasts: pd.DataFrame) -> dict[str, object]:
    selected = forecasts[
        (forecasts["Business_Category_001"] == "Operations_A")
        & (forecasts["Business_Category_002"] == "KPI_Group_1")
        & (forecasts["Language"] == "Segment_A")
        & (forecasts["target"] == "volume")
    ].sort_values("ds")
    actual = source[
        (source["Business_Category_001"] == "Operations_A")
        & (source["Business_Category_002"] == "KPI_Group_1")
        & (source["Language"] == "Segment_A")
        & source["Business_Category_003"].notna()
    ].sort_values("Date")
    view_start = CUTOFF - pd.Timedelta(days=120)
    actual = actual[actual["Date"] >= view_start]
    fitted = selected[(selected["row_type"] == "fitted") & (selected["ds"] >= view_start)]
    future = selected[selected["row_type"] == "forecast"]

    fig, ax = plt.subplots(figsize=(16, 9), dpi=100, facecolor=PAPER)
    ax.set_facecolor(PAPER)
    ax.fill_between(
        future["ds"],
        future["yhat_lower"].astype(float),
        future["yhat_upper"].astype(float),
        color=BLUE,
        alpha=0.14,
        label="80% prediction interval",
    )
    ax.plot(fitted["ds"], fitted["yhat"], color=MUTED, linewidth=2.2, linestyle="--", label="Fitted")
    ax.plot(future["ds"], future["yhat"], color=BLUE, linewidth=3.2, label="Forecast")
    ax.scatter(actual["Date"], actual["Business_Category_003"], color=INK, s=20, alpha=0.72, label="Observed")
    ax.axvline(CUTOFF, color=ORANGE, linewidth=2.5, linestyle=(0, (4, 4)))
    ax.annotate(
        "Forecast cutoff",
        xy=(CUTOFF, ax.get_ylim()[1]),
        xytext=(8, -24),
        textcoords="offset points",
        color=ORANGE,
        fontsize=12,
        weight="bold",
        va="top",
    )
    ax.set_title(
        "Synthetic Prophet forecast with uncertainty",
        loc="left",
        fontsize=28,
        weight="bold",
        color=INK,
        pad=28,
    )
    ax.text(
        0,
        1.015,
        "Weekday series | actual repository pipeline | three-calendar-month horizon",
        transform=ax.transAxes,
        fontsize=14,
        color=SLATE,
    )
    ax.set_ylabel("Synthetic volume", color=SLATE, fontsize=13)
    ax.set_xlabel("")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.grid(axis="y", color="#CBD5E1", linewidth=0.8, alpha=0.8)
    ax.grid(axis="x", visible=False)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#CBD5E1")
    ax.spines["bottom"].set_color("#CBD5E1")
    ax.tick_params(colors=SLATE, labelsize=12)
    ax.legend(loc="upper left", frameon=False, ncol=4, fontsize=12, bbox_to_anchor=(0, 0.98))
    fig.text(0.08, 0.035, "Synthetic demonstration - not production performance", fontsize=11, color=SLATE)
    fig.subplots_adjust(left=0.08, right=0.96, top=0.82, bottom=0.13)
    svg = OUTPUT / "synthetic_forecast.svg"
    png = OUTPUT / "synthetic_forecast.png"
    fig.savefig(svg, format="svg", facecolor=PAPER)
    fig.savefig(png, format="png", facecolor=PAPER, dpi=100)
    plt.close(fig)
    with Image.open(png) as image:
        clean = image.convert("RGB")
        clean.save(png, optimize=True)
    export = selected[["ds", "yhat", "yhat_lower", "yhat_upper", "row_type", "horizon_day"]].copy()
    export.to_csv(OUTPUT / "synthetic_forecast.csv", index=False)
    return {
        "selected_forecast_rows": len(selected),
        "selected_future_rows": len(future),
        "selected_observations": len(actual),
        "forecast_max_date": future["ds"].max().date().isoformat(),
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    hero()
    architecture()
    lifecycle()
    source = synthetic_source()
    config = ProjectConfig.from_yaml(ROOT / "conf/base.yml", ROOT / "conf/dev.yml")
    np.random.seed(SEED)
    result = run_collection(source, config, CUTOFF.date().isoformat())
    chart_stats = forecast_chart(source, result.forecasts)
    digest = hashlib.sha256((OUTPUT / "synthetic_forecast.csv").read_bytes()).hexdigest()
    manifest = {
        "schema_version": 1,
        "generated_with": "tools/generate_portfolio_assets.py",
        "seed": SEED,
        "cutoff": CUTOFF.date().isoformat(),
        "data_classification": "deterministic synthetic demonstration",
        "collection": {
            "source_rows": len(source),
            "series": int(
                source[["Business_Category_001", "Business_Category_002", "Language"]].drop_duplicates().shape[0]
            ),
            "targets": 2,
            "completed_fits": int((result.statuses["status"] == "completed").sum()),
            "failed_fits": int((result.statuses["status"] == "failed").sum()),
            "forecast_rows": len(result.forecasts),
            "backtest_rows": len(result.performance),
        },
        "chart": chart_stats,
        "forecast_csv_sha256": digest,
        "assets": {
            "hero": {"dimensions": [1600, 560], "formats": ["svg", "png"]},
            "architecture": {"dimensions": [1600, 900], "formats": ["svg", "png"]},
            "lifecycle": {"dimensions": [1600, 600], "formats": ["svg", "png"]},
            "synthetic_forecast": {"dimensions": [1600, 900], "formats": ["svg", "png", "csv"]},
        },
    }
    (OUTPUT / "visual_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["collection"], indent=2))


if __name__ == "__main__":
    main()
