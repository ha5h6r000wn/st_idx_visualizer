import os
import time

import pandas as pd

from config import config, param_cls, style_config
from data_preparation.data_access import get_bond_yields, get_economic_data, get_index_prices, get_index_valuations
from data_preparation.db import get_or_create_session


def read_csv_data(table_name: str) -> pd.DataFrame:
    """Read data from CSV file based on table name"""
    csv_path = os.path.join(config.CSV_DATA_DIR, config.CSV_FILE_MAPPING[table_name])
    if not os.path.exists(csv_path):
        print(f'Warning: CSV file not found at {csv_path}')
        return pd.DataFrame()

    try:
        # Read CSV with specified data types
        df = pd.read_csv(csv_path, dtype=config.CSV_DTYPE_MAPPING[table_name])

        # Verify all required columns are present
        missing_cols = set(config.CSV_DTYPE_MAPPING[table_name].keys()) - set(df.columns)
        if missing_cols:
            raise ValueError(f'Missing columns in {table_name} CSV file: {missing_cols}')

        # Verify data types and handle any conversion errors
        for col, dtype in config.CSV_DTYPE_MAPPING[table_name].items():
            try:
                if dtype is float:
                    # Convert to numeric, coerce errors to NaN
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    # Check for NaN values that indicate conversion errors
                    nan_count = df[col].isna().sum()
                    if nan_count > 0:
                        print(f'Warning: {nan_count} rows in column {col} contain invalid numeric values')
                elif dtype is str:
                    # Convert to string, replace NaN with empty string
                    df[col] = df[col].fillna('').astype(str)
            except Exception as e:
                raise ValueError(f'Error converting column {col} to {dtype}: {str(e)}')

        return df
    except Exception as e:
        print(f'Error reading CSV file {csv_path}: {str(e)}')
        return pd.DataFrame()


# Functions to fetch data from local database
# @st.cache_data(ttl=config.ST_CACHE_TTL)
def fetch_index_data_from_local(latest_date: str, _config: param_cls.WindListedSecParam):
    """Fetch index data from local database or CSV file"""
    start_time = time.time()
    print(f' - Fetching data from local {config.CURRENT_DATA_SOURCE}: {param_cls.WindLocal.A_IDX_PRICE.value}')

    if config.CURRENT_DATA_SOURCE == config.DataSource.CSV:
        df = read_csv_data('A_IDX_PRICE')
        if not df.empty:
            # Filter data based on date range and wind codes
            df = df[
                (df['TRADE_DT'] >= _config.start_date)
                & (df['TRADE_DT'] <= latest_date)
                & (df['S_INFO_WINDCODE'].isin(_config.wind_codes))
            ]
    else:
        with get_or_create_session() as session:
            df = get_index_prices(
                session=session,
                start_date=_config.start_date,
                end_date=latest_date,
                wind_codes=_config.wind_codes,
            )

    if df is not None and not df.empty:
        df = df.sort_values(by='TRADE_DT', ascending=False)

    print(f' - [IDX] {time.time() - start_time:.2f}s')
    return df


# @st.cache_data(ttl=config.ST_CACHE_TTL)
def fetch_data_from_local(latest_date: str, table_name: str) -> pd.DataFrame:
    """Fetch data from local database or CSV file"""
    start_time = time.time()
    print(f' - Fetching data from local {config.CURRENT_DATA_SOURCE}: {table_name}')

    if config.CURRENT_DATA_SOURCE == config.DataSource.CSV:
        df = read_csv_data(table_name)
        if not df.empty:
            # Filter data based on date range
            date_col = 'TRADE_DT' if table_name == param_cls.WindLocal.A_IDX_PRICE else '交易日期'
            start_date = style_config.DATA_CONFIG[getattr(param_cls.WindPortal, table_name)]['DATA_START_DT']
            df = df[(df[date_col] >= start_date) & (df[date_col] <= latest_date)]

            # Additional filters based on table type
            if table_name == 'CN_BOND_YIELD':
                df = df[
                    df['曲线名称'].isin(
                        style_config.DATA_CONFIG[param_cls.WindPortal.CN_BOND_YIELD]['YIELD_CURVE_NAMES']
                    )
                    & df['交易期限'].isin(
                        style_config.DATA_CONFIG[param_cls.WindPortal.CN_BOND_YIELD]['YIELD_CURVE_TERMS']
                    )
                ]
            elif table_name == 'A_IDX_VAL':
                df = df[df['证券代码'].isin(style_config.DATA_CONFIG[param_cls.WindPortal.A_IDX_VAL]['WIND_CODE'])]
            elif table_name == 'EDB':
                df = df[df['指标代码'].isin(style_config.DATA_CONFIG[param_cls.WindPortal.EDB]['WIND_CODE'])]
    else:
        with get_or_create_session() as session:
            if table_name == 'CN_BOND_YIELD':
                df = get_bond_yields(
                    session=session,
                    start_date=style_config.DATA_CONFIG[param_cls.WindPortal.CN_BOND_YIELD]['DATA_START_DT'],
                    end_date=latest_date,
                    curve_names=style_config.DATA_CONFIG[param_cls.WindPortal.CN_BOND_YIELD]['YIELD_CURVE_NAMES'],
                    curve_terms=style_config.DATA_CONFIG[param_cls.WindPortal.CN_BOND_YIELD]['YIELD_CURVE_TERMS'],
                )
            elif table_name == 'A_IDX_VAL':
                df = get_index_valuations(
                    session=session,
                    start_date=style_config.DATA_CONFIG[param_cls.WindPortal.A_IDX_VAL]['DATA_START_DT'],
                    end_date=latest_date,
                    wind_codes=style_config.DATA_CONFIG[param_cls.WindPortal.A_IDX_VAL]['WIND_CODE'],
                )
            elif table_name == 'EDB':
                df = get_economic_data(
                    session=session,
                    start_date=style_config.DATA_CONFIG[param_cls.WindPortal.EDB]['DATA_START_DT'],
                    end_date=latest_date,
                    indicator_codes=style_config.DATA_CONFIG[param_cls.WindPortal.EDB]['WIND_CODE'],
                )
            else:
                raise ValueError(f'Unknown table name: {table_name}')

    if df is not None and not df.empty:
        # Sort by trade date in descending order
        date_col = 'TRADE_DT' if table_name == param_cls.WindLocal.A_IDX_PRICE else '交易日期'
        df = df.sort_values(by=date_col, ascending=False)

    print(f' - [GEN] {time.time() - start_time:.2f}s')
    return df
