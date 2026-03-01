"""
Data Provider Interfaces for MES Price Action Chart Pack Generator
Defines contracts that all data providers must implement
"""
from abc import ABC, abstractmethod
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any


class MarketDataProvider(ABC):
    """
    Abstract interface that all market data providers must implement
    """
    
    @abstractmethod
    def get_data(self, 
                 symbol: str,
                 start_date: datetime,
                 end_date: datetime,
                 timeframe: str = "5m",
                 **kwargs) -> pd.DataFrame:
        """
        Fetch market data for specified parameters
        
        Returns:
            pd.DataFrame with columns: ['open', 'high', 'low', 'close', 'volume']
            Index: DatetimeIndex
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if data provider is available/configured"""
        pass
    
    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """Return metadata about this data provider"""
        pass


class DataProviderConfig:
    """Configuration for data providers"""
    
    def __init__(self, 
                 provider_type: str,
                 symbol: str = "MES",
                 start_date: str = "2024-01-01",
                 end_date: str = "2024-06-30",
                 timeframe: str = "5m",
                 cache_enabled: bool = True,
                 cache_path: Optional[str] = None,
                 **provider_specific_config):
        self.provider_type = provider_type
        self.symbol = symbol
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")
        self.timeframe = timeframe
        self.cache_enabled = cache_enabled
        self.cache_path = cache_path or f"data/__cache__/{symbol.lower()}_{timeframe}_{start_date}_{end_date}.csv"
        self.provider_config = provider_specific_config