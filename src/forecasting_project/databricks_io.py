"""Databricks/Spark boundary; ordinary modules do not import Spark."""

from forecasting_project.config import ProjectConfig


def ensure_schema_and_tables(spark, config: ProjectConfig) -> None:
    catalog, schema = config.storage.catalog, config.storage.schema_name
    spark.sql(f"CREATE CATALOG IF NOT EXISTS `{catalog}`")
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{catalog}`.`{schema}`")


def load_source(spark, config: ProjectConfig):
    return spark.table(config.storage.table("source_table")).toPandas()


def source_table_version(spark, table_name: str) -> int:
    return int(spark.sql(f"DESCRIBE HISTORY {table_name} LIMIT 1").select("version").first()[0])


def write_run_frame(spark, frame, table_name: str, run_id: str) -> None:
    """Replace one run partition logically, making retries idempotent."""
    if frame.empty:
        return
    safe_run_id = run_id.replace("'", "''")
    if spark.catalog.tableExists(table_name):
        spark.sql(f"DELETE FROM {table_name} WHERE run_id = '{safe_run_id}'")
    spark.createDataFrame(frame).write.option("mergeSchema", "true").mode("append").saveAsTable(table_name)
