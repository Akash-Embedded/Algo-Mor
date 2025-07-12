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
    
    short_term_periods = [2, 5, 8, 12, 15, 20]
    long_term_periods = [25, 30, 35, 40, 45]
    mor = Mor(short_term_periods, long_term_periods)

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

if __name__ == "__main__":
    main()