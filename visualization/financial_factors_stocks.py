import pandas as pd
import streamlit as st

from config import financial_factors_config
from data_preparation.data_fetcher import fetch_financial_factors_stocks_from_local
from utils import msg_printer

# format:  str, "plain", "localized", "percent", "dollar", "euro", "yen", "accounting", "compact", "scientific", "engineering", or None
PERCENT_COL_KEYWORDS = ('分位', '同比', '环比', '增速', '比例', '率', '比', 'ROE')
BIG_NUM_COL_KEYWORDS = ('利润', '现金')
PERCENT_DISPLAY_FORMAT = '%.0f%%'


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


def _render_strategy_stock_pool(df: pd.DataFrame, strategy_name: str, trade_dates: list[str] | None = None) -> None:
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

    with tab2:
        _render_strategy_stock_pool(df=df, strategy_name='细分龙头', trade_dates=trade_dates)

    with tab3:
        _render_strategy_stock_pool(df=df, strategy_name='景气成长', trade_dates=trade_dates)
