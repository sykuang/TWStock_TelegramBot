from fugle_realtime import intraday
import matplotlib.pyplot as plt
import io
class realTimeProvider:
    def __init__(self, apiToken):
        self.apiToken = apiToken

    def getStockInfo(self, id):
        ret = dict()
        output_meta = intraday.meta(
            apiToken=self.apiToken, output="dataframe", symbolId=id)
        output_chart = intraday.chart(
            apiToken=self.apiToken, output="dataframe", symbolId=id)
        ref_price=output_meta.iloc[0,
                                       output_meta.columns.get_loc("priceReference")]
        current_price=output_chart.iloc[-1, output_chart.columns.get_loc("close")]
        if ref_price>current_price:
            graph=output_chart.plot(x="at",y='close',color='green')
        elif ref_price==current_price:
            graph=output_chart.plot(x="at",y='close',color='gray')
        else:
            graph=output_chart.plot(x="at",y='close',color='red')
        graph.axhline(ref_price, linestyle='dashed', color='xkcd:dark grey', alpha=0.6, label='參考價', marker='')
        graph.legend().set_visible(False)
        fig = graph.get_figure()
        buf=io.BytesIO()
        fig.savefig(buf,format='png')
        ret['Name'] = output_meta.iloc[0,
                                       output_meta.columns.get_loc("nameZhTw")]
        ret['RealPrice'] = current_price
        ret['ID'] = id
        ret['photo']=buf
        return ret


if __name__ == '__main__':
    import os
    TOKEN_FUGLE = os.getenv("TOKEN_FUGLE")
    rtProvider = realTimeProvider(TOKEN_FUGLE)
    ret = rtProvider.getStockInfo(2454)
    print(ret)
