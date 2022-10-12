from dataclasses import dataclass
from typing import Union

import talib as ta
import pandas as pd
from pandas import DataFrame, Series

from src.domain.model.execution import Execution
from src.domain.model.ticker import Ticker


@dataclass(frozen=True, eq=True)
class MovingAverageCalculator(object):
    ticker: Ticker
    start_date: str
    end_date: str
    sht: int
    lng: int
    data_frame: DataFrame

    @classmethod
    def build(cls,
              dt_frame: pd.DataFrame,
              exec_param: Execution,
              raw_data: Union[DataFrame, Series]
              ) -> "MovingAverageCalculator":

        name = dt_frame[0][0]
        start_date = exec_param.start_date
        end_date = exec_param.end_date
        sht = int(dt_frame[1].configuration.sht)
        lng = int(dt_frame[1].configuration.lng)

        data_frame = pd.DataFrame()
        data_frame['Adj Close'] = raw_data['Adj Close'][name].dropna()

        data_frame['Lng'] = data_frame['Adj Close'].rolling(lng).mean()
        data_frame['Sht'] = data_frame['Adj Close'].ewm(span=sht).mean()
        # stocks['Lng'] = stocks['Adj Close'].ewm(span=lng).mean()
        # stocks['Sht'] = stocks['Adj Close'].rolling(sht).mean()
        data_frame['RSI'] = ta.RSI(data_frame['Adj Close'], timeperiod=14)

        return MovingAverageCalculator(exec_param.symbols[name], start_date, end_date, sht, lng, data_frame)
