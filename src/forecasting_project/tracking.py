"""Small, collection-level lineage records for MLflow and Delta."""

import hashlib
import json
from datetime import UTC, datetime

import mlflow
import pandas as pd

from forecasting_project.config import ProjectConfig
from forecasting_project.orchestration import CollectionResult


def configuration_hash(config: ProjectConfig) -> str:
    payload = json.dumps(config.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def build_run_manifest(
    result: CollectionResult,
    config: ProjectConfig,
    run_id: str,
    as_of_date: str,
    source_version: int,
    created_at: datetime | None = None,
) -> pd.DataFrame:
    completed = int((result.statuses.get("status") == "completed").sum())
    failed = int((result.statuses.get("status") == "failed").sum())
    return pd.DataFrame(
        [
            {
                "run_id": run_id,
                "as_of_date": pd.Timestamp(as_of_date),
                "environment": config.environment,
                "source_table": config.storage.table("source_table"),
                "source_version": source_version,
                "config_hash": configuration_hash(config),
                "completed_fits": completed,
                "failed_fits": failed,
                "forecast_rows": len(result.forecasts),
                "backtest_rows": len(result.performance),
                "status": "completed" if failed == 0 else "completed_with_failures",
                "created_at": created_at or datetime.now(UTC),
            }
        ]
    )


def log_collection_run(manifest: pd.DataFrame, result: CollectionResult, config: ProjectConfig) -> None:
    """Log one bounded MLflow run instead of one noisy run per fitted series."""
    row = manifest.iloc[0]
    mlflow.set_experiment(config.tracking.experiment_name)
    with mlflow.start_run(run_name=f"forecast-{row['run_id']}"):
        mlflow.set_tags(
            {
                "project": config.project_name,
                "environment": config.environment,
                "run_id": str(row["run_id"]),
                "config_hash": row["config_hash"],
            }
        )
        mlflow.log_params(
            {
                "as_of_date": str(row["as_of_date"]),
                "forecast_months": config.forecast_months,
                "tuning_trials": config.tuning.trials,
                "source_table": row["source_table"],
                "source_version": int(row["source_version"]),
            }
        )
        mlflow.log_metrics(
            {
                "completed_fits": int(row["completed_fits"]),
                "failed_fits": int(row["failed_fits"]),
                "forecast_rows": int(row["forecast_rows"]),
                "backtest_rows": int(row["backtest_rows"]),
            }
        )
        mlflow.log_dict(result.parameters.to_dict(orient="records"), "selected_parameters.json")
