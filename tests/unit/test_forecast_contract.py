import pandas as pd

from forecasting_project.config import ProjectConfig
from forecasting_project.orchestration import select_forecast_output


def test_forecast_contract_excludes_prophet_holiday_component_columns() -> None:
    config = ProjectConfig.from_yaml("conf/base.yml", "conf/dev.yml")
    prediction = pd.DataFrame(
        {
            "ds": pd.to_datetime(["2025-01-01", "2025-01-02"]),
            "yhat": [1.0, 2.0],
            "yhat_lower": [0.5, 1.5],
            "yhat_upper": [1.5, 2.5],
            "trend": [1.0, 1.1],
            "Holiday Name's component": [0.2, 0.0],
        }
    )
    result = select_forecast_output(
        prediction,
        config,
        ("Category_A", "Category_B", "Segment_A"),
        "volume",
        "2025-01-02",
    )
    assert "Holiday Name's component" not in result
    assert set(result.row_type) == {"fitted", "forecast"}
    assert result.horizon_day.tolist() == [0, 0]
    assert result.columns.tolist() == [
        "ds",
        "yhat",
        "yhat_lower",
        "yhat_upper",
        "trend",
        "target",
        *config.series_columns,
        "as_of_date",
        "row_type",
        "horizon_day",
    ]
