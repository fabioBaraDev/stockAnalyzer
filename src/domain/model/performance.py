from sqlalchemy import Column, String, INT, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Performance(Base):
    __tablename__ = "performances"
    id = Column(INT, primary_key=True)
    ticker_id = Column(INT, nullable=False)
    configuration_id = Column(INT, nullable=False)
    update_at = Column(DateTime)
    final_return = Column(Float, nullable=False)
    annual_rate_percent = Column(Float, nullable=False)
    month_rate_percent = Column(Float, nullable=False)
    rsi = NUMERIC = Column(Float, nullable=False)
