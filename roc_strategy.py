import os
import alpaca_trade_api as tradeapi
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def pairs_trading_algo(self):
    os.environ['APCA_API_BASE_URL'] = 'https://paper-api.alpaca.markets'

    api = tradeapi.REST('API_KEY', 'API_SECRET', api_version='v2')
    account = api.get_account()

    sender_address = 'tradingbot691@gmail.com'
    sender_password = "PASSWORD"
    receiver_address = "tradingbot691@gmail.com"

    message = MIMEMultipart()
    message["From"] = 'Trading Bot'
    message['To'] = receiver_address
    message['Subject'] = 'Pairs Trading Algo'

    # selection of stocks to choose from
    days = 1000
    stock1 = 'ADBE'
    stock2 = 'AAPL'

    # Get historical data for a stock
    stock1_barset = api.get_barset(stock1, 'day', limit=days)
    stock2_barset = api.get_barset(stock2, 'day', limit=days)
    stock1_bars = stock1_barset[stock1]
    stock2_bars = stock2_barset[stock2]

    data_1 = []
    times_1 = []
    for i in range(days):
        stock1_close = stock1_bars[i].c
        stock1_time = stock1_bars[i].t

        data_1.append(stock1_close)
        times_1.append(stock1_time)

    data_2 = []
    times_2 = []
    for i in range(days):
        stock2_close = stock2_bars[i].c
        stock2_time = stock2_bars[i].t

        data_2.append(stock2_close)
        times_2.append(stock2_time)

        hist_close = pd.DataFrame(data_1, columns=[stock1])
        hist_close[stock2] = data_2
