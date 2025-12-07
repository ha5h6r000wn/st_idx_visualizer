import pathlib
import sys

import pandas as pd
import pytest


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import config, param_cls, style_config  # noqa: E402
from data_preparation.data_fetcher import fetch_data_from_local, fetch_index_data_from_local  # noqa: E402
from visualization.style import (  # noqa: E402
    prepare_shibor_prices_data,
    prepare_value_growth_data,
)


def _load_style_index_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load wide index price data and index name mapping for style charts."""
    wind_idx_param = param_cls.WindListedSecParam(
        wind_codes=tuple(style_config.STYLE_IDX_CODES.values()),
        start_date=style_config.START_DT,
        sql_param=param_cls.SqlParam(sql_name=config.IDX_PRICE_SQL_NAME),
    )
    idx_col_param = param_cls.WindIdxColParam()

    raw_long_idx_df = fetch_index_data_from_local(latest_date='99991231', _config=wind_idx_param)

    idx_name_df = (
        raw_long_idx_df[[idx_col_param.code_col, idx_col_param.name_col]]
        .drop_duplicates()
        .set_index(idx_col_param.code_col, drop=True)
        .reindex(wind_idx_param.wind_codes)
    )

    raw_wide_idx_df = raw_long_idx_df.pivot(
        index=idx_col_param.dt_col,
        columns=idx_col_param.name_col,
        values=idx_col_param.price_col,
    )

    return raw_wide_idx_df, idx_name_df


@pytest.mark.style_prep
def test_prepare_value_growth_data_basic_invariants():
    raw_wide_idx_df, idx_name_df = _load_style_index_data()

    ratio_mean_df, pct_change_df, signal_df = prepare_value_growth_data(
        raw_wide_idx_df=raw_wide_idx_df,
        idx_name_df=idx_name_df,
    )

    # Basic shape/column invariants
    assert not ratio_mean_df.empty
    assert not pct_change_df.empty
    assert not signal_df.empty

    # Index should be monotonically increasing by trade date
    assert ratio_mean_df.index.is_monotonic_increasing
    assert pct_change_df.index.is_monotonic_increasing
    assert signal_df.index.is_monotonic_increasing

    # Signal column must exist and only contain expected labels
    assert '交易信号' in signal_df.columns
    signal_values = set(signal_df['交易信号'].dropna().unique().tolist())
    expected = {
        param_cls.TradeSignal.LONG_GROWTH.value,
        param_cls.TradeSignal.LONG_VALUE.value,
        param_cls.TradeSignal.NO_SIGNAL.value,
    }
    assert signal_values.issubset(expected)


@pytest.mark.style_prep
def test_prepare_shibor_prices_data_basic_invariants():
    shibor_long_df = fetch_data_from_local(latest_date='99991231', table_name='SHIBOR_PRICES')

    shibor_prices_df = prepare_shibor_prices_data(long_raw_shibor_df=shibor_long_df)

    assert not shibor_prices_df.empty
    assert shibor_prices_df.index.is_monotonic_increasing

    # The configured price and rolling-mean columns must be present
    price_col = style_config.SHIBOR_PRICES_CONFIG['SHIBOR_PRICE_COL']
    mean_col = style_config.SHIBOR_PRICES_CONFIG['MEAN_COL']
    for col in (price_col, mean_col):
        assert col in shibor_prices_df.columns
