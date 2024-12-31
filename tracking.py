import pandas as pd
import numpy as np
from SmartApi import SmartConnect 
from collections import namedtuple
from datetime import datetime

class base_strategy:
    def check_crossovers(self, hist_data, short_term_periods, long_term_periods):

        # Iterate through each row of data to check for crossovers
        first_clear_signal = "No Signal"
        second_clear_signal = "No Signal"
        signal = "No Signal"
        return_dict = {}
        
        days_count = 0
        idx = 0
        for idx in range(len(hist_data) - 1, 0, -1):
            days_count += 1
            short_ema = []
            for period in short_term_periods:
                short_ema.append(getattr(hist_data[idx], f'EMA_{period}'))

            long_ema = []
            for period in long_term_periods:
                long_ema.append(getattr(hist_data[idx], f'EMA_{period}'))
            #print(min(long_ema))
            short_ema.sort()
            long_ema.sort()
            if (short_ema[-1] < long_ema[0]):
                signal = "Bear"
            
            if (short_ema[0] > long_ema[-1]):
                signal = "Bull"

            if (signal == "Bull" or signal == "Bear" ):
                if first_clear_signal == "No Signal":
                    first_clear_signal = signal
                elif signal != first_clear_signal:
                    second_clear_signal = signal
                    break
    
        if first_clear_signal != "No Signal" and second_clear_signal != "No Signal":
            signal =  "No Signal"
            for i in range(idx, len(hist_data)):
                days_count -= 1
                short_ema = []
                for period in short_term_periods:
                    short_ema.append(getattr(hist_data[i], f'EMA_{period}'))

                long_ema = []
                for period in long_term_periods:
                    long_ema.append(getattr(hist_data[i], f'EMA_{period}'))

                short_ema.sort()
                long_ema.sort()
                if (short_ema[-1] < long_ema[0]):
                    signal = "Bear"
            
                if (short_ema[0] > long_ema[-1]):
                    signal = "Bull"

                
                if signal == first_clear_signal:
                    return_dict["time"]= hist_data[i].time
                    return_dict["indicator"]= signal
                    return_dict["age"] = days_count

                    return return_dict 
        
        return_dict["time"]= datetime.now()
        return_dict["indicator"]= "No Signal"
        return_dict["age"] = 0
        return return_dict

class Mor(base_strategy):
    def __init__(self, short_term_periods, long_term_periods):
        # Define short-term and long-term EMA periods
        self.short_term_periods = short_term_periods
        self.long_term_periods = long_term_periods

    def indicator(self, hist_data):
        """
        Analyze the trading signal based on EMA crossovers and trends.
    
        Args:
            hist_data (pd.DataFrame): Historical data containing at least 200 candles.
    
        Returns:
            str: "New Buy", "New Sell", "Continue_Bull_Trend", "Continue_Bear_Trend", or "No Signal".
        """
        # Ensure historical data contains at least 200 candles
        return_dict = {}

        if len(hist_data) < 200:
            print("Insufficient data. At least 200 candles are required.")
            return_dict["time"]= datetime.now()
            return_dict["indicator"]= "No Signal"
            return_dict["age"] = 0
            return return_dict

        # Check for crossovers and continuous trends
        return_dict = self.check_crossovers(hist_data, self.short_term_periods, self.long_term_periods)
    
        return return_dict

