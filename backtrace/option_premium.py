import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

import TradeBook as excel_book
from datetime import datetime
import Smart_API_Client as broker
import sys

if len(sys.argv) != 2:
    print("Usage: python script.py <file path>")
    sys.exit(1)

file_path = sys.argv[1]


def atm_symbols(date, spot_price):
    symbols = []
    nearest_lower_strike = int((spot_price // 50) * 50)
    nearest_upper_strike = int(nearest_lower_strike + 50)
    
    date_str = date.strftime('%d%b%y').upper()
    
    symbols.append(f'NIFTY{date_str}{nearest_upper_strike}{"PE"}')
    symbols.append(f'NIFTY{date_str}{nearest_lower_strike}{"PE"}')
    symbols.append(f'NIFTY{date_str}{nearest_upper_strike}{"CE"}')
    symbols.append(f'NIFTY{date_str}{nearest_lower_strike}{"CE"}')

    return symbols

def main():
 
    client = broker.smart_client(r'D:\Akash\Share Market\Algo\MyAlgo')
    # Load the book stock list
    book = excel_book.trade_book(file_path, "backtrace")
    book.empty_Sheet()

    for expiry_date in book.stocks:
        nifty_data = client.get_historical_data("Nifty 50", "ONE_MINUTE", 2625, expiry_date, 'indices')
        nifty_candles = nifty_data["Nifty 50"]['candles']
        previous_symbol = {}
        for tick in nifty_candles:
            premium_data = {}
            symbols = atm_symbols(expiry_date, tick.close)

            if previous_symbol != symbols:
                combine_preimum_data = {}
                for symbol in symbols:
                    premium_data[symbol] = client.get_option_historical_data(symbol, "ONE_MINUTE", 2625, expiry_date)
                    if len(premium_data[symbol]) == 0:
                        print("premium_data is empty")
                    else:
                        combine_preimum_data.append(premium_data[symbol]['candles'])
            previous_symbol = symbols

    premium_dict = {}
    for symbol_data in combine_preimum_data:
        for candle in symbol_data['candles']:
            key = (candle['time'].strftime('%A'), candle['time'].strftime('%H:%M'))
            if key not in premium_dict:
                premium_dict[key] = {'sum': 0, 'count': 0}
            premium_dict[key]['sum'] += candle['close']
            premium_dict[key]['count'] += 1

    # Calculate the average premium for each key
    for key in premium_dict:
        premium_dict[key] = premium_dict[key]['sum'] / premium_dict[key]['count']

    book.write_sheet()

if __name__ == "__main__":    main()