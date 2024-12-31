import TradeBook as excel_book
import my_algo as algo
import threading
from datetime import datetime
import time
import Smart_API_Client as broker
from threading import Lock

def is_green(candles):
    for candle in candles[-3:]:
        if candle.close > candle.open:
            continue
        else:
            return False
    return True

def is_volumehigh(candles, volume_20_ma):
    last_three = candles[-1].volume + candles[-2].volume + candles[-3].volume 
    average = last_three / 3
    if(average > (volume_20_ma *2)):
        return True
    else:
        return False

#file_path = "TradeBook_Nifty20.xlsx"  # Replace with the actual path to your file
file_path = "TradeBook.xlsx"  # Replace with the actual path to your file
# Function for tracking thread
def tracking_thread(smart_api_lock, excel_sheet_lock, history_stocks_data, client: broker.smart_client, book: excel_book.trade_book):
    #while True:
    if True:
        for stock_data in history_stocks_data:
            try:
                # Program here
                smart_api_lock.acquire()
                current_stocks_data = client.get_historical_data(stock_data.name, "ONE_DAY", 5)
                smart_api_lock.release()
                history_candle = stock_data.history[stock_data.name]['candles'][-2]
                current_candle = current_stocks_data[stock_data.name]['candles'][-1]
                if current_candle.volume > history_candle.volume_20_ma :
                    price_diff_percentage = ((current_candle.close - history_candle.close )/history_candle.close)* 100
                    if price_diff_percentage > 1 :
                        excel_sheet_lock.acquire()
                        book.write_high_volume_stock(current_candle, file_path, "volume", stock_data.name, history_candle.volume_20_ma, price_diff_percentage)
                        excel_sheet_lock.release()
                        print("high volume", stock_data.name)
                        print(current_candle.time)
                        print(current_candle.volume)
                        print(history_candle.volume_20_ma)
            except: 
                print("Some error")
                pass
# Function for the high-priority thread
def trading_thread(smart_api_lock, excel_sheet_lock, history_stocks_data, client: broker.smart_client, book: excel_book.trade_book):
    while True:
        # Wait until the next minute starts
        now = datetime.now()
        seconds_to_wait = 60 - now.second
        time.sleep(seconds_to_wait)

        excel_sheet_lock.acquire()
        volume_data = book.read_high_volume_stock(file_path, "volume")
        excel_sheet_lock.release()

        for stock in volume_data:
            current_stocks_data = client.get_historical_data(stock.name, "ONE_MINUTE", 5)
            #"date", "open", "high", "low", "close", "volume"
            candles = current_stocks_data[stock.name]['candles']
            
            if is_green(candles, 3) and \
                is_volumehigh(candles, 3, volume_data.volume_20_ma):
                client.position("Buy", stock.name)
            else:
                print("No trade: ",current_stocks_data)
        

def main():
    # Define the path to the Excel file
 
    client = broker.smart_client(r'D:\Akash\Share Market\Algo\MyAlgo')
    # Load the book stock list
    book = excel_book.trade_book(file_path)

    # load historical data
    history_stocks_data = client.get_stocks_historical_data(book.stocks)

    smart_api_lock = Lock()
    excel_sheet_lock = Lock()

    # Create and start threads
    low_priority = threading.Thread(target=tracking_thread, args=(smart_api_lock, excel_sheet_lock, history_stocks_data, client, book), daemon=True)
    high_priority = threading.Thread(target=trading_thread, args=(smart_api_lock, excel_sheet_lock, history_stocks_data, client, book), daemon=True)

    low_priority.start()
    high_priority.start()

    # Keep the main thread alive
    low_priority.join()
    high_priority.join()

    # track volume on 1 day candle, volume shall be more than previous 20 days ma volume, and stock price is +1%, put in today sheet


    # if volume more than 20 days ma, go to 1 minute candle to buy sold

    # Get and print the stocks
    #stocks = reader.get_stocks()
    #for stock in reader.stocks:
    #    print(stock.name)  # Access the 'name' field of the namedtuple

if __name__ == "__main__":
    main()