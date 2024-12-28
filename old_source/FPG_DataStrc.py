import numpy as np
import random as rnd
import pandas as pd
import gc

from dataclasses import dataclass

from FPG_Inp import FPG_Input
from Company import Company
from Trader import Trader

import FPG_Reference_Utils as FPG_RefUtils
import FPG_Utils

@dataclass
class FPG_RefData:
    World_idx      = pd.DataFrame()
    Sector_idx     = pd.DataFrame()
    Geographic_idx = pd.DataFrame()

@dataclass
class FPG_Manager:
    randomSeed: int     = 0
    numTotalDays: int   = 0
    start_date: str     = ''

    day: int            = 0
    company_activated: bool = False

@dataclass
class FPG_Market:
    tickers                 = []
    ''' Traded stocks involved in the simulation '''

    numTickers              = 0
    ''' Number of traded stocks in the simulation '''

    Sectors                 = []
    ''' Sectors involved in the simulation '''

    Regions                 = []
    ''' Regions involved in the simulation '''

    traderPoolSize: int     = 0
    ''' Number of traders in the simulation '''

    meanIncome: float       = 0
    ''' Traders mean income in the simulation '''

    giniCoeff: float        = 0
    ''' Gini coefficient '''

    alphaCoeff: float       = 0
    ''' Income inequality shape factor '''

    totalMarketCap: float   = 0
    ''' Also stands for the total traders' wealth '''

    wealthDistribution      = []
    ''' A vector that represents the wealth distribution amog traders '''

    wealthNPopulation       = [0]*4
    ''' Actual wealth distribution that took place '''

    wealthThresholds        = [1e4, 1e5, 1e6]
    ''' Wealth benchmarks '''

    returnDistributions     = {"World_idx": {}, "Sector_idx": {}, "Geographical_idx": {}}
    ''' Daily return distributions of the various indices '''

    marketTrends = {"World": 0, "Sectors": {}, "Geogarphical": {}}
    ''' Market current trends '''

    minMarketRrends = {"World": 0, "Sectors": {}, "Geogarphical": {}}
    ''' Market minimum trends '''

    maxMarketRrends = {"World": 0, "Sectors": {}, "Geogarphical": {}}
    ''' Market maximum trends '''

    marketTrendPosition = {"World": 0, "Sectors": {}, "Geogarphical": {}}
    ''' Position of the market trend compared to the min and max '''

    day: int = 0
    ''' Market trading day '''

class FPG_Data:
    def __init__(self, Inp: FPG_Input) -> None:
        self.Manager = FPG_Manager()
        self.RefData = FPG_RefData()
        self.Market  = FPG_Market()

        self.Market.tickers = Inp.tickers
        self.Market.numTickers = len(self.Market.tickers)

        self.Companies = {ticker: Company(ticker,Inp.start_date) for ticker in self.Market.tickers}

        # Reference data calculation
        historical_data = FPG_RefUtils.load_historical_data(Inp)
        MarketCaps      = FPG_RefUtils.calculate_market_caps(self.Companies, historical_data)

        Stock_Weights   = FPG_RefUtils.calculate_stock_weights(MarketCaps) # Stock weights only for world index
        self.RefData.World_idx, self.Market.returnDistributions["World_idx"] = FPG_RefUtils.calculate_index(historical_data,Stock_Weights) # Calculate world index using all of the stocks
        self.RefData.Sector_idx, self.Market.returnDistributions["Sector_idx"], \
        self.RefData.Geographic_idx, self.Market.returnDistributions["Geographical_idx"] = FPG_RefUtils.calculate_sector_geographic_indices(historical_data, MarketCaps, self.Companies)

        self.Market.Sectors = list(self.Market.returnDistributions["Sector_idx"].keys())
        self.Market.Regions = list(self.Market.returnDistributions["Geographical_idx"].keys())

        del historical_data, MarketCaps, Stock_Weights

        # Initialize market
        self.Manager.start_date     = Inp.start_date
        self.Manager.numTotalDays   = self.RefData.World_idx.__len__()
        self.Manager.randomSeed     = Inp.randomSeed

        self.Market.traderPoolSize  = Inp.traderPoolSize
        self.Market.meanIncome      = Inp.meanIncome
        self.Market.giniCoeff       = Inp.gini_coeff
        self.Market.alphaCoeff      = FPG_Utils.alpha_from_gini(self.Market.giniCoeff)

        distribution_sum = sum(self.Companies[ticker].trading_volume/self.Companies[ticker].shares_outstanding \
                               for ticker in self.Market.tickers if self.Companies[ticker].Active)
        totalMarketCap = 0
        for ticker in self.Market.tickers:
            if(self.Companies[ticker].Active):
                self.Companies[ticker].popularity = (self.Companies[ticker].trading_volume/self.Companies[ticker].shares_outstanding)\
                                                    /distribution_sum
            
                totalMarketCap += self.Companies[ticker].market_cap

            self.Companies[ticker].Allocate_History(self)

            self.Companies[ticker].fundamental_influence = FPG_Utils.fundamental_analysis_influence(self.Companies[ticker])
            self.Companies[ticker].technical_influence   = FPG_Utils.technical_analysis_influence(self.Companies[ticker], 0)

        self.Market.totalMarketCap = totalMarketCap
        self.Market.wealthDistribution = np.cumsum(Inp.wealthDistribution)

        # Initialize traders
        self.Traders = [Trader(Inp, self) for _ in range(self.Market.traderPoolSize)]

        gc.collect()  # Force garbage collection to free memory