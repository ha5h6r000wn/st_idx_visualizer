"""SQLAlchemy models for database tables."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BondYield(Base):
    """Bond yield curve data model."""

    __tablename__ = 'bond_yields'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    交易日期 = Column(String, nullable=False)
    曲线名称 = Column(String, nullable=False)
    交易期限 = Column(String, nullable=False)
    到期收益率 = Column(Float, nullable=False)
    更新时间 = Column(DateTime, nullable=False)

    __table_args__ = (UniqueConstraint('交易日期', '曲线名称', '交易期限', name='uix_bond_yields'),)

    def __repr__(self):
        return f'<BondYield(交易日期={self.交易日期}, 曲线名称={self.曲线名称}, 交易期限={self.交易期限})>'


class IndexValuation(Base):
    """Index valuation data model."""

    __tablename__ = 'index_valuations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    交易日期 = Column(String, nullable=False)
    证券代码 = Column(String, nullable=False)
    证券简称 = Column(String, nullable=False)
    日换手率 = Column(Float)
    市盈率 = Column(Float)
    更新时间 = Column(DateTime, nullable=False)

    __table_args__ = (UniqueConstraint('交易日期', '证券代码', name='uix_index_valuations'),)

    def __repr__(self):
        return f'<IndexValuation(交易日期={self.交易日期}, 证券代码={self.证券代码})>'


class EconomicData(Base):
    """Economic indicator data model."""

    __tablename__ = 'economic_data'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    交易日期 = Column(String, nullable=False)
    指标代码 = Column(String, nullable=False)
    指标名称 = Column(String, nullable=False)
    指标单位 = Column(String)
    指标频率 = Column(String)
    指标数值 = Column(Float, nullable=False)
    更新时间 = Column(DateTime, nullable=False)

    __table_args__ = (UniqueConstraint('交易日期', '指标代码', name='uix_economic_data'),)

    def __repr__(self):
        return f'<EconomicData(交易日期={self.交易日期}, 指标代码={self.指标代码})>'


class IndexPrice(Base):
    """Index price data model."""

    __tablename__ = 'index_prices'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    TRADE_DT = Column(String, nullable=False)
    S_INFO_WINDCODE = Column(String, nullable=False)
    S_INFO_NAME = Column(String, nullable=False)
    S_DQ_CLOSE = Column(Float, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    __table_args__ = (UniqueConstraint('TRADE_DT', 'S_INFO_WINDCODE', name='uix_index_prices'),)

    def __repr__(self):
        return f'<IndexPrice(TRADE_DT={self.TRADE_DT}, S_INFO_WINDCODE={self.S_INFO_WINDCODE})>'


class ShiborPrice(Base):
    """Shibor price data model."""

    __tablename__ = 'shibor_prices'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    交易日期 = Column(String, nullable=False)
    证券代码 = Column(String, nullable=False)
    利率 = Column(Float, nullable=False)
    期限 = Column(String, nullable=False)
    更新时间 = Column(DateTime, nullable=False)

    __table_args__ = (UniqueConstraint('交易日期', '证券代码', '期限', name='uix_shibor_prices'),)

    def __repr__(self):
        return f'<ShiborPrice(交易日期={self.交易日期}, 证券代码={self.证券代码}, 期限={self.期限})>'
