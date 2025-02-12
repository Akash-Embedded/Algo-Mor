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

def main():
    # Define the path to the Excel file
    overall_periad = 10000

    client = broker.smart_client(r'D:\Akash\Share Market\Algo\MyAlgo')
    # Load the book stock list
    print (file_path)
    book = excel_book.trade_book(file_path, "moves")
    book.empty_Sheet()

    count = 0
    #for stock in book.stocks :
    if True:
        stock = "India VIX"
        count += 1 
        print(f'{count}- ' + f'{stock}, ' +  f'Time - {datetime.now()}')

        now = datetime.now()
        current_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        candles_count = 0

        while candles_count < overall_periad:
            current_stocks_data = client.get_historical_data(stock, "ONE_DAY", 2000, current_date, "indices")
                
            if len(current_stocks_data):
                book.calculate_monthly_ohlc(current_stocks_data[stock]['candles'], stock)
                #book.calculate_weekly_ohlc(current_stocks_data[stock]['candles'], stock)
                current_date = current_date - timedelta(days=2000)
                current_date = current_date.replace(tzinfo=None)
            else:
                print("Some issue", stock)
                break
            candles_count += 2000
    book.write_sheet()

if __name__ == "__main__":
    main()