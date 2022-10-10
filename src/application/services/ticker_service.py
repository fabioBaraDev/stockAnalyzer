import pandas as pd

from src.application.services.analysis_service import AnalysisService
from src.application.services.performance_service import PerformanceService
from src.domain.model.execution import Execution
from src.domain.model.ticker import Ticker
from src.infrastructure.adapters.api.yahoo_adapter import YahooAdapter
from src.infrastructure.adapters.repository.file_repository import FileRepository


class TickerService:

    def __init__(self, file_repository: FileRepository, analysis_service: AnalysisService,
                 performance_service: PerformanceService):
        self.file_repository = file_repository
        self.analysis_service = analysis_service
        self.performance_service = performance_service

    def execute_buy_position(self, exec_param: Execution):
        dt = pd.DataFrame(columns=['Adj Close', 'action', 'Stop_loss', 'Stock'])

        raw_stocks_data = YahooAdapter.get_tickers(exec_param)
        ticker_performances = self.performance_service.get_performance(exec_param, raw_stocks_data).iterrows()

        for row in ticker_performances:

            ticker = Ticker.build(row, exec_param, raw_stocks_data)

            history_analysis = self.analysis_service.get_analysis(ticker, exec_param)

            if history_analysis.tail(1)['action'][0] == 'buy':
                self.file_repository.save_graph(ticker, exec_param)
                self.file_repository.save_ticker_csv(history_analysis, ticker, exec_param)

                history_analysis['Stock'] = ticker.name + ' - ' + str(ticker.sht) + ' - ' + str(ticker.lng)
                dt = dt.append(history_analysis, ignore_index=False, verify_integrity=False, sort=None)

        return dt.sort_index()
