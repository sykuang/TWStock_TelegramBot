import yfinance as yf
import io


class yahoo:
    def getMA(self, symbolId, days="1mo"):
        symbolId = symbolId+".TW"
        stock = yf.Ticker(symbolId)
        hist = stock.history(period=days)
        return round(sum([int(data) for data in hist["Close"]])/len(hist["Close"]), 2)

    def getHistory(self, symbolId, days="1d"):
        symbolId = symbolId+".TW"
        stock = yf.Ticker(symbolId)
        if days != "1d":
            hist = stock.history(period=days)
        else:
            hist = stock.history(period="1d", interval="1m")
        return hist

    def getTodayPrice(self, symbolId):
        data = self.getHistory(symbolId)
        symbolId_tw = symbolId+".TW"
        stock = yf.Ticker(symbolId_tw)
        PreClose = stock.info["previousClose"]
        current_price = data.iloc[-1, data.columns.get_loc("High")]
        if PreClose > current_price:
            graph = data.plot(y='High', color='green')
        elif PreClose == current_price:
            graph = data.plot(y='High', color='gray')
        else:
            graph = data.plot(y='High', color='red')

        graph.axhline(PreClose, linestyle='dashed',
                      color='xkcd:dark grey', alpha=0.6, label='參考價', marker='')
        graph.legend().set_visible(False)
        fig = graph.get_figure()
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        ret = dict()
        ret['Name'] = stock.info["shortName"]
        ret['RealPrice'] = current_price
        ret['ID'] = symbolId
        ret['photo'] = buf
        return ret


if __name__ == '__main__':
    hp = yahoo()
    # ma = hp.getMA("2454", "1mo")
    # print(ma)
    # hist = hp.getHistory("2454")
    # print(hist)
    hp.getTodayPrice("2454")
