import inspect
import os
import re
import sys
import time
from datetime import datetime
from enum import Enum
from functools import wraps
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv


class BaseAvgCnDtCount(Enum):
    交易日_一年 = 242 + 1 / 4
    工作日_一年 = 252 + 1 / 4


class AvgCnTradeDtCount(Enum):
    一周 = int(BaseAvgCnDtCount.交易日_一年.value / 48)
    两周 = int(BaseAvgCnDtCount.交易日_一年.value / 24)
    一月 = int(BaseAvgCnDtCount.交易日_一年.value / 12)
    两月 = int(BaseAvgCnDtCount.交易日_一年.value / 6)
    三月 = int(BaseAvgCnDtCount.交易日_一年.value / 4)
    半年 = int(BaseAvgCnDtCount.交易日_一年.value / 2)
    一年 = int(BaseAvgCnDtCount.交易日_一年.value)
    两年 = int(BaseAvgCnDtCount.交易日_一年.value * 2)
    四年 = int(BaseAvgCnDtCount.交易日_一年.value * 4)


class AvgCnWorkDtCount(Enum):
    一周 = int(BaseAvgCnDtCount.工作日_一年.value / 48)
    两周 = int(BaseAvgCnDtCount.工作日_一年.value / 24)
    一月 = int(BaseAvgCnDtCount.工作日_一年.value / 12)
    两月 = int(BaseAvgCnDtCount.工作日_一年.value / 6)
    三月 = int(BaseAvgCnDtCount.工作日_一年.value / 4)
    半年 = int(BaseAvgCnDtCount.工作日_一年.value / 2)
    一年 = int(BaseAvgCnDtCount.工作日_一年.value)
    两年 = int(BaseAvgCnDtCount.工作日_一年.value * 2)
    四年 = int(BaseAvgCnDtCount.工作日_一年.value * 4)


class TradeDtType(Enum):
    STOCK_MKT = '证券交易日'
    FUND_MKT = '资金交易日'


def get_avg_dt_count_via_dt_type(dt_type: str, period: str) -> int:
    if dt_type == TradeDtType.STOCK_MKT:
        return AvgCnTradeDtCount[period].value
    elif dt_type == TradeDtType.FUND_MKT:
        return AvgCnWorkDtCount[period].value
    else:
        raise ValueError(f'不支持的日期类型：{dt_type}')


def get_rolling_window_col(window_name: str, window_type: str, extra_info: str = '') -> str:
    return f'近{window_name}{extra_info}{window_type}'


def load_env():
    load_dotenv()
    # print('Environment variables loaded')

    env_var = os.environ

    return dict(env_var)


def get_script_dir():
    if getattr(sys, 'frozen', False):  # this is a bundle (e.g., PyInstaller)
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    return os.path.dirname(path)


def get_cwd_file_path(dir: str, file: str):
    return Path(get_script_dir()) / dir / file


def msg_printer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f' [INFO] || {datetime.now():%y%b%d %H:%M:%S} || {func.__name__} ||')
        T1 = time.perf_counter()
        res = func(*args, **kwargs)
        T2 = time.perf_counter()
        print(f' - {T2 - T1:.2f}s')
        return res

    return wrapper


def read_sql_from_template(path):
    with open(path, 'r', encoding='utf-8') as file:
        sql = file.read()
    return sql


def get_wind_col_alias_with_sql_parser(path_sql):
    # 读取 SQL 文件
    sql = read_sql_from_template(path_sql)

    # 找到最外层的 SELECT 和 FROM 之间的部分，用(?i)表示忽略大小写
    pattern = re.compile(r'(?i)\bSELECT\b(.*?)\bFROM\b', re.DOTALL)
    matches = pattern.findall(sql)
    if not matches:
        return {}

    # 取最后一个匹配，即最外层的SELECT和FROM之间的部分
    select_part = matches[0]

    # 按逗号分割，得到每一列
    columns = select_part.split(',')

    # 创建一个空字典来存储结果
    column_dict = {}

    # 遍历每一列
    for column in columns:
        # 按 'as' 分割，得到列名和别名, 忽略大小写
        parts = re.split(r'(?i)\bAS\b', column)
        if len(parts) == 2:
            # 去除空格和换行符，然后添加到字典中
            # 如果列名中包含点（即有表别名前缀），则剥离前缀
            column_name = parts[0].strip().split('.')[-1]
            alias = parts[1].strip()
            column_dict[column_name] = alias

    return column_dict


def divide_by_100(x):
    try:
        return x / 100
    except TypeError:
        return x


def get_np_quantile_inv_q(quantile: float, sequence, method: str = 'median_unbiased'):
    if quantile == max(sequence):
        return 1
    elif quantile == min(sequence):
        return 0
    n = len(sequence)
    col_name = 'col'
    df = pd.DataFrame({col_name: sorted(sequence)})
    i = df[df <= quantile][col_name].idxmax()
    x_i = df.loc[i, col_name]
    x_i_next = df.loc[i + 1, col_name]
    if method == 'median_unbiased':
        alpha = 1 / 3
        beta = 1 / 3
    elif method == 'linear':
        alpha = 1
        beta = 1
    else:
        raise ValueError('method must be either "median_unbiased" or "linear"')
    return ((i + 1) + (quantile - x_i) / (x_i_next - x_i) - alpha) / (n - alpha - beta + 1)
