# -*- coding: utf-8 -*-
import os
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import talib as ta

from estrategia import get_estategia
from get_stock_configuration import get_stock_configuration


def run_buy_position():
    dt = pd.DataFrame(columns=['Adj Close', 'action', 'Stop_loss', 'Stock'])

    for row in get_stock_configuration().iterrows():
        stock_name = row[0][0]
        startDate = '2020-07-10'
        endDate = datetime.today().strftime('%Y-%m-%d')
        sht = int(row[0][1][0:2])
        lng = int(row[0][1][-2:])
        path = os.getcwd() + '/relatorios/' + datetime.today().strftime('%Y-%m-%d') + '/buy/'

        result = get_estategia(stock_name, startDate, endDate, sht, lng)

        if result.tail(1)['action'][0] == 'buy':

            plot_it(stock_name, startDate, endDate, sht, lng, path)
            result.to_csv(path + stock_name + ' - ' + str(sht) + ' - ' + str(lng) + '.csv', index=False)

            result['Stock'] = stock_name + ' - ' + str(sht) + ' - ' + str(lng)
            dt = dt.append(result, ignore_index=False, verify_integrity=False, sort=None)

    dt = dt.sort_index()

    # print the newest to cross the long avg
    print('** THE NEWEST TO CROSS THE LONG AVG **')
    print(dt.loc[str(dt.tail(1).index[0]):str(dt.tail(1).index[0])])


def plot_it(ticker, startDate, endDate, exp_sht, exp_lng, path):
    kc = yf.download(ticker, start=startDate, end=endDate)
    kc = calculate_RSI(kc)


    stocksac = kc['Adj Close']
    stocksac.head()
    stocksac.isna().sum()
    stocksac.interpolate(inplace=True)
    # Criando um novo dataframe com o retorno da função def que seta a quantidade de valores NaN

    # stocksac = stocksac[good_stocks(stocksac, 10)]

    kc['exp_Sht'] = stocksac.ewm(span=exp_sht).mean()
    # kc['exp_Lng'] = stocksac.ewm(span=exp_lng).mean()
    # kc['exp_Sht'] = stocksac.rolling(window=exp_sht).mean()
    kc['exp_Lng'] = stocksac.rolling(window=exp_lng).mean()

    kc.dropna(inplace=True)

    kc[['Adj Close', 'exp_Sht', 'exp_Lng']].plot()
    # kc['Volume'].plot(secondary_y=True, color='lightgray', title=ticker)
    kc['RSI'].plot(secondary_y=True, color='lightgray', title=ticker)

    plt.title = ticker
    plt.grid()

    plt.savefig(path + ticker + ' - ' + str(exp_sht) + ' - ' + str(exp_lng) + '.jpg')


def calculate_RSI(stocks: pd.DataFrame):
    stocks['RSI'] = ta.RSI(stocks['Adj Close'], timeperiod=14)

    return stocks


def main():
    path = os.getcwd() + '/relatorios'
    if not os.path.isdir(path):
        os.mkdir(path)
    path = path + '/' + datetime.today().strftime('%Y-%m-%d')
    if not os.path.isdir(path):
        os.mkdir(path)
    if not os.path.isdir(path + '/buy'):
        os.mkdir(path + '/buy')

    run_buy_position()
    # res = get_estategia('PRIO3.SA', '2020-07-10', datetime.today().strftime('%Y-%m-%d'), 10, 60)
    # print(res)
    # plot_it('PRIO3.SA', '2020-07-10', datetime.today().strftime('%Y-%m-%d'), 10, 60, path + '/buy/')
    #
    print("END")


main()
