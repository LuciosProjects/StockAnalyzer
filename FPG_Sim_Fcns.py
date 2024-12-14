import numpy as np

from FPG_DataStrc import FPG_Data

def Initialize_Market(Data: FPG_Data):
    '''
        Initializes the simulation market:
        - Allocates stocks in every trader's portfolio
    '''

    # Have every trader go through a trading session, just for the initialization - all trader bids 
    # (no asks take place here) will be accepted
    for Trader in Data.Traders:
        Trader.trading_day(Data,'Init')
    pass