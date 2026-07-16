import pandas as pd

from forecasting_project.config import ProjectConfig
from forecasting_project.orchestration import CollectionResult
from forecasting_project.tracking import build_run_manifest, configuration_hash


def test_run_manifest_records_collection_counts() -> None:
    config = ProjectConfig.from_yaml("conf/base.yml", "conf/dev.yml")
    result = CollectionResult(
        forecasts=pd.DataFrame({"ds": [pd.Timestamp("2025-01-01")] * 3}),
        performance=pd.DataFrame({"rmse": [1.0, 2.0]}),
        parameters=pd.DataFrame({"target": ["volume"]}),
        statuses=pd.DataFrame({"status": ["completed", "failed"]}),
    )
    manifest = build_run_manifest(result, config, "run-1", "2025-01-01", 7)
    row = manifest.iloc[0]
    assert row.completed_fits == 1
    assert row.failed_fits == 1
    assert row.forecast_rows == 3
    assert row.status == "completed_with_failures"
    assert len(configuration_hash(config)) == 64
