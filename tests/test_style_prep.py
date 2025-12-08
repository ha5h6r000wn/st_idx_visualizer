import pathlib
import sys

import pandas as pd
import pytest


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import config, param_cls, style_config  # noqa: E402
from data_preparation.data_fetcher import fetch_data_from_local, fetch_index_data_from_local  # noqa: E402
from data_preparation.data_processor import append_rolling_mean_column, apply_signal_from_conditions, reshape_long_df_into_wide_form  # noqa: E402
from visualization import data_visualizer  # noqa: E402
from visualization.style import (  # noqa: E402
    prepare_big_small_momentum_data,
    prepare_housing_invest_data,
    prepare_index_erp_data,
    prepare_index_turnover_data,
    prepare_shibor_prices_data,
    prepare_style_focus_data,
    prepare_term_spread_data,
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
def test_index_erp_style_chart_config_matches_bar_line_param():
    """Ensure the slim style chart config for ERP matches the existing bar+line config."""
    erp_chart_param = style_config.INDEX_ERP_CHART_PARAM
    erp_style_config = style_config.INDEX_ERP_STYLE_CHART_CONFIG

    assert erp_style_config.bar_axis_names == erp_chart_param.bar_param.axis_names
    assert erp_style_config.bar_axis_types == erp_chart_param.bar_param.axis_types
    assert erp_style_config.line_axis_names == erp_chart_param.line_param.axis_names
    assert erp_style_config.line_axis_types == erp_chart_param.line_param.axis_types
    assert erp_style_config.title == erp_chart_param.bar_param.title
    assert erp_style_config.bar_y_axis_format == erp_chart_param.bar_param.y_axis_format
    assert erp_style_config.line_y_axis_format == erp_chart_param.line_param.y_axis_format
    assert erp_style_config.line_stroke_dash == erp_chart_param.line_param.stroke_dash


@pytest.mark.style_prep
def test_prepare_bar_line_with_signal_data_respects_existing_signal_column():
    """prepare_bar_line_with_signal_data SHOULD NOT overwrite an existing signal column."""
    index = pd.date_range(start='2024-01-01', periods=5, freq='D').strftime('%Y%m%d')
    df = pd.DataFrame(
        {
            'TRADE_DT': index,
            'value': [1, 2, 3, 4, 5],
            'upper': [10, 10, 10, 10, 10],
            'lower': [0, 0, 0, 0, 0],
            'signal': ['A', 'B', 'C', 'D', 'E'],
        }
    ).set_index('TRADE_DT')

    bar_param = param_cls.SignalBarParam(
        axis_names={'X': 'TRADE_DT', 'Y': 'value', 'LEGEND': 'signal'},
        title='test',
        true_signal='UP',
        false_signal='DOWN',
        no_signal=None,
    )
    line_param = param_cls.LineParam(
        axis_names={'X': 'TRADE_DT', 'Y': 'upper', 'LEGEND': 'line_legend'},
        compared_cols=['upper', 'lower'],
        y_axis_format=config.CHART_NUM_FORMAT['float'],
    )
    chart_config = param_cls.BarLineWithSignalParam(
        dt_slider_param=None,
        bar_param=bar_param,
        line_param=line_param,
        isLineDrawn=True,
        isConvertedToPct=False,
        isSignalAssigned=False,
    )

    result = data_visualizer.prepare_bar_line_with_signal_data(dt_indexed_df=df, config=chart_config)

    assert 'signal' in result.columns
    assert result['signal'].tolist() == ['A', 'B', 'C', 'D', 'E']


@pytest.mark.style_prep
def test_prepare_bar_line_with_signal_data_computes_signal_when_missing():
    """prepare_bar_line_with_signal_data SHOULD compute signal when not present."""
    index = pd.date_range(start='2024-01-01', periods=3, freq='D').strftime('%Y%m%d')
    df = pd.DataFrame(
        {
            'TRADE_DT': index,
            'value': [1.0, 2.0, 3.0],
            'upper': [1.5, 1.5, 1.5],
            'lower': [0.5, 0.5, 0.5],
        }
    ).set_index('TRADE_DT')

    bar_param = param_cls.SignalBarParam(
        axis_names={'X': 'TRADE_DT', 'Y': 'value', 'LEGEND': 'signal'},
        title='test',
        true_signal='UP',
        false_signal='DOWN',
        no_signal='FLAT',
    )
    line_param = param_cls.LineParam(
        axis_names={'X': 'TRADE_DT', 'Y': 'upper', 'LEGEND': 'line_legend'},
        compared_cols=['upper', 'lower'],
        y_axis_format=config.CHART_NUM_FORMAT['float'],
    )
    chart_config = param_cls.BarLineWithSignalParam(
        dt_slider_param=None,
        bar_param=bar_param,
        line_param=line_param,
        isLineDrawn=True,
        isConvertedToPct=False,
        isSignalAssigned=False,
    )

    result = data_visualizer.prepare_bar_line_with_signal_data(dt_indexed_df=df, config=chart_config)

    assert 'signal' in result.columns
    signal_values = set(result['signal'].dropna().unique().tolist())
    expected = {'UP', 'DOWN', 'FLAT'}
    assert signal_values.issubset(expected)


@pytest.mark.style_prep
def test_get_custom_dt_with_slider_and_prepare_bar_line_with_signal_data_respects_window():
    """Slider default window SHOULD match DtSliderParam offsets and be used by prepare_bar_line_with_signal_data."""
    index = pd.date_range(start='2024-01-01', periods=10, freq='D').strftime('%Y%m%d')
    df = pd.DataFrame(
        {
            'TRADE_DT': index,
            'value': list(range(10)),
            'upper': [10] * 10,
            'lower': [0] * 10,
        }
    ).set_index('TRADE_DT')

    # Sanity: use the same base slider semantics as production: offsets from the end.
    dt_slider_param = param_cls.DtSliderParam(
        start_dt='20240101',
        default_start_offset=5,
        default_end_offset=1,
        key='TEST_SLIDER',
    )

    bar_param = param_cls.SignalBarParam(
        axis_names={'X': 'TRADE_DT', 'Y': 'value', 'LEGEND': 'signal'},
        title='test',
        true_signal='UP',
        false_signal='DOWN',
        no_signal='FLAT',
    )
    line_param = param_cls.LineParam(
        axis_names={'X': 'TRADE_DT', 'Y': 'upper', 'LEGEND': 'line_legend'},
        compared_cols=['upper', 'lower'],
        y_axis_format=config.CHART_NUM_FORMAT['float'],
    )
    chart_config = param_cls.BarLineWithSignalParam(
        dt_slider_param=dt_slider_param,
        bar_param=bar_param,
        line_param=line_param,
        isLineDrawn=True,
        isConvertedToPct=False,
        isSignalAssigned=False,
    )

    # Monkeypatch st.select_slider so that get_custom_dt_with_slider returns a deterministic window.
    trade_dt = df.index
    selected_dt = [dt for dt in trade_dt if dt >= dt_slider_param.start_dt]
    expected_window = (
        selected_dt[-dt_slider_param.default_start_offset],
        selected_dt[-dt_slider_param.default_end_offset],
    )

    def _fake_select_slider(*args, **kwargs):
        return expected_window

    original_select_slider = data_visualizer.st.select_slider
    try:
        data_visualizer.st.select_slider = _fake_select_slider  # type: ignore[assignment]
        result = data_visualizer.prepare_bar_line_with_signal_data(dt_indexed_df=df, config=chart_config)
    finally:
        data_visualizer.st.select_slider = original_select_slider  # type: ignore[assignment]

    # After prepare_bar_line_with_signal_data, result should have been sliced to the expected window.
    assert not result.empty
    assert result['TRADE_DT'].iloc[0] == expected_window[0]
    assert result['TRADE_DT'].iloc[-1] == expected_window[1]


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


@pytest.mark.style_prep
def test_prepare_index_turnover_data_basic_invariants():
    # Load all-A index valuation data and filter to the benchmark index
    _, idx_name_df = _load_style_index_data()

    # Use the same local fetcher and config wiring as generate_style_charts
    # does for A_IDX_VAL.
    from visualization.style import fetch_data_from_local as _fetch_data_from_local  # type: ignore

    latest_date = "99991231"
    long_raw_df_collection = {
        "A_IDX_VAL": _fetch_data_from_local(latest_date=latest_date, table_name="A_IDX_VAL")
    }

    long_wind_all_a_idx_val_df = long_raw_df_collection["A_IDX_VAL"].query(
        f'{style_config.DATA_COL_PARAM[param_cls.WindPortal.A_IDX_VAL].name_col} == "万得全A"'
    )

    turnover_df = prepare_index_turnover_data(long_wind_all_a_idx_val_df=long_wind_all_a_idx_val_df)

    assert not turnover_df.empty
    assert turnover_df.index.is_monotonic_increasing

    # Check that the rolling-mean columns and signal column exist
    for key in ("MEAN_COL", "MEAN_1M_COL", "MEAN_2Y_COL"):
        col = style_config.INDEX_TURNOVER_CONFIG[key]
        assert col in turnover_df.columns

    assert "交易信号" in turnover_df.columns
    signal_values = set(turnover_df["交易信号"].dropna().unique().tolist())
    expected = {
        param_cls.TradeSignal.LONG_GROWTH.value,
        param_cls.TradeSignal.LONG_VALUE.value,
    }
    assert signal_values.issubset(expected)


@pytest.mark.style_prep
def test_prepare_term_spread_data_basic_invariants():
    from data_preparation.data_fetcher import fetch_data_from_local as _fetch_table  # type: ignore

    latest_date = "99991231"
    long_raw_cn_bond_yield_df = _fetch_table(latest_date=latest_date, table_name="CN_BOND_YIELD")

    term_spread_df, yield_curve_df, wide_raw_cn_bond_yield_df = prepare_term_spread_data(
        long_raw_cn_bond_yield_df=long_raw_cn_bond_yield_df
    )

    # All returned frames should be non-empty with monotonic trade-date index
    for df in (term_spread_df, yield_curve_df, wide_raw_cn_bond_yield_df):
        assert not df.empty
        assert df.index.is_monotonic_increasing

    # Term spread frame must contain the configured spread and rolling-mean columns
    spread_col = style_config.TERM_SPREAD_CONFIG["TERM_SPREAD_COL"]
    mean_col = style_config.TERM_SPREAD_CONFIG["MEAN_COL"]
    for col in (spread_col, mean_col):
        assert col in term_spread_df.columns


@pytest.mark.style_prep
def test_prepare_index_erp_data_basic_invariants():
    # Reuse the same data wiring as generate_style_charts:
    # - CN_BOND_YIELD wide frame from prepare_term_spread_data
    # - A_IDX_VAL filtered to the benchmark index for ERP.
    latest_date = "99991231"

    long_raw_cn_bond_yield_df = fetch_data_from_local(latest_date=latest_date, table_name="CN_BOND_YIELD")
    term_spread_df, yield_curve_df, wide_raw_cn_bond_yield_df = prepare_term_spread_data(
        long_raw_cn_bond_yield_df=long_raw_cn_bond_yield_df
    )

    long_a_idx_val_df = fetch_data_from_local(latest_date=latest_date, table_name="A_IDX_VAL")
    name_col = style_config.DATA_COL_PARAM[param_cls.WindPortal.A_IDX_VAL].name_col
    long_wind_all_a_idx_val_df = long_a_idx_val_df.query(f"{name_col} == '万得全A'")

    wide_erp_df, erp_conditions = prepare_index_erp_data(
        long_wind_all_a_idx_val_df=long_wind_all_a_idx_val_df,
        wide_raw_cn_bond_yield_df=wide_raw_cn_bond_yield_df,
    )

    assert not wide_erp_df.empty
    assert wide_erp_df.index.is_monotonic_increasing

    # ERP frame must contain ERP value, rolling mean, and quantile bands
    erp_col = style_config.INDEX_ERP_CONFIG["ERP_COL"]
    mean_col = "近一月均值"
    ceil_col = style_config.INDEX_ERP_CONFIG["QUANTILE_CEILING_COL"]
    floor_col = style_config.INDEX_ERP_CONFIG["QUANTILE_FLOOR_COL"]
    for col in (erp_col, mean_col, ceil_col, floor_col):
        assert col in wide_erp_df.columns

    # Conditions should be aligned with ERP frame and boolean
    assert isinstance(erp_conditions, list)
    assert len(erp_conditions) == 2
    for cond in erp_conditions:
        assert len(cond) == len(wide_erp_df)
        assert cond.dtype == bool


@pytest.mark.style_prep
def test_index_erp_bar_line_pipeline_basic_invariants():
    """End-to-end invariants for ERP data prep + bar+line+signal helper."""
    latest_date = "99991231"

    long_raw_cn_bond_yield_df = fetch_data_from_local(latest_date=latest_date, table_name="CN_BOND_YIELD")
    _, _, wide_raw_cn_bond_yield_df = prepare_term_spread_data(long_raw_cn_bond_yield_df=long_raw_cn_bond_yield_df)

    long_a_idx_val_df = fetch_data_from_local(latest_date=latest_date, table_name="A_IDX_VAL")
    name_col = style_config.DATA_COL_PARAM[param_cls.WindPortal.A_IDX_VAL].name_col
    long_wind_all_a_idx_val_df = long_a_idx_val_df.query(f"{name_col} == '万得全A'")

    wide_erp_df, erp_conditions = prepare_index_erp_data(
        long_wind_all_a_idx_val_df=long_wind_all_a_idx_val_df,
        wide_raw_cn_bond_yield_df=wide_raw_cn_bond_yield_df,
    )

    # Apply the same signal assignment logic as generate_style_charts.
    erp_choices = [
        style_config.INDEX_ERP_CHART_PARAM.bar_param.true_signal,
        style_config.INDEX_ERP_CHART_PARAM.bar_param.false_signal,
    ]
    wide_erp_df = apply_signal_from_conditions(
        df=wide_erp_df,
        signal_col=style_config.INDEX_ERP_CONFIG["SIGNAL_COL"],
        conditions=erp_conditions,
        choices=erp_choices,
        default=style_config.INDEX_ERP_CHART_PARAM.bar_param.no_signal,
    )

    # Use full date range as custom window to avoid Streamlit slider state.
    idx = wide_erp_df.index
    custom_dt = (idx[0], idx[-1])

    result = data_visualizer.prepare_bar_line_with_signal_data(
        dt_indexed_df=wide_erp_df,
        config=style_config.INDEX_ERP_CHART_PARAM,
        custom_dt=custom_dt,
    )

    assert not result.empty

    # TRADE_DT column should exist and be monotonically increasing.
    dt_col = style_config.INDEX_ERP_COL_PARAM.dt_col
    assert dt_col in result.columns
    assert result[dt_col].is_monotonic_increasing

    # Bar axis columns must exist.
    bar_axis_names = style_config.INDEX_ERP_CHART_PARAM.bar_param.axis_names
    for col in bar_axis_names.values():
        assert col in result.columns

    # Line X/LEGEND axis columns must exist. The Y axis is a semantic
    # alias ("分位数") and does not correspond to a direct column on
    # the wide frame.
    line_axis_names = style_config.INDEX_ERP_CHART_PARAM.line_param.axis_names
    for col in (line_axis_names['X'], line_axis_names['LEGEND']):
        assert col in result.columns

    # ERP core columns must still be present after helper processing.
    erp_col = style_config.INDEX_ERP_CONFIG["ERP_COL"]
    mean_col = "近一月均值"
    ceil_col = style_config.INDEX_ERP_CONFIG["QUANTILE_CEILING_COL"]
    floor_col = style_config.INDEX_ERP_CONFIG["QUANTILE_FLOOR_COL"]
    for col in (erp_col, mean_col, ceil_col, floor_col):
        assert col in result.columns

    # Signal column and its value set should remain valid.
    signal_col = style_config.INDEX_ERP_CONFIG["SIGNAL_COL"]
    assert signal_col in result.columns
    signal_values = set(result[signal_col].dropna().unique().tolist())
    expected = {
        style_config.INDEX_ERP_CONFIG["TRUE_SIGNAL"],
        style_config.INDEX_ERP_CONFIG["FALSE_SIGNAL"],
        style_config.INDEX_ERP_CONFIG["NO_SIGNAL"],
    }
    assert signal_values.issubset(expected)


@pytest.mark.style_prep
def test_prepare_big_small_momentum_data_basic_invariants():
    raw_wide_idx_df, idx_name_df = _load_style_index_data()

    ratio_mean_df, pct_change_df, signal_df = prepare_big_small_momentum_data(
        raw_wide_idx_df=raw_wide_idx_df,
        idx_name_df=idx_name_df,
    )

    assert not ratio_mean_df.empty
    assert not pct_change_df.empty
    assert not signal_df.empty

    assert ratio_mean_df.index.is_monotonic_increasing
    assert pct_change_df.index.is_monotonic_increasing
    assert signal_df.index.is_monotonic_increasing

    # Signal column and value set
    assert "交易信号" in signal_df.columns
    signal_values = set(signal_df["交易信号"].dropna().unique().tolist())
    expected = {
        param_cls.TradeSignal.LONG_SMALL.value,
        param_cls.TradeSignal.LONG_BIG.value,
        param_cls.TradeSignal.NO_SIGNAL.value,
    }
    assert signal_values.issubset(expected)


@pytest.mark.style_prep
def test_prepare_style_focus_data_basic_invariants():
    raw_wide_idx_df, idx_name_df = _load_style_index_data()

    # Build big/small momentum signals
    _, _, big_small_signal_df = prepare_big_small_momentum_data(
        raw_wide_idx_df=raw_wide_idx_df,
        idx_name_df=idx_name_df,
    )

    latest_date = "99991231"
    long_a_idx_val_df = fetch_data_from_local(latest_date=latest_date, table_name="A_IDX_VAL")
    name_col = style_config.DATA_COL_PARAM[param_cls.WindPortal.A_IDX_VAL].name_col
    long_big_small_idx_val_df = long_a_idx_val_df.query(f"{name_col} in ('沪深300', '中证1000')")

    style_focus_df = prepare_style_focus_data(
        long_big_small_idx_val_df=long_big_small_idx_val_df,
        big_small_df=big_small_signal_df,
    )

    assert not style_focus_df.empty
    assert style_focus_df.index.is_monotonic_increasing

    # Check presence of style-focus core columns and signal
    focus_col = style_config.STYLE_FOCUS_CONFIG["STYLE_FOCUS_COL"]
    ceil_col = style_config.STYLE_FOCUS_CONFIG["QUANTILE_CEILING_COL"]
    floor_col = style_config.STYLE_FOCUS_CONFIG["QUANTILE_FLOOR_COL"]
    for col in (focus_col, ceil_col, floor_col):
        assert col in style_focus_df.columns

    assert style_config.STYLE_FOCUS_CONFIG["SIGNAL_COL"] in style_focus_df.columns
    signal_values = set(style_focus_df[style_config.STYLE_FOCUS_CONFIG["SIGNAL_COL"]].dropna().unique().tolist())
    expected = {
        style_config.STYLE_FOCUS_CONFIG["TRUE_SIGNAL"],
        style_config.STYLE_FOCUS_CONFIG["FALSE_SIGNAL"],
        style_config.STYLE_FOCUS_CONFIG["NO_SIGNAL"],
    }
    assert signal_values.issubset(expected)


@pytest.mark.style_prep
def test_prepare_housing_invest_and_credit_expansion_basic_invariants():
    latest_date = "99991231"
    long_edb_df = fetch_data_from_local(latest_date=latest_date, table_name="EDB")

    wide_raw_edb_df = reshape_long_df_into_wide_form(
        long_df=long_edb_df,
        index_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.EDB].dt_col,
        name_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.EDB].name_col,
        value_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.EDB].value_col,
    )

    # Housing investment YoY prep
    housing_df = prepare_housing_invest_data(wide_raw_edb_df=wide_raw_edb_df)
    assert not housing_df.empty
    assert housing_df.index.is_monotonic_increasing

    for col in (
        style_config.HOUSING_INVEST_CONFIG["YOY_COL"],
        style_config.HOUSING_INVEST_CONFIG["PRE_YOY_COL"],
    ):
        assert col in housing_df.columns

    # Credit expansion prep (inline data-prep replicated from generate_style_charts)
    credit_df = (
        wide_raw_edb_df[[style_config.CREDIT_EXPANSION_CONFIG["CREDIT_EXPANSION_COL"]]]
        .copy()
        .rename(
            columns={
                style_config.CREDIT_EXPANSION_CONFIG["CREDIT_EXPANSION_COL"]: style_config.CREDIT_EXPANSION_CONFIG[
                    "YOY_COL"
                ],
            }
        )
    )

    credit_df = append_rolling_mean_column(
        df=credit_df,
        window_name=style_config.CREDIT_EXPANSION_CONFIG["ROLLING_WINDOW"],
        window_size=style_config.CREDIT_EXPANSION_CONFIG["ROLLING_WINDOW_SIZE"],
        rolling_mean_col=style_config.CREDIT_EXPANSION_CONFIG["MEAN_COL"],
    )

    assert not credit_df.empty
    assert credit_df.index.is_monotonic_increasing

    for col in (
        style_config.CREDIT_EXPANSION_CONFIG["YOY_COL"],
        style_config.CREDIT_EXPANSION_CONFIG["MEAN_COL"],
    ):
        assert col in credit_df.columns

    conditions = [
        credit_df[style_config.CREDIT_EXPANSION_CONFIG["YOY_COL"]]
        >= credit_df[style_config.CREDIT_EXPANSION_CONFIG["MEAN_COL"]],
    ]
    choices = [
        style_config.CREDIT_EXPANSION_CONFIG["TRUE_SIGNAL"],
    ]
    credit_df = apply_signal_from_conditions(
        df=credit_df,
        signal_col=style_config.CREDIT_EXPANSION_CONFIG["SIGNAL_COL"],
        conditions=conditions,
        choices=choices,
        default=style_config.CREDIT_EXPANSION_CONFIG["FALSE_SIGNAL"],
    )

    assert style_config.CREDIT_EXPANSION_CONFIG["SIGNAL_COL"] in credit_df.columns
    signal_values = set(credit_df[style_config.CREDIT_EXPANSION_CONFIG["SIGNAL_COL"]].dropna().unique().tolist())
    expected = {
        style_config.CREDIT_EXPANSION_CONFIG["TRUE_SIGNAL"],
        style_config.CREDIT_EXPANSION_CONFIG["FALSE_SIGNAL"],
    }
    assert signal_values.issubset(expected)
