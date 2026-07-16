from forecasting_project.splitting import calendar_month_horizon, source_cv_window


def test_calendar_month_horizon_uses_calendar_boundaries() -> None:
    assert calendar_month_horizon("2025-05-01", 3) == 92


def test_short_history_returns_none() -> None:
    assert source_cv_window(29) is None


def test_long_history_uses_ninety_day_horizon() -> None:
    window = source_cv_window(850)
    assert window is not None
    assert window.horizon_days == 90
    assert window.period_days == 45
