import pandas as pd
from sqlalchemy import insert

from src.domain.model.analysis_configuration import AnalysisConfiguration
from src.domain.model.performance import Performance
from src.domain.model.ticker import Ticker
from src.infrastructure.factory.session_factory import SessionFactory


class PostgresRepository:
    def __init__(self):
        self.session = SessionFactory.get_session()

    def get_brl_tickers(self):
        return (
            self.session.query(Ticker).all()
        )

    def get_sht_lng_configuration(self):
        return (
            self.session.query(AnalysisConfiguration).all()
        )

    def save_performances(self, data: pd.DataFrame):
        performance_mapping = [{
            "ticker_id": row['stock_id'],
            "configuration_id": key[1],
            "final_return": row['final_return'],
            "annual_rate_percent": row['annual_rate_percent'],
            "month_rate_percent": row['month_rate_percent'],
            "rsi": row['RSI'],
        } for key, row in data.iterrows()]

        table = Performance.__table__
        insert_command = insert(table).values(performance_mapping)
        self.session.execute(insert_command)
        self.session.commit()
