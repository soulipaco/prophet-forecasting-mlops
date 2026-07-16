"""Pure source-equivalent preprocessing."""

from dataclasses import dataclass

import pandas as pd

from forecasting_project.config import ProjectConfig


@dataclass(frozen=True)
class PreparedSeries:
    frame: pd.DataFrame
    excluded_dates: tuple[pd.Timestamp, ...]
    non_operating_weekdays: tuple[int, ...]


def expand_daily_series(df: pd.DataFrame, config: ProjectConfig) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    date_col = config.date_column
    source = df.copy()
    source[date_col] = pd.to_datetime(source[date_col])
    result = pd.DataFrame({date_col: pd.date_range(source[date_col].min(), source[date_col].max())})
    result = result.merge(source, on=date_col, how="left")
    for column in [*config.series_columns, config.country_column]:
        result[column] = source[column].iloc[0]
    result[config.volume_column] = result[config.volume_column].fillna(0)
    return result.reset_index(drop=True)


def infer_non_operating_weekdays(
    df: pd.DataFrame, config: ProjectConfig, threshold: float | None = None
) -> tuple[int, ...]:
    frame = df.copy()
    date_col = config.date_column
    frame["_year"] = frame[date_col].dt.year
    frame["_weekday"] = frame[date_col].dt.dayofweek
    weeks_per_year = frame.groupby("_year")[date_col].nunique() // 7
    counts = (
        frame[(frame[config.volume_column] == 0) & frame[config.non_operating_null_column].isna()]
        .groupby(["_year", "_weekday"])
        .size()
    )
    limit = config.non_operating_threshold if threshold is None else threshold
    values = {day for (year, day), count in counts.items() if count >= weeks_per_year[year] * limit}
    return tuple(sorted(values))


def prepare_series(df: pd.DataFrame, config: ProjectConfig) -> PreparedSeries:
    expanded = expand_daily_series(df, config)
    weekdays = infer_non_operating_weekdays(expanded, config)
    excluded = expanded[
        (expanded[config.volume_column] == 0)
        | expanded[config.regressor_columns[0]].isna()
        | expanded[config.date_column].dt.dayofweek.isin(weekdays)
    ][config.date_column]
    clean = expanded[~expanded[config.date_column].isin(excluded)].reset_index(drop=True)
    return PreparedSeries(clean, tuple(pd.Timestamp(x) for x in excluded), weekdays)


def logistic_bounds(frame: pd.DataFrame, target: str, volume_column: str) -> tuple[float, float]:
    cap = float(frame[target].max())
    eligible = frame.loc[frame[volume_column] > 0, target]
    if eligible.empty:
        raise ValueError("no_positive_volume_for_floor")
    floor = float(eligible.min())
    if floor > cap:
        raise ValueError("invalid_logistic_bounds")
    return cap, floor
