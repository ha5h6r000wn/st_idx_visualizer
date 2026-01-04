import os

# Data directory configuration
DATA_ROOT_DIR = 'data'
CSV_DATA_DIR = os.path.join(DATA_ROOT_DIR, 'csv')

# CSV file configuration
CSV_FILE_MAPPING = {
    'A_IDX_PRICE': 'index_prices.csv',
    'CN_BOND_YIELD': 'bond_yields.csv',
    'A_IDX_VAL': 'index_valuations.csv',
    'EDB': 'economic_data.csv',
    'SHIBOR_PRICES': 'shibor_prices.csv',
    'FINANCIAL_FACTORS_STOCKS': 'financial_factors_stocks.csv',
}


STG_IDX_CODES = (
    'CN2370.CNI',
    '931067.CSI',
    '930939.CSI',
    '931052.CSI',
    '000922.CSI',
)
BENCH_IDX_CODES = ('000906.SH',)

WIND_COLS = {
    'trade_dt': 'TRADE_DT',
    'sec_code': 'S_INFO_WINDCODE',
    'sec_name': 'S_INFO_NAME',
    'close': 'S_DQ_CLOSE',
}
# NOTE:
# `WIND_COLS` exists for legacy index/DB tooling and expresses the raw Wind
# column names used by strategy/style consumers. When `index_prices.csv` uses
# Chinese physical headers, the CSV loader materializes these raw Wind columns
# from the physical columns to keep downstream code stable.
ST_CACHE_TTL = 6 * 60 * 60
START_DT = '20200101'
WIND_DT_FORMAT = r'%Y%m%d'
CUSTOM_PERIOD_SLIDER_NAME = '自选周期'
PERIOD_HEADERS = ['周度', '月度', '年度', '自选']
TRADE_DT_COUNT = {
    '两周': 10,
    '一月': 21,
    '一年': 242,
}
TRADE_DT_COUNT.update(
    {
        '两年': TRADE_DT_COUNT['一年'] * 2,
        '半年': TRADE_DT_COUNT['一年'] // 2,
    }
)
STG_IDX_CORR_TRADE_DT_COUNT = {
    '近一年': TRADE_DT_COUNT['一年'],
    '近半年': TRADE_DT_COUNT['半年'],
    '近一月': TRADE_DT_COUNT['一月'],
}

IDX_PRICE_SQL_NAME = 'query_idx_price.sql'

CHART_HEIGHT = 500
CHART_Y_LIMIT_EXTRA = 0.05
CHART_NUM_FORMAT = {'pct': '.2%', 'float': '.2f'}

STG_IDX_SLIDER_START_DT = {
    'RET_BAR': '20240101',
    'NAV_LINE': START_DT,
}
STG_IDX_CHART_AXIS_NAMES = {
    'RET_BAR': {
        'X': '策略指数',
        'LEGEND': '统计周期',
        'Y': '绝对收益',
    },
    'NAV_LINE': {
        'X': '日期',
        'LEGEND': '指数名称',
        'Y': '净值',
    },
    'CORR_HEATMAP': {
        'X': '策略指数_X',
        'LEGEND': '相关系数',
        'Y': '策略指数_Y',
    },
}
STG_IDX_CHART_AXIS_TYPES = {
    'RET_BAR': {
        'X': 'N',
        'LEGEND': 'N',
        'Y': 'Q',
    },
    'NAV_LINE': {
        'X': 'N',
        'LEGEND': 'N',
        'Y': 'Q',
    },
    'CORR_HEATMAP': {
        'X': 'N',
        'LEGEND': 'Q',
        'Y': 'N',
    },
}
STG_IDX_CHART_TITLES = {
    'RET_BAR': '策略指数与中证800收益对比',
    'NAV_LINE': '策略指数与中证800走势对比',
    'CORR_HEATMAP': '策略指数相对中证800超额收益相关性',
}

# CSV column data types configuration
CSV_DTYPE_MAPPING = {
    'A_IDX_PRICE': {
        '交易日期': str,
        '证券代码': str,
        '证券简称': str,
        '收盘价': float,
    },
    'CN_BOND_YIELD': {
        '交易日期': str,
        '曲线名称': str,
        '交易期限': str,
        '到期收益率': float,
    },
    'A_IDX_VAL': {
        '交易日期': str,
        '证券代码': str,
        '证券简称': str,
        '日换手率': float,
        '市盈率': float,
    },
    'EDB': {
        '交易日期': str,
        '指标代码': str,
        '指标名称': str,
        '指标单位': str,
        '指标频率': str,
        '指标数值': float,
    },
    'SHIBOR_PRICES': {
        '交易日期': str,
        '证券代码': str,
        '利率': float,
        '期限': str,
    },
    'FINANCIAL_FACTORS_STOCKS': {
        '交易日期': str,
        '证券代码': str,
        '证券简称': str,
        '申万一级行业': str,
        '申万二级行业': str,
        '申万三级行业': str,
        '景气成长策略': float,
        '细分龙头策略': float,
        '中性股息策略': float,
    },
}
