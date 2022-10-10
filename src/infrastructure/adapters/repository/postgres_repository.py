from src.infrastructure.factory.session_factory import SessionFactory


class PostgresRepository:
    def __init__(self):
        self.session = SessionFactory.get_session()

