from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

from src.domain.model.execution import Execution
from src.domain.model.moving_average_calculator import MovingAverageCalculator

rcParams['figure.figsize'] = 20, 8


class FileRepository:

    def save_graph(self, mov_avg_calc: MovingAverageCalculator, execution_param: Execution):
        mov_avg_calc.data_frame[['Adj Close', 'Sht', 'Lng']].plot()
        # kc['Volume'].plot(secondary_y=True, color='lightgray', title=ticker)
        mov_avg_calc.data_frame['RSI'].plot(secondary_y=True, color='lightgray', title=mov_avg_calc.ticker.name)

        plt.title = mov_avg_calc.ticker.name
        plt.grid()

        figure = plt.savefig(
            execution_param.path + '/buy/' + mov_avg_calc.ticker.name + ' - ' + str(mov_avg_calc.sht) + ' - ' + str(mov_avg_calc.lng) + '.jpg')
        plt.close(figure)

    def save_ticker_csv(self,
                        history_analysis: pd.DataFrame,
                        mov_avg_calc: MovingAverageCalculator,
                        execution_param: Execution):
        history_analysis.to_csv(
            execution_param.path + '/buy/' + mov_avg_calc.ticker.name + ' - ' + str(mov_avg_calc.sht) + ' - ' + str(mov_avg_calc.lng) + '.csv',
            index=False)
