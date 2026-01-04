import pandas as pd
import streamlit as st

from config import config, financial_factors_config, param_cls
from data_preparation.data_fetcher import fetch_data_from_local, fetch_financial_factors_stocks_from_local
from utils import msg_printer
from visualization.data_visualizer import (
    add_altair_bar_with_highlighted_signal,
    add_altair_line_with_stroke_dash,
)

# format:  str, "plain", "localized", "percent", "dollar", "euro", "yen", "accounting", "compact", "scientific", "engineering", or None
PERCENT_COL_KEYWORDS = ('分位', '同比', '环比', '增速', '比例', '率', '比', 'ROE')
BIG_NUM_COL_KEYWORDS = ('利润', '现金')
PERCENT_DISPLAY_FORMAT = '%.0f%%'

BACKTEST_NAV_TABLE_NAME = 'FINANCIAL_FACTORS_BACKTEST_NAV'
BACKTEST_NAV_CSV_PATH = 'data/csv/financial_factors_backtest_nav.csv'
BACKTEST_NAV_DATE_COL = '交易日期'
BACKTEST_NAV_STRATEGY_COL = '中性股息股票池'
BACKTEST_NAV_STRATEGY_LABEL = '中性股息'
BACKTEST_NAV_BENCH_COL = '中证红利全收益'
BACKTEST_NAV_PERIOD_OPTIONS = ['2025年', '近一年', '近半年', '2018年5月以来']
BACKTEST_NAV_DEFAULT_PERIOD = '2025年'

BACKTEST_NAV_EXCESS_COL = '超额'
BACKTEST_NAV_EXCESS_STATE_COL = '累计超额'
BACKTEST_NAV_EXCESS_POS = '正超额'
BACKTEST_NAV_EXCESS_NEG = '负超额'


def _wrap_header_label(label: str) -> str:
    if '（' in label:
        head, tail = label.split('（', 1)
        return f'{head}\n（{tail}'
    if ' ' in label:
        head, tail = label.split(' ', 1)
        return f'{head}\n{tail}'

    wrap_suffixes = ('环比', '分位', '增速')
    for suffix in wrap_suffixes:
        if label.endswith(suffix) and len(label) > len(suffix) + 4:
            return f'{label[: -len(suffix)]}\n{suffix}'

    return label


def _is_percent_col(col_name: str) -> bool:
    return any(keyword in col_name for keyword in PERCENT_COL_KEYWORDS)


def _is_big_num_col(col_name: str) -> bool:
    return any(keyword in col_name for keyword in BIG_NUM_COL_KEYWORDS)


def _build_column_config(cols: list[str]) -> dict[str, st.column_config.Column]:
    column_config: dict[str, st.column_config.Column] = {}
    for col in cols:
        width = 'small'
        label = _wrap_header_label(col)
        if _is_percent_col(col):
            column_config[col] = st.column_config.NumberColumn(
                label=label,
                help=col,
                width=width,
                format=PERCENT_DISPLAY_FORMAT,
            )
        elif _is_big_num_col(col):
            column_config[col] = st.column_config.NumberColumn(label=label, help=col, width=width, format='compact')
        else:
            column_config[col] = st.column_config.Column(label=label, help=col, width=width)
    return column_config


def _get_trade_dates_desc(df: pd.DataFrame) -> list[str]:
    date_col = financial_factors_config.DATE_COL
    raw_dates = df[date_col].astype(str).map(str.strip)
    valid_dates = [dt for dt in raw_dates.unique().tolist() if dt and dt.isdigit()]
    return sorted(valid_dates, reverse=True)


def _filter_stock_pool(df: pd.DataFrame, trade_date: str, signal_col: str) -> pd.DataFrame:
    date_col = financial_factors_config.DATE_COL
    date_mask = df[date_col].astype(str) == str(trade_date)
    signal_mask = pd.to_numeric(df[signal_col], errors='coerce') == 1
    return df.loc[date_mask & signal_mask].copy()


def _prepare_backtest_nav_chart_df(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Prepare dt-indexed frame for raw NAV lines.

    Normalization and excess calculation are applied after the user selects
    a date window so they re-base on every slider change.
    """
    df = raw_df[[BACKTEST_NAV_DATE_COL, BACKTEST_NAV_STRATEGY_COL, BACKTEST_NAV_BENCH_COL]].copy()
    df[BACKTEST_NAV_DATE_COL] = df[BACKTEST_NAV_DATE_COL].astype(str).str.strip()

    df = (
        df.sort_values(by=BACKTEST_NAV_DATE_COL, ascending=True)
        .drop_duplicates(subset=[BACKTEST_NAV_DATE_COL], keep='last')
        .rename(columns={BACKTEST_NAV_STRATEGY_COL: BACKTEST_NAV_STRATEGY_LABEL})
    )

    df = df.set_index(BACKTEST_NAV_DATE_COL, drop=True)
    return df


def _get_backtest_nav_period_range(trade_dt: list[str], period: str) -> tuple[str, str]:
    if not trade_dt:
        return '', ''

    trade_dt = sorted(trade_dt)
    latest_dt = trade_dt[-1]

    if period == '近一年':
        start_idx = max(0, len(trade_dt) - config.TRADE_DT_COUNT['一年'])
        return trade_dt[start_idx], latest_dt

    if period == '近半年':
        start_idx = max(0, len(trade_dt) - config.TRADE_DT_COUNT['半年'])
        return trade_dt[start_idx], latest_dt

    if period == '2018年5月以来':
        start_dt = '20180501'
        eligible_dt = [dt for dt in trade_dt if dt >= start_dt]
        return (eligible_dt[0], latest_dt) if eligible_dt else (trade_dt[0], latest_dt)

    if period == '2025年':
        year_start = '20250101'
        year_end = '20251231'
        eligible_dt = [dt for dt in trade_dt if year_start <= dt <= year_end]
        return (eligible_dt[0], eligible_dt[-1]) if eligible_dt else (trade_dt[0], latest_dt)

    return trade_dt[0], latest_dt


def _render_dividend_neutral_backtest_nav_chart() -> None:
    st.subheader('股票池累计收益与超额')

    raw_df = fetch_data_from_local(latest_date='99991231', table_name=BACKTEST_NAV_TABLE_NAME)
    if raw_df.empty:
        st.warning(f'未读取到回测净值数据：{BACKTEST_NAV_CSV_PATH}')
        return

    dt_indexed_df = _prepare_backtest_nav_chart_df(raw_df=raw_df)
    trade_dt = dt_indexed_df.index.tolist()

    selected_period = st.selectbox(
        '区间',
        options=BACKTEST_NAV_PERIOD_OPTIONS,
        index=BACKTEST_NAV_PERIOD_OPTIONS.index(BACKTEST_NAV_DEFAULT_PERIOD),
        key='FINANCIAL_FACTORS_BACKTEST_NAV_PERIOD',
    )
    custom_dt = _get_backtest_nav_period_range(trade_dt=trade_dt, period=selected_period)
    selected_df = dt_indexed_df.loc[custom_dt[0] : custom_dt[1]].reset_index()
    if selected_df.empty:
        st.info('当前区间无可用数据')
        return

    for nav_col in (BACKTEST_NAV_STRATEGY_LABEL, BACKTEST_NAV_BENCH_COL):
        selected_df[nav_col] = selected_df[nav_col].div(selected_df[nav_col].iloc[0]).sub(1)

    selected_df[BACKTEST_NAV_EXCESS_COL] = (
        selected_df[BACKTEST_NAV_STRATEGY_LABEL] - selected_df[BACKTEST_NAV_BENCH_COL]
    )
    is_pos = selected_df[BACKTEST_NAV_EXCESS_COL].ge(0)
    selected_df[BACKTEST_NAV_EXCESS_STATE_COL] = is_pos.map(
        {True: BACKTEST_NAV_EXCESS_POS, False: BACKTEST_NAV_EXCESS_NEG}
    )

    bar_param = param_cls.SignalBarParam(
        axis_names={
            'X': BACKTEST_NAV_DATE_COL,
            'Y': BACKTEST_NAV_EXCESS_COL,
            'LEGEND': BACKTEST_NAV_EXCESS_STATE_COL,
        },
        title='中性股息 vs 中证红利全收益：累计收益与累计超额',
        y_axis_format=config.CHART_NUM_FORMAT['pct'],
        true_signal=BACKTEST_NAV_EXCESS_POS,
        false_signal=BACKTEST_NAV_EXCESS_NEG,
        no_signal=None,
        signal_order=[BACKTEST_NAV_EXCESS_NEG, BACKTEST_NAV_EXCESS_POS],
    )
    line_param = param_cls.LineParam(
        axis_names={
            'X': BACKTEST_NAV_DATE_COL,
            'Y': '累计收益',
            'LEGEND': '投资标的',
        },
        y_axis_format=config.CHART_NUM_FORMAT['pct'],
        compared_cols=[BACKTEST_NAV_STRATEGY_LABEL, BACKTEST_NAV_BENCH_COL],
    )

    bar = add_altair_bar_with_highlighted_signal(selected_df, bar_param)
    line = add_altair_line_with_stroke_dash(selected_df, line_param)
    st.altair_chart(
        (bar + line).resolve_scale(color='independent'),
        theme='streamlit',
        use_container_width=True,
    )


def _render_strategy_stock_pool(df: pd.DataFrame, strategy_name: str, trade_dates: list[str] | None = None) -> None:
    st.subheader(f'{strategy_name}股票池')

    strategy_cfg = financial_factors_config.STOCK_POOL_STRATEGIES[strategy_name]
    signal_col = strategy_cfg['signal_col']
    display_cols = strategy_cfg['display_cols']
    code_col = financial_factors_config.CODE_COL

    if trade_dates is None:
        trade_dates = _get_trade_dates_desc(df)
    if not trade_dates:
        st.warning('CSV中无可用交易日期')
        return
    selected_date = st.selectbox('交易日期', options=trade_dates, index=0, key=strategy_cfg['date_select_key'])

    pool_df = _filter_stock_pool(df=df, trade_date=selected_date, signal_col=signal_col)

    st.caption(f'入池数量：{len(pool_df)}')
    if pool_df.empty:
        st.info('该日期无入池股票')
        return

    pool_df[code_col] = pool_df[code_col].astype(str).str.strip()
    pool_df = pool_df.set_index(code_col, drop=True).sort_index()

    effective_display_cols = [col for col in display_cols if col != code_col]
    available_cols = [col for col in effective_display_cols if col in pool_df.columns]
    missing_cols = [col for col in effective_display_cols if col not in pool_df.columns]
    if missing_cols:
        st.warning(f'以下字段在CSV中不存在，已忽略：{missing_cols}')

    if not available_cols:
        st.warning('当前策略未配置可用展示字段，将展示全部字段。')
        available_cols = pool_df.columns.tolist()

    for col in available_cols:
        if _is_percent_col(col):
            pool_df[col] = pd.to_numeric(pool_df[col], errors='coerce') * 100
        elif _is_big_num_col(col):
            pool_df[col] = pd.to_numeric(pool_df[col], errors='coerce')

    st.dataframe(
        pool_df[available_cols],
        use_container_width=True,
        column_config=_build_column_config(available_cols),
    )


@msg_printer
def generate_financial_factors_stocks_charts():
    st.header('财务选股')
    tab1, tab2, tab3 = st.tabs(['中性股息', '细分龙头', '景气成长'])

    df = fetch_financial_factors_stocks_from_local(latest_date='99991231')
    if df.empty:
        st.warning('未读取到财务选股数据：data/csv/financial_factors_stocks.csv')
        return
    trade_dates = _get_trade_dates_desc(df)

    with tab1:
        _render_strategy_stock_pool(df=df, strategy_name='中性股息', trade_dates=trade_dates)
        _render_dividend_neutral_backtest_nav_chart()

    with tab2:
        _render_strategy_stock_pool(df=df, strategy_name='细分龙头', trade_dates=trade_dates)

    with tab3:
        _render_strategy_stock_pool(df=df, strategy_name='景气成长', trade_dates=trade_dates)
