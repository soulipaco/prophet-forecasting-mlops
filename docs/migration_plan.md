# Migration plan

Each stage is independently reviewable and keeps the old source notebook untouched. No stage changes forecasting mathematics until parity evidence exists.

## Execution status

Stages 0-1 are complete. Stages 2-7 have been implemented for the confidentiality-safe synthetic/dev path: package extraction, contracts, Prophet/Optuna flow, Delta persistence, MLflow lineage, tests, CI, Asset Bundle deployment, and Databricks smoke validation all pass. The production-data parity and activation gates remain deliberately open because the saved notebook output is not authoritative and the production source/cadence/promotion thresholds are not yet evidenced. See `known_limitations.md`.

## Stage 0 — Confidentiality gate

Deliverables:

- Sanitized notebook and anonymization report.
- Private alias map outside the repository.
- Repeatable decoded-field second scan.

Exit criteria:

- No persisted outputs, execution counts, sensitive metadata, original high-risk values, or unresolved scan locations.
- All sanitized code cells parse.
- Technical Prophet/Optuna controls remain intact.

Status: complete.

## Stage 1 — Evidence and behavioral inventory

Deliverables:

- Discovery report and capability matrix.
- Anonymized workbook profile.
- Explicit list of behavior to preserve, questionable behavior, and open questions.
- Persisted-output/source mismatch record.

Validation:

- Recompute series/date/cardinality statistics from the attached workbook without emitting raw values.
- Independently inspect the reference package, scripts, resources, tests, notebooks, CI, CD, and dependency files.

Status: complete in the current staging workspace.

## Stage 2 — Behavioral baseline

Deliverables:

- `docs/behavioral_baseline.md`.
- Deterministic synthetic fixture specification with daily data, planned future regressors, calendar gaps, non-operating weekdays, two targets, and explicit edge variants.
- A local harness that executes extracted source-equivalent functions without Databricks.

Validation:

- Record input/output schemas, fold settings, selected parameters, forecast dates/row counts, point/bounds, metrics, and failure outcomes.
- Use tolerances and fixed seeds where the source permits.
- Mark the saved one-series notebook output as non-reproducible rather than forcing a false match.

Review boundary: approve the baseline and documented parity limitations before modular extraction.

## Stage 3 — Package scaffold and contracts

Deliverables:

- Confirmed target directory.
- `pyproject.toml`, lock file, package skeleton, base/environment configs, lint/test configuration, and README bootstrap.
- Pydantic configuration and pure input/output contracts.

Validation:

- Configuration tests for valid/invalid environments and parameter combinations.
- Contract tests for required fields, unique series/date keys, data types, nulls, future-regressor completeness, and invalid logistic bounds.
- Wheel builds locally.

Behavior impact: none; no model code is moved yet.

## Stage 4 — Extract pure preprocessing and calendar behavior

Deliverables:

- Daily expansion, zero-fill, series restoration, non-operating-day inference, exclusions, holiday creation, and cap/floor functions.
- Traceability entries from notebook cells 5-7 and the preparation portions of cell 11.

Validation:

- Golden-frame comparisons against source-equivalent functions on synthetic fixtures.
- Tests for gaps, null regressors, duplicates, no positive volume, constant series, country consistency, and non-operating thresholds.
- No Prophet dependency is required for most tests.

Behavior impact: none in parity mode.

## Stage 5 — Extract model construction, tuning, and splits

Deliverables:

- One Prophet builder used for trials and final fitting.
- Existing adaptive CV-window function and Optuna search space.
- Structured trial-failure capture.

Validation:

- Exact parameter and seasonality/regressor configuration assertions.
- Fold/cutoff tests with no future leakage.
- Source-equivalent behavior for spans below 30, 30-59, 60-364, 365-729, and 730+ days.
- A parity-mode test confirms the current short-history failure; a proposed status-based behavior is tested separately and remains disabled.

Behavior impact: none in parity mode; deterministic seeding is not activated until characterized.

## Stage 6 — Extract forecasting and six logical outputs

Deliverables:

- Future-frame/regressor join, prediction, output schema, and collection orchestration.
- In-memory outputs corresponding to the six notebook CSVs.
- Explicit historical/future row type added only in the extended schema while a parity view preserves existing columns.

Validation:

- Forecast dates, row counts, schemas, point/bounds, parameter frames, and performance frames compared with the source harness.
- Missing future regressors and empty result sets tested under parity and proposed production policies.

Review boundary: approve parity before changing failure policy, seeding, metrics, or output schema.

## Stage 7 — Add evaluation and promotion evidence

Deliverables:

- Seasonal-naive baseline, horizon buckets, MAE/RMSE/bias, interval coverage/width, and target-specific metric hooks.
- Challenger-versus-approved collection comparison report.

Validation:

- Metric unit tests including zeros and bounded targets.
- Identical fold definitions across candidates and baselines.
- Promotion policy dry run with no registry alias mutation.

Behavior impact: additive metrics only; RMSE parity remains available.

## Stage 8 — Databricks IO, MLflow, and persistence

Deliverables:

- Source snapshot loader, Delta writers, run/series manifests, MLflow parent run, dataset lineage, and optional model collection artifacts.
- Idempotent rerun behavior.

Validation:

- Local tests use adapters/mocks only at the Databricks boundary.
- Protected Databricks tests verify table schema, Delta version capture, MLflow tags/artifacts, duplicate-run handling, and partial-failure statuses.
- No production tables or aliases are mutated during tests.

Behavior impact: storage changes from local files to managed tables; parity CSV export may remain a temporary compatibility option.

## Stage 9 — Asset Bundle and CI/CD

Deliverables:

- Wheel artifact, DAB targets/resources, paused job schedule, CI workflow, and protected sequential CD workflow.
- Local and Databricks validation commands in README.

Validation:

- `databricks bundle validate` for each target.
- CI runs lint, format, secret checks, unit/parity/integration tests, wheel build, and bundle validation.
- Acceptance deployment and smoke test succeed before production approval.

Behavior impact: none until a schedule is unpaused or a deployment is invoked.

## Stage 10 — Forecast monitoring and controlled activation

Deliverables:

- Freshness/completeness/run monitors and forecast-versus-actual reconciliation.
- Alert thresholds and retraining recommendation logic.
- Runbook for partial failures, rollback, and reprocessing.

Validation:

- Backfilled synthetic forecasts/actuals exercise degradation, bias, under-coverage, missing series, and missing regressor alerts.
- First production run is manual and compared against the notebook/source-equivalent output before scheduling.

Activation decision:

- Confirm cadence, SLA, promotion authority, table retention, and downstream consumers.
- Unpause production only after acceptance evidence and human approval.

## Reversible decision points

- Registration can remain artifact-only or add one collection model later without changing forecast tables.
- Tasks can begin as one compute task and split when runtime/retry evidence justifies it.
- Failure policy defaults to parity fail-fast, then can switch to continue-and-record after explicit approval.
- Deterministic seeds, alternative metrics, and removal of duplicate weekly/holiday effects are challenger changes, never silent refactors.
- Change Data Feed and incremental reconciliation are deferred until actual-arrival volume and latency justify them.
