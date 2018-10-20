import datetime as dt
import pandas_datareader.data as web
import numpy as np
import math
import csv
import time
start_time = time.time()




class Stock(object):
    def __init__(self, ticker, name="Stock"):
        self.name = name
        self.ticker = ticker
        self.prices = None

    def __str__(self):
        return self.name, self.ticker

    def gen_prices(self, start, end):
        df = web.DataReader(self.ticker, "yahoo", start, end)
        self.prices = df

def trim(stock, market):
    stockarray = np.array([])
    marketarray = np.array([])
    date_list = [end - dt.timedelta(days=x) for x in range(time_period)]
    date_list = list(reversed(date_list))
    for date in date_list:
        try:
            if market.prices.ix[date.strftime("%Y-%m-%d")].ix["Close"]:
                if stock.prices.ix[date.strftime("%Y-%m-%d")].ix["Close"]:
                    marketarray = np.append(marketarray,(market.prices.ix[date.strftime("%Y-%m-%d")].ix["Close"],) )
                    stockarray = np.append(stockarray, (stock.prices.ix[date.strftime("%Y-%m-%d")].ix["Close"],) )
        except KeyError:
            pass
    return (stockarray, marketarray)


def standardize(stock):
    return list(map(lambda i: 0 if stock[i + 1] == 0 else (stock[i + 1] - stock[i]) / (stock[i]) * 100, range(len(stock) - 1)))

def covar(A, B):
    if len(A) == 0:
        return 0
    else:
        return np.cov(A, B)[0][1] * (len(A) - 1) / len(A)


def var(A):
    return np.var(A)


def beta(Stock, Market):
    Stock = standardize(Stock)
    Market = standardize(Market)
    value = covar(Stock, Market) / var(Market)
    return value



def seperate(Market, Stock):
    BearMarket = list()
    BullMarket = list()
    BearStock = list()
    BullStock = list()
    Market = standardize(Market)
    Stock = standardize(Stock)
    for i in range(len(Market)):
        if Market[i] >= 0:
            BullMarket.append(Market[i])
            BullStock.append(Stock[i])
        else:
            BearMarket.append(Market[i])
            BearStock.append(Stock[i])
    return [BearMarket, BullMarket, BearStock, BullStock]


def stratBetaCalc(BearMarket, BullMarket, BearStock, BullStock):
    BetaBear = covar(BearMarket, BearStock) / var(BearMarket)
    BetaBull = covar(BullMarket, BullStock) / var(BullMarket)
    return [BetaBull, BetaBear]


def stratBeta(Stock, Market):
    BetaList = seperate(Market, Stock)
    return stratBetaCalc(BetaList[0], BetaList[1], BetaList[2], BetaList[3])


def lineFinder(Point1, Point2):
    slope = (Point2[1] - Point1[1]) / (Point2[0] - Point1[0])
    intercept = Point1[1] - slope * Point1[0]
    return [slope, intercept]


def residualArray(xaxis, Line, Pricelist):
    residualArray = []
    for i in range(0, len(Pricelist)):
        residualArray.append(Pricelist[i] - (Line[0] * xaxis[i] + Line[1]))
    return residualArray


def volatilityFinder(PriceList):
    xaxis = []
    for i in range(0, len(PriceList)):
        xaxis.append(i)
    Line = lineFinder([xaxis[0], PriceList[0]], [xaxis[len(xaxis) - 1], PriceList[len(PriceList) - 1]])
    ResidArray = residualArray(xaxis, Line, PriceList)
    return math.sqrt(var(ResidArray))


def directionFinder(Pricelist):
    if Pricelist[len(Pricelist) - 1] < Pricelist[0]:
        if Pricelist[len(Pricelist) - 1] == 0:
            return 0
        else:
            return str(
                round(100 * (Pricelist[0] - Pricelist[len(Pricelist) - 1]) / (Pricelist[len(Pricelist) - 1]), 2)) + '%'
    elif Pricelist[len(Pricelist) - 1] > Pricelist[0]:
        if Pricelist[len(Pricelist) - 1] == 0:
            return 0
        else:
            str(round(100 * (Pricelist[0] - Pricelist[len(Pricelist) - 1]) / (Pricelist[len(Pricelist) - 1]), 2)) + '%'
    else:
        return 0


def StockStat(StockName, Stock, Market):
        Stock, Market = trim(Stock, Market)
        StockS = standardize(Stock)
        MarketS = standardize(Market)
        StratList = stratBeta(Stock, Market)
        BetaDirList = stratBeta(Stock, Market)
        ReturnsMeanData = seperate(Market, Stock)
        StockInfo = {
                        'Stock': StockName,
                        'Start Price': Stock[0],
                        'Finish Price': Stock[-1],
                        'Period High':max(Stock) ,
                        'Period Low': min(Stock),
                        'Gain/Loss %': str((Stock[-1] - Stock[0]) * 100 / (Stock[0])) + "%",
                        'Price Mean': round(sum(Stock) / len(Stock), 2),
                        'Price SD': volatilityFinder(Stock),
                        'Vol %': volatilityFinder(Stock) / round(sum(Stock) / len(Stock), 2) * 100,
                        'Beta': beta(Stock, Market),
                        'Beta-Bull': BetaDirList[0],
                        'Beta-Bear':BetaDirList[1],
                        'Market Correlation': covar(StockS, MarketS) / (math.sqrt(var(StockS) * var(MarketS))),
                        'Average Daily Return': sum(StockS) / len(StockS),
                        'Returns Bull': sum(ReturnsMeanData[3]) / len(ReturnsMeanData[3]),
                        'Returns Bear': sum(ReturnsMeanData[2]) / len(ReturnsMeanData[2]),
            }

        return list(StockInfo.values()) #Dicts maintian correct order in python 3.6 lol very bad but i'm lazy




if __name__ == "__main__":
    time_period = int(input("How many days do you want data for:"))
    start = dt.datetime.now() - dt.timedelta(days=time_period)
    start -= dt.timedelta(days=int(start.strftime("%d")))
    end = dt.datetime.now()
    for i in range(5):
        try:
            Market = Stock("^GSPC")
            Market.gen_prices(start, end)
            break
        except Exception:
            Market = Stock("^GSPC")
            Market.gen_prices(start, end)
            break

    with open(f"stockDataFor{time_period}Days.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(
                ['Stock', 'Start Price ', 'Finish Price', 'Period High', 'Period Low', 'Gain/Loss %', 'Price Mean',
                 'Price SD',
                 'Vol %', 'Beta', 'Beta-Bull', 'Beta-Bear', 'Market Correlation', 'Average Daily Return',
                 'Returns Bull',
                 'Returns Bear'])

        writer.writerow(StockStat("Market", Market, Market))
        stocks_loaded = 0
        stocks_failed = 0
        stocks = list()
        with open("tickersTest.csv", "r") as tickers:
            date = dt.datetime.utcnow().strftime("%b-%d-%Y")
            for line in tickers.readlines():
                for i in range(2):
                    try:
                        start2 = time.time()
                        stock = Stock(line.split(",")[0], line.split(",")[0])
                        stock.gen_prices(start, end)
                        writer.writerow(StockStat(stock.ticker,stock, Market))
                        print("%s seconds for %s --" % ((time.time() - start2), stock.ticker), end=" ")
                        stocks_loaded += 1
                        print("Stocks Loaded:%d" % stocks_loaded)
                        break
                    except Exception:
                        print("Trying to get %s again... for the %d th time" % (stock.ticker, i))
                        if i == 1:
                            print("Couldn't Load %s from Google Finance" % stock.ticker)
                            print()
                            stocks_failed += 1

    print()
    print("--- %s seconds total for program---" % (time.time() - start_time))
    print("Stocks loaded total %s" % stocks_loaded)
    print("Stocks failed total %s" % stocks_failed)





