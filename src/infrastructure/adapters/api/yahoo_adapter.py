
from typing import Union

import yfinance as yf
from pandas import DataFrame, Series

from src.domain.model.execution import Execution


class YahooAdapter:
    @classmethod
    def get_tickers(cls, exec_param: Execution) -> Union[DataFrame, Series]:
        return yf.download(list(map(lambda x: x, exec_param.symbols.keys())), start=exec_param.start_date, end=exec_param.end_date)
