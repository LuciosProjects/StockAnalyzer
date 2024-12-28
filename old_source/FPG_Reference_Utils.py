import numpy as np
import pandas as pd

from FPG_Inp import FPG_Input
from Company import Company

Geographical_Grouping = {'United States': 'North America', 
                         'United Kingdom': 'Europe',
                         'France': 'Europe',
                         'Taiwan': 'Asia',
                         'South Korea': 'Asia',
                         'China': 'Asia',
                         'Japan': 'Asia'
                         }

def load_historical_data(Inp: FPG_Input):

    historical_data = pd.DataFrame()
    for ticker in Inp.tickers:
        temp = pd.read_csv('Database/' + ticker + '_price_history.csv')

        temp['Date'] = pd.to_datetime(temp['Date'])
        temp.set_index('Date',inplace=True)

        temp.columns = pd.MultiIndex.from_product([[ticker], temp.columns])

        historical_data = pd.concat([historical_data, temp], axis=1)
    del temp

    return historical_data

def calculate_market_caps(Cmpnys, historical_data):
    """
    Calculates market cap history for each company

    :param Cmpnys: Company objects for the stock.
    :param historical_data: past prices for each company.

    :return: DataFrame of the calculated market caps.
    """
    
    MarketCaps = pd.DataFrame(columns=list(Cmpnys.keys()),index=historical_data.index)

    for ticker in Cmpnys.keys():
        adj_close_prices = historical_data[ticker]['Adj Close'].to_numpy()
        adj_close_prices = adj_close_prices.reshape(-1)  # Flatten if necessary (e.g., in case it's a 2D array)

        MarketCaps[ticker] = adj_close_prices * Cmpnys[ticker].shares_outstanding

    return MarketCaps

def calculate_stock_weights(market_caps):
    """
    Optimized version to calculate the weight of each stock in the market on each date.
    
    :param market_caps: pandas DataFrame of market caps, indexed by dates, with columns for each stock.
    :return: pandas DataFrame with the weight of each stock on each date.
    """
    # Calculate the total market cap for each date in a vectorized way
    total_market_caps = market_caps.sum(axis=1)

    # Avoid division by zero by filling any NaNs in total_market_caps with 1 (to keep results valid)
    # The result will still be NaN for dates with zero market cap
    total_market_caps = total_market_caps.replace(0, 1)

    # Calculate weights using broadcasting (no loop needed)
    stock_weights = market_caps.div(total_market_caps, axis=0)
    
    return stock_weights

def calculate_index(historical_data, Weights):
    tickers_historical_data = historical_data.loc[:, (slice(None), ["Adj Close"])]

    temp = np.nan_to_num(Weights.to_numpy() * tickers_historical_data.to_numpy(),0).sum(axis=1)
    idx = pd.DataFrame(index=tickers_historical_data.index, columns=["price index", "index returns"])

    first_value_pos = np.where(temp > 0)[0][0]
   
    distribution = {"sorted daily change": np.array([]), "CDF": np.array([])}

    daily_change = (np.append(0,np.diff(temp[first_value_pos:]))/temp[first_value_pos:])*100
    daily_change_sorted = np.sort(daily_change)
    n = daily_change_sorted.__len__()
   
    cumulative_probs = np.arange(1, n + 1) / n # Cumulative probabilities from 0 to 1

    idx["price index"] = temp.astype('float32')
    idx["index returns"] = (((temp/temp[first_value_pos]) - 1)*100).astype('float32')

    distribution["sorted daily change"] = daily_change_sorted
    distribution["CDF"] = cumulative_probs

    del temp

    return idx, distribution

def calculate_sector_geographic_indices(historical_data, MarketCaps, Cmpnys):
    sectors = []
    # countries = []
    regions = []

    SectorGroups = {}
    GeoGroups = {}

    for ticker in Cmpnys.keys():
        sector  = Cmpnys[ticker].sector
        # country = Cmpnys[ticker].country
        region = Cmpnys[ticker].region

        sectors.append(sector)
        # countries.append(country)

        # region = Geographical_Grouping[country]
        regions.append(region)

        if(region not in GeoGroups):
            GeoGroups[region] = []
        GeoGroups[region].append(ticker)

        if(sector not in SectorGroups):
            SectorGroups[sector] = []
        SectorGroups[sector].append(ticker)

    sectors = np.unique(sectors)
    regions = np.unique(regions)

    sector_multi_index = pd.MultiIndex.from_product([sectors, ["price index", "index returns"]], names=["Sector", "Type"])
    geo_multi_index = pd.MultiIndex.from_product([regions, ["price index", "index returns"]], names=["Sector", "Type"])

    Sector_idx = pd.DataFrame(index=historical_data.index, columns=sector_multi_index)
    Geo_idx = pd.DataFrame(index=historical_data.index, columns=geo_multi_index)

    sectors_distributions = {}
    for sector in sectors:
        Tickers = SectorGroups[sector]

        Sector_Weights = calculate_stock_weights(MarketCaps[Tickers])
        Sector_idx[sector], sectors_distributions[sector] = calculate_index(historical_data[Tickers], Sector_Weights)

    Geo_distributions = {}
    for region in regions:
        Tickers = GeoGroups[region]

        region_Weights = calculate_stock_weights(MarketCaps[Tickers])
        Geo_idx[region], Geo_distributions[region] = calculate_index(historical_data.loc[:, (Tickers ,slice(None))], region_Weights)

    return Sector_idx, sectors_distributions, Geo_idx, Geo_distributions