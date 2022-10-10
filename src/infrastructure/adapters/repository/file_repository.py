import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

from src.domain.model.execution import Execution
from src.domain.model.ticker import Ticker

rcParams['figure.figsize'] = 20, 8


class FileRepository:

    def save_csv_data(self, data: pd.DataFrame, execution_param: Execution):
        path = execution_param.path + '/performances_' + datetime.today().strftime('%Y-%m-%d') + '.csv'
        data.to_csv(path)

    def save_graph(self, ticker: Ticker, execution_param: Execution):
        ticker.data_frame[['Adj Close', 'Sht', 'Lng']].plot()
        # kc['Volume'].plot(secondary_y=True, color='lightgray', title=ticker)
        ticker.data_frame['RSI'].plot(secondary_y=True, color='lightgray', title=ticker.name)

        plt.title = ticker
        plt.grid()

        figure = plt.savefig(execution_param.path + '/buy/' + ticker.name + ' - ' + str(ticker.sht) + ' - ' + str(ticker.lng) + '.jpg')
        plt.close(figure)

    def save_ticker_csv(self, history_analysis: pd.DataFrame, ticker: Ticker, execution_param: Execution):
        history_analysis.to_csv(
            execution_param.path + '/buy/' + ticker.name + ' - ' + str(ticker.sht) + ' - ' + str(ticker.lng) + '.csv',
            index=False)
