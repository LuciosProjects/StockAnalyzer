import numpy as np
import datetime as dt

from Company import Company

def gini_from_alpha(alpha) -> float:
    ''' 
        Calculates the gini coefficient given the alpha pareto factor 
    '''
    return (1.0/((2.0*alpha) - 1.0))


def alpha_from_gini(gini_coeff) -> float:
    ''' 
        Calculates the alpha pareto factor given the gini coefficient 
    '''
    return ((1.0/(2.0*gini_coeff)) + 0.5)

def monthly_income_STD(mean_annual_income,gini_coeff) -> float:
    '''
        Calculates the standard deviation of the trader's salary given the market's mean annual income & the gini coefficient
    '''
    if gini_coeff >= 0.6:
        sigma_annual = mean_annual_income*np.sqrt(np.log(1 + gini_coeff**2))
    else:
        K_coeff = 0.5 + 0.5*gini_coeff
        sigma_annual = K_coeff * mean_annual_income

    return (sigma_annual/np.sqrt(12.0))

def technical_analysis_influence(Company: Company, day: int):
    # Example: Use price trends and volatility index
    if(day < 30):
        price_prev = Company.History["price"][0]
    else:
        price_prev = Company.History["price"][day - 30]

    price_trend = (Company.price / price_prev) - 1
    return (price_trend * Company.volatility_index)

def fundamental_analysis_influence(Company: Company):
    # Example: Use earnings and P/E ratio
    return (Company.earnings /Company.pe_ratio)

def one_day_forward(date: str) -> str:
    year, month, day = str.split(date,'-')
    this_day = dt.date(int(year),int(month),int(day))
    next_day = this_day + dt.timedelta(1)

    return str(next_day)

def sigmoid(probability: float) -> float:
    """ Normalize probability using sigmoid function """
    return 1 / (1 + np.exp(-probability))