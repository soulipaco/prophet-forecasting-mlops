# Excluded reference-repository features

| Reference feature | Classification | Why excluded from the forecasting target |
|---|---|---|
| Databricks online Model Serving endpoint | Irrelevant | Current consumers are batch CSV/table outputs; no latency-sensitive request contract exists. |
| MLflow PyFunc wrapper returning human-readable class labels | Irrelevant | Forecast output is a multi-row time-series table with point/bounds, not one class label. |
| Request/response payload parsing | Irrelevant | There is no online inference payload stream. |
| Classification Lakehouse Monitor | Forecasting-specific replacement required | F1/class prediction monitoring does not measure forecast residuals, bias, horizons, or interval coverage. |
| F1-based model comparison | Forecasting-specific replacement required | Notebook tuning uses RMSE; production comparison needs time-aware target/horizon metrics and baselines. |
| Random train/test split | Irrelevant | It leaks future information in time series. Rolling-origin splits are required. |
| Hashed-ID online A/B traffic split | Irrelevant | Forecast challengers should be compared on identical historical folds, not live request traffic. |
| One classifier registry entry with `latest-model` alias copied literally | Forecasting-specific replacement required | The run contains 50 related Prophet fits; collection-level governance is more coherent. |
| Classification feature schema and preprocessing | Irrelevant | Marvel character features, category normalization, and LightGBM encodings have no relationship to the workbook. |
| LightGBM classifier and custom wrapper | Irrelevant | Prophet with regressors/logistic growth is the current behavior. |
| Synthetic static-feature drift generator | Forecasting-specific replacement required | Safe fixtures need temporal structure, gaps, future regressors, bounds, holidays, and horizon behavior. |
| Endpoint load-test notebooks and token extraction | Irrelevant and unsafe pattern | No endpoint is proposed; notebook token handling should not be reproduced. |
| Automatic acc/prd matrix deployment on every main push | Reusable only after adaptation | Production must follow acceptance evidence and protected approval sequentially. |
| Git tag creation during PR CI | Excluded | It can collide with existing tags and does not validate forecasting behavior. Tag after successful production deployment. |
| Scripts/notebooks excluded from linting | Excluded | Thin operational scripts are production code and must be checked. |
| Change Data Feed on all input tables | Insufficient evidence | It may help incremental actual reconciliation later, but the smallest release can use snapshot/version lineage. |
| Weekly Monday production schedule copied verbatim | Insufficient evidence | Forecast cadence is not stated in the notebook; schedules remain configurable and paused. |
| Model endpoint deployment condition task | Irrelevant as written | The useful condition-task pattern may gate persistence/promotion, but endpoint deployment is removed. |

## Reference patterns retained or adapted

Excluded features do not invalidate the reference project's useful engineering patterns. The target retains the `src/` package, thin entry points, Pydantic configuration, uv lock, wheel artifact, environment-aware Asset Bundle, task dependencies, MLflow lineage concepts, pytest/coverage, Ruff/pre-commit, GitHub CI, and protected CD after adapting them to forecasting.
