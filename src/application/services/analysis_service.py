import copy

import numpy as np
import pandas as pd

from src.domain.model.execution import Execution
from src.domain.model.ticker import Ticker

import warnings
warnings.filterwarnings('ignore')


class AnalysisService:

    def get_analysis(self, ticker: Ticker, exec_param: Execution):

        stocks = copy.deepcopy(ticker.data_frame)

        parameters = str(ticker.sht) + ' - ' + str(ticker.lng)

        # Iniciando a tomada de decisão

        ## Se a média móvel de curto prazo for maior que a de longo prazo: Comprado (True)
        ## Se a média móvel de longo prazo for maior que a de curto prazo: Vendido (False)

        stocks['Status'] = stocks['Sht'] > stocks['Lng']

        ## O start da decisão é a alteração do dia anterior. Se houver alteração de Status, está na hora da tomada da decisão.
        ## Vamos usar o status do dia anterior ('.shift()'). Por padrão, '.shift()' utiliza 1 dia como parâmetro.

        stocks['Statusd-1'] = stocks['Status'].shift(1)

        ## Vamos criar agora a coluna que aciona a estratégia.
        ## has-action é true quando o Status de D é diferente de D-1.

        stocks['has_action'] = stocks['Status'] != stocks['Statusd-1']

        ## Filtrando para os valores True
        stocks[stocks['has_action'] == True]

        ### Decisão da compra

        # stock.loc[(stock['has_action']==True) & (stock['Status']==True)] é outra forma de usar o .loc.
        # ,'action' cria uma nova coluna e atribui o registro 'buy' quando a condição é atendida

        stocks.loc[(stocks['has_action'] == True) & \
                   (stocks['Status'] == True), 'action'] = 'buy'

        # Decisão de venda

        # Vamos criar agora a condição de venda do ativo, quando has_action for True e Status for False e
        # Statusd-1 não for valor nulo, pois não tem como vender o que não foi comprado ainda.

        stocks.loc[(stocks['has_action'] == True) & (stocks['Status'] == False) & \
                   (stocks['Statusd-1'].notnull()), 'action'] = 'sell'

        stocks['action'].fillna('wait', inplace=True)

        # Criando um DataFrame apenas com os dias de compra e venda.

        stock_action = stocks[stocks['action'] != 'wait']

        stock_action = stock_action[['Adj Close', 'action']]

        final_return = self._evaluate_stock(stock_action, exec_param.initial_amount)

        result = pd.DataFrame([[final_return]], columns=['final_return'], index=[stocks])

        # Calcular a diferença entre o primeiro e ultima dia do dataframe

        mounth_diff = (stocks.index[-1] - stocks.index[0]) / np.timedelta64(1, 'M')
        year_diff = mounth_diff / 12

        result['AnualRatePercent'] = (result['final_return'] ** (1 / year_diff) - 1) * 100
        result['MounthRatePercent'] = (result['final_return'] ** (1 / mounth_diff) - 1) * 100
        result['Parameters'] = parameters

        self._evaluate_stock(stock_action, exec_param.initial_amount, 'df')
        stock_action['Stop_loss'] = stock_action['Adj Close'] * 0.9
        stock_action['lng'] = round(stocks['Lng'], 2)
        stock_action['sht'] = round(stocks['Sht'], 2)

        return stock_action

    def _evaluate_stock(self, stock_action, initial_amount, return_type='finalReturn'):
        global returndf

        cashstart = np.zeros(len(stock_action))
        cashend = np.zeros(len(stock_action))
        stockstart = np.zeros(len(stock_action))
        stockend = np.zeros(len(stock_action))
        volumebought = np.zeros(len(stock_action))
        volumesold = np.zeros(len(stock_action))
        stockprice = np.zeros(len(stock_action))

        for i in range(len(stock_action)):

            # a lista stockprice vai iterar as linhas da stockaction
            stockprice[i] = stock_action['Adj Close'][i]

            if i == 0:
                # no primeiro dia o cashstart vai ser o capital inicial
                cashstart[i] = initial_amount
            else:
                # cashtart de d é o chasend de d-1
                cashstart[i] = cashend[i - 1]
                # o stockstart de d é o stockend de d-1
                stockstart[i] = stockend[i - 1]

            if (stock_action['action'][i]) == 'buy':
                # quando a decisão for pela compra, vamos fazer uma divisão pegando apenas a parte inteira
                stockend[i] = cashstart[i] // stockprice[i]
                volumebought[i] = stockend[i] * stockprice[i]
                cashend[i] = cashstart[i] - volumebought[i]

            elif stock_action['action'][i] == 'sell':
                volumesold[i] = stockstart[i] * stockprice[i]
                cashend[i] = cashstart[i] + volumesold[i]
            else:
                print("ERRO: temos um valor de acton diferente de BUY e SELL")

        returndf = pd.DataFrame([cashstart, stockstart, stockprice, volumebought, volumesold, stockend, cashend])
        returndf = returndf.T
        returndf.columns = 'cashstart stockstart stockprice volumebought volumesold stockend cashend'.split(' ')
        if return_type == 'df':
            return returndf
        elif return_type == 'finalReturn':
            profit = (cashend[-1] / initial_amount) - 1
            # print('Retorno apurado pela operação foi de {} ' .format(profit.round(2)),'%')
            return profit
        else:
            return print("Tipo de retorno invalido")
