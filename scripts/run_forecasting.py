import argparse
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from pyspark.sql import SparkSession

from forecasting_project.config import ProjectConfig
from forecasting_project.databricks_io import (
    ensure_schema_and_tables,
    load_source,
    source_table_version,
    write_run_frame,
)
from forecasting_project.orchestration import run_collection
from forecasting_project.tracking import build_run_manifest, log_collection_run

parser = argparse.ArgumentParser()
parser.add_argument("--root-path", required=True)
parser.add_argument("--env", choices=["dev", "acc", "prd"], required=True)
parser.add_argument("--as-of-date", required=True)
parser.add_argument("--run-id", required=True)
args = parser.parse_args()

root = Path(args.root_path) / "files"
config = ProjectConfig.from_yaml(root / "conf/base.yml", root / f"conf/{args.env}.yml")
spark = SparkSession.builder.getOrCreate()
ensure_schema_and_tables(spark, config)
source_table = config.storage.table("source_table")
source_version = source_table_version(spark, source_table)
result = run_collection(load_source(spark, config), config, args.as_of_date)
created_at = datetime.now(UTC)
result.statuses["reason"] = result.statuses["reason"].astype("string").fillna("")
for frame in [result.forecasts, result.performance, result.parameters, result.statuses]:
    frame["run_id"] = args.run_id
    frame["created_at"] = created_at
    if "as_of_date" not in frame:
        frame["as_of_date"] = pd.Timestamp(args.as_of_date)
manifest = build_run_manifest(result, config, args.run_id, args.as_of_date, source_version, created_at)
write_run_frame(spark, result.forecasts, config.storage.table("forecast_table"), args.run_id)
write_run_frame(spark, result.performance, config.storage.table("backtest_table"), args.run_id)
write_run_frame(spark, result.parameters, config.storage.table("parameter_table"), args.run_id)
write_run_frame(spark, result.statuses, config.storage.table("series_status_table"), args.run_id)
write_run_frame(spark, manifest, config.storage.table("run_manifest_table"), args.run_id)
log_collection_run(manifest, result, config)
