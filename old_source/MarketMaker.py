from dataclasses import dataclass
import numpy as np
from typing import Dict

@dataclass
class MarketMakerConfig:
    max_inventory: int = 1000
    base_spread: float = 0.05  # 5 cents
    risk_adjustment: float = 0.01
    min_quote_size: int = 100

class MarketMaker:
    def __init__(self, config: MarketMakerConfig):
        self.config = config
        self.inventory: Dict[str, int] = {}
        self.quotes: Dict[str, Dict] = {}
        
    def initialize_security(self, ticker: str, initial_price: float):
        self.inventory[ticker] = 0
        self.quotes[ticker] = {
            'bid': initial_price - self.config.base_spread/2,
            'ask': initial_price + self.config.base_spread/2,
            'bid_size': self.config.min_quote_size,
            'ask_size': self.config.min_quote_size
        }
    
    def update_quotes(self, ticker: str, market_price: float):
        # Adjust spread based on inventory risk
        inventory_risk = abs(self.inventory[ticker]) / self.config.max_inventory
        adjusted_spread = self.config.base_spread * (1 + inventory_risk * self.config.risk_adjustment)
        
        self.quotes[ticker]['bid'] = market_price - adjusted_spread/2
        self.quotes[ticker]['ask'] = market_price + adjusted_spread/2
        
        # Adjust quote sizes based on inventory
        if self.inventory[ticker] > 0:
            self.quotes[ticker]['ask_size'] = self.config.min_quote_size * 2
            self.quotes[ticker]['bid_size'] = self.config.min_quote_size
        else:
            self.quotes[ticker]['bid_size'] = self.config.min_quote_size * 2
            self.quotes[ticker]['ask_size'] = self.config.min_quote_size
    
    def execute_trade(self, ticker: str, size: int, is_buy: bool) -> float:
        if is_buy:
            price = self.quotes[ticker]['ask']
            self.inventory[ticker] -= size
        else:
            price = self.quotes[ticker]['bid']
            self.inventory[ticker] += size
        
        return price