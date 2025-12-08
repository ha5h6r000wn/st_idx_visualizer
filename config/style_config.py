from config import config, param_cls
from utils import (
    TradeDtType,
    get_avg_dt_count_via_dt_type,
    get_cwd_file_path,
    get_rolling_window_col,
    get_wind_col_alias_with_sql_parser,
)

STYLE_IDX_CODES = {
    '价值': '399371.SZ',
    '成长': '399370.SZ',
    '大盘': '000300.SH',
    '小盘': '932000.CSI',
    '小盘(旧)': '000852.SH',
    '万得全A': '881001.WI',
}


START_DT = '20200101'
SQL_DIR = 'sql_template'

DATA_CONFIG = {
    param_cls.WindPortal.CN_BOND_YIELD: {
        'SQL_NAME': 'query_yield_curve.sql',
        'DATA_START_DT': '20150101',
        'YIELD_CURVE_NAMES': ('中债国债收益率曲线',),
        'YIELD_CURVE_TERMS': ('1.0', '10.0'),
    },
    param_cls.WindPortal.A_IDX_VAL: {
        'SQL_NAME': 'query_a_index_valuation.sql',
        'DATA_START_DT': '20150101',
        'WIND_CODE': (
            STYLE_IDX_CODES['万得全A'],
            STYLE_IDX_CODES['大盘'],
            STYLE_IDX_CODES['小盘(旧)'],
        ),
    },
    param_cls.WindPortal.EDB: {
        'SQL_NAME': 'query_edb.sql',
        'DATA_START_DT': '20150101',
        'WIND_CODE': (
            'S0029656',  # 房地产开发投资完成额:累计值
            'M0009970',  # 中国:金融机构:各项贷款余额:人民币:同比
        ),
    },
    param_cls.WindPortal.SHIBOR_PRICES: {
        'SQL_NAME': 'query_shibor_prices.sql',
        'DATA_START_DT': '20200101',
        'B_INFO_TERM': ('3M',),
    },
}
DATA_CONFIG_KEYS = [
    param_cls.WindPortal.CN_BOND_YIELD,
    param_cls.WindPortal.A_IDX_VAL,
    param_cls.WindPortal.EDB,
    param_cls.WindPortal.SHIBOR_PRICES,
]

for key in DATA_CONFIG_KEYS:
    DATA_CONFIG[key].update(
        {
            'WIND_COL_ALIAS': get_wind_col_alias_with_sql_parser(
                path_sql=get_cwd_file_path(
                    dir=SQL_DIR,
                    file=DATA_CONFIG[key]['SQL_NAME'],
                )
            ),
        }
    )

DATA_COL_PARAM = {
    param_cls.WindPortal.EDB: param_cls.WindAIndexValueColParam(
        dt_col=DATA_CONFIG[param_cls.WindPortal.EDB]['WIND_COL_ALIAS']['TDATE'],
        name_col=DATA_CONFIG[param_cls.WindPortal.EDB]['WIND_COL_ALIAS']['F3_4112'],
        value_col=DATA_CONFIG[param_cls.WindPortal.EDB]['WIND_COL_ALIAS']['INDICATOR_NUM'],
    ),
    param_cls.WindPortal.A_IDX_VAL: param_cls.WindAIndexValueColParam(
        dt_col=DATA_CONFIG[param_cls.WindPortal.A_IDX_VAL]['WIND_COL_ALIAS']['TRADE_DT'],
        name_col=DATA_CONFIG[param_cls.WindPortal.A_IDX_VAL]['WIND_COL_ALIAS']['S_INFO_NAME'],
        code_col=DATA_CONFIG[param_cls.WindPortal.A_IDX_VAL]['WIND_COL_ALIAS']['S_INFO_WINDCODE'],
        turnover_col=DATA_CONFIG[param_cls.WindPortal.A_IDX_VAL]['WIND_COL_ALIAS']['TURNOVER'],
        pe_ttm_col=DATA_CONFIG[param_cls.WindPortal.A_IDX_VAL]['WIND_COL_ALIAS']['PE_TTM'],
    ),
}

DATA_QUERY_PARAM = {
    param_cls.WindPortal.CN_BOND_YIELD: param_cls.WindYieldCurveQueryParam(
        start_date=DATA_CONFIG[param_cls.WindPortal.CN_BOND_YIELD]['DATA_START_DT'],
        sql_param=param_cls.SqlParam(
            sql_name=DATA_CONFIG[param_cls.WindPortal.CN_BOND_YIELD]['SQL_NAME'],
        ),
        curve_names=DATA_CONFIG[param_cls.WindPortal.CN_BOND_YIELD]['YIELD_CURVE_NAMES'],
        curve_terms=DATA_CONFIG[param_cls.WindPortal.CN_BOND_YIELD]['YIELD_CURVE_TERMS'],
    ),
    param_cls.WindPortal.A_IDX_VAL: param_cls.WindListedSecParam(
        wind_codes=DATA_CONFIG[param_cls.WindPortal.A_IDX_VAL]['WIND_CODE'],
        start_date=DATA_CONFIG[param_cls.WindPortal.A_IDX_VAL]['DATA_START_DT'],
        sql_param=param_cls.SqlParam(
            sql_name=DATA_CONFIG[param_cls.WindPortal.A_IDX_VAL]['SQL_NAME'],
        ),
    ),
    param_cls.WindPortal.EDB: param_cls.WindListedSecParam(
        wind_codes=DATA_CONFIG[param_cls.WindPortal.EDB]['WIND_CODE'],
        start_date=DATA_CONFIG[param_cls.WindPortal.EDB]['DATA_START_DT'],
        sql_param=param_cls.SqlParam(
            sql_name=DATA_CONFIG[param_cls.WindPortal.EDB]['SQL_NAME'],
        ),
    ),
}
## NOTE 价值成长研判框架
# NOTE 相对动量: 价值 VS 成长
RELATIVE_MOMENTUM_VALUE_GROWTH_CONFIG = {
    'DT_TYPE': TradeDtType.STOCK_MKT,
    'SLIDER_START_DT': '20200601',
    'SLIDER_DEFAULT_OFFSET': '半年',
    'ROLLING_WINDOW': '一月',
    'TARGET_COL': '相对动量',
    'SIGNAL_COL': '交易信号',
    'TRUE_SIGNAL': param_cls.TradeSignal.LONG_GROWTH.value,
    'FALSE_SIGNAL': param_cls.TradeSignal.LONG_VALUE.value,
    'BAR_TITLE': '相对动量: 价值 VS 成长',
}
RELATIVE_MOMENTUM_VALUE_GROWTH_CONFIG.update(
    {
        'SLIDER_DEFAULT_OFFSET_DT_COUNT': get_avg_dt_count_via_dt_type(
            dt_type=RELATIVE_MOMENTUM_VALUE_GROWTH_CONFIG['DT_TYPE'],
            period=RELATIVE_MOMENTUM_VALUE_GROWTH_CONFIG['SLIDER_DEFAULT_OFFSET'],
        ),
    }
)
RELATIVE_MOMENTUM_VALUE_GROWTH_CHART_PARAM = param_cls.BarLineWithSignalParam(
    dt_slider_param=param_cls.DtSliderParam(
        start_dt=RELATIVE_MOMENTUM_VALUE_GROWTH_CONFIG['SLIDER_START_DT'],
        default_start_offset=RELATIVE_MOMENTUM_VALUE_GROWTH_CONFIG['SLIDER_DEFAULT_OFFSET_DT_COUNT'],
        key='RELATIVE_MOMENTUM_VALUE_GROWTH_SLIDER',
    ),
    bar_param=param_cls.SignalBarParam(
        axis_names={
            'X': 'TRADE_DT',
            'Y': RELATIVE_MOMENTUM_VALUE_GROWTH_CONFIG['TARGET_COL'],
            'LEGEND': RELATIVE_MOMENTUM_VALUE_GROWTH_CONFIG['SIGNAL_COL'],
        },
        title=RELATIVE_MOMENTUM_VALUE_GROWTH_CONFIG['BAR_TITLE'],
        y_axis_format=config.CHART_NUM_FORMAT['pct'],
        true_signal=RELATIVE_MOMENTUM_VALUE_GROWTH_CONFIG['TRUE_SIGNAL'],
        false_signal=RELATIVE_MOMENTUM_VALUE_GROWTH_CONFIG['FALSE_SIGNAL'],
        no_signal=param_cls.TradeSignal.NO_SIGNAL.value,
    ),
    isConvertedToPct=False,
    isSignalAssigned=True,
)


# NOTE 期限利差
TERM_SPREAD_CONFIG = {
    'DT_TYPE': TradeDtType.FUND_MKT,
    'SLIDER_START_DT': '20200601',
    'SLIDER_DEFAULT_OFFSET': '半年',
    'SQL_NAME': 'query_yield_curve.sql',
    'YIELD_CURVE_NAMES': ('中债国债收益率曲线',),
    'YIELD_CURVE_TERMS': ('1.0', '10.0'),
    # 需求：基准线从近一年均值改为近一月均值
    'ROLLING_WINDOW': '一月',
    'TERM_SPREAD_COL': '期限利差',
    'SIGNAL_COL': '交易信号',
    'BASELINE_COL': '比较基准',
    'TRUE_SIGNAL': param_cls.TradeSignal.LONG_GROWTH.value,
    'FALSE_SIGNAL': param_cls.TradeSignal.LONG_VALUE.value,
    'BAR_TITLE': '期限利差 —— 10年期、1年期国债到期收益率之差',
    'LINE_STROKE_DASH': (5, 3),
}
TERM_SPREAD_CONFIG.update(
    {
        'SLIDER_DEFAULT_OFFSET_DT_COUNT': get_avg_dt_count_via_dt_type(
            dt_type=TERM_SPREAD_CONFIG['DT_TYPE'],
            period=TERM_SPREAD_CONFIG['SLIDER_DEFAULT_OFFSET'],
        ),
        'WIND_COL_ALIAS': get_wind_col_alias_with_sql_parser(
            get_cwd_file_path(SQL_DIR, TERM_SPREAD_CONFIG['SQL_NAME'])
        ),
        'ROLLING_WINDOW_SIZE': get_avg_dt_count_via_dt_type(
            dt_type=TERM_SPREAD_CONFIG['DT_TYPE'],
            period=TERM_SPREAD_CONFIG['ROLLING_WINDOW'],
        ),
        'MEAN_COL': get_rolling_window_col(
            window_name=TERM_SPREAD_CONFIG['ROLLING_WINDOW'],
            window_type='均值',
        ),
    }
)

YIELD_CURVE_COL_PARAM = param_cls.WindYieldCurveColParam(
    dt_col=TERM_SPREAD_CONFIG['WIND_COL_ALIAS']['TRADE_DT'],
    name_col=TERM_SPREAD_CONFIG['WIND_COL_ALIAS']['B_ANAL_CURVENAME'],
    term_col=TERM_SPREAD_CONFIG['WIND_COL_ALIAS']['B_ANAL_CURVETERM'],
    ytm_col=TERM_SPREAD_CONFIG['WIND_COL_ALIAS']['B_ANAL_YIELD'],
)

TERM_SPREAD_CHART_PARAM = param_cls.BarLineWithSignalParam(
    dt_slider_param=param_cls.DtSliderParam(
        start_dt=TERM_SPREAD_CONFIG['SLIDER_START_DT'],
        default_start_offset=TERM_SPREAD_CONFIG['SLIDER_DEFAULT_OFFSET_DT_COUNT'],
        key='TERM_SPREAD_SLIDER',
    ),
    bar_param=param_cls.SignalBarParam(
        axis_names={
            'X': YIELD_CURVE_COL_PARAM.dt_col,
            'Y': TERM_SPREAD_CONFIG['TERM_SPREAD_COL'],
            'LEGEND': TERM_SPREAD_CONFIG['SIGNAL_COL'],
        },
        title=TERM_SPREAD_CONFIG['BAR_TITLE'],
        true_signal=TERM_SPREAD_CONFIG['TRUE_SIGNAL'],
        false_signal=TERM_SPREAD_CONFIG['FALSE_SIGNAL'],
    ),
    line_param=param_cls.LineParam(
        axis_names={
            'X': YIELD_CURVE_COL_PARAM.dt_col,
            'Y': TERM_SPREAD_CONFIG['MEAN_COL'],
            'LEGEND': TERM_SPREAD_CONFIG['BASELINE_COL'],
        },
        stroke_dash=TERM_SPREAD_CONFIG['LINE_STROKE_DASH'],
        color='red',
    ),
    isConvertedToPct=True,
)

# NOTE 换手率
INDEX_TURNOVER_CONFIG = {
    'WIND_TABLE': param_cls.WindPortal.A_IDX_VAL,
    'DT_TYPE': TradeDtType.STOCK_MKT,
    'SLIDER_START_DT': '20200601',
    'SLIDER_DEFAULT_OFFSET': '半年',
    'DATA_START_DT': '20181101',
    'WIND_CODE': ('881001.WI',),
    'MEAN_ROLLING_WINDOW': '一月',
    'MEDIAN_ROLLING_WINDOW': '两年',
    'QUANTILE_MEDIAN': 50,
    'SIGNAL_COL': '交易信号',
    'BASELINE_COL': '比较基准',
    'TRUE_SIGNAL': param_cls.TradeSignal.LONG_GROWTH.value,
    'FALSE_SIGNAL': param_cls.TradeSignal.LONG_VALUE.value,
    'BAR_TITLE': '市场情绪 —— 万得全A指数近一月换手率水平',
    'LINE_STROKE_DASH': (5, 3),
}
INDEX_TURNOVER_CONFIG.update(
    {
        'SLIDER_DEFAULT_OFFSET_DT_COUNT': get_avg_dt_count_via_dt_type(
            dt_type=INDEX_TURNOVER_CONFIG['DT_TYPE'],
            period=INDEX_TURNOVER_CONFIG['SLIDER_DEFAULT_OFFSET'],
        ),
        'MEAN_ROLLING_WINDOW_SIZE': get_avg_dt_count_via_dt_type(
            dt_type=INDEX_TURNOVER_CONFIG['DT_TYPE'],
            period=INDEX_TURNOVER_CONFIG['MEAN_ROLLING_WINDOW'],
        ),
        'MEAN_COL': '近一月换手率水平',
        # 'MEAN_COL': get_rolling_window_col(
        #     window_name=INDEX_TURNOVER_CONFIG['MEAN_ROLLING_WINDOW'],
        #     window_type='均值',
        # ),
        # 'MEDIAN_ROLLING_WINDOW_SIZE': get_avg_dt_count_via_dt_type(
        #     dt_type=INDEX_TURNOVER_CONFIG['DT_TYPE'],
        #     period=INDEX_TURNOVER_CONFIG['MEDIAN_ROLLING_WINDOW'],
        # ),
        # 'MEDIAN_COL': get_rolling_window_col(
        #     window_name=INDEX_TURNOVER_CONFIG['MEDIAN_ROLLING_WINDOW'],
        #     window_type='中位数',
        # ),
        'MEAN_1M_ROLLING_WINDOW': '一月',
        'MEAN_1M_ROLLING_WINDOW_SIZE': get_avg_dt_count_via_dt_type(
            dt_type=INDEX_TURNOVER_CONFIG['DT_TYPE'],
            period='一月',
        ),
        'MEAN_1M_COL': '近一月均值',
        'MEAN_2Y_ROLLING_WINDOW': '两年',
        'MEAN_2Y_ROLLING_WINDOW_SIZE': get_avg_dt_count_via_dt_type(
            dt_type=INDEX_TURNOVER_CONFIG['DT_TYPE'],
            period='两年',
        ),
        'MEAN_2Y_COL': '近两年均值',
    }
)
INDEX_TURNOVER_COL_PARAM = param_cls.WindAIndexValueColParam(
    dt_col=DATA_CONFIG[INDEX_TURNOVER_CONFIG['WIND_TABLE']]['WIND_COL_ALIAS']['TRADE_DT'],
    name_col=DATA_CONFIG[INDEX_TURNOVER_CONFIG['WIND_TABLE']]['WIND_COL_ALIAS']['S_INFO_NAME'],
    code_col=DATA_CONFIG[INDEX_TURNOVER_CONFIG['WIND_TABLE']]['WIND_COL_ALIAS']['S_INFO_WINDCODE'],
    turnover_col=DATA_CONFIG[INDEX_TURNOVER_CONFIG['WIND_TABLE']]['WIND_COL_ALIAS']['TURNOVER'],
)
INDEX_TURNOVER_CHART_PARAM = param_cls.BarLineWithSignalParam(
    dt_slider_param=param_cls.DtSliderParam(
        start_dt=INDEX_TURNOVER_CONFIG['SLIDER_START_DT'],
        default_start_offset=INDEX_TURNOVER_CONFIG['SLIDER_DEFAULT_OFFSET_DT_COUNT'],
        key='INDEX_TURNOVER_SLIDER',
    ),
    bar_param=param_cls.SignalBarParam(
        axis_names={
            'X': INDEX_TURNOVER_COL_PARAM.dt_col,
            'Y': INDEX_TURNOVER_CONFIG['MEAN_COL'],
            'LEGEND': INDEX_TURNOVER_CONFIG['SIGNAL_COL'],
        },
        title=INDEX_TURNOVER_CONFIG['BAR_TITLE'],
        true_signal=INDEX_TURNOVER_CONFIG['TRUE_SIGNAL'],
        false_signal=INDEX_TURNOVER_CONFIG['FALSE_SIGNAL'],
    ),
    line_param=param_cls.LineParam(
        axis_names={
            'X': INDEX_TURNOVER_COL_PARAM.dt_col,
            'Y': '均线',
            'LEGEND': INDEX_TURNOVER_CONFIG['BASELINE_COL'],
        },
        stroke_dash=INDEX_TURNOVER_CONFIG['LINE_STROKE_DASH'],
        color='red',
        compared_cols=[
            INDEX_TURNOVER_CONFIG['MEAN_1M_COL'],
            INDEX_TURNOVER_CONFIG['MEAN_2Y_COL'],
        ],
    ),
    isConvertedToPct=True,
    isSignalAssigned=True,
)

# NOTE ERP股债性价比
INDEX_ERP_CONFIG = {
    'WIND_TABLE': param_cls.WindPortal.A_IDX_VAL,
    'DT_TYPE': TradeDtType.STOCK_MKT,  # 采用并集
    'SLIDER_START_DT': '20200601',
    'SLIDER_DEFAULT_OFFSET': '半年',
    'QUANTILE_ROLLING_WINDOW': '四年',
    'QUANTILE_CEILING': 90,
    'QUANTILE_FLOOR': 10,
    'ERP_COL': '股债性价比',
    'SIGNAL_COL': '交易信号',
    'BASELINE_COL': '比较基准',
    'TRUE_SIGNAL': param_cls.TradeSignal.LONG_GROWTH.value,
    'FALSE_SIGNAL': param_cls.TradeSignal.LONG_VALUE.value,
    'NO_SIGNAL': param_cls.TradeSignal.NO_SIGNAL.value,
    'BAR_TITLE': 'ERP股债性价比',
    # 'BAR_TITLE': 'ERP股债性价比 —— 万得全A指数市盈率倒数 - 10年期国债到期收益率',
    'LINE_STROKE_DASH': (5, 3),
}
INDEX_ERP_CONFIG.update(
    {
        'SLIDER_DEFAULT_OFFSET_DT_COUNT': get_avg_dt_count_via_dt_type(
            dt_type=INDEX_ERP_CONFIG['DT_TYPE'],
            period=INDEX_ERP_CONFIG['SLIDER_DEFAULT_OFFSET'],
        ),
        'QUANTILE_ROLLING_WINDOW_SIZE': get_avg_dt_count_via_dt_type(
            dt_type=INDEX_ERP_CONFIG['DT_TYPE'],
            period=INDEX_ERP_CONFIG['QUANTILE_ROLLING_WINDOW'],
        ),
        'QUANTILE_CEILING_COL': get_rolling_window_col(
            window_name=INDEX_ERP_CONFIG['QUANTILE_ROLLING_WINDOW'],
            window_type='%分位数',
            extra_info=INDEX_ERP_CONFIG['QUANTILE_CEILING'],
        ),
        'QUANTILE_FLOOR_COL': get_rolling_window_col(
            window_name=INDEX_ERP_CONFIG['QUANTILE_ROLLING_WINDOW'],
            window_type='%分位数',
            extra_info=INDEX_ERP_CONFIG['QUANTILE_FLOOR'],
        ),
    }
)
INDEX_ERP_COL_PARAM = param_cls.WindAIndexValueColParam(
    dt_col=DATA_CONFIG[INDEX_ERP_CONFIG['WIND_TABLE']]['WIND_COL_ALIAS']['TRADE_DT'],
    code_col=DATA_CONFIG[INDEX_ERP_CONFIG['WIND_TABLE']]['WIND_COL_ALIAS']['S_INFO_WINDCODE'],
    pe_ttm_col=DATA_CONFIG[INDEX_ERP_CONFIG['WIND_TABLE']]['WIND_COL_ALIAS']['PE_TTM'],
)
INDEX_ERP_CHART_PARAM = param_cls.BarLineWithSignalParam(
    dt_slider_param=param_cls.DtSliderParam(
        start_dt=INDEX_ERP_CONFIG['SLIDER_START_DT'],
        default_start_offset=INDEX_ERP_CONFIG['SLIDER_DEFAULT_OFFSET_DT_COUNT'],
        key='INDEX_ERP_SLIDER',
    ),
    bar_param=param_cls.SignalBarParam(
        axis_names={
            'X': INDEX_ERP_COL_PARAM.dt_col,
            'Y': INDEX_ERP_CONFIG['ERP_COL'],
            'LEGEND': INDEX_ERP_CONFIG['SIGNAL_COL'],
        },
        title=INDEX_ERP_CONFIG['BAR_TITLE'],
        true_signal=INDEX_ERP_CONFIG['TRUE_SIGNAL'],
        false_signal=INDEX_ERP_CONFIG['FALSE_SIGNAL'],
        no_signal=INDEX_ERP_CONFIG['NO_SIGNAL'],
    ),
    line_param=param_cls.LineParam(
        axis_names={
            'X': INDEX_ERP_COL_PARAM.dt_col,
            'Y': '分位数',
            'LEGEND': INDEX_ERP_CONFIG['BASELINE_COL'],
        },
        stroke_dash=INDEX_ERP_CONFIG['LINE_STROKE_DASH'],
        # color='red',
        compared_cols=[
            '近一月均值',
            INDEX_ERP_CONFIG['QUANTILE_CEILING_COL'],
            INDEX_ERP_CONFIG['QUANTILE_FLOOR_COL'],
        ],
    ),
    isSignalAssigned=True,
)

INDEX_ERP_STYLE_CHART_CONFIG = param_cls.StyleBarLineChartConfig(
    bar_axis_names=INDEX_ERP_CHART_PARAM.bar_param.axis_names,
    bar_axis_types=INDEX_ERP_CHART_PARAM.bar_param.axis_types,
    line_axis_names=INDEX_ERP_CHART_PARAM.line_param.axis_names,
    line_axis_types=INDEX_ERP_CHART_PARAM.line_param.axis_types,
    title=INDEX_ERP_CHART_PARAM.bar_param.title,
    bar_y_axis_format=INDEX_ERP_CHART_PARAM.bar_param.y_axis_format,
    line_y_axis_format=INDEX_ERP_CHART_PARAM.line_param.y_axis_format,
    bar_color=None,
    line_color=INDEX_ERP_CHART_PARAM.line_param.color,
    line_stroke_dash=INDEX_ERP_CHART_PARAM.line_param.stroke_dash,
)


# NOTE 信用扩张
CREDIT_EXPANSION_CONFIG = {
    'WIND_TABLE': param_cls.WindPortal.EDB,
    'SLIDER_START_DT': '20180101',
    # 'SLIDER_DEFAULT_OFFSET_DT_COUNT': 40,
    'CREDIT_EXPANSION_COL': '中国:金融机构:各项贷款余额:人民币:同比',
    'YOY_COL': '信用扩张',
    'SIGNAL_COL': '交易信号',
    'BASELINE_COL': '比较基准',
    'TRUE_SIGNAL': param_cls.TradeSignal.LONG_GROWTH.value,
    'FALSE_SIGNAL': param_cls.TradeSignal.LONG_VALUE.value,
    # 'BAR_TITLE': '信用扩张 —— 中长期贷款余额（中国:金融机构:各项贷款余额:人民币:同比）',
    'BAR_TITLE': '信用扩张',
    'LINE_STROKE_DASH': (5, 3),
    'ROLLING_WINDOW': '三月',
    'ROLLING_WINDOW_SIZE': 3,
}
CREDIT_EXPANSION_CONFIG.update(
    {
        'MEAN_COL': get_rolling_window_col(
            window_name=CREDIT_EXPANSION_CONFIG['ROLLING_WINDOW'],
            window_type='均值',
        ),
    }
)
CREDIT_EXPANSION_CHART_PARAM = param_cls.BarLineWithSignalParam(
    dt_slider_param=param_cls.DtSliderParam(
        start_dt=CREDIT_EXPANSION_CONFIG['SLIDER_START_DT'],
        # default_start_offset=CREDIT_EXPANSION_CONFIG['SLIDER_DEFAULT_OFFSET_DT_COUNT'],
        key='CREDIT_EXPANSION_SLIDER',
    ),
    bar_param=param_cls.SignalBarParam(
        axis_names={
            'X': DATA_COL_PARAM[CREDIT_EXPANSION_CONFIG['WIND_TABLE']].dt_col,
            'Y': CREDIT_EXPANSION_CONFIG['YOY_COL'],
            'LEGEND': CREDIT_EXPANSION_CONFIG['SIGNAL_COL'],
        },
        title=CREDIT_EXPANSION_CONFIG['BAR_TITLE'],
        true_signal=CREDIT_EXPANSION_CONFIG['TRUE_SIGNAL'],
        false_signal=CREDIT_EXPANSION_CONFIG['FALSE_SIGNAL'],
        # y_axis_format=config.CHART_NUM_FORMAT['pct'],
        signal_order=[
            CREDIT_EXPANSION_CONFIG['FALSE_SIGNAL'],
            CREDIT_EXPANSION_CONFIG['TRUE_SIGNAL'],
        ],
    ),
    line_param=param_cls.LineParam(
        axis_names={
            'X': DATA_COL_PARAM[CREDIT_EXPANSION_CONFIG['WIND_TABLE']].dt_col,
            'Y': CREDIT_EXPANSION_CONFIG['MEAN_COL'],
            'LEGEND': CREDIT_EXPANSION_CONFIG['BASELINE_COL'],
        },
        stroke_dash=CREDIT_EXPANSION_CONFIG['LINE_STROKE_DASH'],
        color='red',
    ),
    isConvertedToPct=True,
    isSignalAssigned=True,
)

CREDIT_EXPANSION_STYLE_CHART_CONFIG = param_cls.StyleBarLineChartConfig(
    bar_axis_names=CREDIT_EXPANSION_CHART_PARAM.bar_param.axis_names,
    bar_axis_types=CREDIT_EXPANSION_CHART_PARAM.bar_param.axis_types,
    line_axis_names=CREDIT_EXPANSION_CHART_PARAM.line_param.axis_names,
    line_axis_types=CREDIT_EXPANSION_CHART_PARAM.line_param.axis_types,
    title=CREDIT_EXPANSION_CHART_PARAM.bar_param.title,
    bar_y_axis_format=CREDIT_EXPANSION_CHART_PARAM.bar_param.y_axis_format,
    line_y_axis_format=CREDIT_EXPANSION_CHART_PARAM.line_param.y_axis_format,
    bar_color=None,
    line_color=CREDIT_EXPANSION_CHART_PARAM.line_param.color,
    line_stroke_dash=CREDIT_EXPANSION_CHART_PARAM.line_param.stroke_dash,
)


## NOTE 大小盘研判框架

# NOTE 相对动量: 大盘 VS 小盘
RELATIVE_MOMENTUM_BIG_SMALL_CONFIG = {
    'DT_TYPE': TradeDtType.STOCK_MKT,
    'SLIDER_START_DT': '20200601',
    'SLIDER_DEFAULT_OFFSET': '半年',
    'ROLLING_WINDOW': '一月',
    'TARGET_COL': '相对动量',
    'SIGNAL_COL': '交易信号',
    'TRUE_SIGNAL': param_cls.TradeSignal.LONG_BIG.value,
    'FALSE_SIGNAL': param_cls.TradeSignal.LONG_SMALL.value,
    'BAR_TITLE': '相对动量: 大盘 VS 小盘',
}
RELATIVE_MOMENTUM_BIG_SMALL_CONFIG.update(
    {
        'SLIDER_DEFAULT_OFFSET_DT_COUNT': get_avg_dt_count_via_dt_type(
            dt_type=RELATIVE_MOMENTUM_BIG_SMALL_CONFIG['DT_TYPE'],
            period=RELATIVE_MOMENTUM_BIG_SMALL_CONFIG['SLIDER_DEFAULT_OFFSET'],
        ),
    }
)
RELATIVE_MOMENTUM_BIG_SMALL_CHART_PARAM = param_cls.BarLineWithSignalParam(
    dt_slider_param=param_cls.DtSliderParam(
        start_dt=RELATIVE_MOMENTUM_BIG_SMALL_CONFIG['SLIDER_START_DT'],
        default_start_offset=RELATIVE_MOMENTUM_BIG_SMALL_CONFIG['SLIDER_DEFAULT_OFFSET_DT_COUNT'],
        key='RELATIVE_MOMENTUM_BIG_SMALL_SLIDER',
    ),
    bar_param=param_cls.SignalBarParam(
        axis_names={
            'X': 'TRADE_DT',
            'Y': RELATIVE_MOMENTUM_BIG_SMALL_CONFIG['TARGET_COL'],
            'LEGEND': RELATIVE_MOMENTUM_BIG_SMALL_CONFIG['SIGNAL_COL'],
        },
        title=RELATIVE_MOMENTUM_BIG_SMALL_CONFIG['BAR_TITLE'],
        y_axis_format=config.CHART_NUM_FORMAT['pct'],
        true_signal=RELATIVE_MOMENTUM_BIG_SMALL_CONFIG['TRUE_SIGNAL'],
        false_signal=RELATIVE_MOMENTUM_BIG_SMALL_CONFIG['FALSE_SIGNAL'],
        no_signal=param_cls.TradeSignal.NO_SIGNAL.value,
        signal_order=[
            RELATIVE_MOMENTUM_BIG_SMALL_CONFIG['TRUE_SIGNAL'],
            RELATIVE_MOMENTUM_BIG_SMALL_CONFIG['FALSE_SIGNAL'],
            param_cls.TradeSignal.NO_SIGNAL.value,
        ],
    ),
    isConvertedToPct=False,
    isSignalAssigned=True,
)

# NOTE 货币周期：Shibor3M
SHIBOR_PRICES_CONFIG = {
    'DT_TYPE': TradeDtType.FUND_MKT,
    'SLIDER_START_DT': '20200101',
    'SLIDER_DEFAULT_OFFSET': '半年',
    'SQL_NAME': 'query_shibor_prices.sql',
    'B_INFO_TERM': ('3M',),
    'ROLLING_WINDOW': '三月',
    'SHIBOR_PRICE_COL': '3M',
    'SIGNAL_COL': '交易信号',
    'BASELINE_COL': '比较基准',
    'TRUE_SIGNAL': param_cls.TradeSignal.LONG_BIG.value,
    'FALSE_SIGNAL': param_cls.TradeSignal.LONG_SMALL.value,
    'BAR_TITLE': '货币周期 —— Shibor3M',
    'LINE_STROKE_DASH': (5, 3),
}
SHIBOR_PRICES_CONFIG.update(
    {
        'SLIDER_DEFAULT_OFFSET_DT_COUNT': get_avg_dt_count_via_dt_type(
            dt_type=SHIBOR_PRICES_CONFIG['DT_TYPE'],
            period=SHIBOR_PRICES_CONFIG['SLIDER_DEFAULT_OFFSET'],
        ),
        'ROLLING_WINDOW_SIZE': get_avg_dt_count_via_dt_type(
            dt_type=SHIBOR_PRICES_CONFIG['DT_TYPE'],
            period=SHIBOR_PRICES_CONFIG['ROLLING_WINDOW'],
        ),
        'MEAN_COL': get_rolling_window_col(
            window_name=SHIBOR_PRICES_CONFIG['ROLLING_WINDOW'],
            window_type='均值',
        ),
    }
)

SHIBOR_PRICES_COL_PARAM = param_cls.WindYieldCurveColParam(
    dt_col='交易日期',
    name_col='证券代码',
    term_col='期限',
    ytm_col='利率',
)

SHIBOR_PRICES_CHART_PARAM = param_cls.BarLineWithSignalParam(
    dt_slider_param=param_cls.DtSliderParam(
        start_dt=SHIBOR_PRICES_CONFIG['SLIDER_START_DT'],
        default_start_offset=SHIBOR_PRICES_CONFIG['SLIDER_DEFAULT_OFFSET_DT_COUNT'],
        key='SHIBOR_PRICES_SLIDER',
    ),
    bar_param=param_cls.SignalBarParam(
        axis_names={
            'X': SHIBOR_PRICES_COL_PARAM.dt_col,
            'Y': SHIBOR_PRICES_CONFIG['SHIBOR_PRICE_COL'],
            'LEGEND': SHIBOR_PRICES_CONFIG['SIGNAL_COL'],
        },
        title=SHIBOR_PRICES_CONFIG['BAR_TITLE'],
        true_signal=SHIBOR_PRICES_CONFIG['TRUE_SIGNAL'],
        false_signal=SHIBOR_PRICES_CONFIG['FALSE_SIGNAL'],
        signal_order=[
            SHIBOR_PRICES_CONFIG['TRUE_SIGNAL'],
            SHIBOR_PRICES_CONFIG['FALSE_SIGNAL'],
        ],
    ),
    line_param=param_cls.LineParam(
        axis_names={
            'X': SHIBOR_PRICES_COL_PARAM.dt_col,
            'Y': SHIBOR_PRICES_CONFIG['MEAN_COL'],
            'LEGEND': SHIBOR_PRICES_CONFIG['BASELINE_COL'],
        },
        stroke_dash=SHIBOR_PRICES_CONFIG['LINE_STROKE_DASH'],
        color='red',
    ),
    isConvertedToPct=True,
    isSignalAssigned=True,
)

SHIBOR_PRICES_STYLE_CHART_CONFIG = param_cls.StyleBarLineChartConfig(
    bar_axis_names=SHIBOR_PRICES_CHART_PARAM.bar_param.axis_names,
    bar_axis_types=SHIBOR_PRICES_CHART_PARAM.bar_param.axis_types,
    line_axis_names=SHIBOR_PRICES_CHART_PARAM.line_param.axis_names,
    line_axis_types=SHIBOR_PRICES_CHART_PARAM.line_param.axis_types,
    title=SHIBOR_PRICES_CHART_PARAM.bar_param.title,
    bar_y_axis_format=SHIBOR_PRICES_CHART_PARAM.bar_param.y_axis_format,
    line_y_axis_format=SHIBOR_PRICES_CHART_PARAM.line_param.y_axis_format,
    bar_color=None,
    line_color=SHIBOR_PRICES_CHART_PARAM.line_param.color,
    line_stroke_dash=SHIBOR_PRICES_CHART_PARAM.line_param.stroke_dash,
)


# NOTE 经济增长: 房地产完成额累计同比
HOUSING_INVEST_CONFIG = {
    'WIND_TABLE': param_cls.WindPortal.EDB,
    'SLIDER_START_DT': '20180101',
    'HOUSING_INVEST_COL': '中国:房地产开发投资完成额:累计值',
    'YOY_COL': '经济增长',
    'PRE_YOY_COL': '上一期数值',
    'SIGNAL_COL': '交易信号',
    'BASELINE_COL': '比较基准',
    'TRUE_SIGNAL': param_cls.TradeSignal.LONG_BIG.value,
    'FALSE_SIGNAL': param_cls.TradeSignal.LONG_SMALL.value,
    'BAR_TITLE': '经济增长 —— 中国:房地产开发投资完成额:累计值:同比',
    'LINE_STROKE_DASH': (5, 3),
}
HOUSING_INVEST_CHART_PARAM = param_cls.BarLineWithSignalParam(
    dt_slider_param=param_cls.DtSliderParam(
        start_dt=HOUSING_INVEST_CONFIG['SLIDER_START_DT'],
        key='HOUSING_INVEST_SLIDER',
    ),
    bar_param=param_cls.SignalBarParam(
        axis_names={
            'X': DATA_COL_PARAM[HOUSING_INVEST_CONFIG['WIND_TABLE']].dt_col,
            'Y': HOUSING_INVEST_CONFIG['YOY_COL'],
            'LEGEND': HOUSING_INVEST_CONFIG['SIGNAL_COL'],
        },
        title=HOUSING_INVEST_CONFIG['BAR_TITLE'],
        true_signal=HOUSING_INVEST_CONFIG['TRUE_SIGNAL'],
        false_signal=HOUSING_INVEST_CONFIG['FALSE_SIGNAL'],
        y_axis_format=config.CHART_NUM_FORMAT['pct'],
        signal_order=[
            HOUSING_INVEST_CONFIG['TRUE_SIGNAL'],
            HOUSING_INVEST_CONFIG['FALSE_SIGNAL'],
        ],
    ),
    line_param=param_cls.LineParam(
        axis_names={
            'X': DATA_COL_PARAM[HOUSING_INVEST_CONFIG['WIND_TABLE']].dt_col,
            'Y': HOUSING_INVEST_CONFIG['PRE_YOY_COL'],
            'LEGEND': HOUSING_INVEST_CONFIG['BASELINE_COL'],
        },
        stroke_dash=HOUSING_INVEST_CONFIG['LINE_STROKE_DASH'],
        color='red',
        y_axis_format=config.CHART_NUM_FORMAT['pct'],
    ),
    isSignalAssigned=True,
)

# NOTE 期现利差（大小盘）
TERM_SPREAD_2_CHART_PARAM = param_cls.BarLineWithSignalParam(
    dt_slider_param=param_cls.DtSliderParam(
        start_dt=TERM_SPREAD_CONFIG['SLIDER_START_DT'],
        default_start_offset=TERM_SPREAD_CONFIG['SLIDER_DEFAULT_OFFSET_DT_COUNT'],
        key='TERM_SPREAD_2_SLIDER',
    ),
    bar_param=param_cls.SignalBarParam(
        axis_names={
            'X': YIELD_CURVE_COL_PARAM.dt_col,
            'Y': TERM_SPREAD_CONFIG['TERM_SPREAD_COL'],
            'LEGEND': TERM_SPREAD_CONFIG['SIGNAL_COL'],
        },
        title=TERM_SPREAD_CONFIG['BAR_TITLE'],
        true_signal=param_cls.TradeSignal.LONG_SMALL.value,
        false_signal=param_cls.TradeSignal.LONG_BIG.value,
    ),
    line_param=param_cls.LineParam(
        axis_names={
            'X': YIELD_CURVE_COL_PARAM.dt_col,
            'Y': TERM_SPREAD_CONFIG['MEAN_COL'],
            'LEGEND': TERM_SPREAD_CONFIG['BASELINE_COL'],
        },
        stroke_dash=TERM_SPREAD_CONFIG['LINE_STROKE_DASH'],
        color='red',
    ),
    isConvertedToPct=True,
)


# NOTE ERP股债性价比（大小盘）
INDEX_ERP_2_CHART_PARAM = param_cls.BarLineWithSignalParam(
    dt_slider_param=param_cls.DtSliderParam(
        start_dt=INDEX_ERP_CONFIG['SLIDER_START_DT'],
        default_start_offset=INDEX_ERP_CONFIG['SLIDER_DEFAULT_OFFSET_DT_COUNT'],
        key='INDEX_ERP_2_SLIDER',
    ),
    bar_param=param_cls.SignalBarParam(
        axis_names={
            'X': INDEX_ERP_COL_PARAM.dt_col,
            'Y': INDEX_ERP_CONFIG['ERP_COL'],
            'LEGEND': INDEX_ERP_CONFIG['SIGNAL_COL'],
        },
        title=INDEX_ERP_CONFIG['BAR_TITLE'],
        true_signal=param_cls.TradeSignal.LONG_SMALL.value,
        false_signal=param_cls.TradeSignal.LONG_BIG.value,
        no_signal=INDEX_ERP_CONFIG['NO_SIGNAL'],
    ),
    line_param=param_cls.LineParam(
        axis_names={
            'X': INDEX_ERP_COL_PARAM.dt_col,
            'Y': '分位数',
            'LEGEND': INDEX_ERP_CONFIG['BASELINE_COL'],
        },
        stroke_dash=INDEX_ERP_CONFIG['LINE_STROKE_DASH'],
        color='red',
        compared_cols=[
            '近一月均值',
            INDEX_ERP_CONFIG['QUANTILE_CEILING_COL'],
            INDEX_ERP_CONFIG['QUANTILE_FLOOR_COL'],
        ],
    ),
    isSignalAssigned=True,
)

# NOTE 风格关注度
STYLE_FOCUS_CONFIG = {
    'WIND_TABLE': param_cls.WindPortal.A_IDX_VAL,
    'DT_TYPE': TradeDtType.STOCK_MKT,
    'SLIDER_START_DT': '20200601',
    'SLIDER_DEFAULT_OFFSET': '半年',
    'QUANTILE_ROLLING_WINDOW': '两年',
    'QUANTILE_CEILING': 95,
    'QUANTILE_FLOOR': 5,
    'STYLE_FOCUS_COL': '风格关注度',
    'SIGNAL_COL': '交易信号',
    'BASELINE_COL': '比较基准',
    'TRUE_SIGNAL': param_cls.TradeSignal.LONG_SMALL.value,
    'FALSE_SIGNAL': param_cls.TradeSignal.LONG_BIG.value,
    'NO_SIGNAL': param_cls.TradeSignal.NO_SIGNAL.value,
    'BAR_TITLE': '风格关注度 —— 小盘和大盘指数的滚动90日相对换手率',
    'LINE_STROKE_DASH': (5, 3),
}
STYLE_FOCUS_CONFIG.update(
    {
        'SLIDER_DEFAULT_OFFSET_DT_COUNT': get_avg_dt_count_via_dt_type(
            dt_type=STYLE_FOCUS_CONFIG['DT_TYPE'],
            period=STYLE_FOCUS_CONFIG['SLIDER_DEFAULT_OFFSET'],
        ),
        'QUANTILE_ROLLING_WINDOW_SIZE': get_avg_dt_count_via_dt_type(
            dt_type=STYLE_FOCUS_CONFIG['DT_TYPE'],
            period=STYLE_FOCUS_CONFIG['QUANTILE_ROLLING_WINDOW'],
        ),
        'QUANTILE_CEILING_COL': get_rolling_window_col(
            window_name=STYLE_FOCUS_CONFIG['QUANTILE_ROLLING_WINDOW'],
            window_type='%分位数',
            extra_info=STYLE_FOCUS_CONFIG['QUANTILE_CEILING'],
        ),
        'QUANTILE_FLOOR_COL': get_rolling_window_col(
            window_name=STYLE_FOCUS_CONFIG['QUANTILE_ROLLING_WINDOW'],
            window_type='%分位数',
            extra_info=STYLE_FOCUS_CONFIG['QUANTILE_FLOOR'],
        ),
    }
)
STYLE_FOCUS_CHART_PARAM = param_cls.BarLineWithSignalParam(
    dt_slider_param=param_cls.DtSliderParam(
        start_dt=STYLE_FOCUS_CONFIG['SLIDER_START_DT'],
        default_start_offset=STYLE_FOCUS_CONFIG['SLIDER_DEFAULT_OFFSET_DT_COUNT'],
        key='STYLE_FOCUS_SLIDER',
    ),
    bar_param=param_cls.SignalBarParam(
        axis_names={
            'X': DATA_COL_PARAM[STYLE_FOCUS_CONFIG['WIND_TABLE']].dt_col,
            'Y': STYLE_FOCUS_CONFIG['STYLE_FOCUS_COL'],
            'LEGEND': STYLE_FOCUS_CONFIG['SIGNAL_COL'],
        },
        title=STYLE_FOCUS_CONFIG['BAR_TITLE'],
        true_signal=STYLE_FOCUS_CONFIG['TRUE_SIGNAL'],
        false_signal=STYLE_FOCUS_CONFIG['FALSE_SIGNAL'],
        no_signal=INDEX_ERP_CONFIG['NO_SIGNAL'],
    ),
    line_param=param_cls.LineParam(
        axis_names={
            'X': DATA_COL_PARAM[STYLE_FOCUS_CONFIG['WIND_TABLE']].dt_col,
            'Y': '分位数',
            'LEGEND': STYLE_FOCUS_CONFIG['BASELINE_COL'],
        },
        stroke_dash=STYLE_FOCUS_CONFIG['LINE_STROKE_DASH'],
        color='red',
        compared_cols=[
            STYLE_FOCUS_CONFIG['QUANTILE_CEILING_COL'],
            STYLE_FOCUS_CONFIG['QUANTILE_FLOOR_COL'],
        ],
    ),
    isSignalAssigned=True,
)

STYLE_FOCUS_STYLE_CHART_CONFIG = param_cls.StyleBarLineChartConfig(
    bar_axis_names=STYLE_FOCUS_CHART_PARAM.bar_param.axis_names,
    bar_axis_types=STYLE_FOCUS_CHART_PARAM.bar_param.axis_types,
    line_axis_names=STYLE_FOCUS_CHART_PARAM.line_param.axis_names,
    line_axis_types=STYLE_FOCUS_CHART_PARAM.line_param.axis_types,
    title=STYLE_FOCUS_CHART_PARAM.bar_param.title,
    bar_y_axis_format=STYLE_FOCUS_CHART_PARAM.bar_param.y_axis_format,
    line_y_axis_format=STYLE_FOCUS_CHART_PARAM.line_param.y_axis_format,
    bar_color=None,
    line_color=STYLE_FOCUS_CHART_PARAM.line_param.color,
    line_stroke_dash=STYLE_FOCUS_CHART_PARAM.line_param.stroke_dash,
)


STYLE_CHART_AXIS_NAMES = {
    'VALUE_GROWTH_RATIO_MEAN': {
        'X': '交易日期',
        'LEGEND': '价值成长指数比价',
        'Y': '比值',
    },
    'BIG_SMALL_RATIO_MEAN': {
        'X': '交易日期',
        'LEGEND': '大小盘指数比价',
        'Y': '比值',
    },
    '近两月收益率': {
        'X': '交易日期',
        'LEGEND': '大小盘指数收益率',
        'Y': '近两月收益率',
    },
    'DIFFERENCE_MEAN': {
        'X': '日期',
        'LEGEND': '图例',
        'Y': '期限利差(%)',
    },
    'LONG_SHORT_TERM_RATE': {
        'X': '交易日期',
        'LEGEND': '年限',
        'Y': '到期收益率',
    },
    'VALUE_GROWTH_PCT_CHANGE': {
        'X': '交易日期',
        'LEGEND': '价值/成长',
        'Y': '收益率',
    },
}

# https://coolors.co/83c9ff-ffdd4a-0068c9-000103-ff0000
