# Known limitations and unresolved decisions

## Confirmed limitations

- The sanitized notebook's persisted output is stale or partial: it shows one processed series while the current source workbook yields 25. Numeric parity must therefore be established by a clean, approved run of the original and modular paths on the same anonymized snapshot.
- Current automated fixtures validate deterministic structure, edge behavior, and a real Prophet smoke fit; they are not a golden copy of confidential production rows.
- Databricks Free Edition supports serverless compute only and has tighter concurrency/resource limits. The job is deliberately two tasks and uses small dev tuning budgets.
- The dev bootstrap task creates synthetic data. It must not be treated as the production ingestion design.
- MLflow records collection lineage and selected parameters, but fitted Prophet binaries are not registered. Forecast tables are the current operational product; reusable model artifacts should be added only when a consumer is confirmed.
- Post-actual forecast-accuracy monitoring cannot operate until the arrival table and actual-availability lag are known. Backtest metrics and run completeness are available now.

## Decisions that require business or platform evidence

- Production source table and its ownership/SLA.
- Forecast publication consumers and required schema compatibility.
- Retraining cadence and cutoff timezone.
- Target-specific promotion thresholds and acceptable prediction-interval coverage.
- Whether missing future regressors should reject the run or preserve the notebook's partial-row behavior.
- Approval authority for acceptance-to-production promotion.
- Whether collection artifacts must be registered for governance despite batch-table consumption.

Until these are answered, schedules remain disabled, production deployment remains manual, existing mathematics is preserved, and changes are reversible through configuration.
