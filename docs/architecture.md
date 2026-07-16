# Implemented architecture

This document describes the code that exists in this repository. It is not a roadmap.

![Implemented architecture](../assets/portfolio/architecture.svg)

## System boundary

The project is a scheduled-batch forecasting system. Ordinary Python owns configuration,
validation, preprocessing, model construction, tuning, cross-validation, forecast generation,
evaluation helpers, collection orchestration, and run metadata. Databricks owns Spark/Delta IO,
MLflow tracking, and job execution.

The deployable workflow has two serverless tasks:

1. `bootstrap_synthetic_input` creates a deterministic demonstration table.
2. `train_and_forecast` reads the table, executes the collection, and writes result tables.

The task dependency is declared in `resources/forecasting_job.yml`. Environment overlays in
`conf/dev.yml`, `conf/acc.yml`, and `conf/prd.yml` change catalog and tuning settings without
embedding environment values in Python.

## Runtime flow

![Batch lifecycle](../assets/portfolio/lifecycle.svg)

`run_collection` validates the input, enumerates distinct series keys, and runs both configured
targets for every series. Each fit prepares a daily history, constructs holidays and regressors,
derives a time-aware cross-validation window, searches Prophet parameters with Optuna, refits the
selected model, and produces fitted and future rows.

The default horizon is three calendar months. Prophet uses logistic growth, an 80% interval,
yearly and weekly seasonality, custom monthly and weekly seasonalities, country holidays, a binary
holiday regressor, and three configured external regressors.

## Module responsibilities

| Component | Implemented responsibility |
|---|---|
| `config.py` | Pydantic models, invariants, and YAML overlay loading |
| `contracts.py` | Required-column, date, cutoff, and series/date uniqueness checks |
| `preprocessing.py` | Daily expansion, volume-only gap filling, closure inference, bounds |
| `calendars.py` | Country calendar construction for the relevant years |
| `splitting.py` | Adaptive Prophet CV windows and calendar-month horizons |
| `prophet_model.py` | Model builder, Optuna objective, cross-validation, and final fit |
| `evaluation.py` | MAE, RMSE, bias, WAPE, interval coverage, and seasonal-naive helpers |
| `orchestration.py` | Series-by-target execution, statuses, parameters, and output selection |
| `tracking.py` | Configuration hash, run manifest, and collection-level MLflow logging |
| `databricks_io.py` | Spark reads, Delta version lookup, schema/table creation, idempotent writes |

## Data contracts

The input contract is driven by `ProjectConfig`. It requires a date, three series identifiers, a
country, two targets, three regressors, a non-operating signal, and a normal-operation signal.
Names are neutral aliases in the public demonstration configuration.

The forecast table keeps only the stable contract:

- series keys and `target`;
- `ds`, `yhat`, `yhat_lower`, `yhat_upper`, and `trend`;
- `cap` and `floor` for logistic growth;
- `as_of_date`, `row_type`, and `horizon_day`;
- run lineage added by the Databricks entry point.

Other outputs are backtest rows, selected parameters, per-series status, and one run manifest.
`write_run_frame` deletes records for the same `run_id` before appending, making a retry idempotent
at run scope.

## Reproducibility and lineage

- `uv.lock` fixes the resolved Python dependency graph.
- Configuration is versioned and hashed into the run manifest.
- Dev and acceptance tuning use a fixed seed; production has the same fixed seed with more trials.
- The source Delta version, code version, run identifier, cutoff, row counts, and fit counts are
  captured by the entry point and manifest.
- One MLflow run represents the coordinated collection and logs selected parameters as an artifact.

## Deliberate scope

Batch Delta tables are the delivery interface because the repository contains no request-time
consumer. The project does not implement online serving, a model registry, automated promotion,
accuracy/drift monitoring, a production schedule, or continuous deployment. The bootstrap task is
a deterministic demonstration source, not a production ingestion pipeline.

## Failure behavior

The configured policy is `fail_fast`. The orchestration layer still records a status row for a fit
that raises, then re-raises under that policy. Short histories that cannot support the configured
cross-validation geometry are treated as insufficient data. Databricks task retries can safely use
the same run identifier because output writes replace that run's logical records.

