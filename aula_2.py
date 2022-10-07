from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as y
from dateutil.relativedelta import relativedelta


def main():
    ticker = 'LWSA3.SA'
    start = '2018-01-01'
    end = '2022-04-25'

    # cotacao_response = y.download(ticker, start=end, interval='1m')
    cotacao_response = y.download(ticker, start=start, end=end)

    portfolio = pd.DataFrame([], columns=['Adj Close', 'Short', 'Long'])  # dataframe vazio

    portfolio['Adj Close'] = cotacao_response['Adj Close']
    portfolio['Short'] = cotacao_response['Adj Close'].rolling(15).mean()
    portfolio['Long'] = cotacao_response['Adj Close'].rolling(150).mean()

    monitorar_data_frame(portfolio)
    plot_frame(portfolio)
    # print(portfolio)


def plot_frame(data: pd.DataFrame):
    plt.figure(figsize=(20, 8))

    plt.plot(data['Adj Close'], label='Preco')
    plt.plot(data['Short'], label='Short')
    plt.plot(data['Long'], label='Long')

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


def analisar_data_frame(data: pd.DataFrame):
    dt_ini = datetime.today() - relativedelta(days=+91)
    for index, row in data.iterrows():
        if index >= dt_ini:
            preco_aproximando = row['Adj Close'] * 1.02
            if row['Short'] < preco_aproximando:
                print('O preco na data: ' + str(index) + ' esta proximo do ponto de compra')


main()
