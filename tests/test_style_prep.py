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
def test_index_erp_style_chart_builds_equivalent_bar_line_config():
    """Ensure the builder reproduces the existing ERP bar+line config."""
    erp_chart_param = style_config.INDEX_ERP_CHART_PARAM
    erp_style_config = style_config.INDEX_ERP_STYLE_CHART_CONFIG

    built_config = data_visualizer.build_bar_line_with_signal_param_for_style_chart(
        style_config=erp_style_config,
        dt_slider_param=erp_chart_param.dt_slider_param,
        true_signal=style_config.INDEX_ERP_CONFIG["TRUE_SIGNAL"],
        false_signal=style_config.INDEX_ERP_CONFIG["FALSE_SIGNAL"],
        no_signal=style_config.INDEX_ERP_CONFIG["NO_SIGNAL"],
        signal_order=erp_chart_param.bar_param.signal_order,
        compared_cols=erp_chart_param.line_param.compared_cols,
        is_converted_to_pct=erp_chart_param.isConvertedToPct,
    )

    # Bar param equivalence
    assert built_config.bar_param.axis_names == erp_chart_param.bar_param.axis_names
    assert built_config.bar_param.axis_types == erp_chart_param.bar_param.axis_types
    assert built_config.bar_param.title == erp_chart_param.bar_param.title
    assert built_config.bar_param.y_axis_format == erp_chart_param.bar_param.y_axis_format
    assert built_config.bar_param.true_signal == erp_chart_param.bar_param.true_signal
    assert built_config.bar_param.false_signal == erp_chart_param.bar_param.false_signal
    assert built_config.bar_param.no_signal == erp_chart_param.bar_param.no_signal
    assert built_config.bar_param.signal_order == erp_chart_param.bar_param.signal_order

    # Line param equivalence
    assert built_config.line_param.axis_names == erp_chart_param.line_param.axis_names
    assert built_config.line_param.axis_types == erp_chart_param.line_param.axis_types
    assert built_config.line_param.y_axis_format == erp_chart_param.line_param.y_axis_format
    assert built_config.line_param.stroke_dash == erp_chart_param.line_param.stroke_dash
    assert built_config.line_param.color == erp_chart_param.line_param.color
    assert built_config.line_param.compared_cols == erp_chart_param.line_param.compared_cols

    # Top-level flags
    assert built_config.dt_slider_param == erp_chart_param.dt_slider_param
    assert built_config.isLineDrawn == erp_chart_param.isLineDrawn
    assert built_config.isConvertedToPct == erp_chart_param.isConvertedToPct
    assert built_config.isSignalAssigned is True


@pytest.mark.style_prep
def test_index_erp_2_style_chart_config_matches_bar_line_param():
    """Ensure the slim style chart config for ERP_2 matches the existing bar+line config."""
    erp_2_chart_param = style_config.INDEX_ERP_2_CHART_PARAM
    erp_2_style_config = style_config.INDEX_ERP_2_STYLE_CHART_CONFIG

    assert erp_2_style_config.bar_axis_names == erp_2_chart_param.bar_param.axis_names
    assert erp_2_style_config.bar_axis_types == erp_2_chart_param.bar_param.axis_types
    assert erp_2_style_config.line_axis_names == erp_2_chart_param.line_param.axis_names
    assert erp_2_style_config.line_axis_types == erp_2_chart_param.line_param.axis_types
    assert erp_2_style_config.title == erp_2_chart_param.bar_param.title
    assert erp_2_style_config.bar_y_axis_format == erp_2_chart_param.bar_param.y_axis_format
    assert erp_2_style_config.line_y_axis_format == erp_2_chart_param.line_param.y_axis_format
    assert erp_2_style_config.line_stroke_dash == erp_2_chart_param.line_param.stroke_dash


@pytest.mark.style_prep
def test_index_erp_2_style_chart_builds_equivalent_bar_line_config():
    """Ensure the builder reproduces the existing ERP_2 bar+line config."""
    erp_2_chart_param = style_config.INDEX_ERP_2_CHART_PARAM
    erp_2_style_config = style_config.INDEX_ERP_2_STYLE_CHART_CONFIG

    built_config = data_visualizer.build_bar_line_with_signal_param_for_style_chart(
        style_config=erp_2_style_config,
        dt_slider_param=erp_2_chart_param.dt_slider_param,
        true_signal=erp_2_chart_param.bar_param.true_signal,
        false_signal=erp_2_chart_param.bar_param.false_signal,
        no_signal=erp_2_chart_param.bar_param.no_signal,
        signal_order=erp_2_chart_param.bar_param.signal_order,
        compared_cols=erp_2_chart_param.line_param.compared_cols,
        is_converted_to_pct=erp_2_chart_param.isConvertedToPct,
    )

    # Bar param equivalence
    assert built_config.bar_param.axis_names == erp_2_chart_param.bar_param.axis_names
    assert built_config.bar_param.axis_types == erp_2_chart_param.bar_param.axis_types
    assert built_config.bar_param.title == erp_2_chart_param.bar_param.title
    assert built_config.bar_param.y_axis_format == erp_2_chart_param.bar_param.y_axis_format
    assert built_config.bar_param.true_signal == erp_2_chart_param.bar_param.true_signal
    assert built_config.bar_param.false_signal == erp_2_chart_param.bar_param.false_signal
    assert built_config.bar_param.no_signal == erp_2_chart_param.bar_param.no_signal
    assert built_config.bar_param.signal_order == erp_2_chart_param.bar_param.signal_order

    # Line param equivalence
    assert built_config.line_param.axis_names == erp_2_chart_param.line_param.axis_names
    assert built_config.line_param.axis_types == erp_2_chart_param.line_param.axis_types
    assert built_config.line_param.y_axis_format == erp_2_chart_param.line_param.y_axis_format
    assert built_config.line_param.stroke_dash == erp_2_chart_param.line_param.stroke_dash
    assert built_config.line_param.color == erp_2_chart_param.line_param.color
    assert built_config.line_param.compared_cols == erp_2_chart_param.line_param.compared_cols

    # Top-level flags
    assert built_config.dt_slider_param == erp_2_chart_param.dt_slider_param
    assert built_config.isLineDrawn == erp_2_chart_param.isLineDrawn
    assert built_config.isConvertedToPct == erp_2_chart_param.isConvertedToPct
    assert built_config.isSignalAssigned is True


@pytest.mark.style_prep
def test_credit_expansion_style_chart_config_matches_bar_line_param():
    """Ensure the slim style chart config for credit expansion matches the existing bar+line config."""
    ce_chart_param = style_config.CREDIT_EXPANSION_CHART_PARAM
    ce_style_config = style_config.CREDIT_EXPANSION_STYLE_CHART_CONFIG

    assert ce_style_config.bar_axis_names == ce_chart_param.bar_param.axis_names
    assert ce_style_config.bar_axis_types == ce_chart_param.bar_param.axis_types
    assert ce_style_config.line_axis_names == ce_chart_param.line_param.axis_names
    assert ce_style_config.line_axis_types == ce_chart_param.line_param.axis_types
    assert ce_style_config.title == ce_chart_param.bar_param.title
    assert ce_style_config.bar_y_axis_format == ce_chart_param.bar_param.y_axis_format
    assert ce_style_config.line_y_axis_format == ce_chart_param.line_param.y_axis_format
    assert ce_style_config.line_stroke_dash == ce_chart_param.line_param.stroke_dash


@pytest.mark.style_prep
def test_index_erp_style_draw_helper_smoke():
    """Smoke test for the style-specific ERP draw helper."""
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

    idx = wide_erp_df.index
    custom_dt = (idx[0], idx[-1])

    def _fake_select_slider(*args, **kwargs):
        return custom_dt

    def _fake_altair_chart(*args, **kwargs):
        return None

    original_select_slider = data_visualizer.st.select_slider
    original_altair_chart = data_visualizer.st.altair_chart
    try:
        data_visualizer.st.select_slider = _fake_select_slider  # type: ignore[assignment]
        data_visualizer.st.altair_chart = _fake_altair_chart  # type: ignore[assignment]

        data_visualizer.draw_style_bar_line_chart_with_highlighted_signal(
            dt_indexed_df=wide_erp_df,
            style_chart_config=style_config.INDEX_ERP_STYLE_CHART_CONFIG,
            dt_slider_param=style_config.INDEX_ERP_CHART_PARAM.dt_slider_param,
            true_signal=style_config.INDEX_ERP_CONFIG["TRUE_SIGNAL"],
            false_signal=style_config.INDEX_ERP_CONFIG["FALSE_SIGNAL"],
            no_signal=style_config.INDEX_ERP_CONFIG["NO_SIGNAL"],
            signal_order=style_config.INDEX_ERP_CHART_PARAM.bar_param.signal_order,
            compared_cols=style_config.INDEX_ERP_CHART_PARAM.line_param.compared_cols,
            is_converted_to_pct=style_config.INDEX_ERP_CHART_PARAM.isConvertedToPct,
        )
    finally:
        data_visualizer.st.select_slider = original_select_slider  # type: ignore[assignment]
        data_visualizer.st.altair_chart = original_altair_chart  # type: ignore[assignment]


@pytest.mark.style_prep
def test_index_erp_2_style_draw_helper_smoke():
    """Smoke test for the style-specific ERP_2 draw helper."""
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

    erp_2_choices = [
        style_config.INDEX_ERP_2_CHART_PARAM.bar_param.true_signal,
        style_config.INDEX_ERP_2_CHART_PARAM.bar_param.false_signal,
    ]
    wide_erp_2_df = apply_signal_from_conditions(
        df=wide_erp_df,
        signal_col=style_config.INDEX_ERP_CONFIG["SIGNAL_COL"],
        conditions=erp_conditions,
        choices=erp_2_choices,
        default=style_config.INDEX_ERP_2_CHART_PARAM.bar_param.no_signal,
    )

    idx = wide_erp_2_df.index
    custom_dt = (idx[0], idx[-1])

    def _fake_select_slider(*args, **kwargs):
        return custom_dt

    def _fake_altair_chart(*args, **kwargs):
        return None

    original_select_slider = data_visualizer.st.select_slider
    original_altair_chart = data_visualizer.st.altair_chart
    try:
        data_visualizer.st.select_slider = _fake_select_slider  # type: ignore[assignment]
        data_visualizer.st.altair_chart = _fake_altair_chart  # type: ignore[assignment]

        data_visualizer.draw_style_bar_line_chart_with_highlighted_signal(
            dt_indexed_df=wide_erp_2_df,
            style_chart_config=style_config.INDEX_ERP_2_STYLE_CHART_CONFIG,
            dt_slider_param=style_config.INDEX_ERP_2_CHART_PARAM.dt_slider_param,
            true_signal=style_config.INDEX_ERP_2_CHART_PARAM.bar_param.true_signal,
            false_signal=style_config.INDEX_ERP_2_CHART_PARAM.bar_param.false_signal,
            no_signal=style_config.INDEX_ERP_2_CHART_PARAM.bar_param.no_signal,
            signal_order=style_config.INDEX_ERP_2_CHART_PARAM.bar_param.signal_order,
            compared_cols=style_config.INDEX_ERP_2_CHART_PARAM.line_param.compared_cols,
            is_converted_to_pct=style_config.INDEX_ERP_2_CHART_PARAM.isConvertedToPct,
        )
    finally:
        data_visualizer.st.select_slider = original_select_slider  # type: ignore[assignment]
        data_visualizer.st.altair_chart = original_altair_chart  # type: ignore[assignment]


@pytest.mark.style_prep
def test_credit_expansion_style_draw_helper_smoke():
    """Smoke test for the style-specific credit expansion draw helper."""
    latest_date = "99991231"
    long_edb_df = fetch_data_from_local(latest_date=latest_date, table_name="EDB")

    wide_raw_edb_df = reshape_long_df_into_wide_form(
        long_df=long_edb_df,
        index_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.EDB].dt_col,
        name_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.EDB].name_col,
        value_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.EDB].value_col,
    )

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

    idx = credit_df.index
    custom_dt = (idx[0], idx[-1])

    def _fake_select_slider(*args, **kwargs):
        return custom_dt

    def _fake_altair_chart(*args, **kwargs):
        return None

    original_select_slider = data_visualizer.st.select_slider
    original_altair_chart = data_visualizer.st.altair_chart
    try:
        data_visualizer.st.select_slider = _fake_select_slider  # type: ignore[assignment]
        data_visualizer.st.altair_chart = _fake_altair_chart  # type: ignore[assignment]

        data_visualizer.draw_style_bar_line_chart_with_highlighted_signal(
            dt_indexed_df=credit_df,
            style_chart_config=style_config.CREDIT_EXPANSION_STYLE_CHART_CONFIG,
            dt_slider_param=style_config.CREDIT_EXPANSION_CHART_PARAM.dt_slider_param,
            true_signal=style_config.CREDIT_EXPANSION_CONFIG["TRUE_SIGNAL"],
            false_signal=style_config.CREDIT_EXPANSION_CONFIG["FALSE_SIGNAL"],
            no_signal=None,
            signal_order=style_config.CREDIT_EXPANSION_CHART_PARAM.bar_param.signal_order,
            compared_cols=style_config.CREDIT_EXPANSION_CHART_PARAM.line_param.compared_cols,
            is_converted_to_pct=style_config.CREDIT_EXPANSION_CHART_PARAM.isConvertedToPct,
        )
    finally:
        data_visualizer.st.select_slider = original_select_slider  # type: ignore[assignment]
        data_visualizer.st.altair_chart = original_altair_chart  # type: ignore[assignment]


@pytest.mark.style_prep
def test_style_focus_style_draw_helper_smoke():
    """Smoke test for the style-specific style focus draw helper."""
    raw_wide_idx_df, idx_name_df = _load_style_index_data()

    # Build big/small momentum signals as in the style page.
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

    idx = style_focus_df.index
    custom_dt = (idx[0], idx[-1])

    def _fake_select_slider(*args, **kwargs):
        return custom_dt

    def _fake_altair_chart(*args, **kwargs):
        return None

    original_select_slider = data_visualizer.st.select_slider
    original_altair_chart = data_visualizer.st.altair_chart
    try:
        data_visualizer.st.select_slider = _fake_select_slider  # type: ignore[assignment]
        data_visualizer.st.altair_chart = _fake_altair_chart  # type: ignore[assignment]

        data_visualizer.draw_style_bar_line_chart_with_highlighted_signal(
            dt_indexed_df=style_focus_df,
            style_chart_config=style_config.STYLE_FOCUS_STYLE_CHART_CONFIG,
            dt_slider_param=style_config.STYLE_FOCUS_CHART_PARAM.dt_slider_param,
            true_signal=style_config.STYLE_FOCUS_CONFIG["TRUE_SIGNAL"],
            false_signal=style_config.STYLE_FOCUS_CONFIG["FALSE_SIGNAL"],
            no_signal=style_config.STYLE_FOCUS_CONFIG["NO_SIGNAL"],
            signal_order=style_config.STYLE_FOCUS_CHART_PARAM.bar_param.signal_order,
            compared_cols=style_config.STYLE_FOCUS_CHART_PARAM.line_param.compared_cols,
            is_converted_to_pct=style_config.STYLE_FOCUS_CHART_PARAM.isConvertedToPct,
        )
    finally:
        data_visualizer.st.select_slider = original_select_slider  # type: ignore[assignment]
        data_visualizer.st.altair_chart = original_altair_chart  # type: ignore[assignment]


@pytest.mark.style_prep
def test_shibor_style_draw_helper_smoke():
    """Smoke test for the style-specific Shibor draw helper."""
    latest_date = "99991231"
    shibor_long_df = fetch_data_from_local(latest_date=latest_date, table_name="SHIBOR_PRICES")

    shibor_prices_df = prepare_shibor_prices_data(long_raw_shibor_df=shibor_long_df)

    shibor_conditions = [
        shibor_prices_df[style_config.SHIBOR_PRICES_CONFIG["SHIBOR_PRICE_COL"]]
        >= shibor_prices_df[style_config.SHIBOR_PRICES_CONFIG["MEAN_COL"]],
    ]
    shibor_choices = [
        style_config.SHIBOR_PRICES_CONFIG["TRUE_SIGNAL"],
    ]
    shibor_prices_df = apply_signal_from_conditions(
        df=shibor_prices_df,
        signal_col=style_config.SHIBOR_PRICES_CONFIG["SIGNAL_COL"],
        conditions=shibor_conditions,
        choices=shibor_choices,
        default=style_config.SHIBOR_PRICES_CONFIG["FALSE_SIGNAL"],
    )

    idx = shibor_prices_df.index
    custom_dt = (idx[0], idx[-1])

    def _fake_select_slider(*args, **kwargs):
        return custom_dt

    def _fake_altair_chart(*args, **kwargs):
        return None

    original_select_slider = data_visualizer.st.select_slider
    original_altair_chart = data_visualizer.st.altair_chart
    try:
        data_visualizer.st.select_slider = _fake_select_slider  # type: ignore[assignment]
        data_visualizer.st.altair_chart = _fake_altair_chart  # type: ignore[assignment]

        data_visualizer.draw_style_bar_line_chart_with_highlighted_signal(
            dt_indexed_df=shibor_prices_df,
            style_chart_config=style_config.SHIBOR_PRICES_STYLE_CHART_CONFIG,
            dt_slider_param=style_config.SHIBOR_PRICES_CHART_PARAM.dt_slider_param,
            true_signal=style_config.SHIBOR_PRICES_CONFIG["TRUE_SIGNAL"],
            false_signal=style_config.SHIBOR_PRICES_CONFIG["FALSE_SIGNAL"],
            no_signal=None,
            signal_order=style_config.SHIBOR_PRICES_CHART_PARAM.bar_param.signal_order,
            compared_cols=style_config.SHIBOR_PRICES_CHART_PARAM.line_param.compared_cols,
            is_converted_to_pct=style_config.SHIBOR_PRICES_CHART_PARAM.isConvertedToPct,
        )
    finally:
        data_visualizer.st.select_slider = original_select_slider  # type: ignore[assignment]
        data_visualizer.st.altair_chart = original_altair_chart  # type: ignore[assignment]


@pytest.mark.style_prep
def test_index_turnover_style_draw_helper_smoke():
    """Smoke test for the style-specific index turnover draw helper."""
    from visualization.style import fetch_data_from_local as _fetch_data_from_local  # type: ignore

    latest_date = "99991231"
    long_raw_df_collection = {
        "A_IDX_VAL": _fetch_data_from_local(latest_date=latest_date, table_name="A_IDX_VAL")
    }

    long_wind_all_a_idx_val_df = long_raw_df_collection["A_IDX_VAL"].query(
        f'{style_config.DATA_COL_PARAM[param_cls.WindPortal.A_IDX_VAL].name_col} == "万得全A"'
    )

    turnover_df = prepare_index_turnover_data(long_wind_all_a_idx_val_df=long_wind_all_a_idx_val_df)

    idx = turnover_df.index
    custom_dt = (idx[0], idx[-1])

    def _fake_select_slider(*args, **kwargs):
        return custom_dt

    def _fake_altair_chart(*args, **kwargs):
        return None

    original_select_slider = data_visualizer.st.select_slider
    original_altair_chart = data_visualizer.st.altair_chart
    try:
        data_visualizer.st.select_slider = _fake_select_slider  # type: ignore[assignment]
        data_visualizer.st.altair_chart = _fake_altair_chart  # type: ignore[assignment]

        data_visualizer.draw_style_bar_line_chart_with_highlighted_signal(
            dt_indexed_df=turnover_df,
            style_chart_config=style_config.INDEX_TURNOVER_STYLE_CHART_CONFIG,
            dt_slider_param=style_config.INDEX_TURNOVER_CHART_PARAM.dt_slider_param,
            true_signal=style_config.INDEX_TURNOVER_CONFIG["TRUE_SIGNAL"],
            false_signal=style_config.INDEX_TURNOVER_CONFIG["FALSE_SIGNAL"],
            no_signal=None,
            signal_order=style_config.INDEX_TURNOVER_CHART_PARAM.bar_param.signal_order,
            compared_cols=style_config.INDEX_TURNOVER_CHART_PARAM.line_param.compared_cols,
            is_converted_to_pct=style_config.INDEX_TURNOVER_CHART_PARAM.isConvertedToPct,
        )
    finally:
        data_visualizer.st.select_slider = original_select_slider  # type: ignore[assignment]
        data_visualizer.st.altair_chart = original_altair_chart  # type: ignore[assignment]


@pytest.mark.style_prep
def test_housing_invest_style_draw_helper_smoke():
    """Smoke test for the style-specific housing investment draw helper."""
    latest_date = "99991231"
    long_edb_df = fetch_data_from_local(latest_date=latest_date, table_name="EDB")

    wide_raw_edb_df = reshape_long_df_into_wide_form(
        long_df=long_edb_df,
        index_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.EDB].dt_col,
        name_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.EDB].name_col,
        value_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.EDB].value_col,
    )

    housing_df = prepare_housing_invest_data(wide_raw_edb_df=wide_raw_edb_df)

    housing_invest_conditions = [
        housing_df[style_config.HOUSING_INVEST_CONFIG["YOY_COL"]]
        >= housing_df[style_config.HOUSING_INVEST_CONFIG["PRE_YOY_COL"]],
    ]
    housing_invest_choices = [
        style_config.HOUSING_INVEST_CONFIG["TRUE_SIGNAL"],
    ]
    housing_df = apply_signal_from_conditions(
        df=housing_df,
        signal_col=style_config.HOUSING_INVEST_CONFIG["SIGNAL_COL"],
        conditions=housing_invest_conditions,
        choices=housing_invest_choices,
        default=style_config.HOUSING_INVEST_CONFIG["FALSE_SIGNAL"],
    )

    idx = housing_df.index
    custom_dt = (idx[0], idx[-1])

    def _fake_select_slider(*args, **kwargs):
        return custom_dt

    def _fake_altair_chart(*args, **kwargs):
        return None

    original_select_slider = data_visualizer.st.select_slider
    original_altair_chart = data_visualizer.st.altair_chart
    try:
        data_visualizer.st.select_slider = _fake_select_slider  # type: ignore[assignment]
        data_visualizer.st.altair_chart = _fake_altair_chart  # type: ignore[assignment]

        data_visualizer.draw_style_bar_line_chart_with_highlighted_signal(
            dt_indexed_df=housing_df,
            style_chart_config=style_config.HOUSING_INVEST_STYLE_CHART_CONFIG,
            dt_slider_param=style_config.HOUSING_INVEST_CHART_PARAM.dt_slider_param,
            true_signal=style_config.HOUSING_INVEST_CONFIG["TRUE_SIGNAL"],
            false_signal=style_config.HOUSING_INVEST_CONFIG["FALSE_SIGNAL"],
            no_signal=None,
            signal_order=style_config.HOUSING_INVEST_CHART_PARAM.bar_param.signal_order,
            compared_cols=style_config.HOUSING_INVEST_CHART_PARAM.line_param.compared_cols,
            is_converted_to_pct=style_config.HOUSING_INVEST_CHART_PARAM.isConvertedToPct,
        )
    finally:
        data_visualizer.st.select_slider = original_select_slider  # type: ignore[assignment]
        data_visualizer.st.altair_chart = original_altair_chart  # type: ignore[assignment]


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
def test_prepare_bar_line_with_signal_data_converts_to_pct_when_flag_set():
    """prepare_bar_line_with_signal_data SHOULD divide numeric columns by 100 when isConvertedToPct is True."""
    index = pd.date_range(start='2024-01-01', periods=3, freq='D').strftime('%Y%m%d')
    df = pd.DataFrame(
        {
            'TRADE_DT': index,
            'value': [1.0, 2.0, 3.0],
            'baseline': [0.5, 1.0, 1.5],
            'signal': ['UP', 'DOWN', 'UP'],
        }
    ).set_index('TRADE_DT')

    bar_param = param_cls.SignalBarParam(
        axis_names={'X': 'TRADE_DT', 'Y': 'value', 'LEGEND': 'signal'},
        title='test',
        true_signal='UP',
        false_signal='DOWN',
        no_signal=None,
        y_axis_format=config.CHART_NUM_FORMAT['float'],
    )
    line_param = param_cls.LineParam(
        axis_names={'X': 'TRADE_DT', 'Y': 'baseline', 'LEGEND': 'line_legend'},
        y_axis_format=config.CHART_NUM_FORMAT['float'],
    )
    chart_config = param_cls.BarLineWithSignalParam(
        dt_slider_param=None,
        bar_param=bar_param,
        line_param=line_param,
        isLineDrawn=True,
        isConvertedToPct=True,
        isSignalAssigned=True,
    )

    result = data_visualizer.prepare_bar_line_with_signal_data(dt_indexed_df=df, config=chart_config)

    # TRADE_DT should remain unchanged (string index -> column).
    assert result['TRADE_DT'].tolist() == list(index)

    # Bar and line Y columns should be divided by 100.
    assert result['value'].tolist() == [0.01, 0.02, 0.03]
    assert result['baseline'].tolist() == [0.005, 0.01, 0.015]

    # Axis formats should be updated to percentage format.
    assert chart_config.bar_param.y_axis_format == config.CHART_NUM_FORMAT['pct']
    assert chart_config.line_param.y_axis_format == config.CHART_NUM_FORMAT['pct']


@pytest.mark.style_prep
def test_draw_bar_line_chart_with_highlighted_signal_respects_isLineDrawn():
    """draw_bar_line_chart_with_highlighted_signal SHOULD honor isLineDrawn when line_param is present."""
    index = pd.date_range(start='2024-01-01', periods=3, freq='D').strftime('%Y%m%d')
    df = pd.DataFrame(
        {
            'TRADE_DT': index,
            'value': [1.0, 2.0, 3.0],
            'baseline': [0.5, 1.0, 1.5],
            'signal': ['UP', 'DOWN', 'UP'],
        }
    ).set_index('TRADE_DT')

    bar_param = param_cls.SignalBarParam(
        axis_names={'X': 'TRADE_DT', 'Y': 'value', 'LEGEND': 'signal'},
        title='test',
        true_signal='UP',
        false_signal='DOWN',
        no_signal=None,
        y_axis_format=config.CHART_NUM_FORMAT['float'],
    )
    line_param = param_cls.LineParam(
        axis_names={'X': 'TRADE_DT', 'Y': 'baseline', 'LEGEND': 'line_legend'},
        y_axis_format=config.CHART_NUM_FORMAT['float'],
    )

    base_config_kwargs = {
        'dt_slider_param': None,
        'bar_param': bar_param,
        'line_param': line_param,
        'isConvertedToPct': False,
        'isSignalAssigned': True,
    }

    line_call_count = {'count': 0}

    original_add_line = data_visualizer.add_altair_line_with_stroke_dash
    original_altair_chart = data_visualizer.st.altair_chart

    def _tracked_add_altair_line(df, cfg):
        line_call_count['count'] += 1
        return original_add_line(df, cfg)

    def _fake_altair_chart(*args, **kwargs):
        return None

    try:
        data_visualizer.add_altair_line_with_stroke_dash = _tracked_add_altair_line  # type: ignore[assignment]
        data_visualizer.st.altair_chart = _fake_altair_chart  # type: ignore[assignment]

        # When isLineDrawn is True and line_param is present, the line helper SHOULD be called.
        config_draw_line = param_cls.BarLineWithSignalParam(isLineDrawn=True, **base_config_kwargs)
        data_visualizer.draw_bar_line_chart_with_highlighted_signal(dt_indexed_df=df, config=config_draw_line)
        assert line_call_count['count'] == 1

        # When isLineDrawn is False (even with line_param present), the line helper SHOULD NOT be called.
        config_bar_only = param_cls.BarLineWithSignalParam(isLineDrawn=False, **base_config_kwargs)
        data_visualizer.draw_bar_line_chart_with_highlighted_signal(dt_indexed_df=df, config=config_bar_only)
        assert line_call_count['count'] == 1
    finally:
        data_visualizer.add_altair_line_with_stroke_dash = original_add_line  # type: ignore[assignment]
        data_visualizer.st.altair_chart = original_altair_chart  # type: ignore[assignment]


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
def test_relative_momentum_value_growth_bar_only_config_matches_bar_param():
    """Ensure the bar-only style config for value vs growth relative momentum matches the existing bar config."""
    chart_param = style_config.RELATIVE_MOMENTUM_VALUE_GROWTH_CHART_PARAM
    style_bar_config = getattr(style_config, "RELATIVE_MOMENTUM_VALUE_GROWTH_STYLE_CHART_CONFIG", None)

    # This test will start failing loudly if we forget to wire the style
    # config for the value/growth bar-only chart.
    assert style_bar_config is not None

    assert style_bar_config.axis_names == chart_param.bar_param.axis_names
    assert style_bar_config.axis_types == chart_param.bar_param.axis_types
    assert style_bar_config.title == chart_param.bar_param.title
    assert style_bar_config.y_axis_format == chart_param.bar_param.y_axis_format


@pytest.mark.style_prep
def test_relative_momentum_big_small_bar_only_config_matches_bar_param():
    """Ensure the bar-only style config for big vs small relative momentum matches the existing bar config."""
    chart_param = style_config.RELATIVE_MOMENTUM_BIG_SMALL_CHART_PARAM
    style_bar_config = getattr(style_config, "RELATIVE_MOMENTUM_BIG_SMALL_STYLE_CHART_CONFIG", None)

    assert style_bar_config is not None

    assert style_bar_config.axis_names == chart_param.bar_param.axis_names
    assert style_bar_config.axis_types == chart_param.bar_param.axis_types
    assert style_bar_config.title == chart_param.bar_param.title
    assert style_bar_config.y_axis_format == chart_param.bar_param.y_axis_format


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
def test_shibor_style_chart_config_matches_bar_line_param():
    """Ensure the slim style chart config for Shibor matches the existing bar+line config."""
    shibor_chart_param = style_config.SHIBOR_PRICES_CHART_PARAM
    shibor_style_config = style_config.SHIBOR_PRICES_STYLE_CHART_CONFIG

    assert shibor_style_config.bar_axis_names == shibor_chart_param.bar_param.axis_names
    assert shibor_style_config.bar_axis_types == shibor_chart_param.bar_param.axis_types
    assert shibor_style_config.line_axis_names == shibor_chart_param.line_param.axis_names
    assert shibor_style_config.line_axis_types == shibor_chart_param.line_param.axis_types
    assert shibor_style_config.title == shibor_chart_param.bar_param.title
    assert shibor_style_config.bar_y_axis_format == shibor_chart_param.bar_param.y_axis_format
    assert shibor_style_config.line_y_axis_format == shibor_chart_param.line_param.y_axis_format
    assert shibor_style_config.line_stroke_dash == shibor_chart_param.line_param.stroke_dash


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
def test_index_turnover_style_chart_config_matches_bar_line_param():
    """Ensure the slim style chart config for index turnover matches the existing bar+line config."""
    it_chart_param = style_config.INDEX_TURNOVER_CHART_PARAM
    it_style_config = style_config.INDEX_TURNOVER_STYLE_CHART_CONFIG

    assert it_style_config.bar_axis_names == it_chart_param.bar_param.axis_names
    assert it_style_config.bar_axis_types == it_chart_param.bar_param.axis_types
    assert it_style_config.line_axis_names == it_chart_param.line_param.axis_names
    assert it_style_config.line_axis_types == it_chart_param.line_param.axis_types
    assert it_style_config.title == it_chart_param.bar_param.title
    assert it_style_config.bar_y_axis_format == it_chart_param.bar_param.y_axis_format
    assert it_style_config.line_y_axis_format == it_chart_param.line_param.y_axis_format
    assert it_style_config.line_stroke_dash == it_chart_param.line_param.stroke_dash


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
def test_term_spread_style_chart_config_matches_bar_line_param():
    """Ensure the slim style chart config for term spread matches the existing bar+line config."""
    ts_chart_param = style_config.TERM_SPREAD_CHART_PARAM
    ts_style_config = style_config.TERM_SPREAD_STYLE_CHART_CONFIG

    assert ts_style_config.bar_axis_names == ts_chart_param.bar_param.axis_names
    assert ts_style_config.bar_axis_types == ts_chart_param.bar_param.axis_types
    assert ts_style_config.line_axis_names == ts_chart_param.line_param.axis_names
    assert ts_style_config.line_axis_types == ts_chart_param.line_param.axis_types
    assert ts_style_config.title == ts_chart_param.bar_param.title
    assert ts_style_config.bar_y_axis_format == ts_chart_param.bar_param.y_axis_format
    assert ts_style_config.line_y_axis_format == ts_chart_param.line_param.y_axis_format
    assert ts_style_config.line_stroke_dash == ts_chart_param.line_param.stroke_dash


@pytest.mark.style_prep
def test_term_spread_bar_line_pipeline_basic_invariants():
    """End-to-end invariants for term spread data prep + bar+line+signal helper."""
    from data_preparation.data_fetcher import fetch_data_from_local as _fetch_table  # type: ignore

    latest_date = "99991231"
    long_raw_cn_bond_yield_df = _fetch_table(latest_date=latest_date, table_name="CN_BOND_YIELD")

    term_spread_df, yield_curve_df, wide_raw_cn_bond_yield_df = prepare_term_spread_data(
        long_raw_cn_bond_yield_df=long_raw_cn_bond_yield_df
    )

    idx = term_spread_df.index
    custom_dt = (idx[0], idx[-1])

    result = data_visualizer.prepare_bar_line_with_signal_data(
        dt_indexed_df=term_spread_df,
        config=style_config.TERM_SPREAD_CHART_PARAM,
        custom_dt=custom_dt,
    )

    assert not result.empty

    # TRADE_DT column should exist and be monotonically increasing.
    dt_col = style_config.YIELD_CURVE_COL_PARAM.dt_col
    assert dt_col in result.columns
    assert result[dt_col].is_monotonic_increasing

    # Bar axis columns must exist.
    bar_axis_names = style_config.TERM_SPREAD_CHART_PARAM.bar_param.axis_names
    for col in bar_axis_names.values():
        assert col in result.columns

    # Line X/LEGEND axis columns must exist.
    line_axis_names = style_config.TERM_SPREAD_CHART_PARAM.line_param.axis_names
    for col in (line_axis_names["X"], line_axis_names["LEGEND"]):
        assert col in result.columns

    # Term spread core columns must still be present after helper processing.
    spread_col = style_config.TERM_SPREAD_CONFIG["TERM_SPREAD_COL"]
    mean_col = style_config.TERM_SPREAD_CONFIG["MEAN_COL"]
    for col in (spread_col, mean_col):
        assert col in result.columns

    # Signal column and its value set should remain valid.
    signal_col = style_config.TERM_SPREAD_CONFIG["SIGNAL_COL"]
    assert signal_col in result.columns
    signal_values = set(result[signal_col].dropna().unique().tolist())
    expected = {
        style_config.TERM_SPREAD_CHART_PARAM.bar_param.true_signal,
        style_config.TERM_SPREAD_CHART_PARAM.bar_param.false_signal,
    }
    assert signal_values.issubset(expected)


@pytest.mark.style_prep
def test_term_spread_2_bar_line_pipeline_basic_invariants():
    """End-to-end invariants for term spread 2 data prep + bar+line+signal helper."""
    from data_preparation.data_fetcher import fetch_data_from_local as _fetch_table  # type: ignore

    latest_date = "99991231"
    long_raw_cn_bond_yield_df = _fetch_table(latest_date=latest_date, table_name="CN_BOND_YIELD")

    term_spread_df, yield_curve_df, wide_raw_cn_bond_yield_df = prepare_term_spread_data(
        long_raw_cn_bond_yield_df=long_raw_cn_bond_yield_df
    )

    idx = term_spread_df.index
    custom_dt = (idx[0], idx[-1])

    result = data_visualizer.prepare_bar_line_with_signal_data(
        dt_indexed_df=term_spread_df,
        config=style_config.TERM_SPREAD_2_CHART_PARAM,
        custom_dt=custom_dt,
    )

    assert not result.empty

    # TRADE_DT column should exist and be monotonically increasing.
    dt_col = style_config.YIELD_CURVE_COL_PARAM.dt_col
    assert dt_col in result.columns
    assert result[dt_col].is_monotonic_increasing

    # Bar axis columns must exist.
    bar_axis_names = style_config.TERM_SPREAD_2_CHART_PARAM.bar_param.axis_names
    for col in bar_axis_names.values():
        assert col in result.columns

    # Line X/LEGEND axis columns must exist.
    line_axis_names = style_config.TERM_SPREAD_2_CHART_PARAM.line_param.axis_names
    for col in (line_axis_names["X"], line_axis_names["LEGEND"]):
        assert col in result.columns

    # Term spread core columns must still be present after helper processing.
    spread_col = style_config.TERM_SPREAD_CONFIG["TERM_SPREAD_COL"]
    mean_col = style_config.TERM_SPREAD_CONFIG["MEAN_COL"]
    for col in (spread_col, mean_col):
        assert col in result.columns

    # Signal column and its value set should remain valid and use the size-style labels.
    signal_col = style_config.TERM_SPREAD_CONFIG["SIGNAL_COL"]
    assert signal_col in result.columns
    signal_values = set(result[signal_col].dropna().unique().tolist())
    expected = {
        style_config.TERM_SPREAD_2_CHART_PARAM.bar_param.true_signal,
        style_config.TERM_SPREAD_2_CHART_PARAM.bar_param.false_signal,
    }
    assert signal_values.issubset(expected)


@pytest.mark.style_prep
def test_term_spread_style_draw_helper_smoke():
    """Smoke test for the style-specific term spread draw helper."""
    from data_preparation.data_fetcher import fetch_data_from_local as _fetch_table  # type: ignore

    latest_date = "99991231"
    long_raw_cn_bond_yield_df = _fetch_table(latest_date=latest_date, table_name="CN_BOND_YIELD")

    term_spread_df, yield_curve_df, wide_raw_cn_bond_yield_df = prepare_term_spread_data(
        long_raw_cn_bond_yield_df=long_raw_cn_bond_yield_df
    )

    idx = term_spread_df.index
    custom_dt = (idx[0], idx[-1])

    def _fake_select_slider(*args, **kwargs):
        return custom_dt

    def _fake_altair_chart(*args, **kwargs):
        return None

    original_select_slider = data_visualizer.st.select_slider
    original_altair_chart = data_visualizer.st.altair_chart
    try:
        data_visualizer.st.select_slider = _fake_select_slider  # type: ignore[assignment]
        data_visualizer.st.altair_chart = _fake_altair_chart  # type: ignore[assignment]

        data_visualizer.draw_style_bar_line_chart_with_highlighted_signal(
            dt_indexed_df=term_spread_df,
            style_chart_config=style_config.TERM_SPREAD_STYLE_CHART_CONFIG,
            dt_slider_param=style_config.TERM_SPREAD_CHART_PARAM.dt_slider_param,
            true_signal=style_config.TERM_SPREAD_CHART_PARAM.bar_param.true_signal,
            false_signal=style_config.TERM_SPREAD_CHART_PARAM.bar_param.false_signal,
            no_signal=None,
            signal_order=style_config.TERM_SPREAD_CHART_PARAM.bar_param.signal_order,
            compared_cols=style_config.TERM_SPREAD_CHART_PARAM.line_param.compared_cols,
            is_converted_to_pct=style_config.TERM_SPREAD_CHART_PARAM.isConvertedToPct,
            is_signal_assigned=False,
        )
    finally:
        data_visualizer.st.select_slider = original_select_slider  # type: ignore[assignment]
        data_visualizer.st.altair_chart = original_altair_chart  # type: ignore[assignment]


@pytest.mark.style_prep
def test_term_spread_2_style_draw_helper_smoke():
    """Smoke test for the style-specific term spread 2 draw helper."""
    from data_preparation.data_fetcher import fetch_data_from_local as _fetch_table  # type: ignore

    latest_date = "99991231"
    long_raw_cn_bond_yield_df = _fetch_table(latest_date=latest_date, table_name="CN_BOND_YIELD")

    term_spread_df, yield_curve_df, wide_raw_cn_bond_yield_df = prepare_term_spread_data(
        long_raw_cn_bond_yield_df=long_raw_cn_bond_yield_df
    )

    idx = term_spread_df.index
    custom_dt = (idx[0], idx[-1])

    def _fake_select_slider(*args, **kwargs):
        return custom_dt

    def _fake_altair_chart(*args, **kwargs):
        return None

    original_select_slider = data_visualizer.st.select_slider
    original_altair_chart = data_visualizer.st.altair_chart
    try:
        data_visualizer.st.select_slider = _fake_select_slider  # type: ignore[assignment]
        data_visualizer.st.altair_chart = _fake_altair_chart  # type: ignore[assignment]

        data_visualizer.draw_style_bar_line_chart_with_highlighted_signal(
            dt_indexed_df=term_spread_df,
            style_chart_config=style_config.TERM_SPREAD_2_STYLE_CHART_CONFIG,
            dt_slider_param=style_config.TERM_SPREAD_2_CHART_PARAM.dt_slider_param,
            true_signal=style_config.TERM_SPREAD_2_CHART_PARAM.bar_param.true_signal,
            false_signal=style_config.TERM_SPREAD_2_CHART_PARAM.bar_param.false_signal,
            no_signal=None,
            signal_order=style_config.TERM_SPREAD_2_CHART_PARAM.bar_param.signal_order,
            compared_cols=style_config.TERM_SPREAD_2_CHART_PARAM.line_param.compared_cols,
            is_converted_to_pct=style_config.TERM_SPREAD_2_CHART_PARAM.isConvertedToPct,
            is_signal_assigned=False,
        )
    finally:
        data_visualizer.st.select_slider = original_select_slider  # type: ignore[assignment]
        data_visualizer.st.altair_chart = original_altair_chart  # type: ignore[assignment]


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
def test_index_erp_2_bar_line_pipeline_basic_invariants():
    """End-to-end invariants for ERP_2 data prep + bar+line+signal helper."""
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

    erp_2_choices = [
        style_config.INDEX_ERP_2_CHART_PARAM.bar_param.true_signal,
        style_config.INDEX_ERP_2_CHART_PARAM.bar_param.false_signal,
    ]
    wide_erp_2_df = apply_signal_from_conditions(
        df=wide_erp_df,
        signal_col=style_config.INDEX_ERP_CONFIG["SIGNAL_COL"],
        conditions=erp_conditions,
        choices=erp_2_choices,
        default=style_config.INDEX_ERP_2_CHART_PARAM.bar_param.no_signal,
    )

    idx = wide_erp_2_df.index
    custom_dt = (idx[0], idx[-1])

    result = data_visualizer.prepare_bar_line_with_signal_data(
        dt_indexed_df=wide_erp_2_df,
        config=style_config.INDEX_ERP_2_CHART_PARAM,
        custom_dt=custom_dt,
    )

    assert not result.empty

    # TRADE_DT column should exist and be monotonically increasing.
    dt_col = style_config.INDEX_ERP_COL_PARAM.dt_col
    assert dt_col in result.columns
    assert result[dt_col].is_monotonic_increasing

    # Bar axis columns must exist.
    bar_axis_names = style_config.INDEX_ERP_2_CHART_PARAM.bar_param.axis_names
    for col in bar_axis_names.values():
        assert col in result.columns

    # Line X/LEGEND axis columns must exist. The Y axis is a semantic
    # alias ("分位数") and does not correspond to a direct column on
    # the wide frame.
    line_axis_names = style_config.INDEX_ERP_2_CHART_PARAM.line_param.axis_names
    for col in (line_axis_names["X"], line_axis_names["LEGEND"]):
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
        style_config.INDEX_ERP_2_CHART_PARAM.bar_param.true_signal,
        style_config.INDEX_ERP_2_CHART_PARAM.bar_param.false_signal,
        style_config.INDEX_ERP_2_CHART_PARAM.bar_param.no_signal,
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
def test_style_focus_style_chart_config_matches_bar_line_param():
    """Ensure the slim style chart config for style focus matches the existing bar+line config."""
    sf_chart_param = style_config.STYLE_FOCUS_CHART_PARAM
    sf_style_config = style_config.STYLE_FOCUS_STYLE_CHART_CONFIG

    assert sf_style_config.bar_axis_names == sf_chart_param.bar_param.axis_names
    assert sf_style_config.bar_axis_types == sf_chart_param.bar_param.axis_types
    assert sf_style_config.line_axis_names == sf_chart_param.line_param.axis_names
    assert sf_style_config.line_axis_types == sf_chart_param.line_param.axis_types
    assert sf_style_config.title == sf_chart_param.bar_param.title
    assert sf_style_config.bar_y_axis_format == sf_chart_param.bar_param.y_axis_format
    assert sf_style_config.line_y_axis_format == sf_chart_param.line_param.y_axis_format
    assert sf_style_config.line_stroke_dash == sf_chart_param.line_param.stroke_dash


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


@pytest.mark.style_prep
def test_housing_invest_style_chart_config_matches_bar_line_param():
    """Ensure the slim style chart config for housing investment matches the existing bar+line config."""
    hi_chart_param = style_config.HOUSING_INVEST_CHART_PARAM
    hi_style_config = style_config.HOUSING_INVEST_STYLE_CHART_CONFIG

    assert hi_style_config.bar_axis_names == hi_chart_param.bar_param.axis_names
    assert hi_style_config.bar_axis_types == hi_chart_param.bar_param.axis_types
    assert hi_style_config.line_axis_names == hi_chart_param.line_param.axis_names
    assert hi_style_config.line_axis_types == hi_chart_param.line_param.axis_types
    assert hi_style_config.title == hi_chart_param.bar_param.title
    assert hi_style_config.bar_y_axis_format == hi_chart_param.bar_param.y_axis_format
    assert hi_style_config.line_y_axis_format == hi_chart_param.line_param.y_axis_format
    assert hi_style_config.line_stroke_dash == hi_chart_param.line_param.stroke_dash


@pytest.mark.style_prep
def test_credit_expansion_bar_line_pipeline_basic_invariants():
    """End-to-end invariants for credit expansion data prep + bar+line+signal helper."""
    latest_date = "99991231"
    long_edb_df = fetch_data_from_local(latest_date=latest_date, table_name="EDB")

    wide_raw_edb_df = reshape_long_df_into_wide_form(
        long_df=long_edb_df,
        index_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.EDB].dt_col,
        name_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.EDB].name_col,
        value_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.EDB].value_col,
    )

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

    idx = credit_df.index
    custom_dt = (idx[0], idx[-1])

    result = data_visualizer.prepare_bar_line_with_signal_data(
        dt_indexed_df=credit_df,
        config=style_config.CREDIT_EXPANSION_CHART_PARAM,
        custom_dt=custom_dt,
    )

    assert not result.empty

    # TRADE_DT column should exist and be monotonically increasing.
    dt_col = style_config.DATA_COL_PARAM[style_config.CREDIT_EXPANSION_CONFIG["WIND_TABLE"]].dt_col
    assert dt_col in result.columns
    assert result[dt_col].is_monotonic_increasing

    # Bar axis columns must exist.
    bar_axis_names = style_config.CREDIT_EXPANSION_CHART_PARAM.bar_param.axis_names
    for col in bar_axis_names.values():
        assert col in result.columns

    # Line X/LEGEND axis columns must exist.
    line_axis_names = style_config.CREDIT_EXPANSION_CHART_PARAM.line_param.axis_names
    for col in (line_axis_names["X"], line_axis_names["LEGEND"]):
        assert col in result.columns

    # Credit expansion core columns must still be present after helper processing.
    yoy_col = style_config.CREDIT_EXPANSION_CONFIG["YOY_COL"]
    mean_col = style_config.CREDIT_EXPANSION_CONFIG["MEAN_COL"]
    for col in (yoy_col, mean_col):
        assert col in result.columns

    # Signal column and its value set should remain valid.
    signal_col = style_config.CREDIT_EXPANSION_CONFIG["SIGNAL_COL"]
    assert signal_col in result.columns
    signal_values = set(result[signal_col].dropna().unique().tolist())
    expected = {
        style_config.CREDIT_EXPANSION_CONFIG["TRUE_SIGNAL"],
        style_config.CREDIT_EXPANSION_CONFIG["FALSE_SIGNAL"],
    }
    assert signal_values.issubset(expected)


@pytest.mark.style_prep
def test_style_focus_bar_line_pipeline_basic_invariants():
    """End-to-end invariants for style focus data prep + bar+line+signal helper."""
    raw_wide_idx_df, idx_name_df = _load_style_index_data()

    # Build big/small momentum signals as in the style page.
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

    idx = style_focus_df.index
    custom_dt = (idx[0], idx[-1])

    result = data_visualizer.prepare_bar_line_with_signal_data(
        dt_indexed_df=style_focus_df,
        config=style_config.STYLE_FOCUS_CHART_PARAM,
        custom_dt=custom_dt,
    )

    assert not result.empty

    # TRADE_DT column should exist and be monotonically increasing.
    dt_col = style_config.DATA_COL_PARAM[style_config.STYLE_FOCUS_CONFIG["WIND_TABLE"]].dt_col
    assert dt_col in result.columns
    assert result[dt_col].is_monotonic_increasing

    # Bar axis columns must exist.
    bar_axis_names = style_config.STYLE_FOCUS_CHART_PARAM.bar_param.axis_names
    for col in bar_axis_names.values():
        assert col in result.columns

    # Line X/LEGEND axis columns must exist.
    line_axis_names = style_config.STYLE_FOCUS_CHART_PARAM.line_param.axis_names
    for col in (line_axis_names["X"], line_axis_names["LEGEND"]):
        assert col in result.columns

    # Style focus core columns must still be present after helper processing.
    focus_col = style_config.STYLE_FOCUS_CONFIG["STYLE_FOCUS_COL"]
    ceil_col = style_config.STYLE_FOCUS_CONFIG["QUANTILE_CEILING_COL"]
    floor_col = style_config.STYLE_FOCUS_CONFIG["QUANTILE_FLOOR_COL"]
    for col in (focus_col, ceil_col, floor_col):
        assert col in result.columns

    # Signal column and its value set should remain valid.
    signal_col = style_config.STYLE_FOCUS_CONFIG["SIGNAL_COL"]
    assert signal_col in result.columns
    signal_values = set(result[signal_col].dropna().unique().tolist())
    expected = {
        style_config.STYLE_FOCUS_CONFIG["TRUE_SIGNAL"],
        style_config.STYLE_FOCUS_CONFIG["FALSE_SIGNAL"],
        style_config.STYLE_FOCUS_CONFIG["NO_SIGNAL"],
    }
    assert signal_values.issubset(expected)


@pytest.mark.style_prep
def test_shibor_bar_line_pipeline_basic_invariants():
    """End-to-end invariants for Shibor data prep + bar+line+signal helper."""
    latest_date = "99991231"
    shibor_long_df = fetch_data_from_local(latest_date=latest_date, table_name="SHIBOR_PRICES")

    shibor_prices_df = prepare_shibor_prices_data(long_raw_shibor_df=shibor_long_df)

    shibor_conditions = [
        shibor_prices_df[style_config.SHIBOR_PRICES_CONFIG["SHIBOR_PRICE_COL"]]
        >= shibor_prices_df[style_config.SHIBOR_PRICES_CONFIG["MEAN_COL"]],
    ]
    shibor_choices = [
        style_config.SHIBOR_PRICES_CONFIG["TRUE_SIGNAL"],
    ]
    shibor_prices_df = apply_signal_from_conditions(
        df=shibor_prices_df,
        signal_col=style_config.SHIBOR_PRICES_CONFIG["SIGNAL_COL"],
        conditions=shibor_conditions,
        choices=shibor_choices,
        default=style_config.SHIBOR_PRICES_CONFIG["FALSE_SIGNAL"],
    )

    idx = shibor_prices_df.index
    custom_dt = (idx[0], idx[-1])

    result = data_visualizer.prepare_bar_line_with_signal_data(
        dt_indexed_df=shibor_prices_df,
        config=style_config.SHIBOR_PRICES_CHART_PARAM,
        custom_dt=custom_dt,
    )

    assert not result.empty

    # TRADE_DT column should exist and be monotonically increasing.
    dt_col = style_config.SHIBOR_PRICES_COL_PARAM.dt_col
    assert dt_col in result.columns
    assert result[dt_col].is_monotonic_increasing

    # Bar axis columns must exist.
    bar_axis_names = style_config.SHIBOR_PRICES_CHART_PARAM.bar_param.axis_names
    for col in bar_axis_names.values():
        assert col in result.columns

    # Line X/LEGEND axis columns must exist.
    line_axis_names = style_config.SHIBOR_PRICES_CHART_PARAM.line_param.axis_names
    for col in (line_axis_names["X"], line_axis_names["LEGEND"]):
        assert col in result.columns

    # Shibor price and mean columns must still be present after helper processing.
    price_col = style_config.SHIBOR_PRICES_CONFIG["SHIBOR_PRICE_COL"]
    mean_col = style_config.SHIBOR_PRICES_CONFIG["MEAN_COL"]
    for col in (price_col, mean_col):
        assert col in result.columns

    # Signal column and its value set should remain valid.
    signal_col = style_config.SHIBOR_PRICES_CONFIG["SIGNAL_COL"]
    assert signal_col in result.columns
    signal_values = set(result[signal_col].dropna().unique().tolist())
    expected = {
        style_config.SHIBOR_PRICES_CONFIG["TRUE_SIGNAL"],
        style_config.SHIBOR_PRICES_CONFIG["FALSE_SIGNAL"],
    }
    assert signal_values.issubset(expected)


@pytest.mark.style_prep
def test_index_turnover_bar_line_pipeline_basic_invariants():
    """End-to-end invariants for index turnover data prep + bar+line+signal helper."""
    # Load all-A index valuation data and filter to the benchmark index, mirroring the style page.
    from visualization.style import fetch_data_from_local as _fetch_data_from_local  # type: ignore

    latest_date = "99991231"
    long_raw_df_collection = {
        "A_IDX_VAL": _fetch_data_from_local(latest_date=latest_date, table_name="A_IDX_VAL")
    }

    long_wind_all_a_idx_val_df = long_raw_df_collection["A_IDX_VAL"].query(
        f'{style_config.DATA_COL_PARAM[param_cls.WindPortal.A_IDX_VAL].name_col} == "万得全A"'
    )

    turnover_df = prepare_index_turnover_data(long_wind_all_a_idx_val_df=long_wind_all_a_idx_val_df)

    idx = turnover_df.index
    custom_dt = (idx[0], idx[-1])

    result = data_visualizer.prepare_bar_line_with_signal_data(
        dt_indexed_df=turnover_df,
        config=style_config.INDEX_TURNOVER_CHART_PARAM,
        custom_dt=custom_dt,
    )

    assert not result.empty

    # TRADE_DT column should exist and be monotonically increasing.
    dt_col = style_config.INDEX_TURNOVER_COL_PARAM.dt_col
    assert dt_col in result.columns
    assert result[dt_col].is_monotonic_increasing

    # Bar axis columns must exist.
    bar_axis_names = style_config.INDEX_TURNOVER_CHART_PARAM.bar_param.axis_names
    for col in bar_axis_names.values():
        assert col in result.columns

    # Line X/LEGEND axis columns must exist.
    line_axis_names = style_config.INDEX_TURNOVER_CHART_PARAM.line_param.axis_names
    for col in (line_axis_names["X"], line_axis_names["LEGEND"]):
        assert col in result.columns

    # Turnover-specific columns must still be present after helper processing.
    mean_col = style_config.INDEX_TURNOVER_CONFIG["MEAN_COL"]
    mean_1m_col = style_config.INDEX_TURNOVER_CONFIG["MEAN_1M_COL"]
    mean_2y_col = style_config.INDEX_TURNOVER_CONFIG["MEAN_2Y_COL"]
    for col in (mean_col, mean_1m_col, mean_2y_col):
        assert col in result.columns

    # Signal column and its value set should remain valid.
    signal_col = style_config.INDEX_TURNOVER_CONFIG["SIGNAL_COL"]
    assert signal_col in result.columns
    signal_values = set(result[signal_col].dropna().unique().tolist())
    expected = {
        param_cls.TradeSignal.LONG_GROWTH.value,
        param_cls.TradeSignal.LONG_VALUE.value,
    }
    assert signal_values.issubset(expected)


@pytest.mark.style_prep
def test_housing_invest_bar_line_pipeline_basic_invariants():
    """End-to-end invariants for housing investment data prep + bar+line+signal helper."""
    latest_date = "99991231"
    long_edb_df = fetch_data_from_local(latest_date=latest_date, table_name="EDB")

    wide_raw_edb_df = reshape_long_df_into_wide_form(
        long_df=long_edb_df,
        index_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.EDB].dt_col,
        name_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.EDB].name_col,
        value_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.EDB].value_col,
    )

    housing_df = prepare_housing_invest_data(wide_raw_edb_df=wide_raw_edb_df)

    housing_invest_conditions = [
        housing_df[style_config.HOUSING_INVEST_CONFIG["YOY_COL"]]
        >= housing_df[style_config.HOUSING_INVEST_CONFIG["PRE_YOY_COL"]],
    ]
    housing_invest_choices = [
        style_config.HOUSING_INVEST_CONFIG["TRUE_SIGNAL"],
    ]
    housing_df = apply_signal_from_conditions(
        df=housing_df,
        signal_col=style_config.HOUSING_INVEST_CONFIG["SIGNAL_COL"],
        conditions=housing_invest_conditions,
        choices=housing_invest_choices,
        default=style_config.HOUSING_INVEST_CONFIG["FALSE_SIGNAL"],
    )

    idx = housing_df.index
    custom_dt = (idx[0], idx[-1])

    result = data_visualizer.prepare_bar_line_with_signal_data(
        dt_indexed_df=housing_df,
        config=style_config.HOUSING_INVEST_CHART_PARAM,
        custom_dt=custom_dt,
    )

    assert not result.empty

    # TRADE_DT column should exist and be monotonically increasing.
    dt_col = style_config.DATA_COL_PARAM[style_config.HOUSING_INVEST_CONFIG["WIND_TABLE"]].dt_col
    assert dt_col in result.columns
    assert result[dt_col].is_monotonic_increasing

    # Bar axis columns must exist.
    bar_axis_names = style_config.HOUSING_INVEST_CHART_PARAM.bar_param.axis_names
    for col in bar_axis_names.values():
        assert col in result.columns

    # Line X/LEGEND axis columns must exist.
    line_axis_names = style_config.HOUSING_INVEST_CHART_PARAM.line_param.axis_names
    for col in (line_axis_names["X"], line_axis_names["LEGEND"]):
        assert col in result.columns

    # Housing investment core columns must still be present after helper processing.
    yoy_col = style_config.HOUSING_INVEST_CONFIG["YOY_COL"]
    pre_yoy_col = style_config.HOUSING_INVEST_CONFIG["PRE_YOY_COL"]
    for col in (yoy_col, pre_yoy_col):
        assert col in result.columns

    # Signal column and its value set should remain valid.
    signal_col = style_config.HOUSING_INVEST_CONFIG["SIGNAL_COL"]
    assert signal_col in result.columns
    signal_values = set(result[signal_col].dropna().unique().tolist())
    expected = {
        style_config.HOUSING_INVEST_CONFIG["TRUE_SIGNAL"],
        style_config.HOUSING_INVEST_CONFIG["FALSE_SIGNAL"],
    }
    assert signal_values.issubset(expected)
