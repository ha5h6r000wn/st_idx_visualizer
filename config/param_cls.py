from enum import Enum
from typing import Dict, List, Tuple

from pydantic import BaseModel


# ENUM
class TradeSignal(Enum):
    LONG_GROWTH = '成长'
    LONG_VALUE = '价值'
    LONG_BIG = '大盘'
    LONG_SMALL = '小盘'
    NO_SIGNAL = '中性'


class WindPortal(Enum):
    CN_BOND_YIELD = 'CBondCurveCNBD'
    A_IDX_VAL = 'AIndexValuation'
    A_IDX_PRICE = 'AIndexEODPrices'
    A_IDX_DESC = 'AIndexDescription'
    EDB = 'GFZQEDB'
    SHIBOR_PRICES = 'ShiborPrices'


class WindLocal(Enum):
    CN_BOND_YIELD = 'bond_yields'
    A_IDX_VAL = 'index_valuations'
    A_IDX_PRICE = 'index_prices'
    A_IDX_DESC = 'a_idx_desc'
    EDB = 'economic_data'
    SHIBOR_PRICES = 'shibor_prices'


# WIND
class SqlParam(BaseModel):
    sql_name: str
    sql_dir: str = 'sql_template'


class BaseWindQueryParam(BaseModel):
    start_date: str
    wind_dt_format: str = r'%Y%m%d'
    sql_param: SqlParam
    end_date: str | None = None


class WindListedSecParam(BaseWindQueryParam):
    wind_codes: Tuple[str, ...]


class WindYieldCurveQueryParam(BaseWindQueryParam):
    curve_names: Tuple[str, ...]
    curve_terms: Tuple[int, ...]


class BaseDataColParam(BaseModel):
    dt_col: str
    name_col: str | None = None


class WindIdxColParam(BaseDataColParam):
    dt_col: str = 'TRADE_DT'
    code_col: str = 'S_INFO_WINDCODE'
    name_col: str = 'S_INFO_NAME'
    price_col: str = 'S_DQ_CLOSE'


class WindYieldCurveColParam(BaseDataColParam):
    dt_col: str = 'TRADE_DT'
    name_col: str = 'B_ANAL_CURVENAME'
    term_col: str = 'B_ANAL_CURVETERM'
    ytm_col: str = 'B_ANAL_YIELD'


class WindAIndexValueColParam(BaseDataColParam):
    dt_col: str = 'TRADE_DT'
    name_col: str = 'S_INFO_NAME'
    code_col: str = 'S_INFO_WINDCODE'
    turnover_col: str = 'TURNOVER'
    pe_ttm_col: str = 'PE_TTM'
    value_col: str = 'INDICATOR_NUM'


# St.slider
class BaseSliderParam(BaseModel):
    name: str
    key: str | None = None


class DtSliderParam(BaseSliderParam):
    name: str = '自选周期'
    start_dt: str
    default_start_offset: int = 0
    default_end_offset: int = 1


class SelectSliderParam(BaseSliderParam):
    default_select_offset: Dict[str, int]


# St.chart
class BaseChartParam(BaseModel):
    axis_names: Dict[str, str]
    title: str | None = None
    height: int = 500


class BaseBarParam(BaseChartParam):
    axis_types: Dict[str, str] = {'X': 'N', 'LEGEND': 'N', 'Y': 'Q'}
    y_axis_format: str = '.3f'


class SignalBarParam(BaseBarParam):
    true_signal: str
    false_signal: str
    no_signal: str | None = None
    signal_order: List[str] | None = None


class IdxLineParam(BaseChartParam):
    data_col_param: BaseDataColParam = WindIdxColParam()
    y_limit_extra: float = 0.05
    y_axis_format: str
    dt_slider_param: DtSliderParam | None = None


class LineParam(BaseChartParam):
    axis_types: Dict[str, str] = {'X': 'N', 'LEGEND': 'N', 'Y': 'Q'}
    y_axis_format: str = '.3f'
    y_limit_multiplier: float = 1.05
    stroke_dash: tuple = (5, 0)
    color: str | None = None
    compared_cols: List[str] | None = None


class BarLineWithSignalParam(BaseModel):
    dt_slider_param: DtSliderParam | None = None
    bar_param: BaseBarParam
    line_param: LineParam | None = None
    isLineDrawn: bool = True
    isConvertedToPct: bool = False
    isSignalAssigned: bool = False


class HeatmapParam(BaseChartParam):
    col_types: Dict[str, str]
    legend_format: str
