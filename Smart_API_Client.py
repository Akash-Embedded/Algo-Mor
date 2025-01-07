from SmartApi import SmartConnect
import os
from pyotp import TOTP
import urllib
import json
import pandas as pd
import datetime as dt
import time
import matplotlib.pyplot as plt
import threading
import numpy as np
from collections import namedtuple
from datetime import datetime

class smart_client:
    def __init__(self, credential_path: str):
        self.credential_path = credential_path
        self.obj = None
        self.instrument_list = None
        self.ema_periods = [2, 5, 8, 12, 13, 15, 20, 21, 25, 30, 35, 40, 45, 50]
        self.sma_periods = [200]
        self.candle = namedtuple('candle', ['time', 'open', 'high', 'low', 'close', 'volume', 'volume_20_ma', 'rsi'] + \
                                 [f'EMA_{period}' for period in self.ema_periods] + \
                                 [f'SMA_{period}' for period in self.sma_periods])
        # Define the NamedTuple for Stock Data
        self.stock_data = namedtuple('stock_data', ['name', 'history'])

        self._load_credentials()
        self._initialize_client()
        self._load_instruments()

    def _load_credentials(self):
        """Load API credentials from a file."""
        os.chdir(self.credential_path)
        credentials = open("credential.txt").read().split()
        self.api_key = credentials[0]
        self.username = credentials[2]
        self.password = credentials[3]
        self.totp_secret = credentials[4]

    def _initialize_client(self):
        """Initialize the Smart API client and authenticate."""
        self.obj = SmartConnect(api_key=self.api_key)
        totp_now = TOTP(self.totp_secret).now()
        self.session_data = self.obj.generateSession(self.username, self.password, totp_now)

    def _load_instruments(self):
        """Load instrument list from the API."""
        instrument_url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        response = urllib.request.urlopen(instrument_url)
        self.instrument_list = json.loads(response.read().decode("utf-8"))

    def token_lookup(self, ticker, exchange="NSE"):
        """Find the token for a given ticker."""
        for instrument in self.instrument_list:
            if (
                instrument["name"] == ticker
                and instrument["exch_seg"] == exchange
                and instrument["symbol"].split("-")[-1] == "EQ"
            ):
                return instrument["token"]
        print("ticker not found\n")
        return None

    def get_historical_data(self, ticker, duration, number_of_candle, end_date=None):
        hist_data_tickers = {}
    
        # Define mapping of duration to minutes
        duration_mapping = {
            "ONE_MINUTE": 1,
            "THREE_MINUTE": 3,
            "FIVE_MINUTE": 5,
            "TEN_MINUTE": 10,
            "FIFTEEN_MINUTE": 15,
            "THIRTY_MINUTE": 30,
            "ONE_HOUR": 60,
            "ONE_DAY": 1440,  # 24 hours * 60 minutes
        }
    
        if duration not in duration_mapping:
            raise ValueError(f"Invalid duration: {duration}. Valid options are: {list(duration_mapping.keys())}")
    
        # Calculate the total time span in minutes
        total_minutes = duration_mapping[duration] * number_of_candle
       # Use the provided end_date or default to the current datetime
        if end_date is None:
            end_date = dt.datetime.now()

        start_date = end_date - dt.timedelta(minutes=total_minutes)
        #for ticker in tickers:
        symboltoken = self.token_lookup(ticker)
        if symboltoken == None:
            return hist_data_tickers
        try:
            params = {
                "exchange": "NSE",
                "symboltoken": symboltoken,
                "interval": duration,
                "fromdate": start_date.strftime("%Y-%m-%d %H:%M"),
                "todate": end_date.strftime("%Y-%m-%d %H:%M"),
            }
            time.sleep(0.4)
            response = self.obj.getCandleData(params)
            if "data" in response:
                df = pd.DataFrame(
                    response["data"],
                    columns=["date", "open", "high", "low", "close", "volume"],
                )
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)

                # Calculate the 20-day moving average
                df['volume_20_ma'] = df['volume'].rolling(window=20).mean()
                for period in self.ema_periods:
                    df[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
                
                for period in self.sma_periods:
                    df[f'SMA_{period}'] = df['close'].rolling(period).mean()

                # Convert DataFrame rows into a list of 'candle' namedtuples
                candle_list = []
                technical_list = []
                for _, row in df.iterrows():
                    # Create a dictionary to hold all EMA values dynamically
                    ema_values = {f'EMA_{period}': row[f'EMA_{period}'] if not pd.isna(row[f'EMA_{period}']) else None 
                                  for period in self.ema_periods}
                    sma_values = {f'SMA_{period}': row[f'SMA_{period}'] if not pd.isna(row[f'SMA_{period}']) else None 
                                  for period in self.sma_periods}
                    candle_list.append(self.candle(time=row.name,  # Date is the index of the row
                                          open=row["open"],
                                          high=row["high"],
                                          low=row["low"],
                                          close=row["close"],
                                          volume=row["volume"], 
                                          volume_20_ma=row["volume_20_ma"] if not pd.isna(row["volume_20_ma"]) else None,
                                          rsi=None,
                                          **ema_values,
                                          **sma_values))
                    hist_data_tickers[ticker] = {
                    "candles": candle_list,
                    }
        except:
            pass
        return hist_data_tickers

    @staticmethod
    def calculate_ema(series, n=9):
        """Calculate Exponential Moving Average (EMA)."""
        return series.ewm(span=n, adjust=False).mean()

    @staticmethod
    def calculate_macd(df, a=12, b=26, c=9):
        """Calculate MACD for a DataFrame."""
        df["ma_fast"] = SmartAPIClient.calculate_ema(df["close"], a)
        df["ma_slow"] = SmartAPIClient.calculate_ema(df["close"], b)
        df["macd"] = df["ma_fast"] - df["ma_slow"]
        df["signal"] = SmartAPIClient.calculate_ema(df["macd"], c)
        return df

    @staticmethod
    def calculate_volume_ma(df, n=20):
        """Calculate the 20-day moving average of volume."""
        df["volume_ma_20"] = df["volume"].rolling(n).mean()
        return df

    def print_high_volume_dates(self, df_dict):
        """Print dates with high volume activity."""
        for ticker, df in df_dict.items():
            df["prev_close"] = df["close"].shift(1)
            df["price_change_pct"] = ((df["close"] - df["prev_close"]) / df["prev_close"]) * 100
            high_volume = df[df["volume"] > 2 * df["volume_ma_20"]]
            if not high_volume.empty:
                print(f"\nHigh Volume Dates for {ticker}:")
                print(high_volume[["volume", "volume_ma_20", "price_change_pct"]])


    def get_stocks_historical_data(self, stocks):
        # --debug data start
        current_time = datetime.now()
        formatted_time = current_time.strftime("%H:%M:%S") + f":{current_time.microsecond // 1000:03d}"
        print(formatted_time)
        # --debug data end
        stocks_data = []
        for index, stock in enumerate(stocks):
            start_time = time.time()  # Record the start time of the iteration
            #print(f"Processing stock at index {index}: {stock}")
            stock_history = self.get_historical_data(stock, "ONE_DAY", 50)
            stock_entry = self.stock_data(name=stock, history=stock_history)
            stocks_data.append(stock_entry)
            #print(stocks_data[-1].name)

            # Calculate elapsed time and sleep to maintain 3 iterations per second
            elapsed_time = time.time() - start_time
            sleep_time = max(0, (1/3) - elapsed_time)  # Ensure non-negative sleep time
            time.sleep(sleep_time)
        
        # --debug data start
        current_time = datetime.now()
        formatted_time = current_time.strftime("%H:%M:%S") + f":{current_time.microsecond // 1000:03d}"
        print(formatted_time)
        # --debug data end

        return stocks_data
    def position(self, action, stock_name):
        print(">>>>>>> ", action, stock_name)
    
    def get_day_volume(self, stock, date):
        stock_history = self.get_historical_data(stock, "ONE_MINUTE", 390)
        # Get date in the same format as in the data
        #date = date.strftime('%Y-%m-%d')

        # Filter candles to include only rows from today
        filtered_candles = [
            row for row in stock_history[stock]['candles']
            if row["time"].startswith(date)
        ]
        stock_history[stock]['candles'] = filtered_candles

