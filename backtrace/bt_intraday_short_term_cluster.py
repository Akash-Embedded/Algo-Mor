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
    starting_date = getattr(candles[-((cluster_dict["age"])+1)], 'time')
    starting_date = starting_date.replace(tzinfo=None)
    start_price = getattr(candles[-((cluster_dict["age"])+1)], 'close')
    print(f'\n{phase} phase' + f' for {cluster_dict["age"]} days' + f' start on - {starting_date}' +f' start at - {start_price}\n')
    #print(f'price = ')
    entry_candle = candles[-((cluster_dict["age"])+1)]
    exit_candle = candles[-1]
    if phase == "Bull" :
        profit_loss = ((getattr(exit_candle, 'close') - getattr(entry_candle, 'close'))/getattr(entry_candle, 'close')) * 100
    else:
        profit_loss = ((getattr(entry_candle, 'close') - getattr(exit_candle, 'close'))/getattr(entry_candle, 'close')) * 100
    book.update_backtrace_sheet(stock, phase, entry_candle, exit_candle, cluster_dict["age"], profit_loss)

def is_daily_have_same_trend(cluster_dict, daily_candles):
    cluster_date = cluster_dict["time"].date()
    for candle in daily_candles:
        if candle.time.date() == cluster_date:
            if candle.EMA_5 > candle.EMA_13 and candle.EMA_5 > candle.EMA_21:
                return True
    return False

def main():
    # Define the path to the Excel file
    overall_periad = 1000

    client = broker.smart_client(r'D:\Akash\Share Market\Algo\MyAlgo')
    # Load the book stock list
    print (file_path)
    book = excel_book.trade_book(file_path, "backtrace")
    book.empty_Sheet()
    short_term_periods = [2, 5, 8, 12, 15, 20]
    long_term_periods = [25, 30, 35, 40, 45]
    mor = Mor(short_term_periods, long_term_periods)
    cluster = Mor([5], [13,21])
    count = 0

    for stock in book.stocks :
    #if True:
        #stock = "TRENT"
        count += 1 
        print(f'{count}- ' + f'{stock}, ' +  f'Time - {datetime.now()}')

        now = datetime.now()
        current_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        candles_count = 0
        day_stocks_data = client.get_historical_data(stock, "ONE_DAY", 2000, current_date, "indices")
        daily_candles = day_stocks_data[stock]['candles']

        while candles_count < overall_periad:
            current_stocks_data = client.get_historical_data(stock, "FIFTEEN_MINUTE", 2000, current_date, "indices")
            candles = current_stocks_data[stock]['candles']
            
            counts = len(candles)-1
            # now follow short term cluster till current mor trend
            while(counts > 200):
                cluster_dict = cluster.indicator(candles)
                if is_daily_have_same_trend(cluster_dict, daily_candles):
                    update_profit(stock, candles, cluster_dict, cluster_dict["indicator"], book)
                if(cluster_dict["age"] == 0):
                    cluster_dict["age"] = 1
                counts -= cluster_dict["age"]
                candles = candles[:counts]
                candles_count += cluster_dict["age"]
            current_date = candles[-1].time

    book.write_sheet()
    book.summerised_monthly_profit('entry_date', 'PL', 'name')


if __name__ == "__main__":
    main()