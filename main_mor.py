import TradeBook as excel_book
import my_algo as algo
import threading
from datetime import datetime
import time
import Smart_API_Client as broker
from threading import Lock
from tracking import Mor


#file_path = "TradeBook_Nifty20_Indicator.xlsx"  # Replace with the actual path to your file
file_path = "TradeBook_Indicator.xlsx"  # Replace with the actual path to your file

age_of_mor = 10
def main():
    # Define the path to the Excel file
 
    client = broker.smart_client(r'D:\Akash\Share Market\Algo\MyAlgo')
    # Load the book stock list
    book = excel_book.trade_book(file_path, "indicators")
    short_term_periods = [2, 5, 8, 12, 15, 20]
    long_term_periods = [25, 30, 35, 40, 45]
    mor = Mor(short_term_periods, long_term_periods)
    #short_cluster = strategy([5], [8,13])

    for stock in book.stocks:
        #try:
        if True:
            print("Processing stock - ",stock)
            print(datetime.now())
            current_stocks_data = client.get_historical_data(stock, "ONE_DAY", 350)
            if current_stocks_data != {}:
                mor_dict = mor.indicator(current_stocks_data[stock]['candles'])
                #short_dict= short_cluster.indicator(current_stocks_data[stock]['candles'])
                short_dict = {}
                book.update_indicators_sheet(current_stocks_data[stock]['candles'], file_path, stock, mor_dict, short_dict)
        #except:
        #    pass
    book.write_sheet()


if __name__ == "__main__":
    main()