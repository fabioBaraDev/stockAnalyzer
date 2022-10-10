import os
from dataclasses import dataclass
from datetime import datetime

from src.conf.config import get_brazilian_tickers


@dataclass(frozen=True, eq=True)
class Execution(object):
    symbols: [str]
    start_date: str
    end_date: str
    path: str
    sht_period: [int]
    lng_period: [int]
    initial_amount: int

    @classmethod
    def build(cls) -> "Execution":
        path = os.getcwd() + '/reports'
        if not os.path.isdir(path):
            os.mkdir(path)
        path = path + '/' + datetime.today().strftime('%Y-%m-%d')
        if not os.path.isdir(path):
            os.mkdir(path)
        if not os.path.isdir(path + '/buy'):
            os.mkdir(path + '/buy')

        symbols = get_brazilian_tickers()
        start_date = '2020-07-10'
        end_date = datetime.today().strftime('%Y-%m-%d')
        path = path
        sht_period = [10, 20, 30]
        lng_period = [50, 60, 90]
        initial_amount = 1000

        return Execution(symbols, start_date, end_date, path, sht_period, lng_period, initial_amount)
