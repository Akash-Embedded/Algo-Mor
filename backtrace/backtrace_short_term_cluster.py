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

def main():
    # Define the path to the Excel file
    overall_periad = 900

    client = broker.smart_client(r'D:\Akash\Share Market\Algo\MyAlgo')
    # Load the book stock list
    print (file_path)
    book = excel_book.trade_book(file_path, "backtrace")
    book.empty_backtrace_Sheet()
    short_term_periods = [2, 5, 8, 12, 15, 20]
    long_term_periods = [25, 30, 35, 40, 45]
    mor = Mor(short_term_periods, long_term_periods)
    cluster = Mor([5], [13,21])
    count = 0
    for stock in book.stocks:
    #if True:
    #    stock = "TRENT"
        count += 1
        print(f'{count}- ' + f'{stock}, ' +  f'Time - {datetime.now()}')

        now = datetime.now()

        # Replace the time part with midnight (00:00:00)
        mor_current_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

        outer_end_date = mor_current_date - timedelta(days=overall_periad)

        while mor_current_date >= outer_end_date:
            
            # search for mor indicator trend 
            current_stocks_data = client.get_historical_data(stock, "ONE_DAY", 1000, mor_current_date)
            if len(current_stocks_data):
                mor_candles = current_stocks_data[stock]['candles']
                mor_dict = mor.indicator(current_stocks_data[stock]['candles'])
                mor_phase = mor_dict["indicator"]
                mor_candles = current_stocks_data[stock]['candles']
                index = len(mor_candles) - mor_dict["age"]

                # first position start at mor and end at short term cluster reversal
                cluster_dict = cluster.signal_end(current_stocks_data[stock]['candles'], index, mor_dict["age"], mor_phase) #trade start
                candles = current_stocks_data[stock]['candles'][0:(index+cluster_dict["age"])]
                current_date = getattr(candles[-1], 'time')
                current_date = current_date.replace(tzinfo=None)
                update_profit(stock, candles, cluster_dict, mor_phase, book)
            
                cluster_current_date = mor_current_date
                cluster_end_date = current_date
                # now follow short term cluster till current mor trend
                while(cluster_end_date < cluster_current_date):
                    #print("Processing stock - ",stock)
                    #print(datetime.now())
                    current_stocks_data = client.get_historical_data(stock, "ONE_DAY", 200, cluster_current_date)
                    if len(current_stocks_data) != 0:
                        cluster_dict = cluster.indicator(current_stocks_data[stock]['candles'])
                        phase = cluster_dict["indicator"]
                        if phase != "No Signal":
                            candles = current_stocks_data[stock]['candles']
                            cluster_current_date = getattr(candles[-((cluster_dict["age"]) + 2)], 'time')
                            cluster_current_date = cluster_current_date.replace(tzinfo=None)
                            if (cluster_dict["age"]) == 0: #bug age can't be zero, posistion will not close same day
                                cluster_dict["age"]  = 1
                                cluster_current_date = cluster_current_date - timedelta(days=1)
                            if phase == mor_phase:
                                update_profit(stock, candles, cluster_dict, phase, book)
                            else:
                                print("Next stock")
                                cluster_current_date = cluster_current_date - timedelta(days=2)
                    else:
                        print("Next stock")
                        cluster_current_date = cluster_current_date - timedelta(days=5)
                        break
                mor_current_date = mor_dict["time"]
                mor_current_date = mor_current_date - timedelta(days=1)
                mor_current_date = mor_current_date.replace(tzinfo=None)
            else:
                print("Some issue", stock)
                break
            #except:
            #    pass
    book.write_sheet()
    book.summerised_monthly_profit('entry_date', 'PL', 'name')


if __name__ == "__main__":
    main()