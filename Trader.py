import yfinance as yf
import pandas as pd
import numpy as np
import random as rnd

import datetime as dt

from dataclasses import dataclass

import FPG_Utils

@dataclass
class C_trader_traits:
    @dataclass
    class personality_based:
        trade_frequency:        float   = 0 
        ''' Represents how often a trader engages in buying or selling \n
            can also fit for high frequency trading '''
        
        decision_making_speed:  float   = 0 
        ''' Some traders act impulsively, while others deliberate '''
        
        risk_appetite:          float   = 0 
        ''' not taking risks at all <- [0 1] -> irrational risk taking \n
            Determines if a trader is risk-averse, neutral, or seeking risk '''
    
    @dataclass
    class behavioral_based:
        herd_mentality: float = 0 
        ''' not following any herd <- [0 1] -> can't make descisions on its own \n
            Likelihood of mimicking others' trades '''
        
        rationality: float = 0 
        ''' stoic rationality <- [0 1] -> totally irrational \n
            Weight assigned to logical analysis versus emotional decisions '''
        
        # Biases: # Tendencies like loss aversion or overconfidence.
    
    @dataclass
    class strategy_oriented:
        short_term_vs_long_term: float = 0  
        ''' day trader <- [0 1] -> investor \n
            Day traders versus investors '''
        
        technical_vs_fundamental_analysis: float = 0    
        ''' according to charts, patterns, and indicators <- [0 1] -> according to earnings, P/E ratios, and macroeconomic factors \n
            Preferred methods for making decisions '''
        
        Diversification: float = 0 
        ''' one stock is enough <- [0 1] -> the more the better \n
            Willingness to spread investments across multiple assets '''

    @dataclass
    class environmental_influences:
        market_sentiment: float = 0 
        ''' sticks to its own investing strategy <- [0 1] -> changes strategy on every whim \n
            Reactivity to news, trends, or market signals '''
        
        popularity_dependence: float = 0    
        ''' doesn't case about buzz stocks <- [0 1] -> cares alot \n
            Interest in trending or popular stocks '''
        
        information_advantage: bool = 0 
        ''' Access to exclusive or early information. this should very rarely be true '''
    
    def __init__(self, Data):
        self.securityBiases = {ticker: np.random.rand() for ticker in Data.Market.tickers}
        ''' Personal bias about each security '''

        # Personality traits
        possible_trade_frequencies = [7, 14, 21, 30, 60, 90, 120, 180, 365]
        self.personality_based.trade_frequency = possible_trade_frequencies[np.random.randint(possible_trade_frequencies.__len__())]

        self.personality_based.decision_making_speed    = np.random.rand()
        self.personality_based.risk_appetite            = np.random.rand()

        # Behavioral traits
        self.behavioral_based.herd_mentality            = np.random.rand()
        self.behavioral_based.rationality               = np.random.rand()

        # Strategic traits
        self.strategy_oriented.short_term_vs_long_term              = np.random.rand()
        self.strategy_oriented.technical_vs_fundamental_analysis    = np.random.rand()
        self.strategy_oriented.Diversification                      = np.random.rand()

        # Market environment-related traits
        insider_ratio = 0.02 # Percent of the population that has access to insider information

        self.environmental_influences.market_sentiment              = np.random.rand()
        self.environmental_influences.popularity_dependence         = np.random.rand()
        self.environmental_influences.information_advantage         = np.random.rand() <= insider_ratio

class Trader:
    def __init__(self, Inp, Data) -> None:
        ''' 
            Trader class, represents a single trader unit in the world market
            Inp: Input data of the FPG simulation
            Data: General data structure that is carried throughout the simulation 
        '''

        class_idx = np.where(rnd.random() < Data.Market.wealthDistribution)[0][0]
        Data.Market.wealthNPopulation[class_idx] += 1

        if(class_idx < Data.Market.wealthThresholds.__len__()):
            if(class_idx > 0):
                minWealth = Data.Market.wealthThresholds[class_idx-1]
            else:
                minWealth = 0
            maxWealth = Data.Market.wealthThresholds[class_idx]
        else:
            minWealth = Data.Market.wealthThresholds[-1]
            maxWealth = Data.Market.totalMarketCap/Data.Market.traderPoolSize

        self.balance        = rnd.uniform(minWealth,maxWealth)
        ''' Avaialable cash a trader has to make trades '''

        self.income         = self.calculate_income(Data)
        ''' Income level, obtains that amount (+ uncertainties) once every income_freq days '''

        self.income_sigma = FPG_Utils.monthly_income_STD(Data.Market.meanIncome, Data.Market.giniCoeff)

        self.income_freq    = 30
        ''' Days interval after which the trader gets its income (for now keep it constant at 30 days) '''

        self.time_since_last_trade = 0
        ''' Days past since last trade '''

        self.traits = C_trader_traits(Data)

        # self.Portfolio = C_trader_portfolio(self, Data)
        self.Portfolio = {ticker: {'Holdings': 0, 'ask': 0, 'bid': 0, 'Active': Data.Companies[ticker].Active} for ticker in Data.Market.tickers}
        ''' Trader's portfolio, shows each stock in the market, how many holdings the trader has forr each stock,\n
            asking price (if wants to buy) and selling price (if has any holdings and wants to sell) '''

    def _canTrade(self,dt):
        """
            Determines if a trader is ready to make trades based on trade frequency and randomness.

            Args:
                dt: Time increment (e.g., days) since the last check.

            Returns:
                bool: True if the trader is ready to trade, False otherwise.
        """
        # Stochastic threshold based on trade frequency
        trade_threshold = self.traits.personality_based.trade_frequency + \
                        rnd.gauss(0, np.sqrt(self.traits.personality_based.trade_frequency))

        # Update time since last trade
        self.time_since_last_trade += dt

        # Check if the threshold has been met
        if self.time_since_last_trade > trade_threshold:
            self.time_since_last_trade = 0  # Reset the counter
            return True
        return False

    def calculate_income(self, Data, mode = 'Init') -> float:
        ''' Computes monthly income '''
        if(mode == 'Init'):
            if(Data.Market.giniCoeff < 0.5):
                # Pareto distribution for Gini < 0.5
                if Data.Market.alphaCoeff <= 1:
                    raise ValueError("Invalid alpha derived from Gini coefficient. Check inputs.")
                
                # Calculate minimum income (x_min) to match the mean income
                x_min = Data.Market.meanIncome * (Data.Market.alphaCoeff - 1) / Data.Market.alphaCoeff
                
                # Generate Pareto incomes
                income = (np.random.pareto(Data.Market.alphaCoeff) + 1) * x_min
            else:
                sigma = 2 * Data.Market.giniCoeff  # Example scaling factor; fine-tune for accuracy
                mu = np.log(Data.Market.meanIncome) - (sigma**2 / 2)
                
                # Generate log-normal income
                income = np.random.lognormal(mu, sigma)
        else: # Mode 'Update'
            pass
        
        return (income/12.0)

    def adjust_traits(self):
        pass

    def adjust_balance(self, Data):
        if(np.mod(Data.Market.day,self.income_freq) == 0):
            self.balance += np.max([np.random.normal(self.income, self.income_sigma) ,0.0])

    def trading_day(self, Data, mode='Reg'):

        dt = 1
        if(self._canTrade(dt) or mode == 'Init'):
            for ticker in Data.Market.tickers:
                pass

        pass

# class C_trader_portfolio:
#     def __init__(self, trader: Trader, Data):
        
#         pass
#     pass

if __name__ == "__main__":
    pass