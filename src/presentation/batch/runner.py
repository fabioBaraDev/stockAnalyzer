from src.application.services.analysis_service import AnalysisService
from src.application.services.execution_service import ExecutionService
from src.application.services.performance_service import PerformanceService
from src.application.services.ticker_service import TickerService
from src.domain.model.execution import Execution
from src.infrastructure.adapters.repository.file_repository import FileRepository
from src.infrastructure.adapters.repository.postgres_repository import PostgresRepository


def run():

    postgres_repository = PostgresRepository()
    execution_service = ExecutionService(postgres_repository)
    file_repository = FileRepository()
    analysis_service = AnalysisService()
    performance_service = PerformanceService(file_repository, postgres_repository)
    ticker_service = TickerService(file_repository, analysis_service, performance_service, execution_service)

    dt = ticker_service.execute_buy_position()

    # print the newest to cross the long avg
    print('** THE NEWEST TO CROSS THE LONG AVG **')
    print(dt.loc[str(dt.tail(1).index[0]):str(dt.tail(1).index[0])])

    print("END")

