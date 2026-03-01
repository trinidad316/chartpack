"""
Data Service Layer - Clean interface between data providers and core application
Handles caching, provider selection, and data normalization
"""
import pandas as pd
import os
from typing import Optional, Dict, Any

from .interfaces import MarketDataProvider, DataProviderConfig
from .providers import AVAILABLE_PROVIDERS


class DataProviderFactory:
    """
    Factory for creating data provider instances
    """
    
    _providers = AVAILABLE_PROVIDERS
    
    @classmethod
    def create_provider(cls, provider_type: str, **config) -> MarketDataProvider:
        """Create a data provider instance"""
        if provider_type not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(f"Unknown provider '{provider_type}'. Available: {available}")
        
        provider_class = cls._providers[provider_type]
        
        # Pass provider-specific config
        return provider_class(**config)
    
    @classmethod
    def list_available_providers(cls) -> Dict[str, Any]:
        """List all available providers with their info"""
        providers_info = {}
        for name, provider_class in cls._providers.items():
            try:
                # Create a dummy instance to get info
                if name == "synthetic":
                    instance = provider_class()
                    providers_info[name] = instance.get_provider_info()
                else:
                    # For providers requiring config, just return basic info
                    providers_info[name] = {
                        "name": provider_class.__name__,
                        "description": f"{provider_class.__name__} data provider",
                        "status": "requires_configuration"
                    }
            except Exception as e:
                providers_info[name] = {"error": str(e)}
        
        return providers_info


class MarketDataService:
    """
    High-level service for market data operations
    Handles provider management, caching, and data normalization
    """
    
    def __init__(self, config: DataProviderConfig):
        self.config = config
        self.provider = DataProviderFactory.create_provider(
            config.provider_type,
            **config.provider_config
        )
    
    def get_market_data(self) -> pd.DataFrame:
        """
        Get market data with automatic caching
        """
        # Check cache first
        if self.config.cache_enabled and os.path.exists(self.config.cache_path):
            print(f"📂 Loading cached data from {self.config.cache_path}...")
            data = self._load_from_cache()
            if data is not None and len(data) > 0:
                print(f"✅ Loaded {len(data)} bars from cache")
                return data
        
        # Fetch from provider
        print(f"📈 Fetching data from {self.provider.get_provider_info()['name']}...")
        
        if not self.provider.is_available():
            raise RuntimeError(f"Data provider {self.config.provider_type} is not available")
        
        data = self.provider.get_data(
            symbol=self.config.symbol,
            start_date=self.config.start_date,
            end_date=self.config.end_date,
            timeframe=self.config.timeframe
        )
        
        # Validate data format
        data = self._normalize_data(data)
        
        # Cache if enabled
        if self.config.cache_enabled:
            self._save_to_cache(data)
        
        print(f"✅ Fetched {len(data)} bars from {data.index[0]} to {data.index[-1]}")
        return data
    
    def _load_from_cache(self) -> Optional[pd.DataFrame]:
        """Load data from cache file"""
        try:
            data = pd.read_csv(self.config.cache_path, index_col=0, parse_dates=True)
            return self._normalize_data(data)
        except Exception as e:
            print(f"⚠️  Cache read error: {e}")
            return None
    
    def _save_to_cache(self, data: pd.DataFrame):
        """Save data to cache file"""
        try:
            os.makedirs(os.path.dirname(self.config.cache_path), exist_ok=True)
            data.to_csv(self.config.cache_path)
            print(f"💾 Data cached to {self.config.cache_path}")
        except Exception as e:
            print(f"⚠️  Cache write error: {e}")
    
    def _normalize_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize data to standard format expected by chart generator
        Volume is kept for data integrity but not used in price action calculations
        """
        # Core price columns (OHLC) - volume is optional
        required_columns = ['open', 'high', 'low', 'close']
        optional_columns = ['volume']
        
        # Handle different column naming conventions
        column_mapping = {
            'Open': 'open', 'HIGH': 'high', 'High': 'high',
            'Low': 'low', 'LOW': 'low', 'Close': 'close', 'CLOSE': 'close',
            'Volume': 'volume', 'VOLUME': 'volume', 'Vol': 'volume'
        }
        
        # Rename columns if needed
        data = data.rename(columns=column_mapping)
        
        # Ensure all required OHLC columns exist
        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"Required OHLC column '{col}' missing from data")
        
        # Add volume if missing (for data completeness, not used in calculations)
        if 'volume' not in data.columns:
            data['volume'] = 1000  # Constant volume (not used in price analysis)
        
        # Keep only OHLC + volume columns in correct order
        final_columns = required_columns + ['volume']
        data = data[final_columns]
        
        # Ensure datetime index
        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Data must have DatetimeIndex")
        
        # Sort by date
        data = data.sort_index()
        
        return data
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about current data provider"""
        return self.provider.get_provider_info()