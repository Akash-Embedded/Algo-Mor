import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

import TradeBook as excel_book
from datetime import datetime
import Smart_API_Client as broker
from tracking import Mor

if len(sys.argv) != 2:
    print("Usage: python script.py <file path>")
    sys.exit(1)
file_path = sys.argv[1]

def main():

    # Path for credential.txt as argument
    client = broker.smart_client(r'D:\Akash\Share Market\Algo\MyAlgo')

    # Load the book stock list
    book = excel_book.trade_book(file_path, "indicators")

    short_term_periods = [2, 5, 8, 12, 15, 20]
    long_term_periods = [25, 30, 35, 40, 45]
    mor = Mor(short_term_periods, long_term_periods)
    cluster = Mor([5], [8,13])
    
    count = 0
    for stock in book.stocks:
        #try:
        if True:
            count += 1
            print(f'{count}- ' + f'{stock}, ' +  f'Time - {datetime.now()}')
            current_stocks_data = client.get_historical_data(stock, "ONE_DAY", 650)
            if current_stocks_data != {}:
                mor_dict = mor.indicator(current_stocks_data[stock]['candles'])
                short_dict= cluster.indicator(current_stocks_data[stock]['candles'])
                book.update_indicators_sheet(current_stocks_data[stock]['candles'], file_path, stock, mor_dict, short_dict)
        #except:
        #    pass
    book.write_sheet()
if __name__ == "__main__":
    main()