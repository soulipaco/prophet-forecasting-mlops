# Behavioral baseline

## Baseline authority

The sanitized source code is authoritative for current forecasting behavior. The persisted notebook output is retained only as partial evidence because it is inconsistent with current source plus the attached workbook: the output logs one processed series, while a clean evaluation of the current loop keys produces 25.

Exact confidential-data parity is therefore not yet technically possible. The modular implementation now passes deterministic source-equivalent unit tests, a real local Prophet smoke run, and an end-to-end Databricks synthetic run. Numeric parity still requires a fresh top-to-bottom execution of both paths on the same approved anonymized snapshot; the stale saved output is not used as a false golden result.

## Input baseline

- Daily logical grain.
- Series key: `Business_Category_001`, `Business_Category_002`, `Language`.
- One country per current series.
- Two targets: volume (`Business_Category_003`) and KPI (`Business_Category_008`).
- Three regressors: `Business_Category_005`, `Business_Category_004`, `Business_Category_006`.
- Fixed notebook cutoff: `2025-05-01`.
- Forecast horizon: three calendar months, 92 days for that cutoff.
- Current workbook: 21,103 first-sheet rows, 25 series, no duplicate series/date keys.
- Training rows per series: minimum 79, median 590, maximum 847.
- All 25 series contain calendar gaps; daily expansion adds 4,858 rows.
- Clean rows after notebook exclusions: minimum 79, median 585, maximum 847.

## Model baseline

- Prophet growth: logistic.
- Yearly seasonality: enabled.
- Built-in weekly seasonality: enabled.
- Daily seasonality: disabled.
- Changepoint range: 0.9.
- Interval width: 0.8.
- Custom monthly seasonality: period 30.5; Fourier order tuned from integers 5 through 7.
- Custom weekly seasonality: period 7; Fourier order in `{3, 5, 7}`; prior scale in `{0.1, 0.5, 1.0}`.
- Three external regressors plus binary holiday regressor; common regressor mode is additive or multiplicative.
- Native holidays use the series country and window `[0, +1]` day.
- Optuna trials: 50 per target and series.
- Objective: mean Prophet CV RMSE.
- Current CV horizon selection: 23 series use 90 days; 2 use 30 days.

## Persisted-run evidence

The saved output contains:

- One series-processing message and one non-operating-day summary.
- Two best-trial summaries, consistent with one volume and one KPI model.
- Two forecast frames reported as 608 rows by 75 columns.
- Two performance frames reported as 83 rows by 11 columns.
- One completion/save message.
- No serialized exception object.

The two saved chosen-parameter sets are:

| Parameter | Saved volume-side block | Saved KPI-side block |
|---|---:|---:|
| `seasonality_mode` | additive | multiplicative |
| `changepoint_prior_scale` | 0.09 | 0.01 |
| `seasonality_prior_scale` | 10.0 | 5.0 |
| `holidays_prior_scale` | 10.0 | 10.0 |
| `fourier_order` | 6 | 5 |
| `weekly_fourier_order` | 7 | 5 |
| `weekly_prior_scale` | 0.1 | 0.1 |
| `regressor_mode` | multiplicative | additive |

These values are evidence, not a stable golden result: Optuna is unseeded and the saved run's input state cannot be reconstructed.

## Output baseline

The function returns six pandas DataFrames in this order:

1. `Business_Category_003` forecasts.
2. KPI forecasts.
3. `Business_Category_003` Prophet performance metrics.
4. KPI Prophet performance metrics.
5. `Business_Category_003` chosen parameters by series.
6. KPI chosen parameters by series.

Forecast frames include Prophet's standard prediction/component columns plus the three series identifiers. Performance frames are Prophet `performance_metrics` output plus the series identifiers. Parameter frames contain the series identifiers plus the eight tuned parameters.

The notebook's future frame includes history. It does not label fitted versus future rows. Future rows without the primary regressor are removed. Six distinct CSV files are written after all series complete.

## Failure and skip baseline

- Span below 30 days: tuning returns `(None, None, None)` after printing a message. The caller does not branch and fails when it calls the missing model. This is a confirmed source behavior, not an acceptable production policy.
- Trial fit/CV error: the trial prints an error and returns infinity.
- All trials failing: no explicit handling; behavior depends on Optuna's best-trial state.
- Missing required column or duplicate ambiguity: no early contract; pandas/Prophet fails at the use site.
- Missing future primary regressor: affected rows are silently dropped.
- Empty collection: unconditional `pd.concat` fails.
- Any series exception: the entire run stops; no partial status is persisted.

## Parity tolerances

When a clean source run is available in the target environment:

- Dates, series identifiers, row counts, selected categorical parameters, and output column order: exact equality.
- Floating forecasts, bounds, and metrics under identical package versions and seeds: `rtol=1e-6`, `atol=1e-8` initially; relax only with documented evidence of Stan/platform variation.
- Unseeded source runs: compare schema, dates, row counts, parameter membership in the source search space, and metric/forecast distributions; do not claim exact numeric parity.
- Serialized model metadata: exact growth/seasonality/regressor/interval configuration and library versions; fit timestamps and generated IDs excluded.

## Synthetic fixture specification

`tests/fixtures/synthetic_series_spec.json` defines deterministic cases without confidential records:

- A regular series with omitted weekends so daily expansion creates non-operating-day candidates.
- A series with periodic calendar gaps and complete planned future regressors.
- A short-history series that exercises the source's below-30-day behavior.
- A constant-target variant and missing-regressor variant for newly introduced validation behavior.

The implementation will materialize rows from this compact specification in test code. It must never sample or copy confidential workbook records.

## Baseline completion condition

Before refactoring is declared behaviorally equivalent, run the original source-equivalent harness and modular package against the same generated fixture in the same locked environment. Persist a machine-readable comparison containing input hash, configuration hash, package versions, folds, parameters, schemas, dates, row counts, metrics, and tolerance results.
