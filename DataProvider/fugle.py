from fugle_realtime import intraday
import matplotlib.pyplot as plt
import io
class realTimeProvider:
    def __init__(self, apiToken):
        self.apiToken = apiToken

    def getStockInfo(self, id):
        ret = dict()
        output = intraday.trades(apiToken=self.apiToken,
                                 output="dataframe", symbolId=id)
        output_meta = intraday.meta(
            apiToken=self.apiToken, output="dataframe", symbolId=id)
        output_chart = intraday.chart(
            apiToken=self.apiToken, output="dataframe", symbolId=id)
        graph=output_chart.plot(x="at",y='open')
        fig = graph.get_figure()
        buf=io.BytesIO()
        fig.savefig(buf,format='png')
        # plt.show()
        # except:
        # print("Get Data Error")
        # raise Exception("Get Data Error")
        ret['Name'] = output_meta.iloc[0,
                                       output_meta.columns.get_loc("nameZhTw")]
        ret['RealPrice'] = str(
            output.iloc[-1, output.columns.get_loc("price")])
        ret['ID'] = id
        ret['photo']=buf
        return ret


if __name__ == '__main__':
    import os
    TOKEN_FUGLE = os.getenv("TOKEN_FUGLE")
    rtProvider = realTimeProvider(TOKEN_FUGLE)
    ret = rtProvider.getStockInfo(2454)
    print(ret)
