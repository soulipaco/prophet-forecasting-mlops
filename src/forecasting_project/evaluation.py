"""Forecast metrics and baseline models."""

import numpy as np
import pandas as pd


def seasonal_naive(values: pd.Series, season: int = 7) -> pd.Series:
    return values.shift(season)


def forecast_metrics(
    actual: pd.Series, predicted: pd.Series, lower: pd.Series | None = None, upper: pd.Series | None = None
) -> dict[str, float]:
    a = actual.astype(float).to_numpy()
    p = predicted.astype(float).to_numpy()
    error = p - a
    result = {
        "mae": float(np.mean(np.abs(error))),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "bias": float(np.mean(error)),
    }
    denominator = float(np.sum(np.abs(a)))
    result["wape"] = float(np.sum(np.abs(error)) / denominator) if denominator else float("nan")
    if lower is not None and upper is not None:
        lo, hi = lower.astype(float).to_numpy(), upper.astype(float).to_numpy()
        result["interval_coverage"] = float(np.mean((a >= lo) & (a <= hi)))
        result["interval_width"] = float(np.mean(hi - lo))
    return result
