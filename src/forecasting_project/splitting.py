"""Source-equivalent cross-validation and forecast horizon policies."""

import calendar
from dataclasses import dataclass

import pandas as pd
from dateutil.relativedelta import relativedelta


@dataclass(frozen=True)
class CvWindow:
    initial_days: int
    period_days: int
    horizon_days: int

    @property
    def prophet_args(self) -> dict[str, str]:
        return {
            "initial": f"{self.initial_days} days",
            "period": f"{self.period_days} days",
            "horizon": f"{self.horizon_days} days",
        }


def source_cv_window(total_days: int, initial_ratio: float = 0.8, period_ratio: float = 0.5) -> CvWindow | None:
    if total_days < 30:
        return None
    horizon = 90 if total_days >= 730 else 60 if total_days >= 365 else 30 if total_days >= 60 else 10
    minimum = 90 if total_days >= 750 else 60 if total_days >= 365 else 30 if total_days >= 60 else 10
    initial = max(int(total_days * initial_ratio), minimum)
    remaining = total_days - initial
    if remaining < horizon:
        horizon = max(min(remaining, horizon), 7)
    if remaining < 7:
        initial = max(total_days - 7, minimum)
    return CvWindow(initial, max(int(horizon * period_ratio), 7), horizon)


def calendar_month_horizon(as_of_date: str | pd.Timestamp, months: int = 3) -> int:
    start = pd.Timestamp(as_of_date).to_pydatetime()
    return sum(
        calendar.monthrange((start + relativedelta(months=i)).year, (start + relativedelta(months=i)).month)[1]
        for i in range(months)
    )
