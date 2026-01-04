import os
import time

import pandas as pd

from config import config, param_cls, style_config


# Canonical schema definitions (incrementally introduced per dataset)
INDEX_PRICE_SCHEMA = {
    'table_name': 'A_IDX_PRICE',
    'date_col': 'TRADE_DT',
    # Physical CSV headers are Chinese; normalize to legacy/raw Wind columns.
    'physical_to_raw': {
        '交易日期': 'TRADE_DT',
        '证券代码': 'S_INFO_WINDCODE',
        '证券简称': 'S_INFO_NAME',
        '收盘价': 'S_DQ_CLOSE',
    },
    'canonical_cols': {
        'trade_date': 'TRADE_DT',
        'wind_code': 'S_INFO_WINDCODE',
        'wind_name': 'S_INFO_NAME',
        'close': 'S_DQ_CLOSE',
    },
    'dtypes': config.CSV_DTYPE_MAPPING['A_IDX_PRICE'],
}

CN_BOND_YIELD_SCHEMA = {
    'table_name': 'CN_BOND_YIELD',
    'date_col': '交易日期',
    'canonical_cols': {
        'trade_date': '交易日期',
        'curve_name': '曲线名称',
        'curve_term': '交易期限',
        'ytm': '到期收益率',
    },
    'dtypes': config.CSV_DTYPE_MAPPING['CN_BOND_YIELD'],
}

INDEX_VALUATION_SCHEMA = {
    'table_name': 'A_IDX_VAL',
    'date_col': '交易日期',
    'canonical_cols': {
        'trade_date': '交易日期',
        'wind_code': '证券代码',
        'wind_name': '证券简称',
        'turnover': '日换手率',
        'pe_ttm': '市盈率',
    },
    'dtypes': config.CSV_DTYPE_MAPPING['A_IDX_VAL'],
}

ECONOMIC_DATA_SCHEMA = {
    'table_name': 'EDB',
    'date_col': '交易日期',
    'canonical_cols': {
        'trade_date': '交易日期',
        'indicator_code': '指标代码',
        'indicator_name': '指标名称',
        'indicator_unit': '指标单位',
        'indicator_freq': '指标频率',
        'indicator_value': '指标数值',
    },
    'dtypes': config.CSV_DTYPE_MAPPING['EDB'],
}

SHIBOR_PRICES_SCHEMA = {
    'table_name': 'SHIBOR_PRICES',
    'date_col': '交易日期',
    'canonical_cols': {
        'trade_date': '交易日期',
        'wind_code': '证券代码',
        'rate': '利率',
        'term': '期限',
    },
    'dtypes': config.CSV_DTYPE_MAPPING['SHIBOR_PRICES'],
}

FINANCIAL_FACTORS_STOCKS_SCHEMA = {
    'table_name': 'FINANCIAL_FACTORS_STOCKS',
    'date_col': '交易日期',
    'canonical_cols': {
        'trade_date': '交易日期',
        'wind_code': '证券代码',
        'wind_name': '证券简称',
    },
    'dtypes': config.CSV_DTYPE_MAPPING['FINANCIAL_FACTORS_STOCKS'],
}


CANONICAL_COL_MAPPINGS = {
    INDEX_PRICE_SCHEMA['table_name']: INDEX_PRICE_SCHEMA['canonical_cols'],
    CN_BOND_YIELD_SCHEMA['table_name']: CN_BOND_YIELD_SCHEMA['canonical_cols'],
    INDEX_VALUATION_SCHEMA['table_name']: INDEX_VALUATION_SCHEMA['canonical_cols'],
    ECONOMIC_DATA_SCHEMA['table_name']: ECONOMIC_DATA_SCHEMA['canonical_cols'],
    SHIBOR_PRICES_SCHEMA['table_name']: SHIBOR_PRICES_SCHEMA['canonical_cols'],
    FINANCIAL_FACTORS_STOCKS_SCHEMA['table_name']: FINANCIAL_FACTORS_STOCKS_SCHEMA['canonical_cols'],
}


DATASET_SCHEMAS = {
    schema['table_name']: schema
    for schema in (
        INDEX_PRICE_SCHEMA,
        CN_BOND_YIELD_SCHEMA,
        INDEX_VALUATION_SCHEMA,
        ECONOMIC_DATA_SCHEMA,
        SHIBOR_PRICES_SCHEMA,
        FINANCIAL_FACTORS_STOCKS_SCHEMA,
    )
}


def add_canonical_columns(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """Add normalized English column aliases while retaining original columns."""
    mapping = CANONICAL_COL_MAPPINGS.get(table_name, {})
    for canonical, source in mapping.items():
        if source in df.columns:
            df[canonical] = df[source]
    return df


def read_csv_data(table_name: str) -> pd.DataFrame:
    """Read data from CSV file based on table name"""
    csv_path = os.path.join(config.CSV_DATA_DIR, config.CSV_FILE_MAPPING[table_name])
    if not os.path.exists(csv_path):
        print(f'Warning: CSV file not found at {csv_path}')
        return pd.DataFrame()

    try:
        schema = DATASET_SCHEMAS.get(table_name)
        dtypes = schema['dtypes'] if schema and 'dtypes' in schema else config.CSV_DTYPE_MAPPING[table_name]
        # Read CSV as strings first, then coerce to the declared schema below.
        df = pd.read_csv(csv_path, dtype=str)

        # Verify all required columns are present
        missing_cols = set(dtypes.keys()) - set(df.columns)
        if missing_cols:
            raise ValueError(f'Missing columns in {table_name} CSV file: {missing_cols}')

        # Verify data types and handle any conversion errors
        for col, dtype in dtypes.items():
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

        # Materialize legacy/raw Wind columns from Chinese physical headers
        # when the schema declares a mapping.
        physical_to_raw = schema.get('physical_to_raw') if schema else None
        if physical_to_raw:
            for physical_col, raw_col in physical_to_raw.items():
                if physical_col in df.columns and raw_col not in df.columns:
                    df[raw_col] = df[physical_col]

        return df
    except Exception as e:
        print(f'Error reading CSV file {csv_path}: {str(e)}')
        return pd.DataFrame()


class CSVDataSource:
    """CSV-backed data access with normalized schemas."""

    def fetch_index_data(self, latest_date: str, _config: param_cls.WindListedSecParam) -> pd.DataFrame:
        df = read_csv_data('A_IDX_PRICE')
        if not df.empty:
            date_col = INDEX_PRICE_SCHEMA['date_col']
            df = df[
                (df[date_col] >= _config.start_date)
                & (df[date_col] <= latest_date)
                & (df['S_INFO_WINDCODE'].isin(_config.wind_codes))
            ]
            df = add_canonical_columns(df, 'A_IDX_PRICE')
            df = df.sort_values(by=date_col, ascending=False)
        return df

    def fetch_financial_factors_stocks(self, latest_date: str) -> pd.DataFrame:
        df = read_csv_data('FINANCIAL_FACTORS_STOCKS')
        if not df.empty:
            date_col = FINANCIAL_FACTORS_STOCKS_SCHEMA['date_col']
            df = df[df[date_col] <= latest_date]
            df = add_canonical_columns(df, 'FINANCIAL_FACTORS_STOCKS')
            df = df.sort_values(by=date_col, ascending=False)
        return df

    def fetch_table(self, latest_date: str, table_name: str) -> pd.DataFrame:
        df = read_csv_data(table_name)
        if df.empty:
            return df

        schema = DATASET_SCHEMAS.get(table_name)
        if schema is not None:
            date_col = schema['date_col']
        else:
            date_col = '交易日期'
        start_date = None
        try:
            wind_portal = getattr(param_cls.WindPortal, table_name)
        except AttributeError:
            wind_portal = None
        if wind_portal is not None and wind_portal in style_config.DATA_CONFIG:
            start_date = style_config.DATA_CONFIG[wind_portal]['DATA_START_DT']

        if start_date is not None:
            df = df[(df[date_col] >= start_date) & (df[date_col] <= latest_date)]
        else:
            df = df[df[date_col] <= latest_date]

        if table_name == 'CN_BOND_YIELD':
            df = df[
                df['曲线名称'].isin(style_config.DATA_CONFIG[param_cls.WindPortal.CN_BOND_YIELD]['YIELD_CURVE_NAMES'])
                & df['交易期限'].isin(style_config.DATA_CONFIG[param_cls.WindPortal.CN_BOND_YIELD]['YIELD_CURVE_TERMS'])
            ]
        elif table_name == 'A_IDX_VAL':
            df = df[df['证券代码'].isin(style_config.DATA_CONFIG[param_cls.WindPortal.A_IDX_VAL]['WIND_CODE'])]
        elif table_name == 'EDB':
            df = df[df['指标代码'].isin(style_config.DATA_CONFIG[param_cls.WindPortal.EDB]['WIND_CODE'])]
        elif table_name == 'SHIBOR_PRICES':
            df = df[df['期限'].isin(style_config.DATA_CONFIG[param_cls.WindPortal.SHIBOR_PRICES]['B_INFO_TERM'])]

        df = add_canonical_columns(df, table_name)
        df = df.sort_values(by=date_col, ascending=False)
        return df


_CSV_DATASOURCE = CSVDataSource()


def get_data_source() -> CSVDataSource:
    return _CSV_DATASOURCE


# Functions to fetch data from local CSVs (thin wrappers over CSVDataSource)
def fetch_index_data_from_local(latest_date: str, _config: param_cls.WindListedSecParam):
    """Fetch index data from local CSV file"""
    start_time = time.time()
    print(f' - Fetching data from CSV: {param_cls.WindLocal.A_IDX_PRICE.value}')

    df = get_data_source().fetch_index_data(latest_date=latest_date, _config=_config)

    print(f' - [IDX] {time.time() - start_time:.2f}s')
    return df


def fetch_data_from_local(latest_date: str, table_name: str) -> pd.DataFrame:
    """Fetch data from local CSV file"""
    start_time = time.time()
    print(f' - Fetching data from CSV: {table_name}')

    df = get_data_source().fetch_table(latest_date=latest_date, table_name=table_name)

    print(f' - [GEN] {time.time() - start_time:.2f}s')
    return df


def fetch_financial_factors_stocks_from_local(latest_date: str) -> pd.DataFrame:
    start_time = time.time()
    table_name = 'FINANCIAL_FACTORS_STOCKS'
    print(f' - Fetching data from CSV: {table_name}')

    df = get_data_source().fetch_financial_factors_stocks(latest_date=latest_date)

    print(f' - [GEN] {time.time() - start_time:.2f}s')
    return df
