import pathlib
import sys

import numpy as np
import pandas as pd
import pytest


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from visualization.financial_factors_stocks import (  # noqa: E402
    _calc_nav_metrics,
    _calc_nav_norm_and_excess_nav,
)


def test_calc_nav_metrics_matches_return_based_definitions() -> None:
    nav = pd.Series([100.0, 110.0, 105.0, 120.0])
    trading_days = 4

    metrics = _calc_nav_metrics(nav, rf_annual=0.0, trading_days=trading_days)

    nav_norm = nav / nav.iloc[0]
    daily_returns = nav_norm.pct_change().dropna()

    expected_period_return = float(nav_norm.iloc[-1] - 1)
    expected_annual_return = float((1 + expected_period_return) ** (trading_days / len(daily_returns)) - 1)
    expected_max_drawdown = float((nav_norm / nav_norm.cummax() - 1).min())
    expected_sharpe = float(daily_returns.mean() / daily_returns.std(ddof=1) * np.sqrt(trading_days))

    assert metrics["period_return"] == pytest.approx(expected_period_return)
    assert metrics["annual_return"] == pytest.approx(expected_annual_return)
    assert metrics["max_drawdown"] == pytest.approx(expected_max_drawdown)
    assert metrics["sharpe"] == pytest.approx(expected_sharpe)


def test_ratio_excess_nav_is_strategy_over_benchmark() -> None:
    strategy_nav = pd.Series([100.0, 110.0])
    benchmark_nav = pd.Series([200.0, 210.0])

    strategy_norm, benchmark_norm, excess_nav = _calc_nav_norm_and_excess_nav(strategy_nav, benchmark_nav)

    assert strategy_norm.tolist() == pytest.approx([1.0, 1.1])
    assert benchmark_norm.tolist() == pytest.approx([1.0, 1.05])
    assert excess_nav.tolist() == pytest.approx([1.0, 1.1 / 1.05])


def test_empty_series_returns_nan_metrics() -> None:
    metrics = _calc_nav_metrics(pd.Series(dtype=float), rf_annual=0.013, trading_days=242)
    assert np.isnan(metrics["period_return"])
    assert np.isnan(metrics["annual_return"])
    assert np.isnan(metrics["max_drawdown"])
    assert np.isnan(metrics["sharpe"])


def test_single_point_sharpe_is_nan() -> None:
    metrics = _calc_nav_metrics(pd.Series([100.0]), rf_annual=0.013, trading_days=242)
    assert np.isnan(metrics["sharpe"])


def test_constant_nav_has_nan_sharpe() -> None:
    metrics = _calc_nav_metrics(pd.Series([100.0, 100.0, 100.0, 100.0]), rf_annual=0.013, trading_days=242)
    assert np.isnan(metrics["sharpe"])
