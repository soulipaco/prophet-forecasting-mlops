"""Input contracts that fail before expensive fitting."""

from dataclasses import dataclass

import pandas as pd

from forecasting_project.config import ProjectConfig


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    count: int


class ContractError(ValueError):
    def __init__(self, issues: list[ValidationIssue]):
        self.issues = issues
        super().__init__(", ".join(f"{item.code}={item.count}" for item in issues))


def validate_input(df: pd.DataFrame, config: ProjectConfig, as_of_date: str | pd.Timestamp) -> pd.DataFrame:
    issues: list[ValidationIssue] = []
    missing = sorted(set(config.required_columns) - set(df.columns))
    if missing:
        issues.append(ValidationIssue("missing_required_columns", len(missing)))
        raise ContractError(issues)

    clean = df.copy()
    clean[config.date_column] = pd.to_datetime(clean[config.date_column], errors="coerce")
    invalid_dates = int(clean[config.date_column].isna().sum())
    if invalid_dates:
        issues.append(ValidationIssue("invalid_dates", invalid_dates))

    key = [*config.series_columns, config.date_column]
    duplicates = int(clean.duplicated(key, keep=False).sum())
    if duplicates:
        issues.append(ValidationIssue("duplicate_series_dates", duplicates))

    historical = clean[clean[config.date_column] < pd.Timestamp(as_of_date)]
    target_nulls = int(historical[[config.volume_column, config.kpi_column]].isna().any(axis=1).sum())
    if target_nulls:
        issues.append(ValidationIssue("historical_target_nulls", target_nulls))
    if issues:
        raise ContractError(issues)
    return clean.sort_values(key).reset_index(drop=True)
