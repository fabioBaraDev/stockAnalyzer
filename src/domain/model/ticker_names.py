from sqlalchemy import Column, String, INT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TickerNames(Base):
    __tablename__ = "ticker"
    id = Column(INT, primary_key=True)
    name = Column(String(250))
