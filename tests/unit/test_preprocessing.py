import pandas as pd

from forecasting_project.config import ProjectConfig
from forecasting_project.preprocessing import expand_daily_series, infer_non_operating_weekdays


def _config() -> ProjectConfig:
    return ProjectConfig.from_yaml("conf/base.yml", "conf/dev.yml")


def test_expansion_fills_only_volume() -> None:
    config = _config()
    frame = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2024-01-01", "2024-01-03"]),
            "Business_Category_001": ["A", "A"],
            "Business_Category_002": ["B", "B"],
            "Language": ["Segment_A", "Segment_A"],
            "Country": ["GR", "GR"],
            "Business_Category_003": [10.0, 12.0],
            "Business_Category_004": [1.0, 1.0],
            "Business_Category_005": [1.0, 1.0],
            "Business_Category_006": [1.0, 1.0],
            "Business_Category_007": [1.0, 1.0],
            "Business_Category_008": [2.0, 2.0],
        }
    )
    expanded = expand_daily_series(frame, config)
    assert len(expanded) == 3
    assert expanded.loc[1, config.volume_column] == 0
    assert pd.isna(expanded.loc[1, config.regressor_columns[0]])


def test_detects_consistent_weekend_closure() -> None:
    config = _config()
    frame = pd.DataFrame({"Date": pd.date_range("2024-01-01", periods=70)})
    frame[config.volume_column] = 1.0
    frame[config.non_operating_null_column] = 1.0
    weekend = frame.Date.dt.dayofweek == 6
    frame.loc[weekend, config.volume_column] = 0
    frame.loc[weekend, config.non_operating_null_column] = None
    assert infer_non_operating_weekdays(frame, config) == (6,)
