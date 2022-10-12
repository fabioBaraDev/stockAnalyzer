import os
from dataclasses import dataclass
from datetime import datetime, timedelta

from src.domain.model.ticker import Ticker


@dataclass(frozen=True, eq=True)
class Execution(object):
    symbols: dict[str, Ticker]
    start_date: str
    end_date: str
    path: str
    initial_amount: int

    @classmethod
    def build(cls, symbols) -> "Execution":

        path = os.environ.get("S3_PATH")
        days = os.environ.get("DAYS")
        if not path:
            path = os.getcwd() + '/reports'

        if not os.path.isdir(path):
            os.mkdir(path)
        path = path + '/' + datetime.today().strftime('%Y-%m-%d')
        if not os.path.isdir(path):
            os.mkdir(path)
        if not os.path.isdir(path + '/buy'):
            os.mkdir(path + '/buy')

        if not days:
            days = 730

        start_date = datetime.today() - timedelta(days=days)
        end_date = datetime.today().strftime('%Y-%m-%d')
        initial_amount = 1000

        return Execution(symbols, start_date, end_date, path, initial_amount)
