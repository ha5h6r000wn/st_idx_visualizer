import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import BondYield, EconomicData, IndexPrice, IndexValuation


def get_bond_yields(
    session: Session, start_date: str, end_date: str, curve_names: tuple, curve_terms: tuple
) -> pd.DataFrame:
    """Get bond yield data from database"""
    stmt = (
        select(BondYield)
        .where(
            BondYield.交易日期.between(start_date, end_date),
            BondYield.曲线名称.in_(curve_names),
            BondYield.交易期限.in_([str(term) for term in curve_terms]),
        )
        .order_by(BondYield.交易日期, BondYield.曲线名称, BondYield.交易期限)
    )

    results = session.execute(stmt).scalars().all()

    if not results:
        return pd.DataFrame()

    return pd.DataFrame(
        [
            {
                '交易日期': r.交易日期,
                '曲线名称': r.曲线名称,
                '交易期限': float(r.交易期限),
                '到期收益率': r.到期收益率,
            }
            for r in results
        ]
    )


def get_index_valuations(session: Session, start_date: str, end_date: str, wind_codes: tuple) -> pd.DataFrame:
    """Get index valuation data from database"""
    stmt = (
        select(IndexValuation)
        .where(
            IndexValuation.交易日期.between(start_date, end_date),
            IndexValuation.证券代码.in_(wind_codes),
        )
        .order_by(IndexValuation.交易日期, IndexValuation.证券代码)
    )

    results = session.execute(stmt).scalars().all()

    if not results:
        return pd.DataFrame()

    return pd.DataFrame(
        [
            {
                '交易日期': r.交易日期,
                '证券代码': r.证券代码,
                '证券简称': r.证券简称,
                '日换手率': r.日换手率,
                '市盈率': r.市盈率,
            }
            for r in results
        ]
    )


def get_economic_data(session: Session, start_date: str, end_date: str, indicator_codes: tuple) -> pd.DataFrame:
    """Get economic data from database"""
    stmt = (
        select(EconomicData)
        .where(
            EconomicData.交易日期.between(start_date, end_date),
            EconomicData.指标代码.in_(indicator_codes),
        )
        .order_by(EconomicData.交易日期, EconomicData.指标代码)
    )

    results = session.execute(stmt).scalars().all()

    if not results:
        return pd.DataFrame()

    return pd.DataFrame(
        [
            {
                '交易日期': r.交易日期,
                '指标代码': r.指标代码,
                '指标名称': r.指标名称,
                '指标单位': r.指标单位,
                '指标频率': r.指标频率,
                '指标数值': r.指标数值,
            }
            for r in results
        ]
    )


def get_index_prices(session: Session, start_date: str, end_date: str, wind_codes: tuple) -> pd.DataFrame:
    """Get index price data from database"""
    stmt = (
        select(IndexPrice)
        .where(
            IndexPrice.TRADE_DT.between(start_date, end_date),
            IndexPrice.S_INFO_WINDCODE.in_(wind_codes),
        )
        .order_by(IndexPrice.TRADE_DT, IndexPrice.S_INFO_WINDCODE)
    )

    results = session.execute(stmt).scalars().all()

    if not results:
        return pd.DataFrame()

    return pd.DataFrame(
        [
            {
                'TRADE_DT': r.TRADE_DT,
                'S_INFO_WINDCODE': r.S_INFO_WINDCODE,
                'S_INFO_NAME': r.S_INFO_NAME,
                'S_DQ_CLOSE': r.S_DQ_CLOSE,
            }
            for r in results
        ]
    )
