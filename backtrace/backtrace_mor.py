import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

import TradeBook as excel_book
import my_algo as algo
import threading
from datetime import datetime, timedelta
import time
import Smart_API_Client as broker
from threading import Lock
from tracking import Mor
import sys

if len(sys.argv) != 2:
    print("Usage: python script.py <file path>")
    sys.exit(1)

file_path = sys.argv[1]

def main():
    # Define the path to the Excel file
 
    client = broker.smart_client(r'D:\Akash\Share Market\Algo\MyAlgo')
    # Load the book stock list
    book = excel_book.trade_book(file_path, "backtrace")
    book.empty_Sheet()
    short_term_periods = [2, 5, 8, 12, 15, 20]
    long_term_periods = [25, 30, 35, 40, 45]
    mor = Mor(short_term_periods, long_term_periods)
    #short_cluster = strategy([5], [8,13])
    count = 0
    for stock in book.stocks:
        count += 1
        print(f'{count}- ' + f'{stock}, ' +  f'Time - {datetime.now()}')
        #try:
        # Iterate backward in steps of days_to_jump
        current_date = datetime.now()
        end_date = current_date - timedelta(days=50)
        while current_date >= end_date:
            #print("Processing stock - ",stock)
            #print(datetime.now())
            current_stocks_data = client.get_historical_data(stock, "ONE_DAY", 200, current_date)
            if len(current_stocks_data) != 0:
                mor_dict = mor.indicator(current_stocks_data[stock]['candles'])
                phase = mor_dict["indicator"]
                if phase != "No Signal":
                    candles = current_stocks_data[stock]['candles']
                    current_date = getattr(candles[-((mor_dict["age"]) + 2)], 'time')
                    current_date = current_date.replace(tzinfo=None)
                    starting_date = getattr(candles[-(mor_dict["age"])], 'time')
                    starting_date = starting_date.replace(tzinfo=None)
                    start_price = getattr(candles[-(mor_dict["age"])], 'close')
                    print(f'\n{phase} phase' + f' for {mor_dict["age"]} days' + f' start on - {starting_date}' +f' start at - {start_price}\n')
                    entry_candle = candles[-(cluster_dict["age"])]
                    exit_candle = candles[-1]
                    if phase == "Bull" :
                        profit_loss = ((getattr(exit_candle, 'close') - getattr(entry_candle, 'close'))/getattr(entry_candle, 'close')) * 100
                    else:
                        profit_loss = ((getattr(entry_candle, 'close') - getattr(exit_candle, 'close'))/getattr(entry_candle, 'close')) * 100
                    book.update_backtrace_sheet(stock, phase, candles[-(mor_dict["age"])], candles[-1], mor_dict["age"], profit_loss)
                else:
                    print("Next stock")
                    asasa = 1
                    break
            else:
                print("Next stock")
                break
        #except:
        #    pass
    book.write_sheet()


if __name__ == "__main__":
    main()