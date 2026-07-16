"""Prophet construction and source-equivalent Optuna tuning."""

from dataclasses import dataclass

import optuna
import pandas as pd
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics

from forecasting_project.config import TuningConfig
from forecasting_project.splitting import CvWindow


@dataclass
class FitResult:
    model: Prophet
    performance: pd.DataFrame
    parameters: dict[str, object]


def build_model(parameters: dict[str, object], holidays: pd.DataFrame) -> Prophet:
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode=str(parameters["seasonality_mode"]),
        changepoint_prior_scale=float(parameters["changepoint_prior_scale"]),
        changepoint_range=0.9,
        seasonality_prior_scale=float(parameters["seasonality_prior_scale"]),
        holidays_prior_scale=float(parameters["holidays_prior_scale"]),
        growth="logistic",
        interval_width=0.8,
        holidays=holidays,
    )
    model.add_seasonality("monthly", period=30.5, fourier_order=int(parameters["fourier_order"]))
    model.add_seasonality(
        "weekly_custom",
        period=7,
        fourier_order=int(parameters["weekly_fourier_order"]),
        prior_scale=float(parameters["weekly_prior_scale"]),
    )
    for regressor in ["is_holiday", "regressor_1", "regressor_2", "regressor_3"]:
        model.add_regressor(regressor, mode=str(parameters["regressor_mode"]))
    return model


def tune_and_fit(frame: pd.DataFrame, holidays: pd.DataFrame, window: CvWindow, tuning: TuningConfig) -> FitResult:
    def objective(trial: optuna.Trial) -> float:
        parameters = _trial_parameters(trial)
        try:
            model = build_model(parameters, holidays)
            model.fit(frame)
            # Free Edition serverless does not provide a stable multiprocessing contract.
            # Sequential CV preserves the same folds and forecasting mathematics.
            cv = cross_validation(model, parallel=None, **window.prophet_args)
            return float(performance_metrics(cv)["rmse"].mean())
        except Exception as exc:
            trial.set_user_attr("failure_type", type(exc).__name__)
            trial.set_user_attr("failure_message", str(exc)[:500])
            return float("inf")

    sampler = optuna.samplers.TPESampler(seed=tuning.seed) if tuning.seed is not None else None
    study = optuna.create_study(direction="minimize", sampler=sampler)
    study.optimize(objective, n_trials=tuning.trials)
    if not study.trials or study.best_value == float("inf"):
        detail = study.trials[0].user_attrs if study.trials else {}
        raise RuntimeError(f"all_tuning_trials_failed:{detail}")
    parameters = dict(study.best_params)
    model = build_model(parameters, holidays)
    model.fit(frame)
    cv = cross_validation(model, parallel=None, **window.prophet_args)
    return FitResult(model, performance_metrics(cv), parameters)


def _trial_parameters(trial: optuna.Trial) -> dict[str, object]:
    return {
        "seasonality_mode": trial.suggest_categorical("seasonality_mode", ["additive", "multiplicative"]),
        "changepoint_prior_scale": trial.suggest_float("changepoint_prior_scale", 0.01, 0.1, step=0.02),
        "seasonality_prior_scale": trial.suggest_categorical("seasonality_prior_scale", [5.0, 10.0]),
        "holidays_prior_scale": trial.suggest_categorical("holidays_prior_scale", [5.0, 10.0]),
        "fourier_order": trial.suggest_int("fourier_order", 5, 7),
        "weekly_fourier_order": trial.suggest_categorical("weekly_fourier_order", [3, 5, 7]),
        "weekly_prior_scale": trial.suggest_categorical("weekly_prior_scale", [0.1, 0.5, 1.0]),
        "regressor_mode": trial.suggest_categorical("regressor_mode", ["additive", "multiplicative"]),
    }
