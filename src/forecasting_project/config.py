"""Validated forecasting configuration."""

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, model_validator


class TuningConfig(BaseModel):
    trials: int = Field(default=50, ge=1)
    initial_ratio: float = Field(default=0.8, gt=0, lt=1)
    period_ratio: float = Field(default=0.5, gt=0, le=1)
    seed: int | None = None


class TrackingConfig(BaseModel):
    experiment_name: str
    register_collection: bool = False


class StorageConfig(BaseModel):
    catalog: str
    schema_name: str
    source_table: str = "forecast_input"
    forecast_table: str = "forecast_rows"
    backtest_table: str = "backtest_rows"
    parameter_table: str = "selected_parameters"
    series_status_table: str = "series_status"
    run_manifest_table: str = "run_manifest"

    def table(self, name: str) -> str:
        return f"{self.catalog}.{self.schema_name}.{getattr(self, name)}"


class ProjectConfig(BaseModel):
    project_name: str
    environment: Literal["dev", "acc", "prd"]
    series_columns: list[str]
    date_column: str
    country_column: str
    volume_column: str
    kpi_column: str
    regressor_columns: list[str]
    non_operating_null_column: str
    normal_column: str | None = None
    forecast_months: int = Field(default=3, ge=1, le=24)
    non_operating_threshold: float = Field(default=0.9, gt=0, le=1)
    failure_policy: Literal["fail_fast", "continue_and_record"] = "fail_fast"
    tuning: TuningConfig
    tracking: TrackingConfig
    storage: StorageConfig

    @model_validator(mode="after")
    def validate_columns(self) -> "ProjectConfig":
        if len(self.series_columns) != len(set(self.series_columns)):
            raise ValueError("series_columns must be unique")
        if len(self.regressor_columns) != len(set(self.regressor_columns)):
            raise ValueError("regressor_columns must be unique")
        targets = {self.volume_column, self.kpi_column}
        if targets & set(self.regressor_columns):
            raise ValueError("targets cannot also be regressors")
        return self

    @property
    def required_columns(self) -> list[str]:
        values = [
            self.date_column,
            *self.series_columns,
            self.country_column,
            self.volume_column,
            self.kpi_column,
            *self.regressor_columns,
        ]
        if self.normal_column:
            values.append(self.normal_column)
        return list(dict.fromkeys(values))

    @classmethod
    def from_yaml(cls, base_path: str | Path, overlay_path: str | Path | None = None) -> "ProjectConfig":
        with Path(base_path).open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        if overlay_path:
            with Path(overlay_path).open(encoding="utf-8") as handle:
                overlay = yaml.safe_load(handle) or {}
            data = _deep_merge(data, overlay)
        return cls.model_validate(data)


def _deep_merge(base: dict, overlay: dict) -> dict:
    result = dict(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
