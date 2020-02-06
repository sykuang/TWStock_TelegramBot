import yfinance as yf
class historyProvider:
    def getMA(self,symbolId,days="1mo"):
        symbolId=symbolId+".TW"
        stock=yf.Ticker(symbolId)
        hist=stock.history(period=days)
        return round(sum([int(data) for data in hist["Close"]])/len(hist["Close"]),2)

if __name__ == '__main__':
    hp=historyProvider()
    ma=hp.getMA("2454","1mo")
    print(ma)
