import yfinance as yf
import finnhub as fh
import datetime as dt
import time
import pandas as pd
import numpy as np
# import requests
from dataclasses import dataclass

import TraderConstantData as tcd

@dataclass(frozen=True)
class CUtilityConstants:
    ''' Constants used in the utility functions. '''

    RSI_FACTOR_THRESHOLD = 5
    ''' The threshold for the difference between the short and long term returns to determine a trend. '''
    RSI_WINDOWS = [14, 30, 90, 180, 365, 1095, 1825]
    ''' The window sizes for the RSI calculation, each will be used to give an insight over the short term (most recent) trend.
        The windows are in days & correspond to the following: 2 weeks, 1 month, 3 months, 6 months, 1 year, 3 years & 5 years. '''

    SHORT_MA_WINDOW = 15
    ''' The window size for the short moving average. '''
    LONG_MA_WINDOW = 90
    ''' The window size for the long moving average. '''

    YF_DELAY = 0.3
    ''' The delay in seconds between each request to the Yahoo Finance API. '''

# def check_market_status(market: str = 'US') -> bool:
#     ''' Check if the market is open or closed. '''

#     datetime = dt.datetime.now()
#     tcd.StockExchangeOpHours['TASE']['Saturday']

#     return False # TODO: Implement this function

def retrieve_data_from_yahoo_finance(symbols: list[str], start_date: dt.datetime, end_date: dt.datetime) -> tuple[list[bool], list[float], list[yf.Ticker], pd.DataFrame]:
    ''' Retrieve security data from Yahoo Finance. '''

    Success = [True]*symbols.__len__()

    # Pause for a bit to avoid overloading the Yahoo Finance API
    time.sleep(CUtilityConstants.YF_DELAY)

    # Ticker object for the security
    tickerBundle = yf.Tickers(symbols)

    info = {ticker: tickerBundle.tickers[ticker].info for ticker in tickerBundle.symbols}
    currency = {ticker: info[ticker].get('currency', None) for ticker in tickerBundle.tickers}
    exchange = {ticker: info[ticker].get('exchange', None) for ticker in tickerBundle.tickers}

    history = yf.download(symbols, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), progress=False)

    current_prices = []
    ticker_out = []
    for ticker in tickerBundle.tickers:
        ticker_out.append(tickerBundle.tickers[ticker])

        current_price = tickerBundle.tickers[ticker].info.get('currentPrice', None)

        current_prices.append(tickerBundle.tickers[ticker].info.get('previousClose', None))
        
    return (Success, current_prices, ticker_out, history)

def retrieve_data_from_finnhub(symbol: str, start_date: dt.datetime, end_date: dt.datetime) -> tuple[bool, float, yf.Ticker, pd.DataFrame]:
    pass

def get_current_security_price_in_dollars(symbol: yf.Ticker):
    ''' Returns the current price of a security in dollars. '''

    ticker = yf.Ticker(symbol)
    currency = ticker.info['currency']

    if(currency != 'USD'):
        corrected_currency = tcd.CurrencyExchangePool[currency]
        tkr_currency_exchange = yf.Ticker(corrected_currency['to'] + "USD=X")
        currency_exchange = tkr_currency_exchange.history(period='1d')['Close'].iloc[-1]*corrected_currency['rate']

        current_price = ticker.info.get('previousClose', None)
        if(current_price == None):
            current_price = ticker.info.get('regularMarketPreviousClose', None)
            if(current_price == None):
                current_price = ticker.history(period='1d')['Close'].iloc[-1]

        return current_price*currency_exchange
    else:
        # info = ticker.info
        return ticker.history(period='1d')['Close'].iloc[-1]

def get_security_data(symbol, since_date:dt.datetime=None):
    ''' Returns the historical data of a security, changes to dollars if the currency is not traded in USD. '''

    ticker = yf.Ticker(symbol)
    stockExchange = ticker.info.get('exchange', None)

    if(stockExchange is None):
        # Ticker is not traded in a stock exchange, it could be an index or a currency
        pass

    if(since_date is None):
        history = yf.download(symbol, period='1y', progress=False)
    else:
        history = yf.download(symbol, start=since_date.strftime('%Y-%m-%d'), progress=False)

    if history.empty:
    #     check_market_status(stockExchange)
        pass

    currency = ticker.info['currency']
    if(currency != 'USD'):
        corrected_currency = tcd.CurrencyExchangePool[currency]
        tkr_currency_exchange = yf.Ticker(corrected_currency['to'] + "USD=X")
        currency_exchange = tkr_currency_exchange.history(period='1d')['Close'].iloc[-1]*corrected_currency['rate']
        
        current_price = ticker.info.get('previousClose', None)
        if(current_price == None):
            current_price = ticker.info.get('regularMarketPreviousClose', None)

        ask2LastClose = current_price/history['Close'].iloc[-1].iloc[-1]
        if(ask2LastClose >= (1/corrected_currency['rate'])):
            currency_exchange /= corrected_currency['rate']

        history['Close']    *= currency_exchange
        history['Open']     *= currency_exchange
        history['High']     *= currency_exchange
        history['Low']      *= currency_exchange

    return (ticker, history)

def get_PE_ratio(ticker: yf.Ticker):
    ''' Returns the price over earnings (PE) ratio of a security. '''

    if ticker.info['quoteType'] != 'EQUITY':
        return np.nan
    
    PE = ticker.info.get('trailingPE', None)
    if PE is None:
        PE = ticker.info.get('forwardPE', None)
        if PE is None:
            PE = ticker.info.get('pegRatio', None)

    return PE

def calculate_rsi(prices: np.ndarray, window: int = 14):
    ''' Calculate the Relative Strength Index (RSI) of a security. '''

    if(prices.ndim == 1):
        flattened_prices = prices
    else:
        flattened_prices = prices.flatten()

    deltas = np.diff(flattened_prices, axis=0)
    seed = deltas[:window+1] # Seed is the first window deltas
    up = seed[seed >= 0].sum()/window
    down = -seed[seed < 0].sum()/window
    rs = up/down
    rsi = np.zeros_like(flattened_prices)
    rsi[:window] = 100.*(1. - 1./(1. + rs))
        
    for i in range(window, len(flattened_prices)):
        delta = deltas[i - 1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
        
        up = (up*(window - 1) + upval)/window
        down = (down*(window - 1) + downval)/window

        rs = up/down
        rsi[i] = 100. - 100./(1. + rs)
    
    return rsi

def calculate_risk_free_rate(risk_free_security='^IRX', since_date:dt.datetime=None):
        ''' Calculates the risk-free rate of a security. '''

        end_date = dt.datetime.now()
        if(since_date is None):
            # Set the date to one year ago
            
            since_date = end_date - dt.timedelta(days=365)

        end_date = dt.datetime(end_date.year, end_date.month, 1)    # Set the date to the first day of the month
                                                                    # to be included in the calculation 
                                                                    # for the end date so that the for loop ends 
                                                                    # with all the relevant months included

        # Set the date to the first day of the month to be included in the calculation
        since_date = dt.datetime(since_date.year, since_date.month, 1)

        # HData = yf.download(risk_free_security, start=since_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), progress=False)['Close']
        HData = yf.download(risk_free_security, start=since_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), progress=False)

        monthly_returns = extract_monthly_returns_from_data(HData)

        risk_free_rate = np.mean(monthly_returns)

        return risk_free_rate
    
def extract_monthly_returns_from_data(data: pd.DataFrame) -> np.ndarray:
    ''' Extracts the monthly returns from a given DataFrame. '''

    # Validate full months are present

    # Calculate the monthly returns
    Current_Month = data.index[0].month
    starting_price = data['Close'].iloc[0].iloc[0]
    monthly_returns = []
    for i in range(1, len(data)):
        if data.index[i].month != Current_Month or i == data.__len__() - 1:
            monthly_returns.append((data['Close'].iloc[i-1].iloc[0] - starting_price)/starting_price)

            starting_price = data['Close'].iloc[i].iloc[0]
            Current_Month = data.index[i].month

    return np.array(monthly_returns) * 100

def Volatility(prices: pd.DataFrame, method: str = 'daily') -> float:
    ''' Calculate the volatility of a security. Supports daily and monthly volatility calculations.
        Volatility measures the dispersion of returns for a given security or market index at a yearly rate. '''

    if method == 'daily':
        log_returns = np.diff(np.log(prices['Close'].values))
        volatility = np.std(log_returns) * np.sqrt(252)  # Annualize the daily volatility
    elif method == 'monthly':
        monthly_returns = extract_monthly_returns_from_data(prices)
        volatility = np.std(monthly_returns) * np.sqrt(12)  # Annualize the monthly volatility
    else:
        raise ValueError("Unsupported volatility calculation method. Use 'daily' or 'monthly'.")
    return volatility

# DEBUG Utilities
CURRENT_DATE_OVERRIDE_4_DEBUG: dt.datetime = None

# Test utility functions
if __name__ == "__main__":
    yf.enable_debug_mode()

    # test the retrieve_data_from_yahoo_finance function
    start_date = dt.datetime.now() - dt.timedelta(days=365)
    end_date = dt.datetime.now()

    # Testing for a stock, an american ETF, and israeli ETF, and an index
    Success, price, ticker, history = retrieve_data_from_yahoo_finance(['NVDA', 'SPY', 'IS-FF101.TA', '^GSPC'], start_date, end_date)

