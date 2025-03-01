import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

import TradeBook as excel_book
import my_algo as algo
import threading
from datetime import datetime, timedelta, time
import time as tim
import time
import Smart_API_Client as broker
from threading import Lock
from tracking import Mor
import sys


if len(sys.argv) != 2:
    print("Usage: python script.py <file path>")
    sys.exit(1)
file_path = sys.argv[1]


def update_profit(stock, candles, cluster_dict, phase, book):
    entry_candle = candles[-((cluster_dict["age"])+1)]
    exit_candle = candles[-(1 + cluster_dict["age"] - cluster_dict["age_as_per_rsi"])]

    starting_date = getattr(entry_candle, 'time')
    starting_date = starting_date.replace(tzinfo=None)
    start_price = getattr(entry_candle, 'close')
    print(f'\n{phase} phase' + f' for {cluster_dict["age"]} days' + f' start on - {starting_date}' +f' start at - {start_price}\n')
    #print(f'price = ')
    if phase == "Bull" :
        profit_loss = ((getattr(exit_candle, 'close') - getattr(entry_candle, 'close'))/getattr(entry_candle, 'close')) * 100
    else:
        profit_loss = ((getattr(entry_candle, 'close') - getattr(exit_candle, 'close'))/getattr(entry_candle, 'close')) * 100
    book.update_backtrace_sheet(stock, phase, entry_candle, exit_candle, cluster_dict["age"], profit_loss)


def is_daily_have_same_trend(cluster_dict, daily_candles,candles):
    cross = False

    if cluster_dict["indicator"] == "Bull":
        for i in range (0,3):
            if candles[-((cluster_dict["age"])+1+i)].rsi < 50:
                cross = True
    elif cluster_dict["indicator"] == "Bear":
        for i in range (0,3):
            if candles[-((cluster_dict["age"])+1+i)].rsi > 50:
                cross = True
    timecross = 0
    if cluster_dict["time"].hour < 10 or cluster_dict["time"].hour > 14:
        timecross = 1

    cluster_date = cluster_dict["time"].date()
    for candle in reversed(daily_candles):
        if candle.time.date() == cluster_date:
            if cluster_dict["indicator"] == "Bull":
                if candle.EMA_5 > candle.EMA_13 and candle.EMA_5 > candle.EMA_21:
#                 if   candle.rsi < 58 and candle.rsi > 42 and timecross == 1:
                    return True
            elif cluster_dict["indicator"] == "Bear":
                if candle.EMA_5 < candle.EMA_13 and candle.EMA_5 < candle.EMA_21:
#                if  candle.rsi > 42 and candle.rsi < 58 and timecross == 1:
                    return True
            return False
    return False

#def is_daily_have_same_trend(cluster_dict, daily_candles,candles):
#    cross = False
#
#    if cluster_dict["indicator"] == "Bull":
#        for i in range (0,3):
#            if candles[-((cluster_dict["age"])+1+i)].rsi < 50:
#                cross = True
#    elif cluster_dict["indicator"] == "Bear":
#        for i in range (0,3):
#            if candles[-((cluster_dict["age"])+1+i)].rsi > 50:
#                cross = True
#    timecross = 0
#    if cluster_dict["time"].hour < 10 or cluster_dict["time"].hour > 14:
#        timecross = 1
#
#    cluster_date = cluster_dict["time"].date()
#    for candle in reversed(daily_candles):
#        if candle.time.date() == cluster_date:
#            if cluster_dict["indicator"] == "Bull":
#                if candle.EMA_5 > candle.EMA_13 and candle.EMA_5 > candle.EMA_21:
#                    return True
#            elif cluster_dict["indicator"] == "Bear":
#                if candle.EMA_5 < candle.EMA_13 and candle.EMA_5 < candle.EMA_21 :
#                    return True
#            return False
#    return False

def main():
    # Define the path to the Excel file
    overall_periad = 9000

    client = broker.smart_client(r'D:\Akash\Share Market\Algo\MyAlgo')
    # Load the book stock list
    print (file_path)
    book = excel_book.trade_book(file_path, "backtrace")
    book.empty_Sheet()
    short_term_periods = [2, 5, 8, 12, 15, 20]
    long_term_periods = [25, 30, 35, 40, 45]
    mor = Mor(short_term_periods, long_term_periods)
    cluster = Mor([5], [13, 21])
    count = 0

    #best till now 10 minutes in daily trend
    for stock in book.stocks :
    #if True:
        #stock = "TRENT"
        count += 1 
        print(f'{count}- ' + f'{stock}, ' +  f'Time - {datetime.now()}')

        now = datetime.now()
        #now = datetime(2020, 1, 1)
        current_date = now.replace(second=0, microsecond=0)
        candles_count = 0
        day_stocks_data = client.get_historical_data(stock, "ONE_DAY", 3000, current_date, 'indices')
        daily_candles = day_stocks_data[stock]['candles']

        while candles_count < overall_periad:
            current_stocks_data = client.get_historical_data(stock, "FIFTEEN_MINUTE", 8000, current_date, 'indices')
            candles = current_stocks_data[stock]['candles']
            
            counts = len(candles)
            # now follow short term cluster till current mor trend
            while(counts > 200):
                cluster_dict = cluster.indicator(candles[0:counts], rsi=True)
                if is_daily_have_same_trend(cluster_dict, daily_candles, candles):
                    update_profit(stock, candles, cluster_dict, cluster_dict["indicator"], book)
                if(cluster_dict["age"] == 0):
                    cluster_dict["age"] = 1
                counts -= cluster_dict["age"]
                candles = candles[:counts+1]
                candles_count += cluster_dict["age"]
            current_date = candles[-2].time

    book.write_sheet()
    book.summerised_monthly_profit('entry_date', 'PL', 'name')

if __name__ == "__main__":
    main()