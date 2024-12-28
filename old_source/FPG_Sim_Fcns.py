import numpy as np

from FPG_DataStrc import FPG_Data

def Initialize_Market(Data: FPG_Data):
    '''
        Initializes the simulation market:
        - Allocates stocks in every trader's portfolio
    '''

    # initialize sector trends [%]
    for Sector in Data.Market.Sectors:
        Data.Market.marketTrends["Sectors"][Sector] = np.interp(np.random.rand(), 
                                                                Data.Market.returnDistributions["Sector_idx"][Sector]["CDF"],
                                                                Data.Market.returnDistributions["Sector_idx"][Sector]["sorted daily change"])
        
        Data.Market.minMarketRrends["Sectors"][Sector] = min(Data.Market.returnDistributions["Sector_idx"][Sector]["sorted daily change"])
        Data.Market.maxMarketRrends["Sectors"][Sector] = max(Data.Market.returnDistributions["Sector_idx"][Sector]["sorted daily change"])

        Data.Market.marketTrendPosition["Sectors"][Sector] =    (Data.Market.marketTrends["Sectors"][Sector] - Data.Market.minMarketRrends["Sectors"][Sector])/ \
                                                                (Data.Market.maxMarketRrends["Sectors"][Sector] - Data.Market.minMarketRrends["Sectors"][Sector])

    # Initialize geographical trends via the sector trends [%]
    for Region in Data.Market.Regions:
        Tickers = [ticker for ticker in Data.Market.tickers if Data.Companies[ticker].region == Region]
        Region_Sector_Caps = {Sector: sum(Data.Companies[ticker].market_cap for ticker in Tickers if Data.Companies[ticker].sector == Sector) for Sector in Data.Market.Sectors}
        Total_Region_Cap = sum(Region_Sector_Caps.values())
        Updated_Region_Cap = Total_Region_Cap

        for sector in Data.Market.Sectors:
            if Region_Sector_Caps[sector] == 0:
                continue
            else:
                Updated_Region_Cap += Region_Sector_Caps[sector] * Data.Market.marketTrends["Sectors"][sector]/100.0
        
        Data.Market.marketTrends["Geogarphical"][Region] = ((Updated_Region_Cap - Total_Region_Cap)/Total_Region_Cap)*100.0

        Data.Market.minMarketRrends["Geogarphical"][Region] = min(Data.Market.returnDistributions["Geographical_idx"][Region]['sorted daily change'])
        Data.Market.maxMarketRrends["Geogarphical"][Region] = max(Data.Market.returnDistributions["Geographical_idx"][Region]['sorted daily change'])

        Data.Market.marketTrends["Geogarphical"][Region] = np.clip( Data.Market.marketTrends["Geogarphical"][Region],
                                                                    Data.Market.minMarketRrends["Geogarphical"][Region],
                                                                    Data.Market.maxMarketRrends["Geogarphical"][Region])
        
        Data.Market.marketTrendPosition["Geogarphical"][Region] =   (Data.Market.marketTrends["Geogarphical"][Region] - Data.Market.minMarketRrends["Geogarphical"][Region])/ \
                                                                    (Data.Market.maxMarketRrends["Geogarphical"][Region] - Data.Market.minMarketRrends["Geogarphical"][Region])

    # Initialize market trends based on sector trends [%]
    Data.Market.marketTrends["World"] = 0
    Data.Market.minMarketRrends["World"] = min(Data.Market.returnDistributions["World_idx"]["sorted daily change"])
    Data.Market.maxMarketRrends["World"] = max(Data.Market.returnDistributions["World_idx"]["sorted daily change"])

    Updated_Cap = Data.Market.totalMarketCap
    for sector in Data.Market.Sectors:
        Tickers     = [ticker for ticker in Data.Market.tickers if Data.Companies[ticker].sector == sector]
        Sector_Cap  = sum(Data.Companies[ticker].market_cap for ticker in Tickers)
        
        Updated_Cap += Sector_Cap*(Data.Market.marketTrends["Sectors"][sector]/100.0)

    Data.Market.marketTrends["World"] = (Updated_Cap - Data.Market.totalMarketCap)/Data.Market.totalMarketCap*100.0

    Data.Market.marketTrends["World"] = np.clip(Data.Market.marketTrends["World"],
                                                Data.Market.minMarketRrends["World"],
                                                Data.Market.maxMarketRrends["World"])

    Data.Market.marketTrendPosition["World"] =  (Data.Market.marketTrends["World"] - Data.Market.minMarketRrends["World"])/ \
                                                (Data.Market.maxMarketRrends["World"] - Data.Market.minMarketRrends["World"])

    # Have every trader go through a trading session, just for the initialization - all trader bids 
    # (no asks take place here) will be accepted
    for Trader in Data.Traders:
        Trader.trading_day(Data,'Init')
    pass