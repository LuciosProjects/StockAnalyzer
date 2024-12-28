from dataclasses import dataclass
from typing import List

@dataclass
class FPG_Inp_Settings:
    pass

@dataclass
class FPG_Input:
    """
        This is the input class for the Financial playground (FPG) simulation
    """

    tickers =  []
    ''' ticker symbols pool from which the 'bubble world' market will be built '''
    
    traderPoolSize: int = 1000
    ''' number of traders in the whole market '''

    start_date: str     = '1995-01-01'
    ''' starting date specifies the date from which the simulation will start & base its initial states '''

    randomSeed: int     = 0
    ''' random seed for results reproducibility '''
    
    wealthDistribution  = [0.525, 0.344, 0.12, 0.011]
    ''' how the total wealth should be distributed in the simulation, the remainder corresponds to the most common level of income
        if nothing was defined, it is spread by the wealth distribution data of 2022 
        according to https://www.statista.com/statistics/270388/distribution-of-the-global-population-by-wealth-status/ '''

    gini_coeff: float = 0.67
    ''' Gini coefficient for the global income distribution '''

    meanIncome: float = 13700
    ''' Average trader annual income '''