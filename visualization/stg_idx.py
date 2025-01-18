from datetime import datetime

import pytz
import streamlit as st

import utils
from config import config, param_cls
from data_preparation.data_analyzer import calculate_grouped_return
from data_preparation.data_fetcher import fetch_index_data_from_local
from data_preparation.data_processor import (
    convert_price_ts_into_nav_ts,
    reshape_long_df_into_wide_form,
)
from utils import msg_printer
from visualization.data_visualizer import (
    draw_grouped_bars,
    draw_grouped_lines,
    draw_heatmap,
    get_custom_dt_with_select_slider,
    get_custom_dt_with_slider,
)

# Get current time in China timezone
china_tz = pytz.timezone('Asia/Shanghai')
china_now = datetime.now(china_tz)
formatted_latest_day = china_now.strftime(config.WIND_DT_FORMAT)


@msg_printer
def generate_stg_idx_charts():
    # st.write(formatted_latest_day)
    wind_config = param_cls.WindListedSecParam(
        wind_codes=config.STG_IDX_CODES + config.BENCH_IDX_CODES,
        start_date=config.START_DT,
        sql_param=param_cls.SqlParam(
            sql_name=config.IDX_PRICE_SQL_NAME,
        ),
    )
    data_col_config = param_cls.WindIdxColParam()

    stg_idx_grouped_ret_slider_config = param_cls.DtSliderParam(
        name=config.CUSTOM_PERIOD_SLIDER_NAME,
        start_dt=config.STG_IDX_SLIDER_START_DT['RET_BAR'],
        default_start_offset=utils.get_avg_dt_count_via_dt_type(dt_type=utils.TradeDtType.STOCK_MKT, period='一月'),
    )
    grouped_ret_bar_config = param_cls.BaseBarParam(
        axis_names=config.STG_IDX_CHART_AXIS_NAMES['RET_BAR'],
        title=config.STG_IDX_CHART_TITLES['RET_BAR'],
        y_axis_format=config.CHART_NUM_FORMAT['pct'],
    )
    stg_idx_bench_nav_slider_config = param_cls.DtSliderParam(
        name=config.CUSTOM_PERIOD_SLIDER_NAME,
        start_dt=config.START_DT,
        default_start_offset=utils.get_avg_dt_count_via_dt_type(dt_type=utils.TradeDtType.STOCK_MKT, period='一年'),
    )
    line_config = param_cls.IdxLineParam(
        axis_names=config.STG_IDX_CHART_AXIS_NAMES['NAV_LINE'],
        title=config.STG_IDX_CHART_TITLES['NAV_LINE'],
        y_axis_format=config.CHART_NUM_FORMAT['float'],
    )

    corr_slider_config = param_cls.SelectSliderParam(
        name=config.CUSTOM_PERIOD_SLIDER_NAME,
        default_select_offset=config.STG_IDX_CORR_TRADE_DT_COUNT,
    )
    heatmap_config = param_cls.HeatmapParam(
        axis_names=config.STG_IDX_CHART_AXIS_NAMES['CORR_HEATMAP'],
        col_types=config.STG_IDX_CHART_AXIS_TYPES['CORR_HEATMAP'],
        title=config.STG_IDX_CHART_TITLES['CORR_HEATMAP'],
        legend_format=config.CHART_NUM_FORMAT['float'],
    )

    # raw_long_df = fetch_index_data_with_wind_portal(latest_date=formatted_latest_day, _config=wind_config)
    # st.write(raw_long_df)
    raw_long_df = fetch_index_data_from_local(latest_date=formatted_latest_day, _config=wind_config)
    # st.write(raw_long_df)

    trade_dt = sorted(raw_long_df[data_col_config.dt_col].unique())
    stg_idx_df = raw_long_df[raw_long_df[data_col_config.code_col].isin(config.STG_IDX_CODES)].reset_index(drop=True)
    stg_idx_name_df = (
        stg_idx_df[[data_col_config.code_col, data_col_config.name_col]]
        .drop_duplicates()
        .set_index(data_col_config.code_col, drop=True)
        .reindex(config.STG_IDX_CODES)
    )
    raw_name_df = (
        raw_long_df[[data_col_config.code_col, data_col_config.name_col]]
        .drop_duplicates()
        .set_index(data_col_config.code_col, drop=True)
        .reindex(wind_config.wind_codes)
    )

    st.header('策略指数')

    # 1. 策略指数收益对比条形图

    stg_idx_grouped_ret_custom_dt = get_custom_dt_with_slider(trade_dt, stg_idx_grouped_ret_slider_config)

    raw_grouped_ret_df = calculate_grouped_return(
        raw_long_df,
        formatted_latest_day,
        stg_idx_grouped_ret_custom_dt,
        trade_dt,
        data_col_config,
    )
    # st.write(raw_long_df)
    # st.write(raw_grouped_ret_df)

    draw_grouped_bars(raw_grouped_ret_df, raw_name_df, grouped_ret_bar_config)

    # 2. 策略指数走势图

    stg_idx_bench_nav_custom_dt = get_custom_dt_with_slider(trade_dt, stg_idx_bench_nav_slider_config)

    raw_wide_df = reshape_long_df_into_wide_form(
        raw_long_df,
        data_col_config.dt_col,
        data_col_config.name_col,
        data_col_config.price_col,
    )[raw_name_df[data_col_config.name_col].tolist()]
    stg_idx_bench_close_wide_df = raw_wide_df.loc[stg_idx_bench_nav_custom_dt[0] : stg_idx_bench_nav_custom_dt[1]]
    stg_idx_bench_nav_wide_df = convert_price_ts_into_nav_ts(stg_idx_bench_close_wide_df)

    draw_grouped_lines(wide_df=stg_idx_bench_nav_wide_df, config=line_config)

    # 3. 策略超额相关性热力图

    ret_wide_df = raw_wide_df.pct_change().dropna()

    corr_custom_dt = get_custom_dt_with_select_slider(trade_dt, corr_slider_config)

    excess_ret_wide_df = ret_wide_df.loc[corr_custom_dt:, stg_idx_name_df.iloc[:, 0].tolist()].subtract(
        ret_wide_df.loc[corr_custom_dt:, '中证800'], axis=0
    )
    corr_wide_df = excess_ret_wide_df.corr()

    draw_heatmap(corr_wide_df, heatmap_config)
    # st.write(corr_wide_df.rename_axis('策略指数'))
