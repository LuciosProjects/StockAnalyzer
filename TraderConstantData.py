"""
    This module contains constant data that is used by the trading system.
    The data includes:
        - The regional currencies of the world.
        - A pool of market indices that can be used to track the performance of the stock market.
        - Portfolio status Enum.
"""

import datetime as dt

from dataclasses import dataclass
from enum import Enum

# StockExchangeOpHours = {
#     ''' The opening and closing hours of the stock exchanges. 
#         Open time is in index 0 and close time is in index 1. 
#         If the stock exchange is closed on a certain day, the value is None. '''

#     "NYSE": {  # New York Stock Exchange
#         "Monday": (dt.time(9, 30), dt.time(16, 0)),
#         "Tuesday": (dt.time(9, 30), dt.time(16, 0)),
#         "Wednesday": (dt.time(9, 30), dt.time(16, 0)),
#         "Thursday": (dt.time(9, 30), dt.time(16, 0)),
#         "Friday": (dt.time(9, 30), dt.time(16, 0)),
#         "Saturday": None,
#         "Sunday": None
#     },
#     "NASDAQ": {  # Nasdaq Stock Market
#         "Monday": (dt.time(9, 30), dt.time(16, 0)),
#         "Tuesday": (dt.time(9, 30), dt.time(16, 0)),
#         "Wednesday": (dt.time(9, 30), dt.time(16, 0)),
#         "Thursday": (dt.time(9, 30), dt.time(16, 0)),
#         "Friday": (dt.time(9, 30), dt.time(16, 0)),
#         "Saturday": None,
#         "Sunday": None
#     },
#     "LSE": {  # London Stock Exchange
#         "Monday": (dt.time(8, 0), dt.time(16, 30)),
#         "Tuesday": (dt.time(8, 0), dt.time(16, 30)),
#         "Wednesday": (dt.time(8, 0), dt.time(16, 30)),
#         "Thursday": (dt.time(8, 0), dt.time(16, 30)),
#         "Friday": (dt.time(8, 0), dt.time(16, 30)),
#         "Saturday": None,
#         "Sunday": None
#     },
#     "TASE": {  # Tel Aviv Stock Exchange
#         "Sunday": (dt.time(9, 0), dt.time(16, 25)),
#         "Monday": (dt.time(9, 0), dt.time(16, 25)),
#         "Tuesday": (dt.time(9, 0), dt.time(16, 25)),
#         "Wednesday": (dt.time(9, 0), dt.time(16, 25)),
#         "Thursday": (dt.time(9, 0), dt.time(16, 25)),
#         "Friday": None,
#         "Saturday": None
#     },
#     "JPX": {  # Japan Exchange Group (Tokyo Stock Exchange)
#         "Monday": (dt.time(9, 0), dt.time(15, 0)),
#         "Tuesday": (dt.time(9, 0), dt.time(15, 0)),
#         "Wednesday": (dt.time(9, 0), dt.time(15, 0)),
#         "Thursday": (dt.time(9, 0), dt.time(15, 0)),
#         "Friday": (dt.time(9, 0), dt.time(15, 0)),
#         "Saturday": None,
#         "Sunday": None
#     },
#     "SSE": {  # Shanghai Stock Exchange
#         "Monday": (dt.time(9, 30), dt.time(15, 0)),
#         "Tuesday": (dt.time(9, 30), dt.time(15, 0)),
#         "Wednesday": (dt.time(9, 30), dt.time(15, 0)),
#         "Thursday": (dt.time(9, 30), dt.time(15, 0)),
#         "Friday": (dt.time(9, 30), dt.time(15, 0)),
#         "Saturday": None,
#         "Sunday": None
#     },
#     "HKEX": {  # Hong Kong Stock Exchange
#         "Monday": (dt.time(9, 30), dt.time(16, 0)),
#         "Tuesday": (dt.time(9, 30), dt.time(16, 0)),
#         "Wednesday": (dt.time(9, 30), dt.time(16, 0)),
#         "Thursday": (dt.time(9, 30), dt.time(16, 0)),
#         "Friday": (dt.time(9, 30), dt.time(16, 0)),
#         "Saturday": None,
#         "Sunday": None
#     }
# }

YF_SE_TO_TCD_SE = {
    'NYSE': 'NYSE',
    'NASDAQ': 'NASDAQ',
    'LSE': 'LSE',
    'TLV': 'TASE',
    'JPX': 'JPX',
    'SSE': 'SSE',
    'HKEX': 'HKEX'
}

RegionalCurrencies = {
    'Afghanistan': 'AFN', # Afghan Afghani
    'Algeria': 'DZD', # Algerian Dinar
    'Angola': 'AOA', # Angolan Kwanza
    'Antarctica': 'USD', # United States Dollar
    'Argentina': 'ARS', # Argentine Peso
    'Armenia': 'AMD', # Armenian Dram
    'Aruba': 'AWG', # Aruban Florin
    'Australia': 'AUD', # Australian Dollar
    'Austria': 'EUR', # Euro
    'Azerbaijan': 'AZN', # Azerbaijani Manat
    'Bahamas': 'BSD', # Bahamian Dollar
    'Bahrain': 'BHD', # Bahraini Dinar
    'Bangladesh': 'BDT', # Bangladeshi Taka
    'Barbados': 'BBD', # Barbadian Dollar
    'Belarus': 'BYN', # Belarusian Ruble
    'Belgium': 'EUR', # Euro
    'Belize': 'BZD', # Belize Dollar
    'Benin': 'XOF', # West African CFA Franc
    'Bhutan': 'BTN', # Bhutanese Ngultrum
    'Bolivia': 'BOB', # Bolivian Boliviano
    'Botswana': 'BWP', # Botswana Pula
    'Brazil': 'BRL', # Brazilian Real
    'British Virgin Islands': 'USD', # United States Dollar
    'Brunei': 'BND', # Brunei Dollar
    'Bulgaria': 'BGN', # Bulgarian Lev
    'Burkina Faso': 'XOF', # West African CFA Franc
    'Burundi': 'BIF', # Burundian Franc
    'Cambodia': 'KHR', # Cambodian Riel
    'Cameroon': 'XAF', # Central African CFA Franc
    'Canada': 'CAD', # Canadian Dollar
    'Cape Verde': 'CVE', # Cape Verdean Escudo
    'Central African Republic': 'XAF', # Central African CFA Franc
    'Chad': 'XAF', # Central African CFA Franc
    'Chile': 'CLP', # Chilean Peso
    'China': 'CNY', # Chinese Yuan
    'Colombia': 'COP', # Colombian Peso
    'Comoros': 'KMF', # Comorian Franc
    'Congo': 'XAF', # Central African CFA Franc
    'Costa Rica': 'CRC', # Costa Rican Colon
    'Croatia': 'HRK', # Croatian Kuna
    'Cuba': 'CUP', # Cuban Peso
    'Curaçao': 'ANG', # Netherlands Antillean Guilder
    'Cyprus': 'EUR', # Euro
    'Czech Republic': 'CZK', # Czech Koruna
    'Denmark': 'DKK', # Danish Krone
    'Djibouti': 'DJF', # Djiboutian Franc
    'Dominica': 'XCD', # East Caribbean Dollar
    'Dominican Republic': 'DOP', # Dominican Peso
    'Ecuador': 'USD', # United States Dollar
    'Egypt': 'EGP', # Egyptian Pound
    'El Salvador': 'USD', # United States Dollar
    'Equatorial Guinea': 'XAF', # Central African CFA Franc
    'Eritrea': 'ERN', # Eritrean Nakfa
    'Estonia': 'EUR', # Euro
    'Eswatini': 'SZL', # Swazi Lilangeni
    'Ethiopia': 'ETB', # Ethiopian Birr
    'Falkland Islands': 'FKP', # Falkland Islands Pound
    'Faroe Islands': 'DKK', # Danish Krone
    'Fiji': 'FJD', # Fijian Dollar
    'Finland': 'EUR', # Euro
    'France': 'EUR', # Euro
    'French Guiana': 'EUR', # Euro
    'Gabon': 'XAF', # Central African CFA Franc
    'Gambia': 'GMD', # Gambian Dalasi
    'Georgia': 'GEL', # Georgian Lari
    'Germany': 'EUR', # Euro
    'Ghana': 'GHS', # Ghanaian Cedi
    'Greece': 'EUR', # Euro
    'Greenland': 'DKK', # Danish Krone
    'Grenada': 'XCD', # East Caribbean Dollar
    'Guam': 'USD', # United States Dollar
    'Guatemala': 'GTQ', # Guatemalan Quetzal
    'Guinea': 'GNF', # Guinean Franc
    'Guinea-Bissau': 'XOF', # West African CFA Franc
    'Guyana': 'GYD', # Guyanese Dollar
    'Haiti': 'HTG', # Haitian Gourde
    'Honduras': 'HNL', # Honduran Lempira
    'Hong Kong': 'HKD', # Hong Kong Dollar
    'Hungary': 'HUF', # Hungarian Forint
    'Iceland': 'ISK', # Icelandic Krona
    'India': 'INR', # Indian Rupee
    'Indonesia': 'IDR', # Indonesian Rupiah
    'Iran': 'IRR', # Iranian Rial
    'Iraq': 'IQD', # Iraqi Dinar
    'Ireland': 'EUR', # Euro
    'Israel': 'ILS', # Israeli Shekel
    'Italy': 'EUR', # Euro
    'Ivory Coast': 'XOF', # West African CFA Franc
    'Jamaica': 'JMD', # Jamaican Dollar
    'Japan': 'JPY', # Japanese Yen
    'Jordan': 'JOD', # Jordanian Dinar
    'Kazakhstan': 'KZT', # Kazakhstani Tenge
    'Kenya': 'KES', # Kenyan Shilling
    'Kiribati': 'AUD', # Australian Dollar
    'Kuwait': 'KWD', # Kuwaiti Dinar
    'Kyrgyzstan': 'KGS', # Kyrgyzstani Som
    'Laos': 'LAK', # Lao Kip
    'Latvia': 'EUR', # Euro
    'Lebanon': 'LBP', # Lebanese Pound
    'Lesotho': 'LSL', # Lesotho Loti
    'Liberia': 'LRD', # Liberian Dollar
    'Libya': 'LYD', # Libyan Dinar
    'Liechtenstein': 'CHF', # Swiss Franc
    'Lithuania': 'EUR', # Euro
    'Luxembourg': 'EUR', # Euro
    'Macao': 'MOP', # Macanese Pataca
    'Madagascar': 'MGA', # Malagasy Ariary
    'Malawi': 'MWK', # Malawian Kwacha
    'Malaysia': 'MYR', # Malaysian Ringgit
    'Maldives': 'MVR', # Maldivian Rufiyaa
    'Mali': 'XOF', # West African CFA Franc
    'Malta': 'EUR', # Euro
    'Marshall Islands': 'USD', # United States Dollar
    'Mauritania': 'MRU', # Mauritanian Ouguiya
    'Mauritius': 'MUR', # Mauritian Rupee
    'Mexico': 'MXN', # Mexican Peso
    'Micronesia': 'USD', # United States Dollar
    'Moldova': 'MDL', # Moldovan Leu
    'Monaco': 'EUR', # Euro
    'Mongolia': 'MNT', # Mongolian Tugrik
    'Montserrat': 'XCD', # East Caribbean Dollar
    'Morocco': 'MAD', # Moroccan Dirham
    'Mozambique': 'MZN', # Mozambican Metical
    'Myanmar': 'MMK', # Burmese Kyat
    'Namibia': 'NAD', # Namibian Dollar
    'Nauru': 'AUD', # Australian Dollar
    'Nepal': 'NPR', # Nepalese Rupee
    'Netherlands': 'EUR', # Euro
    'New Zealand': 'NZD', # New Zealand Dollar
    'Nicaragua': 'NIO', # Nicaraguan Cordoba
    'Niger': 'XOF', # West African CFA Franc
    'Nigeria': 'NGN', # Nigerian Naira
    'North Korea': 'KPW', # North Korean Won
    'North Macedonia': 'MKD', # Macedonian Denar
    'Norway': 'NOK', # Norwegian Krone
    'Oman': 'OMR', # Omani Rial
    'Pakistan': 'PKR', # Pakistani Rupee
    'Palau': 'USD', # United States Dollar
    'Panama': 'PAB', # Panamanian Balboa
    'Papua New Guinea': 'PGK', # Papua New Guinean Kina
    'Paraguay': 'PYG', # Paraguayan Guarani
    'Peru': 'PEN', # Peruvian Sol
    'Philippines': 'PHP', # Philippine Peso
    'Poland': 'PLN', # Polish Zloty
    'Portugal': 'EUR', # Euro
    'Puerto Rico': 'USD', # United States Dollar
    'Qatar': 'QAR', # Qatari Riyal
    'Romania': 'RON', # Romanian Leu
    'Russia': 'RUB', # Russian Ruble
    'Rwanda': 'RWF', # Rwandan Franc
    'Saint Kitts and Nevis': 'XCD', # East Caribbean Dollar
    'Saint Lucia': 'XCD', # East Caribbean Dollar
    'Saint Vincent and the Grenadines': 'XCD', # East Caribbean Dollar
    'Samoa': 'WST', # Samoan Tala
    'San Marino': 'EUR', # Euro
    'Saudi Arabia': 'SAR', # Saudi Riyal
    'Senegal': 'XOF', # West African CFA Franc
    'Serbia': 'RSD', # Serbian Dinar
    'Seychelles': 'SCR', # Seychellois Rupee
    'Sierra Leone': 'SLL', # Sierra Leonean Leone
    'Singapore': 'SGD', # Singapore Dollar
    'Sint Eustatius': 'USD', # United States Dollar
    'Sint Maarten': 'ANG', # Netherlands Antillean Guilder
    'Slovakia': 'EUR', # Euro
    'Slovenia': 'EUR', # Euro
    'Solomon Islands': 'SBD', # Solomon Islands Dollar
    'Somalia': 'SOS', # Somali Shilling
    'South Africa': 'ZAR', # South African Rand
    'South Korea': 'KRW', # South Korean Won
    'South Sudan': 'SSP', # South Sudanese Pound
    'Spain': 'EUR', # Euro
    'Sri Lanka': 'LKR', # Sri Lankan Rupee
    'Sudan': 'SDG', # Sudanese Pound
    'Suriname': 'SRD', # Surinamese Dollar
    'Swaziland': 'SZL', # Swazi Lilangeni
    'Sweden': 'SEK', # Swedish Krona
    'Switzerland': 'CHF', # Swiss Franc
    'Syria': 'SYP', # Syrian Pound
    'Taiwan': 'TWD', # New Taiwan Dollar
    'Tajikistan': 'TJS', # Tajikistani Somoni
    'Tanzania': 'TZS', # Tanzanian Shilling
    'Thailand': 'THB', # Thai Baht
    'Togo': 'XOF', # West African CFA Franc
    'Tonga': 'TOP', # Tongan Pa'anga
    'Trinidad and Tobago': 'TTD', # Trinidad and Tobago Dollar
    'Tunisia': 'TND', # Tunisian Dinar
    'Turkey': 'TRY', # Turkish Lira
    'Turkmenistan': 'TMT', # Turkmenistani Manat
    'Tuvalu': 'AUD', # Australian Dollar
    'Uganda': 'UGX', # Ugandan Shilling
    'Ukraine': 'UAH', # Ukrainian Hryvnia
    'United Arab Emirates': 'AED', # UAE Dirham
    'United Kingdom': 'GBP', # British Pound Sterling
    'United States': 'USD', # United States Dollar
    'Uruguay': 'UYU', # Uruguayan Peso
    'Uzbekistan': 'UZS', # Uzbekistani Som
    'Vanuatu': 'VUV', # Vanuatu Vatu
    'Vatican City': 'EUR', # Euro
    'Venezuela': 'VES', # Venezuelan Bolivar
    'Vietnam': 'VND', # Vietnamese Dong
    'Yemen': 'YER', # Yemeni Rial
    'Zambia': 'ZMW', # Zambian Kwacha
    'Zimbabwe': 'ZWL', # Zimbabwean Dollar
}

CurrencyExchangePool = {
    'ILA': {'to': 'ILS', 'rate': 1e-2},
    'ILS': {'to': 'ILS', 'rate': 1},
    'CENT': {'to': 'USD', 'rate': 1e-2},
    'USD': {'to': 'USD', 'rate': 1},
    'EUR': {'to': 'EUR', 'rate': 1},
    'GBP': {'to': 'GBP', 'rate': 1},
    'JPY': {'to': 'JPY', 'rate': 1},
}
    
@dataclass(frozen=True)
class MarketIndicesPool:
    ''' A pool of market indices that can be used to track the performance of the stock market. 
        Each index is represented as a dictionary with the following attributes:
        - symbol: The symbol of the index.
        - Enable: A boolean value that indicates whether the index will be evaluated or not.'''

    # S&P 500 Indices
    SP500                           = {'symbol': '^GSPC', 'Enable': False}
    SP500_GROWTH                    = {'symbol': '^SP500-GR', 'Enable': False}
    SP500_VALUE                     = {'symbol': '^SP500-VL', 'Enable': False}
    SP500_TECH                      = {'symbol': '^SP500-IT', 'Enable': False}
    SP500_FINANCIAL                 = {'symbol': '^SP500-FI', 'Enable': False}
    SP500_HEALTHCARE                = {'symbol': '^SP500-HE', 'Enable': False}
    SP500_INDUSTRIAL                = {'symbol': '^SP500-IN', 'Enable': False}
    SP500_MATERIALS                 = {'symbol': '^SP500-MA', 'Enable': False}
    SP500_REAL_ESTATE               = {'symbol': '^SP500-RE', 'Enable': False}
    SP500_UTILITIES                 = {'symbol': '^SP500-UT', 'Enable': False}
    SP500_COMMUNICATION             = {'symbol': '^SP500-CO', 'Enable': False}
    SP500_CONSUMER_DISCRETIONARY    = {'symbol': '^SP500-CD', 'Enable': False}
    SP500_CONSUMER_STAPLES          = {'symbol': '^SP500-CS', 'Enable': False}
    SP500_ENERGY                    = {'symbol': '^SP500-EN', 'Enable': False}
    
    # NASDAQ Indices
    NASDAQ                  = {'symbol': '^IXIC', 'Enable': False}
    NASDAQ100               = {'symbol': '^NDX', 'Enable': False}
    NASDAQ100_GROWTH        = {'symbol': '^NDXGR', 'Enable': False}
    NASDAQ100_VALUE         = {'symbol': '^NDXVL', 'Enable': False}
    NASDAQ_COMPOSITE        = {'symbol': '^IXIC', 'Enable': False}
    NASDAQ_COMPOSITE_GROWTH = {'symbol': '^IXIC-GR', 'Enable': False}
    NASDAQ_COMPOSITE_VALUE  = {'symbol': '^IXIC-VL', 'Enable': False}

    # Dow Jones Indices
    DOWJONES            = {'symbol': '^DJI', 'Enable': False}
    DOWJONES_TRANSPORT  = {'symbol': '^DJT', 'Enable': False}
    DOWJONES_UTILITIES  = {'symbol': '^DJU', 'Enable': False}
    DOWJONES_COMPOSITE  = {'symbol': '^DJA', 'Enable': False}

    # Russell Indices
    RUSSELL1000         = {'symbol': '^RUI', 'Enable': False}
    RUSSELL2000         = {'symbol': '^RUT', 'Enable': False}
    RUSSELL3000         = {'symbol': '^RUA', 'Enable': False}
    RUSSELL1000_GROWTH  = {'symbol': '^RLG', 'Enable': False}
    RUSSELL1000_VALUE   = {'symbol': '^RLV', 'Enable': False}
    RUSSELL2000_GROWTH  = {'symbol': '^RUO', 'Enable': False}
    RUSSELL2000_VALUE   = {'symbol': '^RUJ', 'Enable': False}
    RUSSELL3000_GROWTH  = {'symbol': '^RUJ', 'Enable': False}
    RUSSELL3000_VALUE   = {'symbol': '^RUJ', 'Enable': False}

    # MSCI World Indices
    MSCI_WORLD              = {'symbol': 'ACWI', 'Enable': False}
    MSCI_EMERGING_MARKETS   = {'symbol': 'EEM', 'Enable': False}
    MSCI_EAFE               = {'symbol': 'EFA', 'Enable': False} # Europe, Australasia, Far East
    
    # Japan Indices
    NIKKEI225   = {'symbol': '^N225', 'Enable': False}
    TOPIX       = {'symbol': '^TPX', 'Enable': False} # Tokyo Stock Price Index
    JASDAQ      = {'symbol': '^JASDAQ', 'Enable': False} # Japan Securities Dealers Association Quotation

    # South east Asia Indices
    FTSE_BURSA_MALAYSIA = {'symbol': '^KLSE', 'Enable': False} # FTSE Bursa Malaysia KLCI
    STRAITS_TIMES       = {'symbol': '^STI', 'Enable': False} # Straits Times Index
    HANG_SENG           = {'symbol': '^HSI', 'Enable': False} # Hang Seng Index
    KOSPI               = {'symbol': '^KS11', 'Enable': False} # Korea Composite Stock Price Index
    TAIEX               = {'symbol': '^TWII', 'Enable': False} # Taiwan Capitalization Weighted Stock Index

    # Indian Indices
    NIFTY50 = {'symbol': '^NSEI', 'Enable': False} # National Stock Exchange of India Index
    SENSEX  = {'symbol': '^BSESN', 'Enable': False} # Bombay Stock Exchange Sensitive Index

    # Europe Indices
    FTSE100 = {'symbol': '^FTSE', 'Enable': False} # Financial Times Stock Exchange 100 Index
    CAC40   = {'symbol': '^FCHI', 'Enable': False} # Cotation Assistée en Continu 40
    DAX     = {'symbol': '^GDAXI', 'Enable': False} # Deutscher Aktienindex
    IBEX35  = {'symbol': '^IBEX', 'Enable': False} # Índice Bursátil Español 35
    FTSEMIB = {'symbol': 'FTSEMIB.MI', 'Enable': False} # FTSE MIB
    BEL20   = {'symbol': '^BFX', 'Enable': False} # Brussels Stock Exchange
    AEX     = {'symbol': '^AEX', 'Enable': False} # Amsterdam Exchange Index
    SMI     = {'symbol': '^SSMI', 'Enable': False} # Swiss Market Index
    OMXC25  = {'symbol': '^OMXC25', 'Enable': False} # OMX Copenhagen 25
    OMXH25  = {'symbol': '^OMXH25', 'Enable': False} # OMX Helsinki 25
    OMXS30  = {'symbol': '^OMXS30', 'Enable': False} # OMX Stockholm 30
    PSI20   = {'symbol': '^PSI20', 'Enable': False} # Portuguese Stock Index 20
    ATX     = {'symbol': '^ATX', 'Enable': False} # Austrian Traded Index 
    MOEX    = {'symbol': 'IMOEX.ME', 'Enable': False} # Moscow Exchange Index
    WIG20   = {'symbol': 'WIG20.WA', 'Enable': False} # Warsaw Stock Exchange Index 
    PX      = {'symbol': 'PX', 'Enable': False} # Prague Stock Exchange Index
    BUX     = {'symbol': 'BUX', 'Enable': False} # Budapest Stock Exchange Index
    BET     = {'symbol': 'BET', 'Enable': False} # Bucharest Stock Exchange Trading Index

    # Middle East Indices
    TASI    = {'symbol': '^TASI', 'Enable': False} # Tadawul All Share Index
    EGX30   = {'symbol': '^EGX30', 'Enable': False} # Egyptian Exchange 30 Index
    TA35    = {'symbol': '^TA35', 'Enable': False} # Tel Aviv 35 Index
    QSE     = {'symbol': '^QSE', 'Enable': False} # Qatar Stock Exchange Index
    MSM30   = {'symbol': '^MSM30', 'Enable': False} # Muscat Securities Market 30 Index
    ADX     = {'symbol': '^ADX', 'Enable': False} # Abu Dhabi Securities Exchange Index
    DFMGI   = {'symbol': '^DFMGI', 'Enable': False} # Dubai Financial Market General Index
    BVC     = {'symbol': '^BVC', 'Enable': False} # Bahrain Bourse All Share Index
    NSEI    = {'symbol': '^NSEI', 'Enable': False} # National Stock Exchange of India Index

class EPortfolioStatus(Enum):
    GOOD                = 0
    GOOD_FOR_BUYING     = 1
    GOOD_FOR_SELLING    = 2
    BAD                 = 3

