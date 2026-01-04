import pathlib
import sys

import pandas as pd
import pytest


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import financial_factors_config  # noqa: E402
from data_preparation.data_fetcher import fetch_financial_factors_stocks_from_local  # noqa: E402
from visualization.financial_factors_stocks import _filter_stock_pool  # noqa: E402


@pytest.mark.schema
def test_stock_pool_filtering_matches_signal_sum_for_selected_date() -> None:
    df = fetch_financial_factors_stocks_from_local(latest_date='99991231')
    assert isinstance(df, pd.DataFrame)

    if df.empty:
        return

    date_col = financial_factors_config.DATE_COL
    selected_date = str(df[date_col].iloc[0])
    date_mask = df[date_col].astype(str) == selected_date

    for strategy_cfg in financial_factors_config.STOCK_POOL_STRATEGIES.values():
        signal_col = strategy_cfg['signal_col']
        expected_count = int(pd.to_numeric(df.loc[date_mask, signal_col], errors='coerce').fillna(0).sum())
        pool_df = _filter_stock_pool(df=df, trade_date=selected_date, signal_col=signal_col)
        assert len(pool_df) == expected_count

