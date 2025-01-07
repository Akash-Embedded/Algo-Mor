import pandas as pd
from collections import namedtuple
import SMART_API_CONSTANT as CONST
import openpyxl

class trade_book:
    def __init__(self, file_path: str, sheet_name):
        self.file_path = file_path
        self.stocks = []
        self.file_path = file_path
        self.read_stock_names()
        self.sheet_name = sheet_name
        # Load existing sheet
        self.existing_data = pd.read_excel(file_path, sheet_name=sheet_name)

    def read_stock_names(self):
        # Read the Excel file into a DataFrame
        try:
            df = pd.read_excel(self.file_path, usecols="A")  # Only read column A
            df.dropna(inplace=True)  # Remove empty rows

            # Convert the column 'A' into a list
            self.stocks = df.iloc[:, 0].tolist()
        except Exception as e:
            print(f"Error reading the Excel file: {e}")

    def append_to_excel(self, file_path, df, sheet_name):
        try:
            # Load the workbook
            workbook = openpyxl.load_workbook(file_path)

            # Check if the sheet exists
            if sheet_name in workbook.sheetnames:
                with pd.ExcelWriter(file_path, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                    # Get the last row of the existing sheet
                    existing_sheet = workbook[sheet_name]
                    startrow = existing_sheet.max_row

                    # Append data starting from the next available row
                    df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=startrow, header=False)
            else:
                # If the sheet doesn't exist, create it
                with pd.ExcelWriter(file_path, mode='a', engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

        except FileNotFoundError:
            # If the file doesn't exist, create it and write the data
            with pd.ExcelWriter(file_path, mode='w', engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)

    def write_high_volume_stock(self, candle, excel, sheet_name, stock_name, volume_20_ma, price_diff_percentage):
        candle

        # Combine candle and technical data into a DataFrame
        data = []
        data.append({
                "name": stock_name,
                "volume_change": ((candle.volume - volume_20_ma) / volume_20_ma ) * 100,
                "price_change": price_diff_percentage,
                "date":  candle.time.replace(tzinfo=None),  # Remove timezone info
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
                "volume": candle.volume,
                "volume_20_ma": volume_20_ma,
                "rsi": candle.rsi,  # Placeholder if RSI is not calculated
            })

        df = pd.DataFrame(data)
        self.append_to_excel(excel, df, sheet_name)

    def update_indicators_sheet(self, candles, excel_path, stock, mor_dict, short_dict):
        current_candle = candles[-1]
        past_candle = candles[-2]
        data = [{
            "name": stock,
            "volume_change": ((current_candle.volume - current_candle.volume_20_ma) / current_candle.volume_20_ma) * 100,
            "price_change": ((current_candle.close - past_candle.close) / past_candle.close) * 100,
            "date": current_candle.time.replace(tzinfo=None),  # Remove timezone info
            "open": current_candle.open,
            "high": current_candle.high,
            "low": current_candle.low,
            "close": current_candle.close,
            "volume": current_candle.volume,
            "volume_20_ma": current_candle.volume_20_ma,
            "rsi": current_candle.rsi,
            "mor": mor_dict["indicator"],
            "mor_age": mor_dict["age"],
            "mor_date": mor_dict["time"].replace(tzinfo=None),
            "price_above_200_sma": mor_dict["ma_200_cross"],
        }]
        new_data = pd.DataFrame(data)
    
        try:
        #if True:
    
            # Ensure matching columns between existing_data and new_data
            for col in ["volume_change", "price_change", "date", "open", "high", "low", "close", "volume", "volume_20_ma", "rsi", "mor", "mor_age", "mor_date", "price_above_200_sma"]:
                if col in self.existing_data.columns and col in new_data.columns:
                    new_data[col] = new_data[col].astype(self.existing_data[col].dtype, errors="ignore")
    
            # Update matching stock row or append if it doesn't exist
            if stock in self.existing_data["name"].values:
                # Replace matching columns with new data
                for col in ["volume_change", "price_change", "date", "open", "high", "low", "close", "volume", "volume_20_ma", "rsi", "mor", "mor_age", "mor_date", "price_above_200_sma"]:
                    self.existing_data.loc[self.existing_data["name"] == stock, col] = new_data[col].values[0]
            else:
                # Append new row for non-existing stock
                self.existing_data = pd.concat([self.existing_data, new_data], ignore_index=True)
    
        except Exception as e:
            print(f"Error updating indicators sheet: {e}")

    def read_high_volume_stock(self, excel, sheet_name):
        try:
            # Read the data from the specified sheet in the Excel file
            df = pd.read_excel(excel, sheet_name=sheet_name)
            return df.to_dict(orient='records')

        except FileNotFoundError:
            print(f"The file {excel} was not found.")
            return None
        except ValueError:
            print(f"The sheet {sheet_name} does not exist in the file {excel}.")
            return None

    def get_stocks(self):
        return self.stocks
    
    def write_sheet(self):
        # Write the updated data back to Excel
        with pd.ExcelWriter(self.file_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            self.existing_data.to_excel(writer, self.sheet_name, index=False)


    def update_backtrace_sheet(self, stock, phase, entry_candle, exit_candle, mor_age, profit_loss):
        data = [{
            "name": stock,
            "phase": phase, 
            "age" : mor_age,
            "entry_price":getattr(entry_candle, 'close'),
            "entry_date": getattr(entry_candle, 'time').replace(tzinfo=None),
            "exit_price": getattr(exit_candle, 'close'),
            "exit_date":  getattr(exit_candle, 'time').replace(tzinfo=None),
            "PL": profit_loss,
        }]
        new_data = pd.DataFrame(data)
        self.existing_data = pd.concat([self.existing_data, new_data], ignore_index=True)

    def update_backtrace_summry(self, total_profit_loss):
        data = [{
            "total_profit_loss": total_profit_loss,
        }]
        new_data = pd.DataFrame(data)
        self.existing_data = pd.concat([self.existing_data, new_data], ignore_index=True)

    def summerised_monthly_profit(self, date_column_name, profit_column_name, stock_column_name):
        # Ensure the DateTime column is in datetime format
        self.existing_data['DateTime'] = pd.to_datetime(self.existing_data[date_column_name])

        # Extract year and month
        self.existing_data['Year-Month'] = self.existing_data['DateTime'].dt.to_period('M')

        # Group by Year-Month and calculate total profit/loss
        summary = self.existing_data.groupby('Year-Month')[profit_column_name].sum().reset_index()

        # Convert Year-Month back to string for better Excel compatibility
        summary['Year-Month'] = summary['Year-Month'].astype(str)

        # Save the summary to a new sheet in the same workbook
        with pd.ExcelWriter(self.file_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
            summary.to_excel(writer, sheet_name="summary-total", index=False)

        # Group by Year-Month and calculate total profit/loss
        summary = self.existing_data.groupby(['Year-Month', stock_column_name])[profit_column_name].sum().reset_index()

        # Convert Year-Month back to string for better Excel compatibility
        summary['Year-Month'] = summary['Year-Month'].astype(str)

        # Save the summary to a new sheet in the same workbook
        with pd.ExcelWriter(self.file_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
            summary.to_excel(writer, sheet_name="summary-stock", index=False)

    def empty_backtrace_Sheet(self):
        self.existing_data = pd.DataFrame()


