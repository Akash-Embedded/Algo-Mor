import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

import TradeBook as excel_book
from datetime import datetime
import time
import Smart_API_Client as broker
from logzero import logger


if len(sys.argv) != 2:
    print("Usage: python script.py <file path>")
    sys.exit(1)
file_path = sys.argv[1]

correlation_id = "stream_1"
action = 1
mode = 3
token_list = [
    {
        "exchangeType": 1,
        "tokens": ["26009"]
    }
]
client = broker.smart_client(r'D:\Akash\Share Market\Algo\MyAlgo')
print("client created")
#sws = client.create_web_socket()
#print("socket created")

def on_data(wsapp, message):
    logger.info("Ticks: {}".format(message))
    print(message)
    # close_connection()

def on_open(wsapp):
    logger.info("on open")
    print("on open")
    sws.subscribe(correlation_id, mode, token_list)
    # sws.unsubscribe(correlation_id, mode, token_list1)


def on_error(wsapp, error):
    print("on error")
    logger.error(error)


def on_close(wsapp):
    print("on close")
    logger.info("Close")



def close_connection():
    sws.close_connection()


def main():
    positions = {}
    number_of_position = 0
    # Define the path to the Excel file
    # Assign the callbacks.
#    sws.on_open = on_open
#    sws.on_data = on_data
#    sws.on_error = on_error
#    sws.on_close = on_close
#
#    sws.connect()
    orderResponse = client.place_order("HDFCBANK", "BUY", 1, "INTRADAY")
    if(orderResponse  == None)
        print("No Order ID")
    else:
        positions[number_of_position]["order_id"] = orderResponse
        positions[number_of_position]["stock"] = "HDFCBANK"
        positions[number_of_position]["quantity"] = 1

        
        

#    # Load the book stock list
#    book = excel_book.trade_book(file_path, "indicators")
#
#    for stock in book.stocks:
#        #try:
#        if True:
#            count += 1
#            print(f'{count}- ' + f'{stock}, ' +  f'Time - {datetime.now()}')
#            current_stocks_data = client.get_historical_data(stock, "ONE_DAY", 650)
#            if current_stocks_data != {}:
#                mor_dict = mor.indicator(current_stocks_data[stock]['candles'])
#                short_dict= cluster.indicator(current_stocks_data[stock]['candles'])
#                book.update_indicators_sheet(current_stocks_data[stock]['candles'], file_path, stock, mor_dict, short_dict)
#        #except:
#        #    pass
#    book.write_sheet()


if __name__ == "__main__":
    main()