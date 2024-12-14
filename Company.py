import yfinance as yf
import pandas as pd
import numpy as np

from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2
import datetime as dt
import os

continent_names = {
                    "AF": "Africa",
                    "AS": "Asia",
                    "EU": "Europe",
                    "NA": "North America",
                    "SA": "South America",
                    "OC": "Oceania",
                    "AN": "Antarctica"
                }

exchange_currency = {
    'NYSE':     'USD',
    'NASDAQ':   'USD',
    'NYQ':      'USD',
    'LSE':      'GBP',
    'TSE':      'JPY',
    'Euronext': 'EUR',
    'HKEX':     'HKD',
    'NSE':      'INR',
    'BSE':      'INR'
}

def one_day_forward(date: str) -> str:
    year, month, day = str.split(date,'-')
    this_day = dt.date(int(year),int(month),int(day))
    next_day = this_day + dt.timedelta(1)

    return str(next_day)

class Company:
    def __init__(self, symbol: str, start_date: str) -> None:
        """
            symbol:        ticker symbol of the company
            start_date:    issuing the starting date of the simulation, all of the company's
                           attributes will be derived from yfinance data of that date
        """
        self.ticker = symbol

        if(os.path.isfile('Database/' + symbol + '.csv')):
            save_data_start_date = self.load_from_csv(symbol)

            if(save_data_start_date != start_date):
                print(f"{symbol}'s saved data's start date doesn't match the requierd start date, extracting from yfinance")
                self.load_from_yfinance(symbol, start_date)
        else:
            print(f"{symbol} is missing database file, extracting from yfinance")
            self.load_from_yfinance(symbol, start_date)

        self.popularity         = 0 # Default, will be adjusted later
        self.growth_potential   = 0

        self._active             = self.starting_day == np.int64(0)

        self.startingDay        = self.starting_day


    def load_from_csv(self, symbol) -> pd.Timestamp:
        data = pd.read_csv('Database/' + symbol + '.csv')

        self.name                   = data["name"][0]
        self.country                = data["country"][0]
        self.region                 = data["region"][0]
        self.industry               = data["industry"][0]
        self.sector                 = data["sector"][0]
        self.price                  = data["price"][0]
        self.trading_volume         = data["trading_volume"][0]
        self.shares_outstanding     = data["shares_outstanding"][0]
        self.market_cap             = data["market_cap"][0]
        self.revenue                = data["revenue"][0]
        self.earnings               = data["earnings"][0]
        self.profits                = data["profits"][0]
        self.expenses               = data["expenses"][0]
        self.EPS                    = data["EPS"][0]
        self.PE_ratio               = data["PE_ratio"][0]
        self.volatility_window_size = data["volatility_window_size"][0]
        self.volatility_index       = data["volatility_index"][0]
        self.starting_day           = data["days since start date"][0]

        return data["start date"][0]

    def load_from_yfinance(self,symbol,start_date):
        # Fetch data from yfinance
        stock = yf.Ticker(symbol)

        self.name       = stock.info['shortName']

        self.industry   = stock.info['industry']
        self.sector     = stock.info['sector']
        self.country    = stock.info['country']

        country_alpha2 = country_name_to_country_alpha2(self.country)
        self.region = continent_names[country_alpha2_to_continent_code(country_alpha2)]

        dt_start_date = pd.to_datetime(start_date)

        # historical_data = yf.download(symbol,start=start_date,progress=False)
        # historical_data = stock.history(period="max")
        historical_data = yf.download(stock.ticker,period="max")

        first_trading_day = historical_data.index.min()

        if(pd.to_datetime(first_trading_day).tz_localize(None) < dt_start_date):
            idx_start = historical_data.index.get_indexer([dt_start_date.tz_localize(first_trading_day.tz)], method='nearest')[0]
        else:
            idx_start = 0

        try:
            if(stock.info['currency'] != 'USD'):
                currency_exchange = yf.download(stock.info['currency'] + "USD=X",period='1d', interval="1d")['Adj Close']
                currency_exchange = currency_exchange.iloc[-1][stock.info['currency'] + "USD=X"]

                historical_data["Close"]        *= currency_exchange
                historical_data["Adj. Close"]   *= currency_exchange
        except KeyError:
            print("could not calculate currency exchange!")

        self.price = historical_data["Close"].values[idx_start][0]  # Initial price
        self.trading_volume = historical_data["Volume"].values[idx_start][0]

        # Use `info` for company details
        # Try to get the sharesOutstanding (if available)
        self.shares_outstanding = stock.info.get('sharesOutstanding', None)
        
        # If sharesOutstanding is not available, fall back to using floatShares (if available)
        if self.shares_outstanding is None:
            self.shares_outstanding = stock.info.get('floatShares', None)
            if self.shares_outstanding is None:
                print(f"Warning: Both sharesOutstanding and floatShares are missing for {stock.ticker}.")
                exit(1)

        self.market_cap = self.shares_outstanding * self.price

        price_change_factor = self.price/historical_data["Close"].values[-1][0]

        self.revenue = stock.info.get('totalRevenue', 0) * price_change_factor
        self.earnings = self.price * self.shares_outstanding * price_change_factor
        try:
            rawExpenses = stock.financials.loc["Total Expenses"].values[0]
            rawExpenses_idx = 0
            while(np.isnan(rawExpenses)):
                rawExpenses_idx += 1
                rawExpenses = stock.financials.loc["Total Expenses"].values[rawExpenses_idx]
            
            if(np.isnan(rawExpenses)):
                    raise RuntimeError("Failed to get total expenses directly!")
        except KeyError:
            try:
                netIncome = stock.financials.loc["Net Income"].values[0]
                totalRevenue = stock.financials.loc["Total Revenue"].values[0]
                rawExpenses = totalRevenue - netIncome 
                rawExpenses_idx = 0
                while(np.isnan(rawExpenses)):
                    rawExpenses_idx += 1
                    netIncome = stock.financials.loc["Net Income"].values[rawExpenses_idx]
                    totalRevenue = stock.financials.loc["Total Revenue"].values[rawExpenses_idx]
                    rawExpenses = totalRevenue - netIncome 
                
                if(np.isnan(rawExpenses)):
                    raise RuntimeError("Failed to get total expenses from net income & total revenue!")
            except KeyError:
                raise RuntimeError("Failed to get total expenses!")
            
        self.expenses = rawExpenses * price_change_factor
        self.profits = self.revenue - self.expenses
        
        self.EPS = self.earnings/self.shares_outstanding # earnings per share
        self.PE_ratio = self.price/self.EPS # price to earnigns (EPS) ratio 

        self.volatility_window_size = 20

        if(idx_start > self.volatility_window_size - 1):
            self.volatility_index = np.std(historical_data["Close"].values[idx_start - self.volatility_window_size + 1:idx_start + 1])*np.sqrt(self.volatility_window_size)
        else:
            # if past data is not available, use the NEXT 'self.volatility_window_size' days
            self.volatility_index = np.std(historical_data["Close"].values[0:self.volatility_window_size])*np.sqrt(self.volatility_window_size)

        # Number of days till company's inception
        days_since_start_date = (first_trading_day.tz_localize(None) - dt_start_date).days
        if(days_since_start_date < 0):
            days_since_start_date = 0

        # save ticker data to .csv file in datbase
        derived_data = pd.DataFrame([{
                                        "name": self.name,
                                        "country": self.country,
                                        "region": self.region,
                                        "industry": self.industry,
                                        "sector": self.sector,
                                        "price": self.price.astype('float32'),
                                        "trading_volume": self.trading_volume,
                                        "shares_outstanding": self.shares_outstanding,
                                        "market_cap": self.market_cap.astype('float32'),
                                        "revenue": self.revenue.astype('float32'),
                                        "earnings": self.earnings.astype('float32'),
                                        "profits": self.profits.astype('float32'),
                                        "expenses": self.expenses.astype('float32'),
                                        "EPS": self.EPS.astype('float32'),
                                        "PE_ratio": self.PE_ratio.astype('float32'),
                                        "volatility_window_size": self.volatility_window_size,
                                        "volatility_index": self.volatility_index.astype('float32'),
                                        "start date": start_date,
                                        "days since start date": days_since_start_date
                                        }])
    
        derived_data.to_csv('Database/' + symbol + '.csv',index=False)
        historical_data_df = pd.DataFrame(index=historical_data.index, columns=['Close', 'Adj Close'])
        historical_data_df['Close']     = historical_data['Close']
        historical_data_df['Adj Close'] = historical_data['Adj Close']

        del historical_data

        historical_data_df.astype('float32').to_csv('Database/' + symbol + '_price_history.csv')
        print(f"{symbol} data saved to database folder.")

    @property
    def Active(self):
        return self._active
    
    @Active.setter
    def Active(self, value: bool):
        self._active = value

    def Allocate_History(self, Data):
        numTotalDays = Data.Manager.numTotalDays

        self.History = {"price":                    np.nan*np.ones(numTotalDays,dtype='float32'),
                        "trading_volume":           np.zeros(numTotalDays,dtype='int32'),
                        "shares_outstanding":       np.zeros(numTotalDays,dtype='int32'),
                        "market_cap":               np.nan*np.ones(numTotalDays,dtype='float32'),
                        "revenue":                  np.nan*np.ones(numTotalDays,dtype='float32'),
                        "earnings":                 np.nan*np.ones(numTotalDays,dtype='float32'),
                        "profits":                  np.nan*np.ones(numTotalDays,dtype='float32'),
                        "expenses":                 np.nan*np.ones(numTotalDays,dtype='float32'),
                        "EPS":                      np.nan*np.ones(numTotalDays,dtype='float32'),
                        "PE_ratio":                 np.nan*np.ones(numTotalDays,dtype='float32'),
                        "volatility_index":         np.nan*np.ones(numTotalDays,dtype='float32')
                        }
        
        if(self.Active):
            self.History["price"][0]                = self.price
            self.History["trading_volume"][0]       = self.trading_volume
            self.History["shares_outstanding"][0]   = self.shares_outstanding
            self.History["market_cap"][0]           = self.market_cap
            self.History["revenue"][0]              = self.revenue
            self.History["earnings"][0]             = self.earnings
            self.History["profits"][0]              = self.profits
            self.History["expenses"][0]             = self.expenses
            self.History["EPS"][0]                  = self.EPS
            self.History["PE_ratio"][0]             = self.PE_ratio
            self.History["volatility_index"][0]     = self.volatility_index

    def record_to_history(self, day):
        if(self.Active):
            self.History["price"][day]                = self.price
            self.History["trading_volume"][day]       = self.trading_volume
            self.History["shares_outstanding"][day]   = self.shares_outstanding
            self.History["market_cap"][day]           = self.market_cap
            self.History["revenue"][day]              = self.revenue
            self.History["earnings"][day]             = self.earnings
            self.History["profits"][day]              = self.profits
            self.History["expenses"][day]             = self.expenses
            self.History["EPS"][day]                  = self.EPS
            self.History["PE_ratio"][day]             = self.PE_ratio
            self.History["volatility_index"][day]     = self.volatility_index

    def update_price(self, demand, supply):
        """
        Update the stock price based on demand, supply, and other influencing factors.
        """
        pass
    
    def update_metrics(self):
        """
        Update the metrics based on current companies performance & market status.
        """
        pass


if __name__ == "__main__":
    CMPNY = Company('O',"1995-01-01")
    # CMPNY = Company('TSLA',"1995-01-01")