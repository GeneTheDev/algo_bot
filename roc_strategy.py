import os
import alpaca_trade_api as tradeapi
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def trading_algo(self):
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

        # Current spread between the two stocks
        stock1_curr = data_1[days-1]
        stock2_curr = data_2[days-1]
        spread_curr = (stock1_curr-stock2_curr)

        move_avg_days = 5

        stock1_last = []
        for i in range(move_avg_days):
            stock1_last.append(data_1[(days-1)-i])

        stock1_hist = pd.DataFrame(stock1_last)

        stock1_mavg = stock1_hist.mean()

        stock2_last = []
        for i in range(move_avg_days):
            stock2_last.append(data_2[(days-1)-i])
        stock2_hist = pd.DataFrame(stock2_last)
        stock2_mavg = stock2_hist.mean()

        spread_avg = min(stock1_mavg - stock2_mavg)

        spreadFactor = .01
        wideSpread = spread_avg*(1+spreadFactor)
        thinSpread = spread_avg*(1-spreadFactor)

        # Calculate  shares to trade
        cash = float(account.buying_power)
        limit_stock1 = cash//stock1_curr
        limit_stock2 = cash//stock2_curr
        number_of_shares = int(min(limit_stock1, limit_stock2)/2)

        # Trading algorithim
        portfolio = api.get.list_positions()
        clock = api.get_clock()

        if clock.is_open == True:
            if bool(portfolio) == False:
                # detect a wide spread
                if spread_curr > wideSpread:
                    # short top stock
                    api.submit_order(symbol=stock1, qty=number_of_shares,
                                     side='sell', type='market', time_in_force='day')

                    # long bottom stock
                    api.submit_order(symbol=stock2, qty=number_of_shares,
                                     side='buy', type='market', time_in_force='day')
                    mail_content = "Trades have been made, short top stock and long bottom stock"

                # detect a tight spread
                elif spread_curr < thinSpread:
                    # long top stock
                    api.submit_order(symbol=stock1, qty=number_of_shares,
                                     side='buy', type='market', time_in_force='day')

                    # short bottom stock
                    api.submit_order(symbol=stock2, qty=number_of_shares,
                                     side='sell', type='market', time_in_force='day')
                    mail_content = "Trades have been made, long top stock and short bottom stock"
            else:
                wideTradeSpread = spread_avg * (1+spreadFactor + .03)
                thinTradeSpread = spread_avg * (1+spreadFactor - .03)
                if spread_curr <= wideTradeSpread and spread_curr >= thinTradeSpread:
                    api.close_position(stock1)
                    api.close_position(stock2)
                    mail_content = "Positions has been closed"
                else:
                    mail_content = "No trades were made, position remains open"
                    pass
        else:
            mail_content = "The Market Is Closed"

        message.attach(MIMEText(mail_content, 'plain'))

        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()

        session.login(sender_address, sender_password)
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()

        done = 'Mail Sent'

        return done
