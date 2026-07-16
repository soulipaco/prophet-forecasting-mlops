# Notebook-to-project traceability

This table maps the sanitized notebook to the implemented package. The workspace root was adopted as the target after the user authorized building the project directly.

| Notebook section | Current responsibility | Planned implementation | Required verification | Status |
|---|---|---|---|---|
| Cell 2: imports, timing, warning suppression | Environment setup and Excel load | `config.py`, `contracts.py`, `databricks_io.py`, thin entry point | Dependency lock, source snapshot/version, no global warning suppression | Implemented; Delta source replaces local Excel at the IO boundary |
| Cell 5: `get_holidays` | Country holiday dictionary for requested years | `calendars.py::holiday_frame` | Country/year parity and invalid-country behavior | Implemented and exercised by smoke run |
| Cell 6: `process_language_data` | Per-language daily expansion, identifier restoration, zero-fill volume | `preprocessing.py::expand_daily_series` | Exact dates, inserted rows, zero/null rules, column order | Implemented; unit tested |
| Cell 7: `find_non_operating_days` | Infer weekdays with >=90% zero-volume/null-auxiliary occurrences | `preprocessing.py::infer_non_operating_weekdays` | Threshold and weekday behavior | Implemented; unit tested |
| Cell 8: CV span logic | Choose initial/period/horizon strings | `splitting.py::source_cv_window` | Boundary and insufficient-history behavior | Implemented; unit tested |
| Cell 8: Optuna objective | Build model, fit, rolling CV, mean RMSE, infinity on failure | `prophet_model.py`, `evaluation.py` | Search-space, model configuration, failure recording, RMSE | Implemented; local and Databricks Prophet smoke tested |
| Cell 8: final fit and CV | Rebuild chosen model, refit, calculate performance table | `prophet_model.py::tune_and_fit` | No builder drift between trial/final; schema and numeric tolerance | Implemented; Databricks output verified |
| Cell 11: cutoff and three-month period | Split source; calculate calendar-month horizon | `splitting.py`, `config.py` | Exact cutoff semantics and month-length totals | Implemented; unit tested |
| Cell 11: series enumeration | Distinct business-dimension/KPI/language loop | `orchestration.py::run_collection` | Exact current keys, deterministic ordering, neutral aliases | Implemented |
| Cell 11: training preparation | Expansion, non-operating detection, exclusions | `preprocessing.py`, `calendars.py` | Current workbook aggregate counts and fixture behavior | Implemented; aggregate baseline retained |
| Cell 11: holidays and holiday regressor | Native holiday table and binary regressor | `calendars.py`, `orchestration.py` | Holiday dates, country isolation, duplicate holiday effect retained in parity | Implemented; exercised in local and Databricks smoke runs |
| Cell 11: volume frame | Rename volume target, derive cap/floor, tune | `orchestration.py::_model_frame`, `preprocessing.py::logistic_bounds` | Positive-floor rule, regressors, logistic bounds, parameter selection | Implemented |
| Cell 11: KPI frame | Rename KPI target, derive cap/floor using positive-volume mask, tune | Same generic target-frame path | KPI-specific floor parity | Implemented; source behavior preserved |
| Cell 11: future volume/KPI frames | Include history, add horizon, remove excluded/non-operating dates, merge known-future regressors, drop missing primary regressor | `forecasting.py::build_future_frame` | Date/row equality, incomplete-regressor parity, explicit completeness status | Documented; fixture specified |
| Cell 11: predictions and identifiers | Predict point/components/bounds; attach series keys | `orchestration.py::select_forecast_output` | Stable schema, identifiers, dates, bounds | Implemented; unit and Databricks schema tested |
| Cell 11: performance/parameter collection | Append per-series CV metrics and chosen params | `evaluation.py`, `orchestration.py`, `tracking.py` | Row counts, keys and parameter values | Implemented; Delta and MLflow persistence |
| Cell 11: six CSV writes | Persist forecasts, performance, parameters | `databricks_io.py` managed Delta tables | Logical outputs, run idempotency and lineage | Implemented as forecast, backtest, parameter, status and manifest tables; CSV excluded |
| Cell 12: fixed invocation | Run with cutoff and output path | `scripts/run_forecasting.py` and DAB parameters | Arguments, run/config hashes, no source path in code | Implemented and deployed to dev |
| Persisted cell 12 output | Partial one-series evidence | `docs/behavioral_baseline.md` only | Fresh clean run required; do not force-match stale state | Captured as non-authoritative evidence |

## Planned change traceability

The following additions have no notebook equivalent and must remain separately testable and reversible:

- Data contracts and neutral reason codes.
- Seasonal-naive baseline and horizon-bucket metrics.
- Interval coverage and width monitoring.
- Per-series status and resumable/idempotent execution.
- MLflow/Delta/code/config lineage.
- Collection-level artifact manifest and optional collection registration.
- Asset Bundle, CI/CD, environment overlays, and secret management.
- Explicit fitted/future row typing and production completeness policies.

None of these additions may silently alter the parity view of notebook calculations.
