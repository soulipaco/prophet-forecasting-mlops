import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from pyspark.sql import SparkSession

from forecasting_project.config import ProjectConfig
from forecasting_project.databricks_io import ensure_schema_and_tables

parser = argparse.ArgumentParser()
parser.add_argument("--root-path", required=True)
parser.add_argument("--env", choices=["dev", "acc", "prd"], required=True)
parser.add_argument("--as-of-date", required=True)
args = parser.parse_args()

root = Path(args.root_path) / "files"
config = ProjectConfig.from_yaml(root / "conf/base.yml", root / f"conf/{args.env}.yml")
spark = SparkSession.builder.getOrCreate()
ensure_schema_and_tables(spark, config)
rng = np.random.default_rng(314159)
cutoff = pd.Timestamp(args.as_of_date)
rows = []
for index, language in enumerate(["Segment_A", "Segment_B"]):
    dates = pd.date_range(cutoff - pd.Timedelta(days=200), cutoff + pd.Timedelta(days=100), freq="D")
    for day_number, day in enumerate(dates):
        if day.dayofweek in (5, 6):
            continue
        trend = 80 + index * 15 + day_number * 0.05
        volume = max(1.0, trend + 12 * np.sin(day_number * 2 * np.pi / 7) + rng.normal(0, 2))
        rows.append(
            {
                "Date": day.to_pydatetime(),
                "Business_Category_001": "Operations_A",
                "Business_Category_002": f"KPI_Group_{index + 1}",
                "Language": language,
                "Country": "GR",
                "Business_Category_003": float(volume) if day < cutoff else None,
                "Business_Category_004": float(day.dayofweek),
                "Business_Category_005": float(100 + day_number),
                "Business_Category_006": float(index + 1 + 0.1 * np.cos(day_number * 2 * np.pi / 7)),
                "Business_Category_007": 1.0,
                "Business_Category_008": float(50 + 5 * np.sin(day_number * 2 * np.pi / 7)) if day < cutoff else None,
            }
        )

spark.createDataFrame(pd.DataFrame(rows)).write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(
    config.storage.table("source_table")
)
