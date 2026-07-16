# Discovery report

## 1. Current forecasting pipeline summary

### Source and scale

The sanitized notebook reads the first sheet of the attached Excel workbook into pandas. The workbook has two sheets; only the first is referenced by the notebook. The first sheet contains 21,103 records and 13 columns with no formulas. Its date coverage spans 1,106 days. After applying the notebook's fixed training cutoff (`2025-05-01`), the data contains 25 distinct series identified by the combination of `Business_Category_001`, `Business_Category_002`, and `Language`. Each series has future rows after the cutoff.

The 25 series represent 4 values of the first business dimension, 10 values of the second business dimension, and 6 languages, but only 25 combinations are present. Each combination has one country. The notebook trains two Prophet models for each combination: one for volume (`Business_Category_003`) and one for a KPI (`Business_Category_008`). A complete run therefore attempts 50 final models plus hyperparameter-search and cross-validation fits.

### Actual workflow

1. Imports a very broad collection of libraries, although the executed forecasting path primarily uses pandas, Prophet, Optuna, holidays, NumPy, matplotlib-related imports, and date utilities.
2. Reads an Excel file from a local absolute path and suppresses all warnings globally.
3. Splits records at a string cutoff date. `df_validation` is created from post-cutoff rows but never used for evaluation.
4. Enumerates series by two business dimensions and language.
5. For each series, expands the historical date range to daily grain. Missing calendar days are inserted; only the volume target is filled with zero. Series identifiers and country are forward-restored as constants, while other fields remain null on inserted days.
6. Detects non-operating weekdays when at least 90% of the estimated weeks in a year have both zero volume and a null auxiliary field on that weekday.
7. Removes zero-volume dates, dates with a missing primary regressor, and all detected non-operating weekdays from training.
8. Builds country holidays for all years from training start through the forecast end. Holidays affect the day itself and the following day (`lower_window=0`, `upper_window=1`). A separate holiday indicator is also included as a regressor.
9. Creates two logistic-growth Prophet datasets with the same holiday and regressor structure. The cap is the observed training maximum. The volume floor is the minimum positive volume; the KPI floor is the minimum KPI value on positive-volume dates.
10. Tunes eight parameters using 50 Optuna trials per target and series: seasonality mode, changepoint prior scale, seasonality prior scale, holiday prior scale, monthly Fourier order, custom weekly Fourier order, custom weekly prior scale, and regressor mode.
11. Uses Prophet rolling cross-validation with an automatically selected horizon based on observed span. In the current workbook, 23 series select a 90-day horizon and 2 select a 30-day horizon. The Optuna objective is mean RMSE.
12. Fits the selected final model and repeats cross-validation to produce Prophet's full performance-metric table.
13. Constructs a three-calendar-month forecast horizon. For the fixed cutoff this is 92 days. Future regressors are left-joined from rows already present in the source workbook, and rows missing the primary future regressor are dropped.
14. Returns and writes six CSV outputs: volume forecasts, KPI forecasts, volume performance, KPI performance, volume parameters, and KPI parameters.

### Data-quality observations

- All 25 current series span at least 30 training days, so the explicit short-history return path is not reached with the attached workbook.
- Training rows per series range from 79 to 847 before calendar expansion; the median is 590.
- Every series has missing calendar dates. Daily expansion adds 4,858 rows across the 25 series.
- Nineteen series imply non-operating weekdays: 10 imply one weekday and 9 imply two; 6 imply none.
- After the notebook's exclusions, clean training rows range from 79 to 847, with a median of 585.
- No current series is constant for either forecast target, no series lacks positive volume, no retained KPI values are null, and no series spans multiple countries.
- There are no duplicate date/series keys in the current workbook.

### Undocumented and implied behavior

- The forecast is operationally batch-oriented. The code writes multi-series CSV tables and has no request/response contract or latency-sensitive path.
- Future forecasts depend on planned future regressor rows already existing in the input workbook. The notebook cannot forecast all horizon dates when those regressors are absent; it silently drops those rows.
- The three-month horizon is calendar-month-based, not a fixed 90 days.
- The non-operating-day rule is inferred separately for every series and uses `number_of_distinct_dates // 7` as the expected week count.
- The built-in Prophet weekly seasonality remains enabled while an additional custom weekly seasonality is added. This may be intentional but is not documented.
- Holidays are represented twice: as Prophet holidays and as a binary external regressor.
- `Business_Category_007` is read into an unused local variable.
- The post-cutoff validation slice is created but never used.
- Results include in-sample prediction rows because `make_future_dataframe` includes history.

### Hidden state, duplication, and testability problems

- Notebook execution counts are non-sequential. Comment-only cells were executed before the final function definitions and invocation, so the saved kernel state cannot be reconstructed from top-to-bottom source alone.
- Persisted output reports one processed series, two best-trial summaries, two 608-by-75 forecast tables, and two 83-by-11 performance tables. Current source plus the attached workbook yields 25 series. The saved output is therefore not a trustworthy golden baseline for the current source state.
- Model construction is duplicated between trial evaluation and final fit, and target-specific volume/KPI preparation and prediction are largely duplicated.
- The short-history function returns `(None, None, None)`, but its caller immediately invokes methods on the returned model. The intended skip/fail behavior is undefined.
- A failed Optuna trial returns infinity, but an all-failed study is not handled explicitly.
- Empty result lists are concatenated unconditionally, causing a secondary failure that can obscure the original cause.
- Six output filenames, the source path, cutoff, trial count, horizon rule, threshold, seasonality settings, regressors, and output directory are hard-coded.
- Global warning suppression can hide Prophet convergence, numerical, and deprecation warnings.
- The core function combines data validation, preprocessing, calendar construction, tuning, fitting, evaluation, prediction, persistence, and logging, so it cannot be tested in isolation.
- The notebook relies on local files and pandas, not Databricks tables or Unity Catalog lineage. It contains no MLflow tracking, model artifacts, run manifest, idempotency key, retry semantics, or structured failure record.

## 2. Reference repository architecture summary

The reference repository is an educational classification project, not a forecasting template. Its important components work together as follows:

- `pyproject.toml`, `uv.lock`, and `version.txt` define a Python 3.12 package, pinned runtime dependencies, development/test extras, wheel building, pytest coverage, and Ruff rules. This is a useful packaging baseline, although the declared package include contains a stray unrelated pattern and some imported packages are only transitively available.
- `src/marvel_characters/config.py` uses Pydantic to validate a YAML configuration and injects environment-specific catalog/schema values. It also defines lineage tags. The separation is useful; the concrete feature lists, classifier parameters, and experiment names are not.
- `src/marvel_characters/data_processor.py` owns pandas preprocessing and Spark/Delta persistence. It separates reusable transformation logic from scripts, but combines pure pandas behavior with Spark side effects in one class.
- `src/marvel_characters/models/basic_model.py` loads versioned Delta tables, prepares a scikit-learn/LightGBM pipeline, trains, logs MLflow datasets and model signatures, evaluates a classifier, compares F1 against an aliased registered model, and registers a new version. The lineage and artifact concepts are relevant; random splitting, classification evaluation, and one-model promotion logic are not directly reusable.
- `src/marvel_characters/models/custom_model.py` wraps the classifier as an MLflow PyFunc with human-readable online predictions. This exists to support serving and is not relevant to a scheduled forecast table.
- `src/marvel_characters/serving/model_serving.py` deploys or updates a Databricks Model Serving endpoint using a registered-model alias. This is an online classification concern.
- `src/marvel_characters/monitoring.py` parses serving request/response payloads into a Delta inference table and creates a classification Lakehouse Monitor. Its use of managed tables and scheduled refresh is informative, but the schema, cadence, prediction monitor, and problem type must be replaced for forecasting.
- `scripts/` provides thin Databricks entry points for preprocessing, training/registration, endpoint deployment, and monitor refresh. This is a strong responsibility pattern, though several scripts still contain duplicated or hard-coded naming.
- `resources/model_deployment.yml` defines a Databricks Asset Bundle job with preprocessing, training, a condition task driven by task values, and deployment. `resources/bundle_monitoring.yml` defines a separate refresh job. Job dependencies and wheel installation are reusable patterns.
- `databricks.yml` builds the wheel and defines `dev`, `acc`, and `prd` targets with environment-specific roots and a paused schedule variable. The environment boundary is useful, but hosts/profiles are placeholders and production is paused.
- `.github/workflows/ci.yml` installs with uv, runs pre-commit, and runs pytest on pull requests. `.github/workflows/cd.yml` deploys Asset Bundles to acceptance and production on main and tags production. The mechanics are useful; parallel acceptance/production deployment without an evidence-based promotion gate should not be copied.
- `.pre-commit-config.yaml` checks file integrity, secrets, Ruff lint, and formatting, but explicitly excludes notebooks and scripts, leaving operational entry points unchecked.
- `tests/` covers some preprocessing and synthetic-data behavior. Coverage is narrow: the catalog-write test mocks the method under test, model training/promotion/serving/monitoring are untested, and time-aware leakage is irrelevant to the reference classifier.
- `notebooks/` are lecture/demo drivers for preprocessing, MLflow, registration, A/B serving, endpoint load testing, and monitoring. Production scripts call package code, which is a useful pattern. The notebooks themselves include mutable state, locally obtained tokens, and duplicated demonstrations and should not be treated as production orchestration.

Notable reference risks include first-run failure when no registered-model alias exists, loss of `job_run_id` because it does not match the `Tags` model field, a constant endpoint name overriding the environment-specific name, a production deployment matrix with no acceptance dependency, scripts excluded from Ruff, and tests that do not meaningfully verify persistence.

## 3. Capability matrix

| Capability | Reference implementation | Current notebook implementation | Relevance to forecasting | Reuse directly | Adapt | Exclude | Evidence | Reasoning |
|---|---|---|---|---|---|---|---|---|
| Packaged source layout | `src/` package plus thin scripts | One stateful notebook | High | Yes, pattern |  |  | Reference `pyproject.toml`, `src/`, `scripts/`; notebook cells 5-12 | Pure forecasting logic should be importable and testable. |
| Locked dependencies | uv lock and pinned core packages | Environment implied by imports | High |  | Yes |  | `uv.lock`; notebook imports Prophet/Optuna/holidays | Reuse uv, but choose forecasting dependencies and a Databricks-compatible Python version. |
| Structured configuration | Pydantic over environment-aware YAML | Hard-coded cutoff, trials, paths, horizon, regressors | High |  | Yes |  | `config.py`; notebook cells 8, 11, 12 | Forecast contracts and tuning settings require validation; classification features must be replaced. |
| Wheel build | Asset Bundle wheel artifact | None | High | Yes, pattern |  |  | `databricks.yml` | Appropriate for installing reusable modules in Databricks jobs. |
| Databricks Asset Bundle | Multi-target bundle and task graph | None | High if Databricks is production runtime |  | Yes |  | `databricks.yml`, `resources/*.yml` | Keep wheel/tasks/targets; replace serving flow with batch ingest/train/forecast/persist/monitor tasks. |
| Delta/Unity Catalog data storage | Train/test Delta tables with version lookup | Excel input and CSV outputs | High |  | Yes |  | `DataProcessor.save_to_catalog`, `BasicModel.load_data` | Managed versioned tables suit lineage and idempotent batch output, but schemas and partitions are forecasting-specific. |
| Dataset lineage | MLflow `from_spark` with Delta version | None | High |  | Yes |  | `BasicModel.log_model` | Log source table/version or snapshot ID, cutoff, and series coverage for every run. |
| Experiment tracking | MLflow params, metrics, tags, artifacts | Optuna and metrics only in memory/stdout | High |  | Yes |  | reference MLflow code; notebook cell 8 | Use one parent run per forecast execution and nested/structured series records; avoid uncontrolled run explosion. |
| Model registry and aliases | One classifier model, `latest-model` alias | No registration; in-memory models only | Medium |  | Forecasting-specific replacement |  | `BasicModel.register_model`; 25 series x 2 targets | A model collection or artifact manifest is more manageable than independent promotion of every fit. Registry is optional until a downstream model-loading need is confirmed. |
| Promotion logic | Current F1 >= aliased model F1 | Best Optuna RMSE within each run; no champion comparison | High |  | Forecasting-specific replacement |  | `model_improved`; notebook Optuna objective | Promotion must use rolling-origin, target/horizon-specific metrics, interval coverage, and baselines. |
| Online model serving | Databricks serving endpoint and PyFunc wrapper | CSV batch forecasts | Low |  |  | Yes | `serving/`, deployment notebooks; notebook CSV outputs | No evidence of online consumers or latency requirements. Scheduled batch tables are the appropriate initial interface. |
| Batch orchestration | Preprocess/train/deploy job | Single function invocation | High |  | Yes |  | `resources/model_deployment.yml`; notebook cell 12 | Replace endpoint deployment with validation, backtest/train, forecast, persist, and monitoring tasks. |
| Classification A/B testing | Traffic split by hashed ID | None | None |  |  | Yes | `lecture6.ab_testing.py` | Online traffic allocation does not map to time-series forecast promotion. Use backtesting/challenger comparison instead. |
| Monitoring | Serving-payload classification monitor | None | High, but different |  | Forecasting-specific replacement |  | `monitoring.py` | Monitor data freshness/completeness, residual accuracy after actuals arrive, bias, interval coverage, and failed series—not request payloads. |
| Tests | Preprocessing unit tests and Spark mocks | None | High |  | Yes |  | `tests/`; notebook edge paths | Retain pytest structure but add time-aware, leakage, parity, schema, failure, and Databricks integration layers. |
| Lint/format/pre-commit | Ruff and basic pre-commit checks | None | High |  | Yes |  | `.pre-commit-config.yaml`, Ruff config | Include scripts and package; do not repeat the reference exclusion of production entry points. |
| CI | uv, pre-commit, pytest on PR | None | High |  | Yes |  | `.github/workflows/ci.yml` | Add deterministic local tests and a separate optional Databricks integration stage. |
| CD | Bundle deploy to acc/prd and git tag | None | Medium |  | Yes |  | `.github/workflows/cd.yml` | Require sequential validation/promotion and environment protection; cadence and production authority remain open. |
| Versioning | Static version file and git tag | None | Medium |  | Yes |  | `version.txt`, CD workflow | Package/version/run metadata are useful; do not create a tag during PR CI. |
| Logging | Loguru in package/scripts | `print`, warnings suppressed | High |  | Yes |  | reference logger usage; notebook prints | Use structured run/series context and preserve warnings as captured diagnostics. |
| Secrets | GitHub secrets/service principal; notebooks also obtain tokens | No explicit credentials found; local paths present | High |  | Yes |  | CD workflow and lecture notebooks; anonymization scan | Use Databricks/GitHub secret stores and workload identity; never notebook-extracted tokens or committed `.env` values. |
| Change Data Feed | Enabled on reference train/test tables | None | Insufficient evidence |  |  |  | `enable_change_data_feed` | Useful only if incremental actual/forecast reconciliation is selected; not required for the smallest first release. |
| Synthetic data | Distribution sampling for classification | None | High for confidentiality-safe tests |  | Forecasting-specific replacement |  | reference generator; confidentiality gate | Generate deterministic daily series with gaps, regressors, holidays, bounds, and short-history cases rather than sampling confidential distributions. |

Classification summary: packaged source, wheel building, and the broad CI pattern are directly reusable. Configuration, dependency locking, Asset Bundles, Delta lineage, MLflow, task graphs, monitoring, tests, CI/CD, and logging are reusable after adaptation. Promotion, registry granularity, monitoring, fixtures, and evaluation require forecasting-specific replacements. Online serving, PyFunc label wrapping, traffic A/B testing, classifier metrics, and classifier schemas are irrelevant. Change Data Feed and automatic production cadence have insufficient evidence.

## 4. Current risks and technical debt

1. Saved-output/source mismatch prevents exact reproducibility and indicates hidden notebook state.
2. The current code has no data contract and can fail late on missing columns, duplicates, invalid dates, null targets, missing future regressors, or non-positive values.
3. Short-history and all-failed-trial behavior is internally inconsistent and can cause secondary exceptions.
4. A single series failure stops the entire run; no durable per-series status exists.
5. Optuna has no seed and Prophet execution uses process parallelism, so results and resource use are not controlled.
6. Fifty trials, Prophet cross-validation inside every trial, and two targets across 25 series imply expensive repeated fitting without budget controls or cached splits.
7. The fixed post-cutoff validation data is ignored, so there is no true holdout result despite future actuals being present.
8. Only mean RMSE drives tuning; no baseline, horizon segmentation, interval coverage, business weighting, or target-specific metric policy exists.
9. Logistic cap/floor values are derived from each training slice without explicit validation of all bounds.
10. Forecast output mixes historical fitted values and future forecasts without an explicit row type.
11. Output CSV writes are not atomic, versioned, partitioned, or idempotent.
12. No model/dataset/config/code lineage is persisted.
13. Warnings and errors are printed or suppressed rather than recorded structurally.
14. Broad unused imports make environment resolution slow and fragile.

## 5. Confidentiality findings

The original notebook contained sensitive paths, non-technical identifiers/labels, messages, outputs, and metadata-bearing execution state. The sanitized notebook removes all 14 output objects, clears execution counts and cell metadata, minimizes notebook metadata, neutralizes markdown and comments, replaces paths and business identifiers consistently, and preserves technical Prophet/Optuna control strings. The independent decoded-field scan passed with zero residual findings. See `docs/anonymization_report.md` for counts and residual-risk language.

The original notebook and workbook remain confidential inputs and must not be committed or copied into the target repository. The private alias mapping remains outside the workspace in the operating-system temporary directory.

## 6. Behavior that must be preserved

- Daily grain and the three-field series key.
- Two forecast targets per series.
- Calendar expansion and zero-fill of volume only.
- Existing non-operating-weekday detection and 90% threshold in parity mode.
- Exclusion of zero volume, missing primary regressor, and non-operating weekdays.
- Country holiday generation, day-plus-following-day window, and holiday regressor.
- Logistic growth with observed cap/floor rules.
- Built-in yearly/weekly seasonality plus custom monthly and weekly components.
- The same three external regressors and shared regressor mode.
- Existing Optuna search space, 50 trials, RMSE objective, and cross-validation window rules for the parity baseline.
- Three calendar months of future dates and dependency on supplied future regressors.
- Both point and interval forecasts and the six logical output datasets.
- Current source-order behavior must be the baseline, while the incompatible persisted output is retained only as evidence of state drift.

## 7. Behavior that appears accidental or questionable

- Creating but not using `df_validation`.
- Reading but not using `Business_Category_007`.
- Adding weekly seasonality twice.
- Representing holidays both as native Prophet holidays and a regressor.
- Returning `None` for short series without a caller branch.
- Returning infinity for trial exceptions without preserving failure details.
- Dropping future dates with missing regressors without a completeness result.
- Global warning suppression.
- Unseeded tuning and process-level parallelism.
- Including historical fitted rows in forecast outputs without a row-type field.
- Using one metric averaged across all CV horizons.
- Recomputing final cross-validation after tuning without persisting the folds or cutoff definitions.
- Writing local CSVs and printing confidential series values.

These items must remain unchanged in the first parity implementation unless a test proves the current source behavior and a separately documented change is approved.

## 8. Open questions not answerable from code

1. What target project path should receive the implementation?
2. Which Databricks workspace/cloud and supported runtime/Python version are authoritative?
3. What are the production catalog, schema, source table, and destination table contracts? The neutral names in design documents are placeholders only.
4. What operational cadence and forecast availability SLA are required? A monthly cadence is plausible from the horizon but not proven.
5. Are future regressors guaranteed for every required horizon date, and which team owns them?
6. Which target is bounded by business definition, and are the observed logistic cap/floor rules intentional?
7. Are both native weekly seasonality and `weekly_custom` intentional?
8. Should holidays remain both native events and a binary regressor?
9. How should metrics be weighted across series, targets, and 1-30/31-60/61-92 day horizons?
10. What minimum improvement and guardrails authorize promotion, and must a human approve production?
11. Do any downstream consumers load model artifacts, or do they consume only forecast tables?
12. What retry/skip policy is acceptable for failed or insufficient-data series?
13. What retention periods apply to forecasts, backtests, model artifacts, logs, and source snapshots?
14. Was the persisted one-series notebook output produced from an earlier mutation of `df_raw` or a different notebook state? Current files cannot reconstruct it.

## Forecasting-specific design findings

- **Registry granularity:** 25 series and two targets do not justify 50 independently promoted registered models. The smallest operable unit is one coordinated forecast run containing a manifest and per-series artifacts. If registration is required, register one collection version per run or target family, not one model per series.
- **Individual versus coordinated models:** Prophet still fits individual models, but orchestration, lineage, promotion, and failure reporting should treat them as one coordinated collection.
- **Batch versus online:** Batch is supported by all current evidence; online serving is excluded.
- **Retraining frequency:** insufficient evidence. Expose cadence as deployment configuration and keep production schedules paused until confirmed.
- **Promotion:** compare a challenger collection against the currently approved collection and seasonal-naive baselines on identical rolling-origin folds. Begin with RMSE parity, then add MAE/WAPE or sMAPE by target after business validation. Do not use classifier F1.
- **Horizons:** persist fold cutoff and horizon day; report 1-30, 31-60, and 61-92 day buckets as well as aggregate results.
- **Intervals:** retain 80% intervals and measure empirical coverage and average width after actuals arrive.
- **Storage:** versioned Delta tables for forecast rows, backtest rows, run manifests, and series statuses; MLflow for run metadata and optional serialized model artifacts.
- **Failed series:** record an explicit status and reason. A parity mode should fail fast; a production mode may continue other series only after the new behavior is documented and tested.
- **Monitoring:** source freshness, expected-series coverage, future-regressor completeness, forecast row completeness, post-actual RMSE/MAE/bias/coverage, and repeated failure counts are more relevant than feature drift alone.
