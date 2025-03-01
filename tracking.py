import pandas as pd
import numpy as np
from SmartApi import SmartConnect 
from collections import namedtuple
from datetime import datetime

class base_strategy:
    def check_crossovers(self, hist_data, crossing_periods, base_periods, rsi=False):

        # Iterate through each row of data to check for crossovers
        first_clear_signal = "No Signal"
        second_clear_signal = "No Signal"
        signal = "No Signal"
        return_dict = {}
        
        days_count = 0
        idx = 0
        for idx in range(len(hist_data) - 1, 0, -1):
            days_count += 1
            crossing_ma = []
            for period in crossing_periods:
                crossing_ma.append(getattr(hist_data[idx], f'EMA_{period}'))

            base_ma = []
            for period in base_periods:
                base_ma.append(getattr(hist_data[idx], f'EMA_{period}'))
            #print(min(base_ma))
            crossing_ma.sort()
            base_ma.sort()
            if (crossing_ma[-1] < base_ma[0]):
                signal = "Bear"
            
            if (crossing_ma[0] > base_ma[-1]):
                signal = "Bull"

            if (signal == "Bull" or signal == "Bear" ):
                if first_clear_signal == "No Signal":
                    first_clear_signal = signal
                    rsi_on_first_signal = getattr(hist_data[idx], 'rsi')
                elif signal != first_clear_signal:
                    second_clear_signal = signal
                    break
    
        if first_clear_signal != "No Signal" and second_clear_signal != "No Signal":
            signal =  "No Signal"
            for i in range(idx+1, len(hist_data)):
                days_count -= 1
                crossing_ma = []
                for period in crossing_periods:
                    crossing_ma.append(getattr(hist_data[i], f'EMA_{period}'))

                base_ma = []
                for period in base_periods:
                    base_ma.append(getattr(hist_data[i], f'EMA_{period}'))

                crossing_ma.sort()
                base_ma.sort()
                if (crossing_ma[-1] < base_ma[0]):
                    signal = "Bear"
            
                if (crossing_ma[0] > base_ma[-1]):
                    signal = "Bull"

                
                if signal == first_clear_signal:
                    return_dict["time"]= hist_data[i].time
                    return_dict["indicator"]= signal
                    return_dict["age"] = days_count
                    if getattr(hist_data[i], f'SMA_200') is not None:
                        if getattr(hist_data[i], f'close') >  getattr(hist_data[i], f'SMA_200') :
                            return_dict["ma_200_cross"] = "True"
                        else:
                            return_dict["ma_200_cross"] = "False"
                    else:
                        return_dict["ma_200_cross"] = ""

                    age_as_per_rsi = 0
                    if rsi == True:
                        #return_dict["enter_rsi"] = rsi_on_first_signal
                        for j in range(i, i+days_count):
                            if signal == "Bull":
                                if age_as_per_rsi > 2 :
                                    comparision = 50 + age_as_per_rsi
                                else :
                                    comparision = 50

                                if getattr(hist_data[j], 'rsi') > comparision:
                                    age_as_per_rsi += 1
                                else:
                                    break
                            if signal == "Bear":
                                if age_as_per_rsi > 2 :
                                    comparision = 50 - age_as_per_rsi 
                                else :
                                    comparision = 50
                                if getattr(hist_data[j], 'rsi') < comparision:
                                    age_as_per_rsi += 1
                                else:
                                    break

                        return_dict["age_as_per_rsi"] = age_as_per_rsi

                    return return_dict 
        elif (first_clear_signal != "No Signal" and second_clear_signal == "No Signal" and idx == 1):
            return_dict["time"]= hist_data[idx].time
            return_dict["indicator"]= first_clear_signal
            return_dict["age"] = len(hist_data) - 1 # bug: related to find the previous candle 
            return_dict["ma_200_cross"] = ""
            return return_dict


        return_dict["time"]= datetime.now()
        return_dict["indicator"]= "No Signal"
        return_dict["age"] = 0
        return_dict["ma_200_cross"] = ""
        return return_dict

class Mor(base_strategy):
    def __init__(self, short_term_ema_periods, long_term_ema_periods, long_term_ma = []):
        # Define short-term and long-term EMA periods
        self.short_term_ema_periods = short_term_ema_periods
        self.long_term_ema_periods = long_term_ema_periods
        self.long_term_ma = long_term_ma

    def indicator(self, hist_data, rsi = False, sma_200 = False):
        """
        Analyze the trading signal based on EMA crossovers and trends.
    
        Args:
            hist_data (pd.DataFrame): Historical data containing at least 200 candles.
    
        Returns:
            str: "New Buy", "New Sell", "Continue_Bull_Trend", "Continue_Bear_Trend", or "No Signal".
        """
        # Ensure historical data contains at least 200 candles
        return_dict = {}


        #if len(hist_data) < 200:
        #    print("Insufficient data. At least 200 candles are required.")
        #    return_dict["time"]= datetime.now()
        #    return_dict["indicator"]= "No Signal"
        #    return_dict["age"] = 0
        #    return_dict["ma_200_cross"] = ""
        #    return return_dict

        # Check for crossovers and continuous trends
        return_dict = self.check_crossovers(hist_data, self.short_term_ema_periods, self.long_term_ema_periods, rsi)
        return return_dict
    
    def signal_end(self,hist_data, index, with_in_days, current_signal):
        signal = "No Signal"
        if current_signal == "Bull":
            search_signal = "Bear"
        elif current_signal == "Bear":
            search_signal = "Bull"
        crossing_periods = self.short_term_ema_periods
        base_periods = self.long_term_ema_periods
        return_dict = {}
        idx = 0
        for idx in range(index, index + with_in_days, 1):
            crossing_ma = []
            for period in crossing_periods:
                crossing_ma.append(getattr(hist_data[idx], f'EMA_{period}'))

            base_ma = []
            for period in base_periods:
                base_ma.append(getattr(hist_data[idx], f'EMA_{period}'))

            crossing_ma.sort()
            base_ma.sort()
            if (crossing_ma[-1] < base_ma[0]):
                signal = "Bear"
            
            if (crossing_ma[0] > base_ma[-1]):
                signal = "Bull"
             
            if signal == search_signal:
                return_dict["time"]= hist_data[idx].time
                return_dict["indicator"]= current_signal
                return_dict["age"] = idx - index
                return_dict["ma_200_cross"] = ""
                return return_dict
        
        return_dict["time"]= hist_data[idx].time
        return_dict["indicator"]= current_signal
        return_dict["age"] = with_in_days
        return_dict["ma_200_cross"] = ""
        return return_dict
    
        

