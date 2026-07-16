# LinkedIn copy package

## Main post

I built a Prophet forecasting project to answer a question that single-model demos usually skip:
what does it take to run a whole collection of time series repeatedly and inspect the result?

I started from an ordered forecasting workflow whose behavior was easier to execute end to end than
to test as components. I preserved the forecasting mathematics while separating configuration,
contracts, preprocessing, model construction, cross-validation, orchestration, and persistence into
reviewable boundaries.

The package discovers the series in its input, fits two configured targets for each series, tunes
with Optuna using time-aware Prophet cross-validation, and produces a three-calendar-month forecast
with an 80% interval.

The architecture keeps forecasting behavior in ordinary Python. Databricks is the delivery boundary
for Spark/Delta IO, one collection-level MLflow run, and an Asset Bundle job with dev, acc, and prd
targets.

I also made the public evidence reproducible. The checked-in deterministic synthetic demo executes
2 series x 2 targets: 4 completed fits, 0 failures, 832 forecast rows, and 84 backtest rows. Those
figures demonstrate execution and output contracts—not production accuracy or business impact.

The design choices I care about most:

- batch tables instead of an unsupported online-serving layer;
- one bounded collection run instead of a registry entry per fit;
- time-aware evaluation instead of random splits;
- stable output contracts and run-idempotent retries;
- explicit exclusions where the code has no consumer or policy yet.

The README, architecture, synthetic chart, and claims traceability table are all in the repository:
https://github.com/soulipaco/prophet-forecasting-mlops

I would be interested in how you would evolve the acceptance gates or monitoring layer once real
operating thresholds and ownership are available.

My main lesson: MLOps maturity is less about adding every platform feature and more about making the
right batch behavior reproducible, observable, and explicit about its limits.


## Short post

I built an inspectable Prophet batch-forecasting collection: ordinary Python for validation,
preprocessing, Optuna tuning, time-aware CV, fitting, and contracts; Databricks for Delta IO, MLflow
lineage, and job delivery.

The deterministic synthetic run executes 2 series x 2 targets with 4 completed fits, 0 failures,
832 forecast rows, and 84 backtest rows. Execution evidence only—not a production-performance claim.

Repo: https://github.com/soulipaco/prophet-forecasting-mlops

## LinkedIn Featured summary

An evidence-backed batch forecasting MLOps project using Prophet, Optuna, MLflow, Delta, and
Databricks Asset Bundles. Demonstrates coordinated series-by-target fitting, time-aware evaluation,
stable output contracts, idempotent persistence, reproducible synthetic evidence, and deliberate
scope decisions.

## CV entry

**Prophet Forecasting MLOps — portfolio project**

- Engineered a packaged batch forecasting collection that coordinates arbitrary input series across
  two targets using Prophet, Optuna tuning, adaptive time-aware cross-validation, and stable forecast
  contracts.
- Separated testable Python forecasting logic from Spark/Delta IO, collection-level MLflow lineage,
  and Databricks Asset Bundle job delivery.
- Added locked dependencies, Pydantic environment overlays, idempotent run-scoped writes, pytest,
  Ruff, CI, and deterministic synthetic execution evidence.

## Repository metadata

Suggested description:

> Inspectable batch Prophet forecasting with Optuna, MLflow, Delta, and Databricks Asset Bundles.

Suggested topics:

`forecasting`, `time-series`, `prophet`, `mlops`, `databricks`, `mlflow`, `optuna`, `delta-lake`,
`databricks-asset-bundles`, `python`

## Hashtags

`#MLOps` `#TimeSeries` `#Forecasting` `#Databricks` `#MLflow` `#Python` `#Prophet`

## Alt text

### Main image

Dark navy banner reading “Forecast collections, engineered for repeatable runs.” A blue forecast
wave crosses an orange boundary beside “Batch, N x 2 series x targets.”

### README hero

Dark navy project banner with a blue oscillating forecast line and orange cutoff. Text highlights
Optuna tuning, time-aware cross-validation, MLflow lineage, Delta outputs, and the Python/Databricks
boundary.

### Architecture visual

Light architecture diagram. A large ordinary-Python area contains validated configuration, input
contracts, preparation, holiday calendars, series-by-target orchestration, Optuna plus Prophet CV,
final fit, forecast contract, and run evidence. A dark Databricks boundary contains Delta input and
outputs, MLflow, an Asset Bundle job, and three environment targets.

### Forecast visual

Synthetic weekday time series from January through July 2024. Observed and fitted history appears
before a May cutoff; a blue three-month forecast and light-blue 80 percent interval appear after it.
The chart is labeled as synthetic, not production performance.

### Carousel slide 1

Title slide: “Prophet forecasting, engineered for repeatable batch runs,” with a stylized blue and
teal forecast path and Optuna, MLflow, and Delta labels.

### Carousel slide 2

Large “N x 2” graphic explains that every distinct series is paired with two targets, followed by a
validate, tune, fit, forecast, and record sequence.

### Carousel slide 3

Split architecture: ordinary Python contains configuration, contracts, preprocessing, Prophet plus
Optuna, and orchestration; the Databricks edge contains Delta IO, MLflow, the bundle job, and three
environment targets.

### Carousel slide 4

Four-step vertical timeline: prepare daily history, search with Prophet cross-validation, refit the
selected model, then forecast and record outputs.

### Carousel slide 5

Four evidence layers—configuration, source version, code and dependency version, and result
metadata—flow into one MLflow collection run.

### Carousel slide 6

Native line chart shows a synthetic forecast with lower and upper interval bounds from May through
July. Below it: 4 fits, 0 failed, 832 forecast rows, and 84 backtest rows, clearly labeled synthetic.

### Carousel slide 7

Scope comparison: stable Delta contracts, collection lineage, idempotent retries, and environment
overlays are implemented; online serving, a model-per-fit registry, automatic promotion, and
unsupported business impact are deliberately not claimed.

### Carousel slide 8

Closing invitation to inspect and run the repository, with the GitHub project name and a call to read
the architecture, run the synthetic demo, and inspect every claim.
