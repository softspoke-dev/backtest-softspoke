from v20 import Context
from v20.instrument import Candlestick, CandlestickData
from CandlestickDataAdvanced import CandlestickAdvanced
from redis import Redis
from renko import Renko
from json import loads
from CandlestickDataAdvanced import CandlestickAdvanced

if __name__ == '__main__':
    redis = Redis(host='localhost', port=6379, db=0)
    renko = Renko()

    oanda_context = Context("api-fxpractice.oanda.com",
                            token="5952c019ff679e3bd52cacc82a1599ab-6469870a2ec126764f162fafc5e36be5")
    hist = oanda_context.pricing.candles("101-004-5674482-001", "EUR_USD", price="M", granularity="M15", count=5000)

    for candle in hist.body['candles']:
        renko.feed(candle.mid.c)

    sub = redis.pubsub()
    sub.psubscribe('ticks.EUR_USD')

    candlestick_data_advanced = CandlestickAdvanced("M15")
    for message in sub.listen():
        if message is not None and isinstance(message, dict):
            if message.get('data') != 1:
                data = loads(message.get('data').decode('utf-8'))
                candle = Candlestick(
                    mid=CandlestickData(c=data['mid']),
                    bid=CandlestickData(c=data['bid']),
                    ask=CandlestickData(c=data['ask']),
                    time=data['time']
                )
                candlestick_data_advanced.feed(candle)
                print(message.get('data'))
