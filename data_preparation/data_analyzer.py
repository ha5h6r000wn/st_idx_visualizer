from datetime import datetime
from enum import Enum
from typing import List, Tuple

import pandas as pd
from pydantic import BaseModel

from config import param_cls
from config.config import PERIOD_HEADERS, WIND_DT_FORMAT


class PeriodName(str, Enum):
    WEEK = 'week'
    MONTH = 'month'
    YEAR = 'year'


class Period(BaseModel):
    period_name: PeriodName


def get_1st_trade_dt_of_period(date: str, trade_dt: List[str], dt_format: str, period: Period):
    period_format = {
        PeriodName.WEEK.value: '%Y%W',
        PeriodName.MONTH.value: '%Y%m',
        PeriodName.YEAR.value: '%Y',
    }

    end_dt = min(trade_dt[-1], date)
    period_number = list(
        map(
            lambda dt: datetime.strptime(dt, dt_format).strftime(period_format[period.period_name.value]),
            trade_dt,
        )
    )
    return trade_dt[period_number.index(period_number[trade_dt.index(end_dt)])]


def calculate_pct_change(df_indexed: pd.DataFrame, start_idx: str, end_idx: str):
    return df_indexed[end_idx] / df_indexed[start_idx] - 1


def calculate_period_return(series, date: str, custom_dt: Tuple[str, str], trade_dt: List[str]):
    end_dt = min(trade_dt[-1], date)
    first_dt_list = list(
        map(
            lambda x: get_1st_trade_dt_of_period(end_dt, trade_dt, WIND_DT_FORMAT, Period(period_name=x)),
            ['week', 'month', 'year'],
        )
    ) + [custom_dt[0]]
    # 注意：计算收益率时，需要取区间起始交易日前一交易日价格来计算
    start_dt_list = [trade_dt[trade_dt.index(x) - 1] for x in first_dt_list]
    end_dt_list = [end_dt] * 3 + [custom_dt[1]]
    index_list = list(
        map(
            (lambda x, y, z: f'{x} [{y[-6:]} - {z[-6:]}]'),
            PERIOD_HEADERS,
            first_dt_list,
            end_dt_list,
        )
    )

    return pd.Series(
        data=list(
            map(
                lambda x, y: calculate_pct_change(series, x, y),
                start_dt_list,
                end_dt_list,
            )
        ),
        index=index_list,
    )


def calculate_grouped_return(
    df: pd.DataFrame,
    date: str,
    custom_dt: Tuple[str, str],
    trade_dt: List[str],
    config: param_cls.BaseDataColParam,
):
    df_indexed = df.set_index(config.dt_col)

    return (
        df_indexed.groupby(config.name_col)[config.price_col]
        .apply(calculate_period_return, date=date, custom_dt=custom_dt, trade_dt=trade_dt)
        .unstack()
    )
