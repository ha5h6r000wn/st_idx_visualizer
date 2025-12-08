import pathlib
import sys
from datetime import datetime

import numpy as np
import pandas as pd
import pytest


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import config, param_cls  # noqa: E402
from data_preparation.data_analyzer import calculate_grouped_return  # noqa: E402
from data_preparation.data_fetcher import INDEX_PRICE_SCHEMA, fetch_index_data_from_local  # noqa: E402
from data_preparation.data_processor import (  # noqa: E402
    convert_price_ts_into_nav_ts,
    reshape_long_df_into_wide_form,
)


def _load_stg_idx_raw_prices(latest_date: str) -> tuple[pd.DataFrame, param_cls.WindIdxColParam]:
    wind_config = param_cls.WindListedSecParam(
        wind_codes=config.STG_IDX_CODES + config.BENCH_IDX_CODES,
        start_date=config.START_DT,
        sql_param=param_cls.SqlParam(sql_name=config.IDX_PRICE_SQL_NAME),
    )
    data_col_config = param_cls.WindIdxColParam()

    raw_long_df = fetch_index_data_from_local(latest_date=latest_date, _config=wind_config)
    return raw_long_df, data_col_config


@pytest.mark.schema
@pytest.mark.stg_idx_prep
def test_stg_idx_loader_columns_from_canonical_index_price_schema() -> None:
    """Strategy-index loader MUST use columns that come from the canonical A_IDX_PRICE schema."""
    canonical_cols = INDEX_PRICE_SCHEMA["canonical_cols"]
    idx_col_param = param_cls.WindIdxColParam()

    used_cols = {
        idx_col_param.dt_col,
        idx_col_param.code_col,
        idx_col_param.name_col,
        idx_col_param.price_col,
    }
    allowed_raw_cols = set(canonical_cols.values())

    assert used_cols.issubset(allowed_raw_cols)


@pytest.mark.stg_idx_prep
def test_stg_idx_grouped_return_basic_invariants() -> None:
    """Grouped return frame MUST be non-empty and cover all strategy indices."""
    latest_date = datetime.strptime("99991231", config.WIND_DT_FORMAT).strftime(config.WIND_DT_FORMAT)
    raw_long_df, data_col_config = _load_stg_idx_raw_prices(latest_date=latest_date)

    assert not raw_long_df.empty

    trade_dt = sorted(raw_long_df[data_col_config.dt_col].unique())

    # Use a simple "last N dates" window that mirrors the intent of the
    # stg_idx RET_BAR slider without depending on Streamlit helpers.
    window_size = config.TRADE_DT_COUNT["一月"]
    end_dt = trade_dt[-1]
    start_idx = max(0, len(trade_dt) - window_size)
    start_dt = trade_dt[start_idx]
    custom_dt = (start_dt, end_dt)

    grouped_ret_df = calculate_grouped_return(raw_long_df, latest_date, custom_dt, trade_dt, data_col_config)

    assert not grouped_ret_df.empty

    # Each strategy index SHOULD have a corresponding row, identified by its name.
    stg_idx_df = raw_long_df[raw_long_df[data_col_config.code_col].isin(config.STG_IDX_CODES)].reset_index(drop=True)
    stg_idx_name_df = (
        stg_idx_df[[data_col_config.code_col, data_col_config.name_col]]
        .drop_duplicates()
        .set_index(data_col_config.code_col, drop=True)
        .reindex(config.STG_IDX_CODES)
    )
    stg_names = [name for name in stg_idx_name_df[data_col_config.name_col].tolist() if name]

    assert set(stg_names).issubset(set(grouped_ret_df.index))


@pytest.mark.stg_idx_prep
def test_stg_idx_nav_wide_df_basic_invariants() -> None:
    """NAV wide frame MUST have monotonic dates and non-empty series for all indices."""
    latest_date = datetime.strptime("99991231", config.WIND_DT_FORMAT).strftime(config.WIND_DT_FORMAT)
    raw_long_df, data_col_config = _load_stg_idx_raw_prices(latest_date=latest_date)

    assert not raw_long_df.empty

    trade_dt = sorted(raw_long_df[data_col_config.dt_col].unique())
    slider_config = param_cls.DtSliderParam(
        name=config.CUSTOM_PERIOD_SLIDER_NAME,
        start_dt=config.START_DT,
        default_start_offset=config.TRADE_DT_COUNT["一年"],
    )

    end_dt = trade_dt[-1]
    start_idx = max(0, len(trade_dt) - slider_config.default_start_offset)
    start_dt = trade_dt[start_idx]
    custom_dt = (start_dt, end_dt)

    wide_price_df = reshape_long_df_into_wide_form(
        raw_long_df,
        data_col_config.dt_col,
        data_col_config.name_col,
        data_col_config.price_col,
    )

    # Restrict to the same date window as the page.
    wide_price_df = wide_price_df.loc[custom_dt[0] : custom_dt[1]]
    nav_df = convert_price_ts_into_nav_ts(wide_price_df)

    assert not nav_df.empty
    assert nav_df.index.is_monotonic_increasing

    # Each configured strategy/benchmark name should have a non-empty NAV series.
    names = wide_price_df.columns.tolist()
    for name in names:
        series = nav_df[name]
        assert series.notna().any()


@pytest.mark.stg_idx_prep
def test_stg_idx_excess_correlation_basic_invariants() -> None:
    """Excess-return correlation heatmap MUST be symmetric with unit diagonal."""
    latest_date = datetime.strptime("99991231", config.WIND_DT_FORMAT).strftime(config.WIND_DT_FORMAT)
    raw_long_df, data_col_config = _load_stg_idx_raw_prices(latest_date=latest_date)

    assert not raw_long_df.empty

    trade_dt = sorted(raw_long_df[data_col_config.dt_col].unique())

    wide_price_df = reshape_long_df_into_wide_form(
        raw_long_df,
        data_col_config.dt_col,
        data_col_config.name_col,
        data_col_config.price_col,
    )
    ret_wide_df = wide_price_df.pct_change().dropna()

    # Mirror the "near-term" excess return window selection: use the shortest window
    # configured on the page (e.g.,近一月).
    min_window = min(config.STG_IDX_CORR_TRADE_DT_COUNT.values())
    end_idx = len(trade_dt)
    start_idx = max(0, end_idx - min_window)
    start_dt = trade_dt[start_idx]

    # Strategy names are all indices excluding the benchmark "中证800".
    benchmark_name = "中证800"
    stg_names = [name for name in ret_wide_df.columns if name != benchmark_name]

    excess_ret_wide_df = ret_wide_df.loc[start_dt:, stg_names].subtract(
        ret_wide_df.loc[start_dt:, benchmark_name], axis=0
    )
    corr_wide_df = excess_ret_wide_df.corr()

    assert not corr_wide_df.empty

    # Correlation matrix must be symmetric with unit diagonal.
    assert corr_wide_df.shape[0] == corr_wide_df.shape[1]
    assert np.allclose(corr_wide_df.values, corr_wide_df.values.T, equal_nan=True)
    diag = np.diag(corr_wide_df.values)
    # allow small numerical noise
    assert np.allclose(diag, np.ones_like(diag), atol=1e-8, equal_nan=True)
