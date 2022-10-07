from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as y
from dateutil.relativedelta import relativedelta

from AnaliseLinear.acoes import get_ativos_da_bolsa


def main():
    ticker = get_ativos_da_bolsa()
    start = '2018-01-01'
    end = datetime.today().strftime('%Y-%m-%d')
    res = []
    df_ticker = []

    for row in ticker:

        cotacao_response = y.download(row, start=start, end=end)

        portfolio = pd.DataFrame([], columns=['Adj Close', 'Short', 'Long'])  # dataframe vazio

        portfolio['Adj Close'] = cotacao_response['Adj Close']
        portfolio['Short'] = cotacao_response['Adj Close'].rolling(10).mean()
        portfolio['Long'] = cotacao_response['Adj Close'].rolling(70).mean()

        if analisar_ticker(portfolio):
            df_ticker.append([row, portfolio])
            res.append(row)

    print('As Acoes' + str(res) + ' tem potencial')

    for row in df_ticker:
        plot_frame(row[0], row[1])


def plot_frame(title: str, data: pd.DataFrame):
    plt.figure(figsize=(20, 8))

    plt.plot(data['Adj Close'], label='Preco')
    plt.plot(data['Short'], label='Short')
    plt.plot(data['Long'], label='Long')
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.show()


def monitorar_data_frame(data: pd.DataFrame):
    dt_ini = datetime.today() - relativedelta(days=+91)
    for index, row in data.iterrows():
        if index >= dt_ini:
            preco_aproximando = row['Adj Close'] * 1.02
            if row['Short'] < preco_aproximando:
                if row['Short'] < row['Adj Close']:
                    print('O preco na data: ' + str(index) + ' nao eh mais interessante')
                else:
                    print('O preco na data: ' + str(index) + ' esta proximo do ponto de compra')

            if row['Short'] > preco_aproximando:
                if row['Short'] > row['Adj Close']:
                    print('O preco na data: ' + str(index) + ' passou do ponto de venda')
                else:
                    print('O preco na data: ' + str(index) + ' esta proximo do ponto de venda')


def analisar_ticker(data: pd.DataFrame):
    tem_potencial = False

    preco_aproximando = data.iloc[-1]['Long'] * 1.02

    if data.iloc[-1]['Short'] < preco_aproximando:
        tem_potencial = True

    return tem_potencial


main()
# kaggle.com/tossani/compra-venda-macd/edit/run/34833063
