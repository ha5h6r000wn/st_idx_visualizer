import numpy as np
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
BACKTEST_NAV_SEGMENT_LEADERS_COL = '细分龙头股票池'
BACKTEST_NAV_CYCLICAL_GROWTH_COL = '景气成长股票池'
BACKTEST_NAV_CSI300_COL = '沪深300'
BACKTEST_NAV_PERIOD_OPTIONS = ['2025年', '近一年', '近半年', '2018年5月以来']
BACKTEST_NAV_DEFAULT_PERIOD = '2025年'

BACKTEST_NAV_EXCESS_COL = '超额收益'
BACKTEST_NAV_EXCESS_STATE_COL = '累计超额'
BACKTEST_NAV_EXCESS_POS = '正超额'
BACKTEST_NAV_EXCESS_NEG = '负超额'
BACKTEST_NAV_PERF_TABLE_EXCESS_LABEL = '超额收益'
BACKTEST_NAV_DEFAULT_RF_ANNUAL = 0.013

BACKTEST_NAV_CHART_CONFIGS = {
    '中性股息': {
        'strategy_nav_col': BACKTEST_NAV_STRATEGY_COL,
        'strategy_label': BACKTEST_NAV_STRATEGY_LABEL,
        'bench_nav_col': BACKTEST_NAV_BENCH_COL,
        'title': '中性股息 vs 中证红利全收益：累计收益与超额收益',
        'period_select_key': 'FINANCIAL_FACTORS_BACKTEST_NAV_PERIOD',
    },
    '细分龙头': {
        'strategy_nav_col': BACKTEST_NAV_SEGMENT_LEADERS_COL,
        'strategy_label': '细分龙头',
        'bench_nav_col': BACKTEST_NAV_CSI300_COL,
        'title': '细分龙头 vs 沪深300：累计收益与超额收益',
        'period_select_key': 'FINANCIAL_FACTORS_BACKTEST_NAV_PERIOD_SEGMENT_LEADERS',
    },
    '景气成长': {
        'strategy_nav_col': BACKTEST_NAV_CYCLICAL_GROWTH_COL,
        'strategy_label': '景气成长',
        'bench_nav_col': BACKTEST_NAV_CSI300_COL,
        'title': '景气成长 vs 沪深300：累计收益与超额收益',
        'period_select_key': 'FINANCIAL_FACTORS_BACKTEST_NAV_PERIOD_CYCLICAL_GROWTH',
    },
}


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


def _prepare_backtest_nav_chart_df(
    raw_df: pd.DataFrame,
    *,
    strategy_nav_col: str,
    strategy_label: str,
    bench_nav_col: str,
) -> pd.DataFrame:
    """Prepare dt-indexed frame for raw NAV lines.

    Normalization and excess calculation are applied after the user selects
    a date window so they re-base on every slider change.
    """
    df = raw_df[[BACKTEST_NAV_DATE_COL, strategy_nav_col, bench_nav_col]].copy()
    df[BACKTEST_NAV_DATE_COL] = df[BACKTEST_NAV_DATE_COL].astype(str).str.strip()
    df[strategy_nav_col] = pd.to_numeric(df[strategy_nav_col], errors='coerce')
    df[bench_nav_col] = pd.to_numeric(df[bench_nav_col], errors='coerce')

    df = (
        df.sort_values(by=BACKTEST_NAV_DATE_COL, ascending=True)
        .drop_duplicates(subset=[BACKTEST_NAV_DATE_COL], keep='last')
        .rename(columns={strategy_nav_col: strategy_label})
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


def _normalize_nav_series(nav: pd.Series) -> pd.Series:
    nav = pd.to_numeric(nav, errors='coerce').dropna()
    if nav.empty:
        return nav

    base = nav.iloc[0]
    if pd.isna(base) or base == 0:
        return pd.Series(index=nav.index, dtype='float64')

    return nav.div(base)


def _calc_nav_metrics(nav: pd.Series, *, rf_annual: float, trading_days: int) -> dict[str, float]:
    nav_norm = _normalize_nav_series(nav)
    if nav_norm.empty:
        return {
            'period_return': np.nan,
            'annual_return': np.nan,
            'max_drawdown': np.nan,
            'sharpe': np.nan,
        }

    period_return = float(nav_norm.iloc[-1] - 1)

    drawdown = nav_norm.div(nav_norm.cummax()).sub(1)
    max_drawdown = float(drawdown.min()) if not drawdown.empty else np.nan

    daily_returns = nav_norm.pct_change().dropna()
    if daily_returns.empty:
        annual_return = np.nan
        sharpe = np.nan
    else:
        annual_return = float((1 + period_return) ** (trading_days / len(daily_returns)) - 1)

        rf_daily = float((1 + rf_annual) ** (1 / trading_days) - 1)
        excess_returns = daily_returns.sub(rf_daily)
        vol = float(excess_returns.std(ddof=1))
        sharpe = float(excess_returns.mean() / vol * np.sqrt(trading_days)) if vol and not np.isnan(vol) else np.nan

    return {
        'period_return': period_return,
        'annual_return': annual_return,
        'max_drawdown': max_drawdown,
        'sharpe': sharpe,
    }


def _calc_nav_norm_and_excess_nav(strategy_nav: pd.Series, bench_nav: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
    aligned = pd.DataFrame({'strategy': strategy_nav, 'benchmark': bench_nav}).apply(pd.to_numeric, errors='coerce')
    aligned = aligned.dropna()
    if aligned.empty:
        empty = pd.Series(dtype='float64')
        return empty, empty, empty

    strategy_norm = aligned['strategy'].div(aligned['strategy'].iloc[0])
    bench_norm = aligned['benchmark'].div(aligned['benchmark'].iloc[0])
    excess_nav = strategy_norm.div(bench_norm)
    return strategy_norm, bench_norm, excess_nav


def _render_backtest_nav_chart(
    *,
    raw_df: pd.DataFrame,
    strategy_nav_col: str,
    strategy_label: str,
    bench_nav_col: str,
    title: str,
    period_select_key: str,
    rf_annual: float,
) -> None:
    """Render a backtest NAV chart for one strategy vs one benchmark.

    Expects raw_df to contain `交易日期` plus the provided strategy/benchmark NAV columns.
    """
    st.subheader('股票池累计收益与超额')

    if raw_df.empty:
        st.warning(f'未读取到回测净值数据：{BACKTEST_NAV_CSV_PATH}')
        return

    required_cols = {BACKTEST_NAV_DATE_COL, strategy_nav_col, bench_nav_col}
    missing_cols = sorted(required_cols - set(raw_df.columns))
    if missing_cols:
        st.warning(f'回测净值数据缺少字段，已跳过绘图：{missing_cols}')
        return

    dt_indexed_df = _prepare_backtest_nav_chart_df(
        raw_df=raw_df,
        strategy_nav_col=strategy_nav_col,
        strategy_label=strategy_label,
        bench_nav_col=bench_nav_col,
    )
    trade_dt = dt_indexed_df.index.tolist()

    selected_period = st.selectbox(
        '区间',
        options=BACKTEST_NAV_PERIOD_OPTIONS,
        index=BACKTEST_NAV_PERIOD_OPTIONS.index(BACKTEST_NAV_DEFAULT_PERIOD),
        key=period_select_key,
    )
    custom_dt = _get_backtest_nav_period_range(trade_dt=trade_dt, period=selected_period)
    selected_df = dt_indexed_df.loc[custom_dt[0] : custom_dt[1]].reset_index()
    if selected_df.empty:
        st.info('当前区间无可用数据')
        return

    selected_df = selected_df.dropna(subset=[strategy_label, bench_nav_col])
    if selected_df.empty:
        st.info('当前区间无可用数据')
        return

    strategy_norm, bench_norm, excess_nav = _calc_nav_norm_and_excess_nav(
        selected_df[strategy_label], selected_df[bench_nav_col]
    )
    if strategy_norm.empty or bench_norm.empty or excess_nav.empty:
        st.info('当前区间无可用数据')
        return

    selected_df[strategy_label] = strategy_norm.sub(1)
    selected_df[bench_nav_col] = bench_norm.sub(1)

    selected_df[BACKTEST_NAV_EXCESS_COL] = (
        excess_nav.sub(1)
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
        title=title,
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
        compared_cols=[strategy_label, bench_nav_col],
    )

    bar = add_altair_bar_with_highlighted_signal(selected_df, bar_param)
    line = add_altair_line_with_stroke_dash(selected_df, line_param)
    st.altair_chart(
        (bar + line).resolve_scale(color='independent'),
        theme='streamlit',
        use_container_width=True,
    )

    st.subheader('区间绩效')
    trading_days = int(config.TRADE_DT_COUNT['一年'])
    metrics_by_asset = {
        strategy_nav_col: _calc_nav_metrics(strategy_norm, rf_annual=rf_annual, trading_days=trading_days),
        bench_nav_col: _calc_nav_metrics(bench_norm, rf_annual=rf_annual, trading_days=trading_days),
        BACKTEST_NAV_PERF_TABLE_EXCESS_LABEL: _calc_nav_metrics(excess_nav, rf_annual=rf_annual, trading_days=trading_days),
    }
    metrics_df = pd.DataFrame.from_dict(metrics_by_asset, orient='index').rename(
        columns={
            'period_return': '区间收益率',
            'annual_return': '年化收益率',
            'max_drawdown': '最大回撤',
            'sharpe': '夏普率',
        }
    )
    pct_cols = ['区间收益率', '年化收益率', '最大回撤']
    metrics_df[pct_cols] = metrics_df[pct_cols].mul(100)

    st.dataframe(
        metrics_df,
        use_container_width=True,
        column_config={
            '区间收益率': st.column_config.NumberColumn('区间收益率', format='%.2f%%'),
            '年化收益率': st.column_config.NumberColumn('年化收益率', format='%.2f%%'),
            '最大回撤': st.column_config.NumberColumn('最大回撤', format='%.2f%%'),
            '夏普率': st.column_config.NumberColumn('夏普率', format='%.2f'),
        },
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
    rf_pct = st.number_input(
        '无风险利率（年化，%）',
        min_value=0.0,
        max_value=20.0,
        value=float(BACKTEST_NAV_DEFAULT_RF_ANNUAL * 100),
        step=0.1,
        key='FINANCIAL_FACTORS_BACKTEST_RF_ANNUAL_PCT',
    )
    rf_annual = float(rf_pct) / 100
    tab1, tab2, tab3 = st.tabs(['中性股息', '细分龙头', '景气成长'])

    df = fetch_financial_factors_stocks_from_local(latest_date='99991231')
    if df.empty:
        st.warning('未读取到财务选股数据：data/csv/financial_factors_stocks.csv')
        return
    trade_dates = _get_trade_dates_desc(df)

    nav_df = fetch_data_from_local(latest_date='99991231', table_name=BACKTEST_NAV_TABLE_NAME)

    with tab1:
        _render_strategy_stock_pool(df=df, strategy_name='中性股息', trade_dates=trade_dates)
        _render_backtest_nav_chart(raw_df=nav_df, rf_annual=rf_annual, **BACKTEST_NAV_CHART_CONFIGS['中性股息'])

    with tab2:
        _render_strategy_stock_pool(df=df, strategy_name='细分龙头', trade_dates=trade_dates)
        _render_backtest_nav_chart(raw_df=nav_df, rf_annual=rf_annual, **BACKTEST_NAV_CHART_CONFIGS['细分龙头'])

    with tab3:
        _render_strategy_stock_pool(df=df, strategy_name='景气成长', trade_dates=trade_dates)
        _render_backtest_nav_chart(raw_df=nav_df, rf_annual=rf_annual, **BACKTEST_NAV_CHART_CONFIGS['景气成长'])
