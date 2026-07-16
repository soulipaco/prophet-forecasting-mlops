# Claims traceability

Repository baseline: `fa663329f9f3cf5b4904a54a1e135d6d8efc480d`. Local evidence was
reproduced on 2026-07-17; the generated visual manifest retains its 2026-07-16 project cutoff context.

| Claim | Source / command | Exact supporting evidence | Status | Date / commit | Owner confirmation | Approved public wording |
|---|---|---|---|---|---|---|
| Multi-series, two-target collection | `orchestration.py::run_collection`; `conf/base.yml` | Loops distinct configured series keys and the `volume` and `kpi` targets | Direct | 2026-07-17 / baseline | No | Coordinates every distinct input series with two configured targets. |
| Optuna tuning | `prophet_model.py::tune_and_fit` | Creates a seeded TPE study and calls `study.optimize` before the final fit | Direct | 2026-07-17 / baseline | No | Searches Prophet parameters with Optuna. |
| Adaptive time-aware CV | `splitting.py::source_cv_window`; `prophet_model.py` | CV initial, period, and horizon derive from history length and are passed to Prophet diagnostics | Direct | 2026-07-17 / baseline | No | Uses adaptive, time-aware Prophet cross-validation. |
| Logistic growth | `prophet_model.py::build_model`; `preprocessing.py::logistic_bounds` | Model growth is logistic and model frames carry computed `cap` and `floor` | Direct | 2026-07-17 / baseline | No | Fits Prophet with logistic growth and per-series bounds. |
| Custom seasonalities | `prophet_model.py::build_model` | Adds monthly period 30.5 and weekly period 7 with searched Fourier settings | Direct | 2026-07-17 / baseline | No | Combines built-in and custom monthly/weekly seasonalities. |
| Holidays and regressors | `calendars.py`; `prophet_model.py`; `orchestration.py::_model_frame` | Country holiday frame, binary holiday regressor, and three configured external regressors feed the model | Direct | 2026-07-17 / baseline | No | Supports country holidays, a holiday flag, and three future regressors. |
| Three-calendar-month horizon and 80% interval | `conf/base.yml`; `splitting.py::calendar_month_horizon`; `prophet_model.py` | `forecast_months: 3`; horizon uses calendar boundaries; Prophet interval width is 0.8 | Direct | 2026-07-17 / baseline | No | Produces a three-calendar-month forecast with an 80% interval. |
| MLflow collection tracking | `tracking.py::log_collection_run`; `scripts/run_forecasting.py` | One run logs tags, configuration/source metadata, counts, metrics, and selected-parameter artifact | Direct | 2026-07-17 / baseline | No | Captures collection-level lineage in one MLflow run. |
| Delta persistence | `databricks_io.py`; `scripts/run_forecasting.py` | Creates/reads managed tables and writes forecast, backtest, parameter, status, and manifest frames | Direct | 2026-07-17 / baseline | No | Persists stable batch outputs to managed Delta tables. |
| Run-idempotent writes | `databricks_io.py::write_run_frame` | Deletes the target rows for the same `run_id` before append | Direct | 2026-07-17 / baseline | No | Retries are idempotent at logical `run_id` scope. |
| Environment separation | `databricks.yml`; `conf/dev.yml`; `conf/acc.yml`; `conf/prd.yml` | Bundle targets and configuration overlays exist for dev, acc, and prd | Direct | 2026-07-17 / baseline | No | Configured for dev, acc, and prd environments. |
| Two-task serverless job | `resources/forecasting_job.yml` | Synthetic bootstrap task is an explicit dependency of train-and-forecast; both use the bundle environment | Direct | 2026-07-17 / baseline | No | The Asset Bundle defines a two-task batch demonstration job. |
| CI quality gates | `.github/workflows/ci.yml` | CI syncs, lints, checks format, runs non-Databricks tests, validates portfolio assets, and builds | Direct | 2026-07-17 / working tree | No | CI checks code quality, tests, portfolio integrity, and packaging. |
| Ten passing local tests | `uv run pytest -m "not databricks"` | Terminal result: `10 passed in 4.01s` | Reproduced | 2026-07-17 / working tree | No | The local non-Databricks suite has 10 passing tests. |
| Synthetic model/output counts | `tools/generate_portfolio_assets.py`; `assets/portfolio/visual_manifest.json` | Two repeated executions returned 4 completed, 0 failed, 832 forecast, and 84 backtest rows | Reproduced | 2026-07-17 / working tree | No | The deterministic synthetic demo executes 4 fits and emits 832 forecast plus 84 backtest rows. |
| Bundle configuration | `databricks.yml`; `resources/forecasting_job.yml` | Resources exist and previously validated; current recheck stopped at authentication | Direct + external limit | 2026-07-17 / working tree | Only for “deployed” | Deployment-ready/configured; do not say currently deployed without a fresh external check. |
| Production orientation | Package boundaries, lock, CI, contracts, lineage, idempotence, bundle resources | Engineering controls are implemented, but production ingestion, schedule, monitoring, and promotion are absent | Inference | 2026-07-17 / working tree | No | Production-oriented batch forecasting reference. Do not use “production-proven.” |

Claims about current deployment or a successful cloud run are excluded from the primary README
scorecard because they are mutable external state. Owner confirmation plus fresh platform evidence is
required before using “deployed” in a time-sensitive post.

