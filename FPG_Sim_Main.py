import random as rnd

import FPG_Sim_Fcns
from FPG_Inp import FPG_Input
from FPG_DataStrc import FPG_Data

def FPG_Sim(Inp: FPG_Input):
    rnd.seed(Inp.randomSeed)

    Data = FPG_Data(Inp)
    FPG_Sim_Fcns.Initialize_Market(Data)

    for day in range(1, Data.Manager.numTotalDays):
        Data.Manager.day = day

        for ticker in Data.Market.tickers:
            Data.Companies[ticker].record_to_history(day)

if __name__ == "__main__":
    Inp = FPG_Input()

    Inp.tickers = ['AAPL', 'TSLA', 'NVDA', 'INTC', 'MSFT',
                  'PFE', 'JNJ', 'MRNA', 'ABT', 'AMGN',
                  'XOM', 'CVX', 'BP', 'SHEL', 'TTE',
                  'JPM', 'BAC', 'C', 'GS', 'MS',
                  'AMZN', 'WMT', 'COST', 'TGT', 'HD',
                  'TSM', 'TM', 'SFTBY', 'BABA'
                ]
    
    FPG_Sim(Inp)
    