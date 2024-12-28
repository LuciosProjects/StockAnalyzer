__author__      = "Lucio"
__maintainer__  = "Lucio"
__annotations__ = "This module contains the Portfolio class to manage the portfolio of the user."
__version__     = "1.0"

import sqlite3
import datetime as dt
import numpy as np
import pandas as pd
import os
import yfinance as yf

import Utilities as util
import TraderConstantData as tcd

class Portfolio:
    ''' Portfolio class to manage the portfolio of the user. '''

    def __init__(self, db_name='portfolio.db' ,initial_balance=100000, initialize=False):

        # general attributes
        self.db_name        = db_name

        self.balance            = initial_balance
        ''' Available cash for trades. '''
        self.avg_price          = {}
        ''' Average purchase price for each security in the portfolio. '''
        self.holdings           = {}
        ''' Number of shares held for each security in the portfolio. '''
        self.Return            = {}
        ''' Return (percentage of the cost used fo rthe security) for each security in the portfolio. '''
        self.totalReturn       = 0
        ''' Total return (percentage of the cost used for the securities) in the portfolio. '''
        self.PnL                = {}
        ''' Profit or loss (absolute value) for each security in the portfolio. '''
        self.totalPnL           = 0
        ''' Total profit or loss (absolute value) in the portfolio. '''
        self.totalCost          = 0
        ''' Total costs of the securities in the portfolio. '''
        self.netWorth           = self.balance  # net worth is the sum of balance and totalPnL, 
                                                # totalPnL is not considered here since it is initialized to 0
        ''' Net worth of the portfolio, balance + total worth of the securities. '''
        self.last_purchase_date = None
        ''' last recorded purchase date. '''
        self.inception_date     = None
        ''' inception date of the portfolio. '''

        # Security attributes
        self.Volatility         = {}
        ''' Volatility for each security in the portfolio. '''
        self.totalVolatility   = 0
        ''' Total volatility of the portfolio. '''

        # fees
        self.transaction_fee = 5
        '''  Transaction fee in dollars, it goes by 1 cent per share at a minimum fee of $5. '''
        self.revenue_rate_fee = 0.25
        ''' Revenue rate fee factor, it is used to calculate the selling fee based on the return. '''

        # create tables
        if initialize:
            self.initialize_portfolio(initial_balance)
        else:
            self.load_portfolio()
            self.update_portfolio_status()

    def initialize_portfolio(self, initial_balance):
        ''' Initializes the portfolio with the initial balance
            and deletes any existing database of the same name. '''

        # Overwrite the database with initial values
        if(os.path.exists(self.db_name)):
            os.remove(self.db_name)
        self._connect_to_db()

        self.balance                    = initial_balance
        self.avg_price                  = {}
        self.closing_price              = {}
        self.holdings                   = {}
        self.Return                     = {}
        self.totalReturn                = 0
        self.return_since_last_month    = 0
        self.PnL                        = {}
        self.totalPnL                   = 0
        self.totalCost                  = 0  
        self.netWorth                   = self.balance  # net worth is the sum of balance and totalPnL, 
                                                # totalPnL is not considered here since it is initialized to 0
        self.Volatility                 = {}
        self.totalVolatility            = 0

        self.last_purchase_date = None
        self.inception_date     = dt.datetime.now()
        
    def delete_data(self):
        ''' Deletes all data from the database. '''

        with self.conn:
            self.conn.execute('DELETE FROM transactions')
            self.conn.execute('DELETE FROM portfolio')
            self.conn.commit()
        print("All data deleted from the database.")

    def _connect_to_db(self):
        ''' Connects to the database. '''
        self.conn   = sqlite3.connect(self.db_name)
        self.c      = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        ''' Creates the tables in the database if they do not exist. '''

        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS transactions (
                                    id INTEGER PRIMARY KEY,
                                    date TEXT,
                                    action TEXT,
                                    symbol TEXT,
                                    price REAL,
                                    quantity INTEGER,
                                    fee REAL,
                                    status TEXT)''')            
            self.conn.execute('''CREATE TABLE IF NOT EXISTS portfolio (
                                    id INTEGER PRIMARY KEY,
                                    date TEXT,
                                    balance REAL,
                                    holdings TEXT,
                                    avg_price TEXT,
                                    closing_price TEXT, 
                                    Return TEXT,
                                    totalReturn REAL,
                                    return_since_last_month REAL,
                                    PnL TEXT,
                                    totalPnL REAL,
                                    totalCost REAL,
                                    netWorth REAL,
                                    Volaility REAL,
                                    totalVolatility REAL,
                                    last_purchase_date TEXT,
                                    inception_date TEXT)''')

    def load_portfolio(self):
        ''' Loads the portfolio from the database. '''

        if(not os.path.exists(self.db_name)):
            raise RuntimeError("Database does not exist. Please initialize the portfolio first.")
        else:
            self._connect_to_db()

        cursor = self.conn.execute('SELECT balance, holdings, avg_price, closing_price, Return, totalReturn, return_since_last_month, PnL, totalPnL, totalCost, netWorth, Volaility, totalVolatility, last_purchase_date, inception_date  FROM portfolio ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        if row:
            # ASSIGNMENT ORDER IS CRUCIALLY IMPORTANT HERE!
            i = 0
            self.balance                    = row[i]; i += 1
            self.holdings                   = eval(row[i]); i += 1  # Convert string back to dictionary
            self.avg_price                  = eval(row[i]); i += 1  # Convert string back to dictionary
            self.closing_price              = eval(row[i]); i += 1  # Convert string back to dictionary
            self.Return                     = eval(row[i]); i += 1  # Convert string back to dictionary
            self.totalReturn                = row[i]; i += 1
            self.return_since_last_month    = row[i]; i += 1
            self.PnL                        = eval(row[i]); i += 1  # Convert string back to dictionary
            self.totalPnL                   = row[i]; i += 1
            self.totalCost                  = row[i]; i += 1
            self.netWorth                   = row[i]; i += 1
            self.Volatility                 = eval(row[i]); i += 1  # Convert string back to dictionary
            self.totalVolatility            = row[i]; i += 1
            self.last_purchase_date         = dt.datetime.strptime(row[i], '%Y-%m-%d %H:%M:%S') if row[i] else None; i += 1   # Convert string back to datetime
            self.inception_date             = dt.datetime.strptime(row[i], '%Y-%m-%d %H:%M:%S') if row[i] else None           # Convert string back to datetime

    def save_portfolio(self, date: dt.datetime = None):
        ''' Saves the portfolio to the database. '''

        if(date == None):
            date = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.update_portfolio_status()
        recorded_last_purchase_date = self.last_purchase_date.strftime('%Y-%m-%d %H:%M:%S') if self.last_purchase_date else None

        with self.conn:
            # self.conn.execute('DELETE FROM portfolio')  # Delete the existing data
            self.conn.execute('''INSERT INTO portfolio (date, balance, holdings, avg_price, closing_price, Return, totalReturn, return_since_last_month, PnL, totalPnL, totalCost, netWorth, Volaility, totalVolatility, last_purchase_date, inception_date)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                              (date, 
                               self.balance, str(self.holdings), str(self.avg_price), str(self.closing_price),
                               str(self.Return), self.totalReturn, self.return_since_last_month, str(self.PnL), self.totalPnL, 
                               self.totalCost, self.netWorth, str(self.Volatility), self.totalVolatility,
                               recorded_last_purchase_date, self.inception_date.strftime('%Y-%m-%d %H:%M:%S')))
            self.conn.commit()  # Save the changes to the database
    
    def record_transaction(self, date: dt.datetime, action: str, symbol: str, price: float, quantity: int, fee: float, status: str=''):
        ''' Records the transaction in the database. '''
        with self.conn:
            self.conn.execute('''INSERT INTO transactions (date, action, symbol, price, quantity, fee, status)
                                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
                              (date.strftime('%Y-%m-%d %H:%M:%S'), action, symbol, price, quantity, fee, status))
            self.conn.commit()  # Save the changes to the database
    
    def buy(self, date: dt.datetime, symbol, price, quantity):
        ''' Buys the given quantity of the stock at the given price if possible. '''
        purchase_fee = max([self.transaction_fee , quantity*0.01])
        total_cost = price * quantity + purchase_fee
        if self.balance >= total_cost:
            self.balance -= total_cost
            if symbol in self.holdings:
                self.avg_price[symbol]  = ((self.avg_price[symbol] * (self.holdings[symbol])) + (price * quantity)) / (self.holdings[symbol] + quantity)
                self.holdings[symbol]  += quantity
                self.Return[symbol]     = (price - self.avg_price[symbol])*self.holdings[symbol]/(self.avg_price[symbol]*self.holdings[symbol])
            else:
                # The security is bought for the first time
                self.holdings[symbol]   = quantity
                self.avg_price[symbol]  = price
                self.Return[symbol]     = 0
                self.Volatility[symbol] = 0 # Initialize the volatility of the security if it's bought for the first time

            self.record_transaction(date, 'BUY', symbol, price, quantity, purchase_fee)

            self.last_purchase_date = date

            self.update_portfolio_status()
        else:
            self.record_transaction(date, 'BUY', symbol, price, quantity, 0, status='FAILED: Insufficient funds')
            # print("Insufficient funds to buy")

    def sell(self, date: dt.datetime, symbol, price, quantity):
        ''' Sells the given quantity of the stock at the given price if possible. '''

        if(quantity > self.holdings[symbol]):
            corrected_quantity = self.holdings[symbol]

            # The desired quantity is more than the holdings, so all shares of the security are sold.
            MSG = f"SUCCESS, sold {corrected_quantity} shares out of desired {quantity} of {symbol}, remaining: 0."
        else:
            corrected_quantity = quantity

            # The desired quantity is less than or equal to the holdings, so the desired quantity of shares of the security are sold.
            MSG = f"SUCCESS, sold {corrected_quantity} shares of {symbol}, remaining: {self.holdings[symbol] - corrected_quantity} shares."

        if symbol in self.holdings and self.holdings[symbol] >= corrected_quantity:
            total_Return = price * corrected_quantity
            total_fee = max([corrected_quantity * (price - self.avg_price[symbol]) * self.revenue_rate_fee, 0])

            self.balance += total_Return - total_fee
            self.holdings[symbol] -= corrected_quantity

            if self.holdings[symbol] == 0:
                del self.holdings[symbol]
                del self.avg_price[symbol]
                del self.Return[symbol]
                del self.closing_price[symbol]
                del self.PnL[symbol]
            else:
                self.Return[symbol] = (price - self.avg_price[symbol])*self.holdings[symbol]/(self.avg_price[symbol]*self.holdings[symbol])

            self.record_transaction(date, 'SELL', symbol, price, corrected_quantity, total_fee, status=MSG)

            self.update_portfolio_status()
        else:
            MSG = f"FAILED: Insufficient holdings of {symbol} to sell (desired: {quantity})."
            self.record_transaction(date, 'SELL', symbol, 0, 0, 0, status=MSG)
            # print("Insufficient holdings to sell")
    
    def evaluate_securities_to_sell(self):
        ''' Evaluates the securities to sell based on rsi & security trend'''
        
        for symbol, _ in self.Return.items():
            ticker, Hdata = util.get_security_data(symbol)

            short_term  = (((Hdata['Close'].iloc[-1] - Hdata['Close'].iloc[-util.CUtilityConstants.SHORT_MA_WINDOW])/Hdata['Close'].iloc[-util.CUtilityConstants.SHORT_MA_WINDOW])*100).iloc[0]
            long_term   = (((Hdata['Close'].iloc[-1] - Hdata['Close'].iloc[-util.CUtilityConstants.LONG_MA_WINDOW])/Hdata['Close'].iloc[-util.CUtilityConstants.LONG_MA_WINDOW])*100).iloc[0]

            rsi = util.calculate_rsi(Hdata['Close'].values, util.CUtilityConstants.RSI_WINDOWS[0]) # Relative Strength Index (RSI) represents the momentum of the stock's price

            if  rsi[-1] < 30:
                # According to the literature (Investopedia.com):
                # - an rsi below 30 indicates an overselling of the stock, 
                #   which indicates bullish market on an uptrend.
                #   Trends don't matter in this case because the stock is already oversold, leading to bad selling conditions.
                
                # Do nothing, keep looking for good securities to sell in the portfolio
                pass
            elif rsi[-1] > 70:
                # According to the literature (Investopedia.com):
                # - an rsi above 70 indicates an overbuying of the stock,
                #   which indicates bearish market on a downtrend

                if short_term < long_term:
                    return True
                
                # Else do nothing, uptrends during overbuying are not good selling conditions
            else:
                # Unclear selling conditions, better to keep the security
                pass

        return False # if no security is found to be good for selling, return False

    def update_portfolio_status(self):
        ''' Updates the portfolio status: Return, individual security profits & losses, total return, and total profits & losses. '''
        self.Return                     = {}
        self.PnL                        = {}
        self.totalReturn                = 0
        self.totalPnL                   = 0
        self.totalCost                  = 0
        self.netWorth                   = self.balance

        for symbol, quantity in self.holdings.items():
            current_price = util.get_current_security_price_in_dollars(symbol)
            _, Hdata = util.get_security_data(symbol)

            self.closing_price[symbol]  = current_price
            self.Return[symbol]         = (current_price - self.avg_price[symbol]) / self.avg_price[symbol] * 100
            self.PnL[symbol]            = (current_price - self.avg_price[symbol]) * quantity

            self.totalPnL   += self.PnL[symbol]
            self.totalCost  += self.avg_price[symbol]*self.holdings[symbol]
            self.netWorth   += self.holdings[symbol]*current_price

            self.Volatility[symbol] = util.Volatility(Hdata, 'monthly')

        if self.totalCost > 0:
            self.totalReturn = (self.totalPnL / self.totalCost) * 100

        self.return_since_last_month    = self._get_portfolio_monthly_return()

        returns = self.get_portfolio_historical_monthly_data()
        self.totalVolatility = np.std(returns['return_since_last_month']) * np.sqrt(12) # Annualize the volatility

    def get_portfolio_status(self):
        ''' Returns the portfolio status: current balance, holdings, Return, total Return, profits & losses, and total profits & losses. '''
        self.update_portfolio_status()
        return {
            'balance': self.balance,
            'holdings': self.holdings,
            'Return': self.Return,
            'closing_price': self.closing_price,
            'totalReturn': self.totalReturn,
            'PnL': self.PnL,
            'totalPnL': self.totalPnL,
            'netWorth': self.netWorth 
        }
    
    ## Portfolio metrics functions
    def compare_portfolio_performance_to_index(self, index_symbol = '^GSPC', since_date: dt.datetime=None):
        ''' Compares the portfolio performance to the given index. '''

        if(since_date is None):
            since_date = self.inception_date

        portfolio_return = self._get_portfolio_return_since(since_date)

        _, index_data = util.get_security_data(index_symbol, since_date)
        index_return = ((index_data['Close'].iloc[-1] - index_data['Close'].iloc[0]) / index_data['Close'].iloc[0] * 100).iloc[0]

        return (portfolio_return - index_return) # The output is the difference between the portfolio return and the index return in [%]

    def _get_portfolio_monthly_return(self) -> float:
        ''' Returns the monthly return of the portfolio. '''

        cursor = self.conn.execute('SELECT date, totalPnL FROM portfolio ORDER BY date ASC')
        rows = cursor.fetchall()

        if(len(rows) == 0):
            # No returns were recorded in the database yet
            return 0
        
        # Find the closest date to the beginning of this month
        # current_date = dt.datetime.now()
        current_date = util.CURRENT_DATE_OVERRIDE_4_DEBUG # for testing purposes
        current_month_start = dt.datetime(current_date.year, current_date.month, 1)

        delta_days = 32 # maximum days in a month + 1
        closest_date_row = None # Initialize the closest date row to None to avoid errors
        for row in rows:
            candiDATE = dt.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
            if (np.abs(candiDATE - current_month_start).days < delta_days and # if the date is closer to the beginning of the month
                ((current_month_start.month > candiDATE.month) or (current_month_start.month == 1 and candiDATE.month == 12))): # and the date is in the previous month
                delta_days = np.abs(candiDATE - current_month_start).days
                closest_date_row = row
        
        if(closest_date_row):
            prev_total_PnL = closest_date_row[1]

            return_since_last_month = (self.totalPnL - prev_total_PnL) / (self.totalCost + prev_total_PnL) * 100
            return return_since_last_month
        else:
            return 0 

    def _get_portfolio_return_since(self, since_date: dt.datetime=None) -> float:
        ''' Returns the return of the portfolio since the given date 
            (closest date to the given since_date that is recorded in the database). '''

        if(since_date is None):
            since_date = self.inception_date

        cursor = self.conn.execute('SELECT date, totalPnL FROM portfolio ORDER BY date ASC')
        rows = cursor.fetchall()

        if(len(rows) == 0):
            # No returns were recorded in the database yet
            return 0
        
        # Find the closest date to the given since_date
        delta_days = 999 # Just a large number to start with
        prev_delta_days = delta_days # Same value as delta_days for convenience
        closest_date_row = None # Initialize the closest date row to None to avoid errors
        for row in rows:
            candiDATE = dt.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
            temp_delta = np.abs(candiDATE - since_date).days

            if(prev_delta_days < temp_delta):
                break

            if (temp_delta < delta_days):
                delta_days = temp_delta
                closest_date_row = row

            prev_delta_days = temp_delta

        if(closest_date_row):
            prev_total_PnL = closest_date_row[1]

            returnVal = (self.totalPnL - prev_total_PnL) / (self.totalCost + prev_total_PnL) * 100
            return returnVal
        else:
            return 0

    def get_portfolio_historical_monthly_data(self, period="1y"):
        ''' Returns the historical data of the portfolio's total returns. '''

        cursor = self.conn.execute('SELECT date, return_since_last_month FROM portfolio ORDER BY date ASC')
        rows = cursor.fetchall()
        data = {'date': [], 'return_since_last_month': []}
        for row in rows:
            # Append the latest date of the month
            current_date = dt.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
            if(data['date'].__len__() > 0 and 
               current_date.month == data['date'][-1].month and
               current_date.day > data['date'][-1].day):
                # Found a later day of the same month
                data['date'][-1] = current_date
                data['return_since_last_month'][-1] = row[1]
            else:
                # Found a new month
                data['date'].append(current_date)
                data['return_since_last_month'].append(row[1])

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    def Sharpe(self, risk_free_security='^IRX', since_date: dt.datetime=None):
        ''' Calculates the Sharpe ratio of the portfolio.\n
            The Sharpe ratio is the average return earned in excess of the risk-free rate per unit of volatility or total risk. '''

        if(since_date is None):
            since_date = self.inception_date

        returns = self.get_portfolio_historical_monthly_data()['return_since_last_month']
        risk_free_rate = util.calculate_risk_free_rate(risk_free_security, since_date)

        excess_returns = returns.values - risk_free_rate
        sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns)

        return sharpe_ratio

    def Sortino(self, risk_free_security='^IRX', since_date: dt.datetime=None):
        ''' Calculates the Sortino ratio of the portfolio.\n
            The Sortino ratio is a variation of the Sharpe ratio that only factors in the downside risk. '''
        
        returns = self.get_portfolio_historical_monthly_data()['return_since_last_month']
        risk_free_rate = util.calculate_risk_free_rate(risk_free_security, since_date)

        excess_returns = returns.values - risk_free_rate
        downside_returns = excess_returns[excess_returns < 0]

        if(downside_returns.__len__() == 0):
            # No downside risk, all excess returns are positive
            sortino_ratio = np.inf
        else:
            sortino_ratio = np.mean(excess_returns) / np.std(downside_returns)

        return sortino_ratio

    def Beta(self, market_index='^GSPC', since_date: dt.datetime=None):
        ''' Calculates the Beta of the portfolio.\n
            The Beta is a measure of the volatility of the portfolio compared to the market index. '''

        returns = self.get_portfolio_historical_monthly_data()['return_since_last_month'].values

        _, Market_HData = util.get_security_data(market_index, since_date)
        market_monthly_returns = util.extract_monthly_returns_from_data(Market_HData)

        beta = np.cov(returns, market_monthly_returns)[0, 1] / np.var(market_monthly_returns)

        return beta

    def Alpha(self, market_index='^GSPC', risk_free_security='^IRX', since_date: dt.datetime=None):
        ''' Calculates the Alpha of the portfolio.\n
            The Alpha is a measure of the active return on an investment, 
            the performance of the portfolio compared to a benchmark index. '''
        
        returns = self.get_portfolio_historical_monthly_data()['return_since_last_month'].values
        _, Market_HData = util.get_security_data(market_index, since_date)

        market_monthly_returns = util.extract_monthly_returns_from_data(Market_HData)

        risk_free_rate = util.calculate_risk_free_rate(risk_free_security, since_date)

        excess_returns = returns - risk_free_rate
        market_excess_returns = market_monthly_returns - risk_free_rate

        beta = self.Beta(market_index, since_date)

        alpha = np.mean(excess_returns) - beta * np.mean(market_excess_returns)

        return alpha

    ## Built-in functions' overrides
    def __str__(self):
        status = self.get_portfolio_status()

        for key, value in status.items():
            if key == 'holdings': # holdings prints
                if(value == {}):
                    print(f"{key}: None")
                else:
                    print(f"{key}:")
                    for symbol, quantity in value.items():
                        print(f"  {symbol}: {quantity}, avg price: ${self.avg_price[symbol]:.2f}, current price: ${self.closing_price[symbol]:.2f}, Return: {self.Return[symbol]:.2f}%")

            elif key == 'totalReturn': # %-type prints
                print(f"{key}: {value:.2f}%")
            elif key in ['balance', 'totalPnL', 'netWorth']: # $-type prints
                print(f"{key}: ${value:.2f}")
        
        return ''


def close_and_reconnect_to_db(self: Portfolio, date: dt.datetime = None):
    ''' Closes the connection to the database and reconnects.
        No object needs to be returned since the object is passed by reference. '''

    if(date == None):
        date = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    self.save_portfolio(date)
    self.conn.close()

    self.conn = sqlite3.connect(self.db_name)
    self.load_portfolio()

if __name__ == '__main__':
    p = Portfolio(initialize=True)
    print(p)

    starting_date = dt.datetime(2024, 8, 1, 16, 0, 0)

    date = starting_date
    util.CURRENT_DATE_OVERRIDE_4_DEBUG = date
    p.buy(date, 'IN-FF1.TA', 1120, 15)
    close_and_reconnect_to_db(p, date)

    date = dt.datetime(2024, 8, 4, 16, 0, 0)
    util.CURRENT_DATE_OVERRIDE_4_DEBUG = date
    p.buy(date, 'NVDA', 130, 10)
    close_and_reconnect_to_db(p, date)

    date = dt.datetime(2024, 8, 8, 16, 0, 0)
    util.CURRENT_DATE_OVERRIDE_4_DEBUG = date
    p.buy(date, 'IS-FF101.TA', 36, 300)
    close_and_reconnect_to_db(p, date)

    date = dt.datetime(2024, 8, 16, 16, 0, 0)
    util.CURRENT_DATE_OVERRIDE_4_DEBUG = date
    p.buy(date, 'IS-FF301.TA', 79, 200)
    close_and_reconnect_to_db(p, date)

    date = dt.datetime(2024, 8, 27, 16, 0, 0)
    util.CURRENT_DATE_OVERRIDE_4_DEBUG = date
    p.buy(date, 'IN-FF1.TA', 1107, 20)
    close_and_reconnect_to_db(p, date)

    date = dt.datetime(2024, 9, 1, 16, 0, 0)
    util.CURRENT_DATE_OVERRIDE_4_DEBUG = date
    p.buy(date, 'AAPL', 229, 10)
    close_and_reconnect_to_db(p, date)

    date = dt.datetime(2024, 10, 1, 16, 0, 0)
    util.CURRENT_DATE_OVERRIDE_4_DEBUG = date
    p.buy(date, 'GOOGL', 167, 10)
    close_and_reconnect_to_db(p, date)

    date = dt.datetime(2024, 11, 1, 16, 0, 0)
    util.CURRENT_DATE_OVERRIDE_4_DEBUG = date
    p.buy(date, 'TSLA', 250, 10)
    close_and_reconnect_to_db(p, date)

    date = dt.datetime(2024, 12, 1, 16, 0, 0)
    util.CURRENT_DATE_OVERRIDE_4_DEBUG = date
    # p.sell(dt.datetime.now(), 'AAPL', p.closing_price['AAPL'], 10)
    p.sell(date, 'AAPL', util.get_current_security_price_in_dollars('AAPL'), 11)
    close_and_reconnect_to_db(p, date)

    relative_performance = p.compare_portfolio_performance_to_index(tcd.MarketIndicesPool.SP500['symbol'], since_date=starting_date)
    rSharpe = p.Sharpe(since_date=starting_date)
    rSortino = p.Sortino(since_date=starting_date)
    Alpha = p.Alpha(since_date=starting_date)
    Beta = p.Beta(since_date=starting_date)

    print(p)
    print(f"Relative performance to S&P 500: {relative_performance:.2f}%")
    print(f"Sharpe ratio: {rSharpe:.2f}")
    print(f"Sortino ratio: {rSortino:.2f}")
    print(f"Alpha: {Alpha:.2f}")
    print(f"Beta: {Beta:.2f}")
    p.conn.close()

