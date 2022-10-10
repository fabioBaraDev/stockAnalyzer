from src.application.services.analysis_service import AnalysisService
from src.application.services.performance_service import PerformanceService
from src.application.services.ticker_service import TickerService
from src.domain.model.execution import Execution
from src.infrastructure.adapters.repository.file_repository import FileRepository


def run():
    exec_param = Execution.build()

    file_repository = FileRepository()
    analysis_service = AnalysisService()
    performance_service = PerformanceService(file_repository)
    ticker_service = TickerService(file_repository, analysis_service, performance_service)

    dt = ticker_service.execute_buy_position(exec_param)

    # print the newest to cross the long avg
    print('** THE NEWEST TO CROSS THE LONG AVG **')
    print(dt.loc[str(dt.tail(1).index[0]):str(dt.tail(1).index[0])])

    print("END")

