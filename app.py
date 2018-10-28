import numpy as np
import matplotlib.pyplot as plt
from pandas_datareader import data
import pandas as pd
from datetime import datetime, timedelta
from mpl_finance import candlestick_ohlc
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import tweepy
import time
# Twitter API Keys
# from config import (consumer_key,
#             consumer_secret,
#             access_token,
#             access_token_secret)

# Setup Tweepy API Authentication
consumer_key = os.environ.get("consumer_key")
consumer_secret = os.environ.get("consumer_secret")
access_token = os.environ.get("access_token")
access_token_secret = os.environ.get("access_token_secret")

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())


def get_stock_graph():
    user = []
    store_handle = []
    search_counter = 0
    user_counter = 0


    #Report Current Time
    now = datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M")


    #Search for mention
    bot_reference = "@stock_bot Analyze:"
    mention = api.search(bot_reference)

    for tweet in mention["statuses"]:
        parse_info = tweet["text"].split("Analyze:")
        if parse_info[1] not in store_handle:
            store_handle.append(parse_info[1])
            user.append(tweet["user"]["screen_name"])
            search_counter +=1

    today = datetime.today().strftime('%Y-%m-%d')
    three_year = (datetime.now() - timedelta(days=3*365)).strftime('%Y-%m-%d')

    #Daily Data
    ticker = store_handle[0]

    # User pandas_reader.data.DataReader to load the desired data. As simple as that.

    # for ticker in tickers:
    panel_data = data.DataReader(ticker, 'iex', three_year, today)
    panel_data["Ticker"] = ticker
    panel_data["Moving Average"] = panel_data["close"].rolling(window=5).mean()
    panel_data["Date"]=panel_data.index
    panel_data["Date"]=pd.to_datetime(panel_data["Date"])
    panel_data["Date"] = panel_data["Date"].apply(mdates.date2num)

    ohlc= panel_data[['Date', 'open', 'high', 'low','close']].copy()

    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.2)

    candlestick_ohlc(ax, ohlc.values, width=.6, colorup='green', colordown='red')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))


    fig.autofmt_xdate()
    fig.tight_layout()
    plt.grid()
    plt.savefig(f"Pics/{ticker} candlestick for {today}.png")
    plt.show()
    api.update_with_media(f"Pics/{ticker} candlestick for {today}.png",f"@{user[0]}, see your results for {ticker}!" )

# Have the Twitter bot update once a day for a week
days = 0
while days < 7:
    print("Updating Twitter")

    # Update the twitter
    get_stock_graph()

    # Wait a day
    time.sleep(300)

    # Update day counter
    days += 1
