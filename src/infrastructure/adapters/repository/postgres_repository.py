from src.domain.model.ticker_names import TickerNames
from src.infrastructure.factory.session_factory import SessionFactory


class PostgresRepository:
    def __init__(self):
        self.session = SessionFactory.get_session()

    def get_brl_tickers(self):
        return (
            self.session.query(TickerNames).all()
        )
