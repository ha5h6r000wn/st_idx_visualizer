import numpy as np
import pandas as pd

from utils import get_np_quantile_inv_q


def reshape_long_df_into_wide_form(long_df, index_col, name_col, value_col, add_suffix=False):
    wide_df = long_df.pivot(index=index_col, columns=name_col, values=value_col)
    wide_df.columns = wide_df.columns.astype(str)
    if add_suffix:
        # wide_df.columns = [f'{name_col}_{col}' for col in wide_df.columns]
        wide_df = wide_df.add_suffix('_' + value_col)
    return wide_df


def reshape_wide_df_into_long_form(wide_df, index_col, name_col, value_col):
    return wide_df.reset_index().melt(id_vars=index_col, var_name=name_col, value_name=value_col)


def convert_price_ts_into_nav_ts(ts_df):
    first_row = ts_df.iloc[0]
    return ts_df.div(first_row)


def append_ratio_column(
    df,
    numerator_col: str,
    denominator_col: str,
    ratio_col: str = None,
):
    if ratio_col is None:
        ratio_col = f'{numerator_col}/{denominator_col}'
    df[ratio_col] = df[numerator_col] / df[denominator_col]
    return df


def append_difference_column(
    df,
    minuend_col: str,
    subtrahend_col: str,
    difference_col: str = None,
):
    if difference_col is None:
        difference_col = f'{minuend_col}-{subtrahend_col}'
    df[difference_col] = df[minuend_col] - df[subtrahend_col]
    return df


def append_sum_column(
    df,
    sum_1_col: str,
    sum_2_col: str,
    sum_col: str = None,
    multiplier_1: float = 1,
    multiplier_2: float = 1,
    multiplier_sum: float = 1,
):
    if sum_col is None:
        sum_col = f'{sum_1_col}+{sum_2_col}'
    df[sum_col] = (df[sum_1_col] * multiplier_1 + df[sum_2_col] * multiplier_2) * multiplier_sum
    return df


def append_rolling_mean_column(
    df,
    window_name: str,
    window_size: int,
    target_col: str | None = None,
    rolling_mean_col: str = None,
    dropna: bool = True,
):
    if target_col is None:
        target_col = df.columns[-1]
    if rolling_mean_col is None:
        rolling_mean_col = f'近{window_name}均值'
    df[rolling_mean_col] = df[target_col].rolling(window=window_size).mean()
    if dropna:
        return df.dropna(inplace=False)
    else:
        return df


def append_rolling_sum_column(
    df,
    window_size: int,
    window_name: str | None = None,
    target_col: str | None = None,
    rolling_sum_col: str = None,
    dropna: bool = True,
):
    if target_col is None:
        target_col = df.columns[-1]
    if rolling_sum_col is None:
        rolling_sum_col = f'{window_name}之和'
    df[rolling_sum_col] = df[target_col].rolling(window=window_size).sum()
    if dropna:
        return df.dropna(inplace=False)
    else:
        return df


def append_rolling_quantile_column(
    df,
    window_name: str,
    window_size: int,
    target_col: str | None = None,
    rolling_quantile_col: str = None,
    quantile: float = 50,
    method: str = 'median_unbiased',
    dropna: bool = True,
):
    if target_col is None:
        target_col = df.columns[-1]
    if rolling_quantile_col is None:
        rolling_quantile_col = f'{window_name}{quantile}%分位数'

    # df[rolling_quantile_col] = (
    #     df[target_col].rolling(window=window_size).quantile(quantile / 100)
    # )
    df[rolling_quantile_col] = (
        df[target_col].rolling(window=window_size).apply(lambda x: np.quantile(x, quantile / 100, method=method))
    )

    if dropna:
        return df.dropna(inplace=False)
    else:
        return df


def append_rolling_quantile_inv_q_column(
    df,
    window_size: int,
    window_name: str | None = None,
    data_set_col: str | None = None,
    data_idv_col: str | None = None,
    rolling_q_col: str | None = None,
    dropna: bool = True,
):
    if data_set_col is None:
        data_set_col = df.columns[-1]
    if data_idv_col is None:
        data_idv_col = data_set_col
    if rolling_q_col is None:
        rolling_q_col = f'{window_name}%分位'
    df[rolling_q_col] = (
        df[data_set_col]
        .rolling(window=window_size)
        .apply(
            lambda x: get_np_quantile_inv_q(
                quantile=df.loc[x.index[-1], data_idv_col], sequence=x, method='median_unbiased'
            )
        )
    )
    # print(len(df[target_col]))
    # print(window_size)
    # print(window_name)
    # print(df.tail(20))
    if dropna:
        return df.dropna(inplace=False)
    else:
        return df


def append_year_on_year_growth_column(
    indexed_df,
    yoy_col: str,
    target_col: str | None = None,
    dt_format: str = r'%Y%m%d',
    dropna: bool = True,
):
    if target_col is None:
        target_col = indexed_df.columns[-1]

    indexed_df.index = pd.to_datetime(indexed_df.index, format=dt_format)

    indexed_df[yoy_col] = indexed_df.groupby([indexed_df.index.month])[target_col].pct_change(fill_method=None)

    indexed_df.index = indexed_df.index.strftime(dt_format)

    if dropna:
        return indexed_df.dropna(inplace=False)
    else:
        return indexed_df


def assign_signal(
    row,
    target_col,
    upper_bound_col,
    lower_bound_col,
    top_signal,
    bottom_signal,
    middle_signal,
):
    if row[target_col] >= row[upper_bound_col]:
        return top_signal
    elif row[target_col] <= row[lower_bound_col]:
        return bottom_signal
    else:
        return middle_signal


def append_signal_column(
    df,
    signal_col,
    target_col,
    upper_bound_col,
    lower_bound_col,
    top_signal,
    bottom_signal,
    middle_signal,
):
    # print(signal_col)
    df[signal_col] = df.apply(
        assign_signal,
        args=(
            target_col,
            upper_bound_col,
            lower_bound_col,
            top_signal,
            bottom_signal,
            middle_signal,
        ),
        axis=1,
    )

    return df
