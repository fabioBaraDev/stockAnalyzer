from sqlalchemy import Column, String, INT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AnalysisConfiguration(Base):
    __tablename__ = "analysis_configuration"
    id = Column(INT, primary_key=True)
    sht = Column(INT)
    lng = Column(INT)
