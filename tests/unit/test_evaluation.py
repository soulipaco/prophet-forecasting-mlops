import pandas as pd

from forecasting_project.evaluation import forecast_metrics


def test_metrics_and_interval_coverage() -> None:
    result = forecast_metrics(
        pd.Series([10.0, 20.0]),
        pd.Series([12.0, 18.0]),
        pd.Series([9.0, 17.0]),
        pd.Series([13.0, 21.0]),
    )
    assert result["mae"] == 2.0
    assert result["rmse"] == 2.0
    assert result["interval_coverage"] == 1.0
