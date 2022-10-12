import copy
import warnings
from typing import Union

import numpy as np
import pandas as pd
import talib as ta
from pandas import DataFrame, Series

from src.domain.model.execution import Execution
from src.infrastructure.adapters.repository.postgres_repository import PostgresRepository

warnings.filterwarnings('ignore')
pd.set_option('display.max_rows', None)


class PerformanceService:

    def __init__(self, repository: PostgresRepository):
        self.repository = repository

    def get_performance(self, exec_param: Execution, stocks: Union[DataFrame, Series]):

        stock_sac = copy.deepcopy(stocks)['Adj Close']

        # Criando um novo dataframe com o retorno da função def que seta a quantidade de valores NaN
        stock_sac = stock_sac[self._good_stocks(stock_sac, 10)]

        # Percorrendo a lista com as médias móveis curtas
        result_list = self._calculate_avg_ordered_by_the_best_final_result(exec_param, stock_sac)

        new_df = result_list.copy().reset_index()

        data = self._order_data_by_final_return(new_df)
        self.repository.save_performances(data)
        return data

    def _order_data_by_final_return(self, data: pd.DataFrame):
        ordered = data.groupby(by=['index', 'configuration_id'])[['final_return']]
        ordered.max().sort_values(by='final_return', ascending=False)

        g = data.copy()

        g.set_index(['index', 'configuration_id'])
        g.sort_values(['index', 'final_return'], ascending=False)
        n = g.sort_values(['index', 'final_return'], ascending=False)
        res = n.groupby(['index', 'configuration_id']).max().sort_values(['final_return', 'index'], ascending=False)
        res = res.loc[res['final_return'] > 0]
        return res

    def _calculate_avg_ordered_by_the_best_final_result(self, exec_param: Execution, stock_sac):
        result_list = pd.DataFrame()

        configurations = self.repository.get_sht_lng_configuration()

        print('Starting performance calculation')
        # Percorrendo a lista com as médias móveis curtas e longas
        for conf in configurations:

            # Percorremos a lista de ativos
            for stock_name in list(stock_sac.columns):
                try:
                    stock_id = exec_param.symbols[stock_name].id
                    # Chamamos a função returns_stocks passando todos os parâmetros para a função
                    result = self._returns_stock(conf, stock_id, stock_name, stock_sac,
                                                 exec_param.initial_amount)
                    result['configuration'] = conf
                    result_list = pd.concat([result_list, result])
                except Exception as e:
                    print('{}: ERRO'.format(stock_name))
                    print(str(e))
        print('Finished performance calculation')
        result_list.sort_values(by='annual_rate_percent', ascending=False)[:50]

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

    def _evaluate_stock(self, stock_action, initial_amount, stock_name, return_type='final_return'):
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
        elif return_type == 'final_return':
            profit = cashend[-1] / initial_amount
            # print('Retorno apurado pela operação foi de {} ' .format(profit.round(2)),'%')
            return profit
        else:
            return print("Tipo de retorno inválido")

    def _create_stock_action(self, stock_name, configuration, stocksac):
        global stock_action
        # criando o dataframe com as ações
        stock = stocksac[[stock_name]]

        # preencher os valores nulos com a média do último e do próximo valor
        stock.interpolate(inplace=True)

        # cria as médias móveis de curto e longo prazo
        # stock['Sht'] = stock[stock_name].rolling(sht_period).mean()
        stock['Lng'] = stock[stock_name].rolling(configuration.lng).mean()
        stock['Sht'] = stock[stock_name].ewm(span=configuration.sht).mean()
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

    def _evaluate_returns(self, configuration_id, stock_id, stock_name, final_return, stock, rsi):
        result = pd.DataFrame([[final_return]], columns=['final_return'], index=[stock_name])
        result['stock_id'] = stock_id

        # Calcular a diferença entre o primeiro e ultima dia do dataframe
        month_diff = (stock.index[-1] - stock.index[0]) / np.timedelta64(1, 'M')
        year_diff = month_diff / 12

        # Calcular as taxas de retorno
        result['annual_rate_percent'] = (result['final_return'] ** (1 / year_diff) - 1) * 100
        result['month_rate_percent'] = (result['final_return'] ** (1 / month_diff) - 1) * 100
        result['configuration_id'] = configuration_id
        result['final_return'] = (result['final_return'] - 1) * 100
        result['RSI'] = rsi
        return result

    def _returns_stock(self, configuration, stock_id, stock_name, stock_sac, initial_amount):
        # executa todas as funções do script
        stock_action = self._create_stock_action(stock_name, configuration, stock_sac)[0]
        stock = self._create_stock_action(stock_name, configuration, stock_sac)[1]
        final_return = self._evaluate_stock(stock_action, initial_amount, stock_name)
        rsi = ta.RSI(stock_sac[stock_name].dropna(), timeperiod=14).tail(1)[0]
        return self._evaluate_returns(configuration.id, stock_id, stock_name, final_return, stock, rsi)
