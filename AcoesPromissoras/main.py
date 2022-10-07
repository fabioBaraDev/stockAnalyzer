from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as y
from dateutil.relativedelta import relativedelta

import AcoesPromissoras.acoes as acoes


def melhoresAcoesPorMedia():
    ticker = acoes.get_ativos_da_bolsa()

    cotacao = y.download(ticker, getDateWith6MonthsAgo(), getFormatedCurrentDate())['Adj Close']
    ativo = getRetornoDoAtivoPorDMenosUmEmArrayDeAtivos(cotacao)
    media = ativo.median()
    melhoresMedias = media.sort_values(ascending=False).head()

    ativosFiltradosPorMedias = ativo[melhoresMedias.index]

    print(ativosFiltradosPorMedias)
    plot_frame(ativosFiltradosPorMedias)


def getFormatedCurrentDate():
    return datetime.today().strftime('%Y-%m-%d')


def getDateWith6MonthsAgo():
    date = datetime.today() - relativedelta(months=+6)
    return date.strftime('%Y-%m-%d')


def getVolatilidade(data: pd.DataFrame):
    return data.std()


def main():
    ticker = ['MGLU3.SA', 'BBDC4.SA', 'CASH3.SA', '^BVSP', 'BBAS3.SA', 'GOLL4.SA', 'A2MC34.SA']
    start = '2022-01-03'
    end = '2022-12-07'

    cotacao = y.download(ticker, getDateWith6MonthsAgo(), getFormatedCurrentDate())['Adj Close']
    ativo = getRetornoDoAtivoPorDMenosUmEmArrayDeAtivos(cotacao)
    print(ativo.median())
    plot_frame(ativo)

    # getRetornoDoAtivoPorDMenosUm
    # cotacao.pct_change()

    # ativo = set_retorno_simples(cotacao)
    # # plotFrame(getRetornoDoAtivoPorDMenosUm(ativo))
    # ativo = set_retorno_acumulado_percentual(ativo)
    # print(ativo)
    # plot_frame(ativo)
    # print()


def getRetornoDoAtivoPorDMenosUmEmArrayDeAtivos(data: pd.DataFrame):
    res = data.pct_change() * 100
    res.dropna(axis=0, inplace=True)
    return res


def set_retorno_acumulado_percentual(data: pd.DataFrame):
    data['RetornoAc'] = get_retorno_acumulado_percentual(data)
    return data


def get_retorno_acumulado_percentual(data: pd.DataFrame):
    return (((1 + data['Adj Close'].pct_change()).cumprod()) - 1) * 100


def set_retorno_simples(ticker):
    ativo = pd.DataFrame(ticker['Adj Close'])
    ativo['RetornoSimples'] = get_retorno_do_ativo_por_d_menos_um(ativo)
    ativo.dropna(axis=0, inplace=True)
    return ativo


def get_retorno_do_ativo_por_d_menos_um(data: pd.DataFrame):
    return data['Adj Close'].pct_change()
    # return (data['Adj Close'] / data['Adj Close'].shift(1)) - 1


def plot_frame(data: pd.DataFrame):
    plt.figure(figsize=(20, 8))
    plt.boxplot(data, labels=data.columns)
    plt.grid()
    plt.show()


main2()
