"""Holiday calendars used by Prophet and the holiday regressor."""

import holidays
import pandas as pd


def holiday_frame(countries: list[str], years: list[int]) -> pd.DataFrame:
    rows: list[tuple[object, str, str]] = []
    for country in countries:
        rows.extend((day, name, country) for day, name in holidays.CountryHoliday(country, years=years).items())
    frame = pd.DataFrame(rows, columns=["ds", "holiday", "country"])
    if frame.empty:
        return pd.DataFrame(columns=["ds", "holiday", "lower_window", "upper_window"])
    frame["ds"] = pd.to_datetime(frame["ds"])
    frame["lower_window"] = 0
    frame["upper_window"] = 1
    return frame[["ds", "holiday", "lower_window", "upper_window"]]
