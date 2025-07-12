#import sys
#import os
#
#parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#sys.path.insert(0, parent_dir)
#
#import TradeBook as excel_book
#from datetime import datetime, timedelta
#import Smart_API_Client as broker
#from tracking import Mor
#import sys
#
#
#if len(sys.argv) != 2:
#    print("Usage: python script.py <file path>")
#    sys.exit(1)
#file_path = sys.argv[1]
#
#def main():
#    # Define the path to the Excel file
#    overall_periad = 500
#
#    client = broker.smart_client(r'D:\Akash\Share Market\Algo\MyAlgo')
#    # Load the book stock list
#    print (file_path)
#    book = excel_book.trade_book(file_path, "backtrace")
#    book.empty_Sheet()
#    short_term_periods = [2, 5, 8, 12, 15, 20]
#    long_term_periods = [25, 30, 35, 40, 45]
#    mor = Mor(short_term_periods, long_term_periods)
#    cluster = Mor([5], [13,21])
#    count = 0
#
#    for stock in book.stocks :
#        count += 1 
#        print(f'{count}- ' + f'{stock}, ' +  f'Time - {datetime.now()}')
#
#        now = datetime.now()
#        mor_current_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
#        mor_candles_count = 0
#
#        while mor_candles_count < overall_periad:
#
#            current_stocks_data = client.get_historical_data(stock, "ONE_DAY", 3000, mor_current_date) #"indices"
#
#            if len(current_stocks_data) and len(current_stocks_data[stock]['candles']) > 100:
#                mor_candles = current_stocks_data[stock]['candles']
#                mor_dict = mor.indicator(mor_candles)
#                mor_phase = mor_dict["indicator"]
#                
#                mor_candles_count += mor_dict["age"]
#                mor_start_index = len(mor_candles) - (mor_dict["age"]+1)
#                mor_end_index = len(mor_candles)
#
#                # first position start at mor and end at short term cluster reversal
#                cluster_dict = cluster.signal_end(mor_candles, mor_start_index, mor_dict["age"], mor_phase) #trade start
#                short_end_index = mor_start_index+cluster_dict["age"]
#                candles = mor_candles[0:short_end_index]
#                
#                entry_candle = candles[-((cluster_dict["age"])+1)]
#                exit_candle = candles[-1]
#                book.update_backtrace_sheet(stock, cluster_dict, entry_candle, exit_candle)
#
#                short_start_index = short_end_index
#                short_end_index = mor_end_index
#                # now follow short term cluster till current mor trend
#                while(short_start_index < short_end_index):
#                    candles = mor_candles[short_start_index: short_end_index]
#                    if len(candles) != 0:
#                        cluster_dict = cluster.indicator(candles)
#                        phase = cluster_dict["indicator"]
#                        if phase != "No Signal":
#                            short_end_index = short_end_index - (cluster_dict["age"]+1)
#                            if (cluster_dict["age"]) == 0: #bug age can't be zero, posistion will not close same day
#                                cluster_dict["age"]  = 1
#                                short_end_index -=1
#                            #if phase == mor_phase:
#                            if True:
#                                entry_candle = candles[-((cluster_dict["age"])+1)]
#                                exit_candle = candles[-1]
#                                book.update_backtrace_sheet(stock, cluster_dict, entry_candle, exit_candle)
#                            else:
#                                short_end_index -= 2
#                        else:
#                            short_end_index -= 2
#                    else:
#                        short_end_index -= 2
#                        break
#                mor_current_date = mor_dict["time"]
#                mor_current_date = mor_current_date - timedelta(days=1)
#                mor_current_date = mor_current_date.replace(tzinfo=None)
#            else:
#                print("Some issue", stock)
#                break
#            #except:
#            #    pass
#    book.write_sheet()
#    book.summerised_monthly_profit('entry_date', 'PL', 'name')
#
#
#if __name__ == "__main__":
#    main()
import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

import TradeBook as excel_book
from datetime import datetime, timedelta
import time
import Smart_API_Client as broker
from tracking import Mor
import sys

if len(sys.argv) != 2:
    print("Usage: python script.py <file path>")
    sys.exit(1)

file_path = sys.argv[1]

def main():
    overall_periad = 600
 
    client = broker.smart_client(r'D:\Akash\Share Market\Algo\MyAlgo')
    # Load the book stock list
    book = excel_book.trade_book(file_path, "backtrace")
    book.empty_Sheet()
    
    short_term_periods = [5, 8, 12, 15, 20]
    long_term_periods = [25, 30, 35, 40, 45]
    mor = Mor(short_term_periods, long_term_periods)


    short_term_periods = [5]
    long_term_periods = [13,21]
    short_cluster = Mor(short_term_periods, long_term_periods)

    count = 0
    for stock in book.stocks:
        count += 1
        print(f'{count}- ' + f'{stock}, ' +  f'Time - {datetime.now()}')

        now = datetime.now()
        current_date = now.replace(second=0, microsecond=0)
        candles_count = 0
        
        while candles_count < overall_periad:
            stocks_data = client.get_historical_data(stock, "ONE_DAY", 3000, current_date)
            if len(stocks_data) != 0:
                candles = stocks_data[stock]['candles']
                counts = len(candles)
                if(counts < 200):
                    break

                while(counts > 200):
                    mor_dict = mor.indicator(candles[0:counts])
                    if(mor_dict["age"] == 0):
                        mor_dict["age"] = 1
                    candles_count += mor_dict["age"]
                    entry_candle = candles[-(mor_dict["age"]+1)]
                    exit_candle = candles[-1]
                    book.update_backtrace_sheet(stock, mor_dict, entry_candle, exit_candle)
    
                    counts -= mor_dict["age"]
                    candles = candles[:counts+1]
                current_date = candles[-2].time
            else:
                break

    book.write_sheet()
    book.summerised_monthly_profit('entry_date', 'PL', 'name')

if __name__ == "__main__":
    main()