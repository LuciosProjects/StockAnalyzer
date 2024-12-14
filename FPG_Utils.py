import numpy as np

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

