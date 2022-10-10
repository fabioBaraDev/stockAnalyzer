
from dataclasses import dataclass
from typing import Union

import talib as ta
import pandas as pd
from pandas import DataFrame, Series

from src.domain.model.execution import Execution


@dataclass(frozen=True, eq=True)
class Ticker(object):
    name: str
    start_date: str
    end_date: str
    sht: int
    lng: int
    data_frame: DataFrame

    @classmethod
    def build(cls, dt_frame: pd.DataFrame, exec_param: Execution, raw_data: Union[DataFrame, Series]) -> "Ticker":
        name = dt_frame[0][0]
        start_date = exec_param.start_date
        end_date = exec_param.end_date
        sht = int(dt_frame[0][1][0:2])
        lng = int(dt_frame[0][1][-2:])

        data_frame = pd.DataFrame()
        data_frame['Adj Close'] = raw_data['Adj Close'][name].dropna()

        data_frame['Lng'] = data_frame['Adj Close'].rolling(lng).mean()
        data_frame['Sht'] = data_frame['Adj Close'].ewm(span=sht).mean()
        # stocks['Lng'] = stocks['Adj Close'].ewm(span=lng).mean()
        # stocks['Sht'] = stocks['Adj Close'].rolling(sht).mean()
        data_frame['RSI'] = ta.RSI(data_frame['Adj Close'], timeperiod=14)

        return Ticker(name, start_date, end_date, sht, lng, data_frame)

