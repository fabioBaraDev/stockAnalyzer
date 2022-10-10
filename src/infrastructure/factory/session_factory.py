import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


class SessionFactory(object):
    @staticmethod
    def get_session():
        var_name = "CONN_STRING"

        return SessionFactory._get_session(var_name)

    @staticmethod
    def _get_session(var_name):
        conn_string = os.environ.get(var_name)

        if not conn_string:
            conn_string = "postgresql+psycopg2://admin:admin@localhost:5433/postgres"

        engine = create_engine(
            conn_string,
            poolclass=NullPool,
            connect_args={
                "connect_timeout": int(os.environ.get("DB_CONN_TIMEOUT", 10))
            },
        )
        Session = sessionmaker(bind=engine)
        session = Session()
        return session
