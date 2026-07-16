# Visual identity

The visual system is built for GitHub light/dark contexts and mobile LinkedIn viewing.

## Palette

| Token | Hex | Use |
|---|---|---|
| Ink | `#0B1220` | dark fields, primary text |
| Blue | `#2563EB` | forecast line, process emphasis |
| Orange | `#F97316` | cutoff and decision points |
| Teal | `#14B8A6` | boundaries, start/end state |
| Paper | `#F8FAFC` | light canvas |
| Slate | `#475569` | supporting text |
| Muted | `#94A3B8` | secondary text on dark fields |

Typography uses DejaVu Sans in generated repository assets and an Inter-like sans-serif hierarchy in
the presentation. Headings are compact and bold; monospace is reserved for identifiers and commands.

## Chart contract

Forecast charts must show observed values, fitted values, the future point forecast, the configured
80% prediction interval, and the forecast cutoff. Blue is reserved for the future forecast, orange
for the cutoff, and neutrals for history. Every public performance-looking chart must state that it
uses synthetic data and is not production performance.

## Asset registry

| Asset | Purpose | Size |
|---|---|---:|
| `assets/portfolio/hero.svg` | README/social visual anchor | 1600 x 560 |
| `assets/portfolio/architecture.svg` | implemented boundary and responsibilities | 1600 x 900 |
| `assets/portfolio/lifecycle.svg` | batch execution sequence | 1600 x 600 |
| `assets/portfolio/synthetic_forecast.svg` | repository-generated forecasting evidence | 1600 x 900 |

PNG counterparts support previews that do not render SVG. The source CSV and visual manifest make
the synthetic evidence reproducible. All assets are regenerated with
`uv run --extra portfolio python tools/generate_portfolio_assets.py`.
