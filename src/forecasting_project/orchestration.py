"""Coordinate the individual Prophet fits as one batch collection."""

from dataclasses import dataclass

import pandas as pd

from forecasting_project.calendars import holiday_frame
from forecasting_project.config import ProjectConfig
from forecasting_project.contracts import validate_input
from forecasting_project.preprocessing import logistic_bounds, prepare_series
from forecasting_project.prophet_model import tune_and_fit
from forecasting_project.splitting import calendar_month_horizon, source_cv_window


@dataclass
class CollectionResult:
    forecasts: pd.DataFrame
    performance: pd.DataFrame
    parameters: pd.DataFrame
    statuses: pd.DataFrame


def run_collection(df: pd.DataFrame, config: ProjectConfig, as_of_date: str) -> CollectionResult:
    source = validate_input(df, config, as_of_date)
    historical = source[source[config.date_column] < pd.Timestamp(as_of_date)]
    horizon = calendar_month_horizon(as_of_date, config.forecast_months)
    forecasts, performance, parameters, statuses = [], [], [], []
    keys = historical[config.series_columns].drop_duplicates().sort_values(config.series_columns)
    for key_values in keys.itertuples(index=False, name=None):
        selector = pd.Series(True, index=source.index)
        for column, value in zip(config.series_columns, key_values, strict=True):
            selector &= source[column] == value
        series_all = source[selector]
        series_history = series_all[series_all[config.date_column] < pd.Timestamp(as_of_date)]
        try:
            prepared = prepare_series(series_history, config)
            total_days = (prepared.frame[config.date_column].max() - prepared.frame[config.date_column].min()).days
            window = source_cv_window(total_days, config.tuning.initial_ratio, config.tuning.period_ratio)
            if window is None:
                raise RuntimeError("insufficient_history")
            years = list(
                range(prepared.frame[config.date_column].min().year, prepared.frame[config.date_column].max().year + 2)
            )
            holiday_df = holiday_frame(prepared.frame[config.country_column].dropna().unique().tolist(), years)
            for target_name, target_column in [("volume", config.volume_column), ("kpi", config.kpi_column)]:
                model_frame = _model_frame(prepared.frame, config, target_column, holiday_df)
                cap, floor = logistic_bounds(prepared.frame, target_column, config.volume_column)
                model_frame["cap"], model_frame["floor"] = cap, floor
                fitted = tune_and_fit(model_frame, holiday_df, window, config.tuning)
                future = _future_frame(fitted.model, series_all, prepared, config, horizon, holiday_df, cap, floor)
                prediction = fitted.model.predict(future)
                forecasts.append(select_forecast_output(prediction, config, key_values, target_name, as_of_date))
                metric = fitted.performance.copy()
                metric["target"] = target_name
                for column, value in zip(config.series_columns, key_values, strict=True):
                    metric[column] = value
                performance.append(metric)
                parameters.append(
                    {
                        **dict(zip(config.series_columns, key_values, strict=True)),
                        "target": target_name,
                        **fitted.parameters,
                    }
                )
                statuses.append(
                    {
                        **dict(zip(config.series_columns, key_values, strict=True)),
                        "target": target_name,
                        "status": "completed",
                        "reason": None,
                    }
                )
        except Exception as exc:
            statuses.append(
                {
                    **dict(zip(config.series_columns, key_values, strict=True)),
                    "target": "collection",
                    "status": "failed",
                    "reason": type(exc).__name__,
                }
            )
            if config.failure_policy == "fail_fast":
                raise
    return CollectionResult(
        pd.concat(forecasts, ignore_index=True) if forecasts else pd.DataFrame(),
        pd.concat(performance, ignore_index=True) if performance else pd.DataFrame(),
        pd.DataFrame(parameters),
        pd.DataFrame(statuses),
    )


def select_forecast_output(
    prediction: pd.DataFrame,
    config: ProjectConfig,
    key_values: tuple,
    target_name: str,
    as_of_date: str,
) -> pd.DataFrame:
    """Return the stable Delta contract, excluding Prophet component columns."""
    required = ["ds", "yhat", "yhat_lower", "yhat_upper"]
    missing = [column for column in required if column not in prediction]
    if missing:
        raise ValueError(f"prediction is missing required columns: {missing}")
    optional = [column for column in ["trend", "cap", "floor"] if column in prediction]
    result = prediction[[*required, *optional]].copy()
    result["target"] = target_name
    for column, value in zip(config.series_columns, key_values, strict=True):
        result[column] = value
    cutoff = pd.Timestamp(as_of_date)
    result["as_of_date"] = cutoff
    result["row_type"] = result["ds"].ge(cutoff).map({True: "forecast", False: "fitted"})
    result["horizon_day"] = (result["ds"] - cutoff).dt.days.clip(lower=0)
    return result


def _model_frame(frame: pd.DataFrame, config: ProjectConfig, target: str, holidays: pd.DataFrame) -> pd.DataFrame:
    result = frame[[config.date_column, target, *config.regressor_columns]].rename(
        columns={
            config.date_column: "ds",
            target: "y",
            **{name: f"regressor_{i + 1}" for i, name in enumerate(config.regressor_columns)},
        }
    )
    result["is_holiday"] = result["ds"].isin(holidays["ds"]).astype(int)
    return result


def _future_frame(model, series_all, prepared, config, horizon, holidays, cap, floor):
    future = model.make_future_dataframe(periods=horizon, freq="D")
    future = future[~future["ds"].isin(prepared.excluded_dates)]
    future = future[~future["ds"].dt.dayofweek.isin(prepared.non_operating_weekdays)]
    regressors = series_all[[config.date_column, *config.regressor_columns]].rename(
        columns={
            config.date_column: "ds",
            **{name: f"regressor_{i + 1}" for i, name in enumerate(config.regressor_columns)},
        }
    )
    future = future.merge(regressors, on="ds", how="left")
    future["is_holiday"] = future["ds"].isin(holidays["ds"]).astype(int)
    future["cap"], future["floor"] = cap, floor
    return future[future["regressor_1"].notna()]
