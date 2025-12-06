from datetime import date

import numpy as np
import pandas as pd
import streamlit as st

from config import config, param_cls, style_config
from data_preparation.data_fetcher import (
    fetch_data_from_local,
    fetch_index_data_from_local,
)
from data_preparation.data_processor import (
    append_difference_column,
    append_ratio_column,
    append_rolling_mean_column,
    append_rolling_quantile_column,
    # append_rolling_quantile_inv_q_column,
    append_rolling_sum_column,
    append_sum_column,
    apply_signal_from_conditions,
    append_year_on_year_growth_column,
    reshape_long_df_into_wide_form,
)
from utils import TradeDtType, get_avg_dt_count_via_dt_type, msg_printer
from visualization.data_visualizer import (
    draw_bar_line_chart_with_highlighted_predefined_signal,
    draw_bar_line_chart_with_highlighted_signal,
    draw_grouped_lines,
)


def prepare_value_growth_data(raw_wide_idx_df: pd.DataFrame, idx_name_df: pd.DataFrame):
    """Prepare data for value vs growth style block.

    Returns:
        ratio_mean_df: wide DataFrame with ratio and its rolling mean for the first line chart.
        pct_change_df: wide DataFrame with recent period returns for the second line chart.
        signal_df: full DataFrame including relative momentum and trading signal for bar chart.
    """
    value_name_col, growth_name_col = tuple(
        map(
            lambda x: idx_name_df.loc[style_config.STYLE_IDX_CODES[x]].values[0],
            ['价值', '成长'],
        )
    )

    value_growth_df = raw_wide_idx_df[[value_name_col, growth_name_col]].copy()
    value_growth_df = append_ratio_column(value_growth_df, value_name_col, growth_name_col)
    value_growth_df = append_rolling_mean_column(
        df=value_growth_df,
        window_name='一年',
        window_size=config.TRADE_DT_COUNT['一年'],
        rolling_mean_col='近一年均值',
    )

    ratio_mean_df = value_growth_df.iloc[:, -2:].copy()

    for col, new_col in zip(
        [value_name_col, growth_name_col],
        ['国证价值近一月收益率', '国证成长近一月收益率'],
    ):
        value_growth_df[new_col] = value_growth_df[col].pct_change(
            get_avg_dt_count_via_dt_type(
                dt_type=TradeDtType.STOCK_MKT,
                period='一月',
            )
        )
    for col, new_col in zip(
        [value_name_col, growth_name_col],
        ['国证价值近两周收益率', '国证成长近两周收益率'],
    ):
        value_growth_df[new_col] = value_growth_df[col].pct_change(
            get_avg_dt_count_via_dt_type(
                dt_type=TradeDtType.STOCK_MKT,
                period='两周',
            )
        )
    value_growth_df.dropna(inplace=True)

    pct_change_df = value_growth_df[
        [
            '国证价值近一月收益率',
            '国证成长近一月收益率',
            '国证价值近两周收益率',
            '国证成长近两周收益率',
        ]
    ].dropna(inplace=False)

    value_growth_df = append_difference_column(
        df=value_growth_df,
        minuend_col='国证价值近一月收益率',
        subtrahend_col='国证成长近一月收益率',
        difference_col='价值对成长近一月超额',
    )
    value_growth_df = append_difference_column(
        df=value_growth_df,
        minuend_col='国证价值近两周收益率',
        subtrahend_col='国证成长近两周收益率',
        difference_col='价值对成长近两周超额',
    )
    value_growth_df = append_sum_column(
        df=value_growth_df,
        sum_1_col='价值对成长近一月超额',
        sum_2_col='价值对成长近两周超额',
        sum_col='相对动量',
        multiplier_1=1,
        multiplier_2=2,
        multiplier_sum=0.5,
    )

    value_growth_conditions = [
        (value_growth_df['价值对成长近一月超额'] < 0) & (value_growth_df['价值对成长近两周超额'] < 0),
        (value_growth_df['价值对成长近一月超额'] > 0) & (value_growth_df['价值对成长近两周超额'] > 0),
    ]
    value_growth_choices = [
        param_cls.TradeSignal.LONG_GROWTH.value,
        param_cls.TradeSignal.LONG_VALUE.value,
    ]
    value_growth_df = apply_signal_from_conditions(
        df=value_growth_df,
        signal_col='交易信号',
        conditions=value_growth_conditions,
        choices=value_growth_choices,
        default=param_cls.TradeSignal.NO_SIGNAL.value,
    )

    signal_df = value_growth_df

    return ratio_mean_df, pct_change_df, signal_df


def prepare_index_turnover_data(long_wind_all_a_idx_val_df: pd.DataFrame) -> pd.DataFrame:
    """Prepare data for market sentiment (index turnover) style block."""
    wide_wind_all_a_turnover_df = reshape_long_df_into_wide_form(
        long_df=long_wind_all_a_idx_val_df,
        index_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.A_IDX_VAL].dt_col,
        name_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.A_IDX_VAL].name_col,
        value_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.A_IDX_VAL].turnover_col,
        add_suffix=True,
    )

    wide_wind_all_a_turnover_df = append_rolling_mean_column(
        df=wide_wind_all_a_turnover_df,
        window_name=style_config.INDEX_TURNOVER_CONFIG['MEAN_ROLLING_WINDOW'],
        window_size=style_config.INDEX_TURNOVER_CONFIG['MEAN_ROLLING_WINDOW_SIZE'],
        rolling_mean_col=style_config.INDEX_TURNOVER_CONFIG['MEAN_COL'],
    )
    wide_wind_all_a_turnover_df = append_rolling_mean_column(
        df=wide_wind_all_a_turnover_df,
        window_name=style_config.INDEX_TURNOVER_CONFIG['MEAN_1M_ROLLING_WINDOW'],
        window_size=style_config.INDEX_TURNOVER_CONFIG['MEAN_1M_ROLLING_WINDOW_SIZE'],
        target_col=style_config.INDEX_TURNOVER_CONFIG['MEAN_COL'],
        rolling_mean_col=style_config.INDEX_TURNOVER_CONFIG['MEAN_1M_COL'],
    )
    wide_wind_all_a_turnover_df = append_rolling_mean_column(
        df=wide_wind_all_a_turnover_df,
        window_name=style_config.INDEX_TURNOVER_CONFIG['MEAN_2Y_ROLLING_WINDOW'],
        window_size=style_config.INDEX_TURNOVER_CONFIG['MEAN_2Y_ROLLING_WINDOW_SIZE'],
        target_col=style_config.INDEX_TURNOVER_CONFIG['MEAN_COL'],
        rolling_mean_col=style_config.INDEX_TURNOVER_CONFIG['MEAN_2Y_COL'],
    )

    turnover_conditions = [
        (
            wide_wind_all_a_turnover_df[style_config.INDEX_TURNOVER_CONFIG['MEAN_COL']]
            > wide_wind_all_a_turnover_df[style_config.INDEX_TURNOVER_CONFIG['MEAN_1M_COL']]
        )
        & (
            wide_wind_all_a_turnover_df[style_config.INDEX_TURNOVER_CONFIG['MEAN_COL']]
            > wide_wind_all_a_turnover_df[style_config.INDEX_TURNOVER_CONFIG['MEAN_2Y_COL']]
        ),
    ]
    turnover_choices = [
        param_cls.TradeSignal.LONG_GROWTH.value,
    ]
    wide_wind_all_a_turnover_df = apply_signal_from_conditions(
        df=wide_wind_all_a_turnover_df,
        signal_col='交易信号',
        conditions=turnover_conditions,
        choices=turnover_choices,
        default=param_cls.TradeSignal.LONG_VALUE.value,
    )

    return wide_wind_all_a_turnover_df


def prepare_term_spread_data(long_raw_cn_bond_yield_df: pd.DataFrame):
    """Prepare data for term spread block (bar+line+signal and yield curves)."""
    wide_raw_cn_bond_yield_df = reshape_long_df_into_wide_form(
        long_df=long_raw_cn_bond_yield_df,
        index_col=style_config.YIELD_CURVE_COL_PARAM.dt_col,
        name_col=style_config.YIELD_CURVE_COL_PARAM.term_col,
        value_col=style_config.YIELD_CURVE_COL_PARAM.ytm_col,
    )

    short_term_col, long_term_col = sorted(style_config.TERM_SPREAD_CONFIG['YIELD_CURVE_TERMS'])
    term_spread_df = append_difference_column(
        df=wide_raw_cn_bond_yield_df,
        minuend_col=long_term_col,
        subtrahend_col=short_term_col,
        difference_col=style_config.TERM_SPREAD_CONFIG['TERM_SPREAD_COL'],
    )
    term_spread_df = append_rolling_mean_column(
        df=term_spread_df,
        window_name=style_config.TERM_SPREAD_CONFIG['ROLLING_WINDOW'],
        window_size=style_config.TERM_SPREAD_CONFIG['ROLLING_WINDOW_SIZE'],
        rolling_mean_col=style_config.TERM_SPREAD_CONFIG['MEAN_COL'],
    )

    yield_curve_df = term_spread_df[
        [
            short_term_col,
            long_term_col,
        ]
    ]

    return term_spread_df, yield_curve_df, wide_raw_cn_bond_yield_df


def prepare_index_erp_data(
    long_wind_all_a_idx_val_df: pd.DataFrame,
    wide_raw_cn_bond_yield_df: pd.DataFrame,
) -> tuple[pd.DataFrame, list]:
    """Prepare data for ERP (equity risk premium) style block (value vs growth).

    Returns:
        wide_erp_df: DataFrame with ERP value, rolling mean, and quantile bands.
        erp_conditions: list of boolean Series used for signal assignment.
    """
    wide_raw_idx_pe_ttm_df = reshape_long_df_into_wide_form(
        long_df=long_wind_all_a_idx_val_df,
        index_col=style_config.INDEX_ERP_COL_PARAM.dt_col,
        name_col=style_config.INDEX_ERP_COL_PARAM.code_col,
        value_col=style_config.INDEX_ERP_COL_PARAM.pe_ttm_col,
    )
    wide_raw_idx_pe_ttm_df.columns = [style_config.INDEX_ERP_COL_PARAM.pe_ttm_col]

    merge_pe_yc_df = wide_raw_cn_bond_yield_df.merge(
        wide_raw_idx_pe_ttm_df, left_index=True, right_index=True, how='inner'
    )
    merge_pe_yc_df = merge_pe_yc_df.assign(
        市盈率倒数=1 / merge_pe_yc_df['市盈率'],
        十年期国债到期收益率=merge_pe_yc_df['10.0'] / 100,
    )
    merge_pe_yc_df[style_config.INDEX_ERP_CONFIG['ERP_COL']] = (
        merge_pe_yc_df['市盈率倒数'] - merge_pe_yc_df['十年期国债到期收益率']
    )

    erp_quantile_info = [
        {
            'quantile': style_config.INDEX_ERP_CONFIG['QUANTILE_CEILING'],
            'col': style_config.INDEX_ERP_CONFIG['QUANTILE_CEILING_COL'],
            'dropna': False,
        },
        {
            'quantile': style_config.INDEX_ERP_CONFIG['QUANTILE_FLOOR'],
            'col': style_config.INDEX_ERP_CONFIG['QUANTILE_FLOOR_COL'],
            'dropna': True,
        },
    ]

    wide_erp_df = pd.DataFrame(merge_pe_yc_df[style_config.INDEX_ERP_CONFIG['ERP_COL']])
    wide_erp_df = append_rolling_mean_column(
        df=wide_erp_df,
        window_name='一月',
        window_size=config.TRADE_DT_COUNT['一月'],
        dropna=False,
    )

    for info in erp_quantile_info:
        wide_erp_df = append_rolling_quantile_column(
            df=wide_erp_df,
            window_name=style_config.INDEX_ERP_CONFIG['QUANTILE_ROLLING_WINDOW'],
            window_size=style_config.INDEX_ERP_CONFIG['QUANTILE_ROLLING_WINDOW_SIZE'],
            target_col=style_config.INDEX_ERP_CONFIG['ERP_COL'],
            rolling_quantile_col=info['col'],
            quantile=info['quantile'],
            dropna=info['dropna'],
        )

    erp_conditions = [
        (
            wide_erp_df[style_config.INDEX_ERP_CONFIG['ERP_COL']]
            >= wide_erp_df[style_config.INDEX_ERP_CONFIG['QUANTILE_CEILING_COL']]
        )
        & (wide_erp_df[style_config.INDEX_ERP_CONFIG['ERP_COL']] < wide_erp_df['近一月均值']),
        (
            wide_erp_df[style_config.INDEX_ERP_CONFIG['ERP_COL']]
            <= wide_erp_df[style_config.INDEX_ERP_CONFIG['QUANTILE_FLOOR_COL']]
        )
        & (wide_erp_df[style_config.INDEX_ERP_CONFIG['ERP_COL']] > wide_erp_df['近一月均值']),
    ]
    return wide_erp_df, erp_conditions


def prepare_style_focus_data(
    long_big_small_idx_val_df: pd.DataFrame,
    big_small_df: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare data for style focus block (small vs big cap attention)."""
    wide_big_small_turnover_df = reshape_long_df_into_wide_form(
        long_df=long_big_small_idx_val_df,
        index_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.A_IDX_VAL].dt_col,
        name_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.A_IDX_VAL].name_col,
        value_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.A_IDX_VAL].turnover_col,
        add_suffix=True,
    )

    wide_big_small_turnover_df = append_ratio_column(
        df=wide_big_small_turnover_df,
        numerator_col='中证1000_日换手率',
        denominator_col='沪深300_日换手率',
        ratio_col='中证1000/沪深300_日换手率',
    )

    style_focus_df = append_rolling_sum_column(
        df=wide_big_small_turnover_df,
        window_size=get_avg_dt_count_via_dt_type(
            dt_type=TradeDtType.STOCK_MKT,
            period='三月',
        ),
        rolling_sum_col='风格关注度',
    )

    merged_style_focus_df = style_focus_df.join(
        big_small_df[['沪深300近两周收益率', '中证2000近两周收益率']], how='inner'
    )
    merged_style_focus_df.index.name = style_focus_df.index.name

    style_focus_quantile_info = [
        {
            'quantile': style_config.STYLE_FOCUS_CONFIG['QUANTILE_CEILING'],
            'col': style_config.STYLE_FOCUS_CONFIG['QUANTILE_CEILING_COL'],
            'dropna': False,
        },
        {
            'quantile': style_config.STYLE_FOCUS_CONFIG['QUANTILE_FLOOR'],
            'col': style_config.STYLE_FOCUS_CONFIG['QUANTILE_FLOOR_COL'],
            'dropna': True,
        },
    ]

    for info in style_focus_quantile_info:
        merged_style_focus_df = append_rolling_quantile_column(
            df=merged_style_focus_df,
            window_name=style_config.STYLE_FOCUS_CONFIG['QUANTILE_ROLLING_WINDOW'],
            window_size=style_config.STYLE_FOCUS_CONFIG['QUANTILE_ROLLING_WINDOW_SIZE'],
            target_col=style_config.STYLE_FOCUS_CONFIG['STYLE_FOCUS_COL'],
            rolling_quantile_col=info['col'],
            quantile=info['quantile'],
            dropna=info['dropna'],
        )

    style_focus_conditions = [
        (
            merged_style_focus_df[style_config.STYLE_FOCUS_CONFIG['STYLE_FOCUS_COL']]
            >= merged_style_focus_df[style_config.STYLE_FOCUS_CONFIG['QUANTILE_CEILING_COL']]
        )
        & (merged_style_focus_df['沪深300近两周收益率'] >= merged_style_focus_df['中证2000近两周收益率']),
        (
            merged_style_focus_df[style_config.STYLE_FOCUS_CONFIG['STYLE_FOCUS_COL']]
            <= merged_style_focus_df[style_config.STYLE_FOCUS_CONFIG['QUANTILE_FLOOR_COL']]
        )
        & (merged_style_focus_df['沪深300近两周收益率'] <= merged_style_focus_df['中证2000近两周收益率']),
    ]
    style_focus_choices = [
        style_config.STYLE_FOCUS_CHART_PARAM.bar_param.false_signal,
        style_config.STYLE_FOCUS_CHART_PARAM.bar_param.true_signal,
    ]
    merged_style_focus_df = apply_signal_from_conditions(
        df=merged_style_focus_df,
        signal_col=style_config.STYLE_FOCUS_CONFIG['SIGNAL_COL'],
        conditions=style_focus_conditions,
        choices=style_focus_choices,
        default=style_config.STYLE_FOCUS_CHART_PARAM.bar_param.no_signal,
    )

    return merged_style_focus_df


def prepare_shibor_prices_data(long_raw_shibor_df: pd.DataFrame) -> pd.DataFrame:
    """Prepare data for Shibor 3M (monetary cycle) block."""
    wide_raw_shibor_prices_df = reshape_long_df_into_wide_form(
        long_df=long_raw_shibor_df,
        index_col=style_config.SHIBOR_PRICES_COL_PARAM.dt_col,
        name_col=style_config.SHIBOR_PRICES_COL_PARAM.term_col,
        value_col=style_config.SHIBOR_PRICES_COL_PARAM.ytm_col,
    )

    shibor_prices_df = append_rolling_mean_column(
        df=wide_raw_shibor_prices_df,
        window_name=style_config.SHIBOR_PRICES_CONFIG['ROLLING_WINDOW'],
        window_size=style_config.SHIBOR_PRICES_CONFIG['ROLLING_WINDOW_SIZE'],
        rolling_mean_col=style_config.SHIBOR_PRICES_CONFIG['MEAN_COL'],
    )

    return shibor_prices_df


def prepare_housing_invest_data(wide_raw_edb_df: pd.DataFrame) -> pd.DataFrame:
    """Prepare data for housing investment YoY growth block."""
    wide_raw_housing_invest_df = wide_raw_edb_df[[style_config.HOUSING_INVEST_CONFIG['HOUSING_INVEST_COL']]]

    wide_raw_housing_invest_df = append_year_on_year_growth_column(
        indexed_df=wide_raw_housing_invest_df,
        yoy_col=style_config.HOUSING_INVEST_CONFIG['YOY_COL'],
    )

    wide_raw_housing_invest_df[style_config.HOUSING_INVEST_CONFIG['PRE_YOY_COL']] = wide_raw_housing_invest_df[
        style_config.HOUSING_INVEST_CONFIG['YOY_COL']
    ].shift(periods=1)
    wide_raw_housing_invest_df.dropna(inplace=True)

    return wide_raw_housing_invest_df


def prepare_big_small_momentum_data(
    raw_wide_idx_df: pd.DataFrame,
    idx_name_df: pd.DataFrame,
):
    """Prepare data for big vs small cap momentum block."""
    big_name_col, small_name_col = tuple(
        map(
            lambda x: idx_name_df.loc[style_config.STYLE_IDX_CODES[x]].values[0],
            ['大盘', '小盘'],
        )
    )
    big_small_df = raw_wide_idx_df[[big_name_col, small_name_col]].copy()
    big_small_df = append_ratio_column(
        df=big_small_df,
        numerator_col=big_name_col,
        denominator_col=small_name_col,
        ratio_col='沪深300/中证2000',
    )
    big_small_df = append_rolling_mean_column(
        df=big_small_df,
        window_name='一月',
        window_size=config.TRADE_DT_COUNT['一月'],
        dropna=False,
    )

    ratio_mean_df = big_small_df[['沪深300/中证2000', '近一月均值']].dropna(inplace=False)

    for col, new_col in zip(
        [big_name_col, small_name_col],
        ['沪深300近一月收益率', '中证2000近一月收益率'],
    ):
        big_small_df[new_col] = big_small_df[col].pct_change(
            get_avg_dt_count_via_dt_type(
                dt_type=TradeDtType.STOCK_MKT,
                period='一月',
            )
        )
    for col, new_col in zip(
        [big_name_col, small_name_col],
        ['沪深300近两周收益率', '中证2000近两周收益率'],
    ):
        big_small_df[new_col] = big_small_df[col].pct_change(
            get_avg_dt_count_via_dt_type(
                dt_type=TradeDtType.STOCK_MKT,
                period='两周',
            )
        )
    big_small_df.dropna(inplace=True)

    pct_change_df = big_small_df[
        [
            '沪深300近一月收益率',
            '中证2000近一月收益率',
            '沪深300近两周收益率',
            '中证2000近两周收益率',
        ]
    ].dropna(inplace=False)

    big_small_df = append_difference_column(
        df=big_small_df,
        minuend_col='沪深300近一月收益率',
        subtrahend_col='中证2000近一月收益率',
        difference_col='大盘对小盘近一月超额',
    )
    big_small_df = append_difference_column(
        df=big_small_df,
        minuend_col='沪深300近两周收益率',
        subtrahend_col='中证2000近两周收益率',
        difference_col='大盘对小盘近两周超额',
    )
    big_small_df = append_sum_column(
        df=big_small_df,
        sum_1_col='大盘对小盘近一月超额',
        sum_2_col='大盘对小盘近两周超额',
        sum_col='相对动量',
        multiplier_1=1,
        multiplier_2=2,
        multiplier_sum=0.5,
    )

    big_small_conditions = [
        (big_small_df['大盘对小盘近一月超额'] < 0) & (big_small_df['大盘对小盘近两周超额'] < 0),
        (big_small_df['大盘对小盘近一月超额'] > 0) & (big_small_df['大盘对小盘近两周超额'] > 0),
    ]
    big_small_choices = [
        param_cls.TradeSignal.LONG_SMALL.value,
        param_cls.TradeSignal.LONG_BIG.value,
    ]
    big_small_df = apply_signal_from_conditions(
        df=big_small_df,
        signal_col='交易信号',
        conditions=big_small_conditions,
        choices=big_small_choices,
        default=param_cls.TradeSignal.NO_SIGNAL.value,
    )

    signal_df = big_small_df

    return ratio_mean_df, pct_change_df, signal_df


@msg_printer
def generate_style_charts():
    formatted_latest_day = date.today().strftime(config.WIND_DT_FORMAT)

    # wind_portal_keys = [
    #     param_cls.WindPortal.CN_BOND_YIELD,
    #     param_cls.WindPortal.A_IDX_VAL,
    #     param_cls.WindPortal.EDB,
    # ]
    wind_local_keys = [
        'CN_BOND_YIELD',
        'A_IDX_VAL',
        'EDB',
        'SHIBOR_PRICES',
    ]

    # long_raw_df_collection = {
    #     key: fetch_data_with_wind_portal(
    #         latest_date=formatted_latest_day,
    #         _config=style_config.DATA_QUERY_PARAM[key],
    #         table_name=key,
    #     )
    #     for key in wind_portal_keys
    # }
    # st.write(long_raw_df_collection[param_cls.WindPortal.CN_BOND_YIELD])

    long_raw_df_collection = {
        key: fetch_data_from_local(
            latest_date=formatted_latest_day,
            table_name=key,
        )
        for key in wind_local_keys
    }
    # st.write(long_raw_df_collection["CN_BOND_YIELD"])
    # st.write(long_raw_df_collection['SHIBOR_PRICES'])
    # long_raw_edb_df = fetch_data_with_wind_portal(
    #     latest_date=formatted_latest_day,
    #     config=style_config.DATA_QUERY_PARAM[param_cls.WindPortal.EDB],
    #     table_name=param_cls.WindPortal.EDB,
    # )
    # # st.write(long_raw_edb_df)
    # long_raw_a_idx_val = fetch_data_with_wind_portal(
    #     latest_date=formatted_latest_day,
    #     config=style_config.DATA_QUERY_PARAM[param_cls.WindPortal.A_IDX_VAL],
    #     table_name=param_cls.WindPortal.A_IDX_VAL,
    # )
    # # st.write(long_raw_a_idx_val)
    # long_raw_cn_bond_yield_df = fetch_data_with_wind_portal(
    #     latest_date=formatted_latest_day,
    #     config=style_config.DATA_QUERY_PARAM[param_cls.WindPortal.CN_BOND_YIELD],
    #     table_name=param_cls.WindPortal.CN_BOND_YIELD,
    # )
    # # st.write(long_raw_cn_bond_yield_df)

    wide_raw_edb_df = reshape_long_df_into_wide_form(
        long_df=long_raw_df_collection['EDB'],
        index_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.EDB].dt_col,
        name_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.EDB].name_col,
        value_col=style_config.DATA_COL_PARAM[param_cls.WindPortal.EDB].value_col,
    )
    # st.write(long_raw_df_collection[param_cls.WindPortal.A_IDX_VAL])
    long_wind_all_a_idx_val_df = long_raw_df_collection['A_IDX_VAL'].query(
        f'{style_config.DATA_COL_PARAM[param_cls.WindPortal.A_IDX_VAL].name_col} == "万得全A"'
    )
    long_big_small_idx_val_df = long_raw_df_collection['A_IDX_VAL'].query(
        f'{style_config.DATA_COL_PARAM[param_cls.WindPortal.A_IDX_VAL].name_col} in ("沪深300", "中证1000")'
    )
    # st.write(long_big_small_idx_val_df)

    # wide_raw_df_collection = {
    #     key: reshape_long_df_into_wide_form(
    #         long_df=long_raw_df_collection[key],
    #         index_col=style_config.DATA_COL_PARAM[key].dt_col,
    #         name_col=style_config.DATA_COL_PARAM[key].name_col,
    #         value_col=style_config.DATA_COL_PARAM[key].value_col,
    #     )
    #     for key in wind_portal_keys
    # }

    # st.write(long_raw_edb_df)

    wind_idx_param = param_cls.WindListedSecParam(
        wind_codes=tuple(style_config.STYLE_IDX_CODES.values()),
        start_date=style_config.START_DT,
        sql_param=param_cls.SqlParam(
            sql_name=config.IDX_PRICE_SQL_NAME,
        ),
        end_date=formatted_latest_day,
    )

    idx_col_param = param_cls.WindIdxColParam()

    # raw_long_idx_df = fetch_index_data_with_wind_portal(latest_date=formatted_latest_day, _config=wind_idx_param)
    # st.write(raw_long_idx_df)
    raw_long_idx_df = fetch_index_data_from_local(latest_date=formatted_latest_day, _config=wind_idx_param)
    # st.write(raw_long_idx_df)

    idx_name_df = (
        raw_long_idx_df[[idx_col_param.code_col, idx_col_param.name_col]]
        .drop_duplicates()
        .set_index(idx_col_param.code_col, drop=True)
        .reindex(wind_idx_param.wind_codes)
    )

    raw_wide_idx_df = reshape_long_df_into_wide_form(
        long_df=raw_long_idx_df,
        index_col=idx_col_param.dt_col,
        name_col=idx_col_param.name_col,
        value_col=idx_col_param.price_col,
    )

    st.header('风格研判')
    tab1, tab2 = st.tabs(['价值成长研判框架', '大小盘研判框架'])

    # 1. 价值成长研判框架

    with tab1:
        # NOTE 国证价值/国证成长

        ratio_mean_df, value_growth_pct_change_df, value_growth_signal_df = prepare_value_growth_data(
            raw_wide_idx_df=raw_wide_idx_df,
            idx_name_df=idx_name_df,
        )

        value_name_col, growth_name_col = tuple(
            map(
                lambda x: idx_name_df.loc[style_config.STYLE_IDX_CODES[x]].values[0],
                ['价值', '成长'],
            )
        )

        value_growth_line_param = param_cls.IdxLineParam(
            axis_names=style_config.STYLE_CHART_AXIS_NAMES['VALUE_GROWTH_RATIO_MEAN'],
            title=f'{value_name_col}/{growth_name_col}',
            y_axis_format=config.CHART_NUM_FORMAT['float'],
        )
        draw_grouped_lines(ratio_mean_df, value_growth_line_param)

        # NOTE 相对动量(价值/成长)
        value_growth_line_config = param_cls.IdxLineParam(
            axis_names=style_config.STYLE_CHART_AXIS_NAMES['VALUE_GROWTH_PCT_CHANGE'],
            title='价值 VS 成长',
            y_axis_format=config.CHART_NUM_FORMAT['pct'],
            dt_slider_param=param_cls.DtSliderParam(
                start_dt='20200603',
                default_start_offset=style_config.RELATIVE_MOMENTUM_VALUE_GROWTH_CONFIG[
                    'SLIDER_DEFAULT_OFFSET_DT_COUNT'
                ],
                key='VALUE_GROWTH_PCT_CHANGE_SLIDER',
            ),
        )

        draw_grouped_lines(
            value_growth_pct_change_df,
            value_growth_line_config,
        )

        # value_growth_pct_change_slider_dt = st.select_slider(
        #     '自选日期',
        #     options=value_growth_df.index.tolist(),
        # )

        draw_bar_line_chart_with_highlighted_predefined_signal(
            dt_indexed_df=value_growth_signal_df,
            config=style_config.RELATIVE_MOMENTUM_VALUE_GROWTH_CHART_PARAM,
        )

        # NOTE 市场情绪

        wide_wind_all_a_turnover_df = prepare_index_turnover_data(long_wind_all_a_idx_val_df)

        draw_bar_line_chart_with_highlighted_predefined_signal(
            dt_indexed_df=wide_wind_all_a_turnover_df,
            config=style_config.INDEX_TURNOVER_CHART_PARAM,
        )

        # NOTE 期限利差
        # 需求：基准线从近一年均值改为近一月均值

        term_spread_df, yield_curve_df, wide_raw_cn_bond_yield_df = prepare_term_spread_data(
            long_raw_cn_bond_yield_df=long_raw_df_collection['CN_BOND_YIELD'],
        )

        draw_bar_line_chart_with_highlighted_signal(
            dt_indexed_df=term_spread_df, config=style_config.TERM_SPREAD_CHART_PARAM
        )

        term_spread_line_config = param_cls.IdxLineParam(
            axis_names=style_config.STYLE_CHART_AXIS_NAMES['LONG_SHORT_TERM_RATE'],
            title='国债到期收益率',
            data_col_param=param_cls.WindIdxColParam(
                dt_col=term_spread_df.index.name,
            ),
            y_limit_extra=0.005,
            y_axis_format=config.CHART_NUM_FORMAT['pct'],
            dt_slider_param=param_cls.DtSliderParam(
                start_dt='20200601',
                default_start_offset=style_config.TERM_SPREAD_CONFIG['SLIDER_DEFAULT_OFFSET_DT_COUNT'],
                key='long_short_term_SLIDER',
            ),
        )

        draw_grouped_lines(
            yield_curve_df.div(100).dropna(inplace=False),
            term_spread_line_config,
        )

        # NOTE ERP股债性价比（价值成长）
        # ERP位置和趋势：高位下行时，做多成长；低位上行时，做多价值;以站上过去1个月均线作为趋势的判断

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
            signal_col=style_config.INDEX_ERP_CONFIG['SIGNAL_COL'],
            conditions=erp_conditions,
            choices=erp_choices,
            default=style_config.INDEX_ERP_CHART_PARAM.bar_param.no_signal,
        )

        draw_bar_line_chart_with_highlighted_predefined_signal(
            dt_indexed_df=wide_erp_df,
            config=style_config.INDEX_ERP_CHART_PARAM,
        )

        # NOTE 信用扩张：金融机构各项贷款余额同比

        credit_expansion_df = (
            wide_raw_edb_df[[style_config.CREDIT_EXPANSION_CONFIG['CREDIT_EXPANSION_COL']]]
            .copy()
            .rename(
                columns=(
                    {
                        style_config.CREDIT_EXPANSION_CONFIG[
                            'CREDIT_EXPANSION_COL'
                        ]: style_config.CREDIT_EXPANSION_CONFIG['YOY_COL'],
                    }
                )
            )
        )

        credit_expansion_df = append_rolling_mean_column(
            df=credit_expansion_df,
            window_name=style_config.CREDIT_EXPANSION_CONFIG['ROLLING_WINDOW'],
            window_size=style_config.CREDIT_EXPANSION_CONFIG['ROLLING_WINDOW_SIZE'],
            rolling_mean_col=style_config.CREDIT_EXPANSION_CONFIG['MEAN_COL'],
        )
        credit_expansion_conditions = [
            credit_expansion_df[style_config.CREDIT_EXPANSION_CONFIG['YOY_COL']]
            >= credit_expansion_df[style_config.CREDIT_EXPANSION_CONFIG['MEAN_COL']],
        ]
        credit_expansion_choices = [
            style_config.CREDIT_EXPANSION_CONFIG['TRUE_SIGNAL'],
        ]
        credit_expansion_df = apply_signal_from_conditions(
            df=credit_expansion_df,
            signal_col=style_config.CREDIT_EXPANSION_CONFIG['SIGNAL_COL'],
            conditions=credit_expansion_conditions,
            choices=credit_expansion_choices,
            default=style_config.CREDIT_EXPANSION_CONFIG['FALSE_SIGNAL'],
        )
        draw_bar_line_chart_with_highlighted_signal(
            dt_indexed_df=credit_expansion_df,
            config=style_config.CREDIT_EXPANSION_CHART_PARAM,
        )

    # 2. 大小盘研判框架
    with tab2:
        # NOTE 大小盘比价 —— 沪深300/中证2000

        big_small_ratio_df, big_small_pct_change_df, big_small_signal_df = prepare_big_small_momentum_data(
            raw_wide_idx_df=raw_wide_idx_df,
            idx_name_df=idx_name_df,
        )

        big_name_col, small_name_col = tuple(
            map(
                lambda x: idx_name_df.loc[style_config.STYLE_IDX_CODES[x]].values[0],
                ['大盘', '小盘'],
            )
        )

        big_small_line_config = param_cls.IdxLineParam(
            axis_names=style_config.STYLE_CHART_AXIS_NAMES['BIG_SMALL_RATIO_MEAN'],
            title=f'{big_name_col}/{small_name_col}',
            y_axis_format=config.CHART_NUM_FORMAT['float'],
        )
        draw_grouped_lines(
            big_small_ratio_df,
            big_small_line_config,
        )
        # st.write(big_small_df)

        # NOTE 相对动量(大盘/小盘)
        big_small_line_config = param_cls.IdxLineParam(
            axis_names=style_config.STYLE_CHART_AXIS_NAMES['VALUE_GROWTH_PCT_CHANGE'],
            title='大盘 VS 小盘',
            y_axis_format=config.CHART_NUM_FORMAT['pct'],
            dt_slider_param=param_cls.DtSliderParam(
                start_dt='20200603',
                default_start_offset=style_config.RELATIVE_MOMENTUM_BIG_SMALL_CONFIG['SLIDER_DEFAULT_OFFSET_DT_COUNT'],
                key='BIG_SMALL_PCT_CHANGE_SLIDER',
            ),
        )

        draw_grouped_lines(
            big_small_pct_change_df,
            big_small_line_config,
        )

        # value_growth_pct_change_slider_dt = st.select_slider(
        #     '自选日期',
        #     options=value_growth_df.index.tolist(),
        # )

        draw_bar_line_chart_with_highlighted_predefined_signal(
            dt_indexed_df=big_small_signal_df,
            config=style_config.RELATIVE_MOMENTUM_BIG_SMALL_CHART_PARAM,
        )

        # NOTE 风格关注度

        merged_style_focus_df = prepare_style_focus_data(
            long_big_small_idx_val_df=long_big_small_idx_val_df,
            big_small_df=big_small_signal_df,
        )
        draw_bar_line_chart_with_highlighted_signal(
            dt_indexed_df=merged_style_focus_df,
            config=style_config.STYLE_FOCUS_CHART_PARAM,
        )

        # NOTE 货币周期：Shibor3M

        shibor_prices_df = prepare_shibor_prices_data(
            long_raw_shibor_df=long_raw_df_collection['SHIBOR_PRICES'],
        )

        shibor_conditions = [
            shibor_prices_df[style_config.SHIBOR_PRICES_CONFIG['SHIBOR_PRICE_COL']]
            >= shibor_prices_df[style_config.SHIBOR_PRICES_CONFIG['MEAN_COL']],
        ]
        shibor_choices = [
            style_config.SHIBOR_PRICES_CONFIG['TRUE_SIGNAL'],
        ]
        shibor_prices_df = apply_signal_from_conditions(
            df=shibor_prices_df,
            signal_col=style_config.SHIBOR_PRICES_CONFIG['SIGNAL_COL'],
            conditions=shibor_conditions,
            choices=shibor_choices,
            default=style_config.SHIBOR_PRICES_CONFIG['FALSE_SIGNAL'],
        )

        draw_bar_line_chart_with_highlighted_signal(
            dt_indexed_df=shibor_prices_df, config=style_config.SHIBOR_PRICES_CHART_PARAM
        )

        # NOTE 经济增长: 房地产完成额累计同比

        wide_raw_housing_invest_df = prepare_housing_invest_data(wide_raw_edb_df)

        housing_invest_conditions = [
            wide_raw_housing_invest_df[style_config.HOUSING_INVEST_CONFIG['YOY_COL']]
            >= wide_raw_housing_invest_df[style_config.HOUSING_INVEST_CONFIG['PRE_YOY_COL']],
        ]
        housing_invest_choices = [
            style_config.HOUSING_INVEST_CONFIG['TRUE_SIGNAL'],
        ]
        wide_raw_housing_invest_df = apply_signal_from_conditions(
            df=wide_raw_housing_invest_df,
            signal_col=style_config.HOUSING_INVEST_CONFIG['SIGNAL_COL'],
            conditions=housing_invest_conditions,
            choices=housing_invest_choices,
            default=style_config.HOUSING_INVEST_CONFIG['FALSE_SIGNAL'],
        )

        draw_bar_line_chart_with_highlighted_signal(
            dt_indexed_df=wide_raw_housing_invest_df,
            config=style_config.HOUSING_INVEST_CHART_PARAM,
        )
        # draw_test(
        #     dt_indexed_df=wide_raw_housing_invest_df,
        #     config=style_config.HOUSING_INVEST_CHART_PARAM,
        # )

        # NOTE 期现利差

        draw_bar_line_chart_with_highlighted_signal(
            dt_indexed_df=term_spread_df, config=style_config.TERM_SPREAD_2_CHART_PARAM
        )

        term_spread_2_line_config = param_cls.IdxLineParam(
            axis_names=style_config.STYLE_CHART_AXIS_NAMES['LONG_SHORT_TERM_RATE'],
            title='国债到期收益率',
            data_col_param=param_cls.WindIdxColParam(
                dt_col=term_spread_df.index.name,
            ),
            y_limit_extra=0.005,
            y_axis_format=config.CHART_NUM_FORMAT['pct'],
            dt_slider_param=param_cls.DtSliderParam(
                start_dt='20200601',
                default_start_offset=style_config.TERM_SPREAD_CONFIG['SLIDER_DEFAULT_OFFSET_DT_COUNT'],
                key='long_short_term_2_SLIDER',
            ),
        )

        draw_grouped_lines(
            term_spread_df[
                [
                    '1.0',
                    '10.0',
                ]
            ]
            .div(100)
            .dropna(inplace=False),
            term_spread_2_line_config,
        )

        # NOTE ERP股债性价比（大小盘）

        # st.write(big_small_df)

        # for col, new_col in zip(
        #     [big_name_col, small_name_col],
        #     ['沪深300近两月收益率', '中证2000近两月收益率'],
        # ):
        #     big_small_df[new_col] = big_small_df[col].pct_change(
        #         get_avg_dt_count_via_dt_type(
        #             dt_type=TradeDtType.STOCK_MKT,
        #             period='两月',
        #         )
        #     )
        # for col, new_col in zip(
        #     [big_name_col, small_name_col],
        #     ['沪深300近两周收益率', '中证2000近两周收益率'],
        # ):
        #     big_small_df[new_col] = big_small_df[col].pct_change(
        #         get_avg_dt_count_via_dt_type(
        #             dt_type=TradeDtType.STOCK_MKT,
        #             period='两周',
        #         )
        #     )

        # st.write(big_small_df)

        merged_erp_df = wide_erp_df.join(big_small_signal_df, how='inner', lsuffix='_erp', rsuffix='_big_small')
        merged_erp_df.index.name = wide_erp_df.index.name
        # st.write(merged_erp_df)
        # erp_conditions = [
        #     (
        #         merged_erp_df[style_config.INDEX_ERP_CONFIG['ERP_COL']]
        #         >= merged_erp_df[style_config.INDEX_ERP_CONFIG['QUANTILE_CEILING_COL']]
        #     )
        #     & (merged_erp_df['沪深300近两月收益率'] < merged_erp_df['中证2000近两月收益率'])
        #     & (merged_erp_df['沪深300近两月收益率'] < 0),
        #     (
        #         merged_erp_df[style_config.INDEX_ERP_CONFIG['ERP_COL']]
        #         >= merged_erp_df[style_config.INDEX_ERP_CONFIG['QUANTILE_CEILING_COL']]
        #     )
        #     & (merged_erp_df['沪深300近两月收益率'] > merged_erp_df['中证2000近两月收益率'])
        #     & (merged_erp_df['沪深300近两月收益率'] > 0),
        #     (
        #         merged_erp_df[style_config.INDEX_ERP_CONFIG['ERP_COL']]
        #         < merged_erp_df[style_config.INDEX_ERP_CONFIG['QUANTILE_FLOOR_COL']]
        #     ),
        # ]
        # erp_choices = [
        #     style_config.INDEX_ERP_2_CHART_PARAM.bar_param.false_signal,
        #     style_config.INDEX_ERP_2_CHART_PARAM.bar_param.true_signal,
        #     style_config.INDEX_ERP_2_CHART_PARAM.bar_param.false_signal,
        # ]

        erp_2_choices = [
            style_config.INDEX_ERP_2_CHART_PARAM.bar_param.true_signal,
            style_config.INDEX_ERP_2_CHART_PARAM.bar_param.false_signal,
        ]
        wide_erp_2_df = wide_erp_df.copy()
        wide_erp_2_df = apply_signal_from_conditions(
            df=wide_erp_2_df,
            signal_col=style_config.INDEX_ERP_CONFIG['SIGNAL_COL'],
            conditions=erp_conditions,
            choices=erp_2_choices,
            default=style_config.INDEX_ERP_2_CHART_PARAM.bar_param.no_signal,
        )
        # st.write(wide_erp_2_df)

        draw_bar_line_chart_with_highlighted_signal(
            dt_indexed_df=wide_erp_2_df,
            config=style_config.INDEX_ERP_2_CHART_PARAM,
        )

        # TODO 对于通过个人api获取的数据和图，需要添加一个按钮，用于切换是否显示
