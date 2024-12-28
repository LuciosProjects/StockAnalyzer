import sqlite3
import datetime as dt
import yfinance as yf
import numpy as np, pandas as pd
import os
from Portfolio import Portfolio

import Utilities as util
import TraderConstantData as tcd

class Investor:
    def __init__(self, Investor_db_name = 'InvestorDB.db',portfolio_db_name='portfolio.db', monthly_deposit=1500, initialize = False):
        self.Investor_db_name = Investor_db_name
        ''' Investor database file name '''

        self.portfolio = Portfolio(db_name=portfolio_db_name)
        ''' Portfolio object used by the investor '''

        self.monthly_deposit = monthly_deposit
        ''' Monthly deposit amount, one of the investor's income sources '''

        self.last_purchase_month = self.portfolio.last_purchase_date.month
        ''' Last month in which the investor made a purchase '''

        self.last_balance_update_month = None
        ''' Last month in which the investor updated the balance '''

        self.rsi_data = {}
        ''' Dictionary to store RSI data for each symbol '''

        self.PE_ratio_data = {}
        ''' Dictionary to store PE (price over earnings) ratio data for each symbol '''

        self.Security_trend = {}
        ''' Dictionary to store the trend of each security (bearish/bullish/neutral) '''

        self.SecurityValid  = {}
        ''' Dictionary to store whether a security is valid for evaluation or not '''

        # create tables
        if initialize:
            self.initialize_InvestorDB()
        else:
            self.load_InvestorDB()
            self.update_InvestorDB()

    def _connect_to_db(self):
        ''' Connects to the database. '''
        self.conn   = sqlite3.connect(self.Investor_db_name)
        self.c      = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        ''' Creates the tables in the database. '''
        self.c.execute('''CREATE TABLE IF NOT EXISTS InvestorDB (
                       id INTEGER PRIMARY KEY, 
                       monthly_deposit REAL, 
                       last_purchase_month INTEGER,
                       last_balance_update_month INTEGER,
                       rsi_data TEXT,
                       PE_ratio_data TEXT,
                       Security_trend TEXT)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS SecurityData (
                       id INTEGER PRIMARY KEY, 
                       SecurityValid TEXT)''')
        self.conn.commit()

    def initialize_InvestorDB(self):
        ''' Initializes the investor database and deletes any existing database of the same name '''

        # Overwrite the database with initial values
        if(os.path.exists(self.Investor_db_name)):
            os.remove(self.Investor_db_name)
        self._connect_to_db()

        self.SecurityValid              = {}
        self.rsi_data                   = {}
        self.PE_ratio_data              = {}
        self.Security_trend             = {}
        self.last_purchase_month        = dt.datetime.now().month
        self.last_balance_update_month  = dt.datetime.now().month

        self.save_InvestorDB()

    def load_InvestorDB(self):
        ''' Loads the portfolio from the database. '''

        if(not os.path.exists(self.Investor_db_name)):
            raise RuntimeError("Investor database does not exist. Please initialize it first.")
        else:
            self._connect_to_db()

        cursor = self.conn.execute('SELECT monthly_deposit, last_purchase_month, last_balance_update_month, rsi_data, PE_ratio_data, Security_trend  FROM InvestorDB ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        if row:
            self.monthly_deposit            = row[0]
            self.last_purchase_month        = row[1]
            self.last_balance_update_month  = row[2]
            self.rsi_data                   = eval(row[3])  # Convert string back to dictionary
            self.PE_ratio_data              = eval(row[4])  # Convert string back to dictionary
            self.Security_trend             = eval(row[5])  # Convert string back to dictionary
        
        cursor = self.conn.execute('SELECT SecurityValid FROM SecurityData')
        row = cursor.fetchone()
        if row:
            self.SecurityValid = eval(row[0]) # Convert string back to dictionary

    def save_InvestorDB(self):
        ''' Saves the Inverstor database to the database. '''
        with self.conn:
            self.conn.execute('''INSERT INTO InvestorDB (monthly_deposit, last_purchase_month, last_balance_update_month, rsi_data, PE_ratio_data, Security_trend)
                                 VALUES (?, ?, ?, ?, ?, ?)''',
                              (self.monthly_deposit, self.last_purchase_month, self.last_balance_update_month,
                               str(self.rsi_data), str(self.PE_ratio_data), str(self.Security_trend)))
            self.conn.execute('DELETE FROM SecurityData')
            self.conn.execute('''INSERT INTO SecurityData (SecurityValid)
                                 VALUES (?)''', 
                              (str(self.SecurityValid),))
            self.conn.commit()  # Save the changes to the database

    def update_InvestorDB(self):
        ''' Updates investor metrics in the database to the latest values. '''

        for symbol in self.rsi_data.keys():
            self.determine_market_condition(symbol)

        self.save_InvestorDB()

    def allocate_monthly_deposit(self):
        current_month = dt.datetime.now().month
        if self.last_purchase_month != current_month:
            self.portfolio.balance += self.monthly_deposit
            self.last_purchase_month = current_month
            # print(f"Allocated ${self.monthly_deposit} from monthly deposit to portfolio balance.")

    def identify_dropping_indices(self):
        # Example: Check major indices like S&P 500, NASDAQ, Dow Jones, Russell 2000 and world index
        indices = ['^GSPC', '^IXIC', '^DJI', '^RUT', '^WORLD']
        dropping_indices = []
        for index in indices:
            _, Hdata = util.get_security_data(index)
            if Hdata['Close'].iloc[-1] < Hdata['Close'].iloc[-30]:
                dropping_indices.append(index)
        return dropping_indices

    def make_trading_decisions(self):
        # Allocate monthly deposit
        self.allocate_monthly_deposit()

        portfolio_status = self.evaluate_portfolio_status()

        if(portfolio_status == tcd.EPortfolioStatus.BAD):
            return # Do not make any trading decisions if the portfolio status is bad
        elif(portfolio_status == tcd.EPortfolioStatus.GOOD_FOR_BUYING):
            # Only look for securities to buy
            pass
        elif(portfolio_status == tcd.EPortfolioStatus.GOOD_FOR_SELLING):
            # Only look for securities to sell
            pass
        elif(portfolio_status == tcd.EPortfolioStatus.GOOD):
            # Look for securities to buy and sell
            pass

        # Identify dropping indices
        dropping_indices = self.identify_dropping_indices()

        # EXAMPLE START
        # Example decision: Buy indices that have dropped if the market is bullish
        for index in dropping_indices:
            _, Hdata = util.get_security_data(index)
            current_price = Hdata['Close'].iloc[-1]
            if self.Security_trend[index] == 'bullish':
                self.portfolio.buy(dt.datetime.now().strftime('%Y-%m-%d'), index, current_price, 10)
            elif self.Security_trend[index] == 'bearish':
                self.portfolio.sell(dt.datetime.now().strftime('%Y-%m-%d'), index, current_price, 10)
        # EXAMPLE END
    
    def evaluate_portfolio_status(self):
        avg_prices = np.mean([self.portfolio.avg_price[symbol] for symbol in self.portfolio.avg_price.keys()])
        amount_possible_with_balance = int(self.portfolio.balance/avg_prices)

        securities_cost = amount_possible_with_balance * avg_prices
        total_fee = max([self.portfolio.transaction_fee, amount_possible_with_balance*0.01])
        
        purchase_cond = (total_fee/securities_cost) < 0.03 # up to 3% transaction fee is acceptable

        sell_cond = self.portfolio.evaluate_securities_to_sell()

        if purchase_cond and sell_cond:
            return tcd.EPortfolioStatus.GOOD
        elif purchase_cond and not sell_cond:
            return tcd.EPortfolioStatus.GOOD_FOR_BUYING
        elif sell_cond and not purchase_cond:
            return tcd.EPortfolioStatus.GOOD_FOR_SELLING
        else:
            return tcd.EPortfolioStatus.BAD

    def determine_market_condition(self, symbol):
        ticker, Hdata = util.get_security_data(symbol)

        if(ticker.info['quoteType'] == 'NONE'):
            # If security doesn't have a quote type, it is not a valid security to be evaluated
            self.SecurityValid[symbol]  = False
            self.rsi_data[symbol]       = np.nan
            self.PE_ratio_data[symbol]  = np.nan
            return
        else: 
            self.SecurityValid[symbol]  = True

        # short_ma = Hdata['Close'].rolling(window=util.CUtilityConstants.SHORT_MA_WINDOW).mean().iloc[-1].iloc[0] # Short moving average represents the short-term trend
        # long_ma = Hdata['Close'].rolling(window=util.CUtilityConstants.LONG_MA_WINDOW).mean().iloc[-1].iloc[0] # long moving average represents the long-term trend

        short_term  = (((Hdata['Close'].iloc[-1] - Hdata['Close'].iloc[-util.CUtilityConstants.SHORT_MA_WINDOW])/Hdata['Close'].iloc[-util.CUtilityConstants.SHORT_MA_WINDOW])*100).iloc[0]
        long_term   = (((Hdata['Close'].iloc[-1] - Hdata['Close'].iloc[-util.CUtilityConstants.LONG_MA_WINDOW])/Hdata['Close'].iloc[-util.CUtilityConstants.LONG_MA_WINDOW])*100).iloc[0]

        rsi = util.calculate_rsi(Hdata['Close'].values, util.CUtilityConstants.RSI_WINDOWS[0]) # Relative Strength Index (RSI) represents the momentum of the stock's price
        self.rsi_data[symbol] = rsi[-1]

        self.PE_ratio_data[symbol] = util.get_PE_ratio(ticker)

        if  rsi[-1] < 30:
            # According to the literature (Investopedia.com):
            # - an rsi below 30 indicates an overselling of the stock, 
            #   which indicates bullish market on an uptrend
            if short_term > long_term:
                self.Security_trend[symbol] = 'bullish'
            else:
                self.Security_trend[symbol] = 'netural'
        elif rsi[-1] > 70:
            # According to the literature (Investopedia.com):
            # - an rsi above 70 indicates an overbuying of the stock,
            #   which indicates bearish market on a downtrend
            if short_term < long_term:
                self.Security_trend[symbol] = 'bearish'
            else:
                self.Security_trend[symbol] = 'neutral'
        else:
            self.Security_trend[symbol] = 'neutral'
    
if __name__ == '__main__':
    Securities2Check = ['AAPL', '^GSPC', 'NVDA', 'TSLA', 'AMZN', 'GOOGL', 'MSFT', 'FB', 'V', 'JPM', 'JNJ', 'UNH', 'HD', 'PG', 'INTC', 'VZ', 'DIS', 'CSCO', 'KO', 'MRK', 'WMT', 'PFE', 'PEP', 'CMCSA', 'BAC', 'NFLX', 'T', 'XOM', 'CVX', 'BA', 'IBM', 'GS', 'MS', 'MMM', 'CAT', 'GE', 'MCD', 'NKE', 'AAPL', 'AMZN', 'GOOGL', 'MSFT', 'FB', 'V', 'JPM', 'JNJ', 'UNH', 'HD', 'PG', 'INTC', 'VZ', 'DIS', 'CSCO', 'KO', 'MRK', 'WMT', 'PFE', 'PEP', 'CMCSA', 'BAC', 'NFLX', 'T', 'XOM', 'CVX', 'BA', 'IBM', 'GS', 'MS', 'MMM', 'CAT', 'GE', 'MCD', 'NKE']
    
    investor = Investor(initialize=True)

    for symbol in Securities2Check:
        investor.determine_market_condition(symbol)

    print('breakpoint')
