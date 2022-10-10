import copy
import warnings
from typing import Union

import numpy as np
import pandas as pd
import talib as ta
from pandas import DataFrame, Series

from src.domain.model.execution import Execution
from src.infrastructure.adapters.repository.file_repository import FileRepository

warnings.filterwarnings('ignore')
pd.set_option('display.max_rows', None)


class PerformanceService:

    def __init__(self, file_repository: FileRepository):
        self.file_repository = file_repository

    def get_performance(self, exec_param: Execution, stocks: Union[DataFrame, Series]):

        stock_sac = copy.deepcopy(stocks)['Adj Close']

        # Criando um novo dataframe com o retorno da função def que seta a quantidade de valores NaN
        stock_sac = stock_sac[self._good_stocks(stock_sac, 10)]

        # Percorrendo a lista com as médias móveis curtas
        result_list = self._calculate_avg_ordered_by_the_best_final_result(exec_param, stock_sac)

        new_df = result_list.copy().reset_index()

        data = self._order_data_by_final_return(new_df)
        self.file_repository.save_csv_data(data, exec_param)

        return data

    def _order_data_by_final_return(self, data: pd.DataFrame):
        ordered = data.groupby(by=['index', 'Parameters'])[['finalReturn']]
        ordered.max().sort_values(by='finalReturn', ascending=False)

        g = data.copy()

        g.set_index(['index', 'Parameters'])
        g.sort_values(['index', 'finalReturn'], ascending=False)
        n = g.sort_values(['index', 'finalReturn'], ascending=False)
        res = n.groupby(['index', 'Parameters']).max().sort_values(['finalReturn', 'index'], ascending=False)
        res = res.loc[res['finalReturn'] > 0]
        return res

    def _calculate_avg_ordered_by_the_best_final_result(self, exec_param: Execution, stock_sac):
        result_list = pd.DataFrame()

        # Percorrendo a lista com as médias móveis curtas
        for i in range(len(exec_param.sht_period)):
            sht_period = exec_param.sht_period[i]

            # Para cada média móvel curta, cruzamos a lista das médias móveis longas
            for j in range(len(exec_param.lng_period)):
                lng_period = exec_param.lng_period[j]
                parameters = str(sht_period) + ' - ' + str(lng_period)

                # Percorremos a lista de ativos
                for stock_name in list(stock_sac.columns):
                    try:

                        # Chamamos a função returns_stocks passando todos os parâmetros para a função
                        result = self._returns_stock(stock_name, sht_period, lng_period, stock_sac,
                                                     exec_param.initial_amount,
                                                     parameters)
                        print('{}: OK'.format(stock_name))
                        result_list = pd.concat([result_list, result])
                    except:
                        print('{}: ERRO'.format(stock_name))

        result_list.sort_values(by='AnualRatePercent', ascending=False)[:50]

        return result_list

    def _data_quality(self, df):
        # pega um dataframe e retorna um outro dataframe com o número de nulos e percentual
        df_evaluation = pd.DataFrame(df.isna().sum())
        df_evaluation.columns = ['Null_Values']
        df_evaluation['Null_Values_Percent'] = ((df_evaluation['Null_Values'] / len(df)) * 100).round(2)
        return df_evaluation

    def _good_stocks(self, df, threshold):
        # pega um dataframe e retorna uma lista com as colunas de boa qualidade e com um número
        # aceitável de NaN.

        data_evaluation = self._data_quality(df)
        data_evaluation = data_evaluation[data_evaluation['Null_Values_Percent'] < threshold]

        return list(data_evaluation.T.columns)

    def _evaluate_stock(self, stock_action, initial_amount, stock_name, return_type='finalReturn'):
        ## Criando as variáveis de cashflow

        cashstart = np.zeros(len(stock_action))
        cashend = np.zeros(len(stock_action))
        stockstart = np.zeros(len(stock_action))
        stockend = np.zeros(len(stock_action))
        volumebought = np.zeros(len(stock_action))
        volumesold = np.zeros(len(stock_action))
        stockprice = np.zeros(len(stock_action))

        for i in range(len(stock_action)):

            # a lista stockprice vai iterar as as cotações da stock_name
            stockprice[i] = stock_action[stock_name][i]

            if i == 0:
                # no primeiro dia o cashstart vai ser o capital inicial
                cashstart[i] = initial_amount
            else:
                # cashtart de d é o chasend de d-1
                cashstart[i] = cashend[i - 1]
                # o stockstart de d é o stockend de d-1
                stockstart[i] = stockend[i - 1]

            # quando a decisao for comprar vamos fazer uma divisao do cash pela
            # cotacao e pegar apenas a parte inteira. É o que os // fazem.
            if stock_action['action'][i] == 'buy':
                stockend[i] = cashstart[i] // stockprice[i]
                volumebought[i] = stockend[i] * stockprice[i]
                cashend[i] = cashstart[i] - volumebought[i]

            elif stock_action['action'][i] == 'sell':
                volumesold[i] = stockstart[i] * stockprice[i]
                cashend[i] = cashstart[i] + volumesold[i]

            else:
                print("ERRO: temos um valor de acton diferente de BUY e SELL")

        returndf = pd.DataFrame([cashstart, stockstart, stockprice,
                                 volumebought, volumesold, stockend, cashend])
        returndf = returndf.T
        returndf.columns = 'cashstart stockstart stockprice volumebought volumesold stockend cashend'.split(' ')

        if return_type == 'df':
            return returndf
        elif return_type == 'finalReturn':
            profit = cashend[-1] / initial_amount
            # print('Retorno apurado pela operação foi de {} ' .format(profit.round(2)),'%')
            return profit
        else:
            return print("Tipo de retorno inválido")

    def _create_stock_action(self, stock_name, sht_period, lng_period, stocksac):
        global stock_action
        # criando o dataframe com as ações
        stock = stocksac[[stock_name]]

        # preencher os valores nulos com a média do último e do próximo valor
        stock.interpolate(inplace=True)

        # cria as médias móveis de curto e longo prazo
        # stock['Sht'] = stock[stock_name].rolling(sht_period).mean()
        stock['Lng'] = stock[stock_name].rolling(lng_period).mean()
        stock['Sht'] = stock[stock_name].ewm(span=sht_period).mean()
        # stock['Lng'] = stock[stock_name].ewm(span=lng_period).mean()

        # excluir os dias que não temos as 2 médias móveis
        stock.dropna(inplace=True)

        # o valor é true se estou comprado e false se estou vendido
        stock['Status'] = stock['Sht'] > stock['Lng']

        # pega o status do dia anterior
        stock['Statusd-1'] = stock['Status'].shift(1)

        # mostra se alguma decisão deve ser tomada
        stock['has_action'] = stock['Status'] != stock['Statusd-1']

        # decisão de compra
        stock.loc[(stock['has_action'] == True) & \
                  (stock['Status'] == True), 'action'] = 'buy'

        # decisão de venda
        stock.loc[(stock['has_action'] == True) & (stock['Status'] == False) & \
                  (stock['Statusd-1'].notnull()), 'action'] = 'sell'

        # decisão de esperar
        stock.loc[stock['action'].isnull(), 'action'] = 'wait'

        # Criando um datafram onde apenas com ações buy and sell
        stock_action = stock[stock['action'] != 'wait']

        # ------------------------------------------
        # Setando a última posição com venda para encerrar a operação e apurar o lucro obtido.
        # -------------------------------------------

        if (stock_action['action'].iloc[-1] == 'buy') & \
                (stock.index.values[-1] != stock_action.index.values[-1]):
            last_day = stock.tail(1)
            last_day['action'].iloc[0] = 'sell'
            stock_action = pd.concat([stock_action, last_day])

        # Criando um DataFrame apenas com os dias de compra e venda.
        stock_action = stock[stock['action'] != 'wait']

        # excluindo as colunas que nao vamos utilizar mais
        stock_action = stock_action[[stock_name, 'action']]

        if len(stock_action) == 0:
            print("Acao sem compra e venda")
        else:
            return [stock_action, stock]

    def _evaluate_returns(self, final_return, stock_name, stock, parameters, rsi):
        result = pd.DataFrame([[final_return]], columns=['finalReturn'], index=[stock_name])

        # Calcular a diferença entre o primeiro e ultima dia do dataframe
        month_diff = (stock.index[-1] - stock.index[0]) / np.timedelta64(1, 'M')
        year_diff = month_diff / 12

        # Calcular as taxas de retorno
        result['AnualRatePercent'] = (result['finalReturn'] ** (1 / year_diff) - 1) * 100
        result['MounthRatePercent'] = (result['finalReturn'] ** (1 / month_diff) - 1) * 100
        result['Parameters'] = parameters
        result['finalReturn'] = (result['finalReturn'] - 1) * 100
        result['RSI'] = rsi
        return result

    def _returns_stock(self, stock_name, sht_period, lng_period, stock_sac, initial_amount, parameters):
        # executa todas as funções do script
        stock_action = self._create_stock_action(stock_name, sht_period, lng_period, stock_sac)[0]
        stock = self._create_stock_action(stock_name, sht_period, lng_period, stock_sac)[1]
        final_return = self._evaluate_stock(stock_action, initial_amount, stock_name)
        rsi = ta.RSI(stock_sac[stock_name].dropna(), timeperiod=14).tail(1)[0]
        return self._evaluate_returns(final_return, stock_name, stock, parameters, rsi)
