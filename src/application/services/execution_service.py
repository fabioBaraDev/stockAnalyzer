from src.domain.model.execution import Execution
from src.infrastructure.adapters.repository.postgres_repository import PostgresRepository


class ExecutionService:

    def __init__(self, repository: PostgresRepository):
        self.repository = repository

    def get_execution(self) -> "Execution":
        tickers = self.repository.get_brl_tickers()
        tickers_dict = dict({ticker.name: ticker for ticker in tickers})

        return Execution.build(tickers_dict)
