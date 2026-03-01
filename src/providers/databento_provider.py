"""
Data Bento Provider - ETL Pipeline Integration
Reads real MES historical data using clear ETL pipeline
"""
import pandas as pd
from datetime import datetime
from typing import Dict, Any

from ..interfaces import MarketDataProvider
from ..etl.pipeline import MESDataPipeline


class DataBentoProvider(MarketDataProvider):
    """
    Data Bento historical data provider using clear ETL pipeline
    """
    
    def __init__(self, csv_file_path: str = "data/databento/GLBX-20260301-5V5QDD9JH6/glbx-mdp3-20100606-20260228.ohlcv-1m.csv"):
        self.csv_file_path = csv_file_path
        
    def get_data(self, 
                 symbol: str,
                 start_date: datetime,
                 end_date: datetime,
                 timeframe: str = "5m",
                 **kwargs) -> pd.DataFrame:
        """Get real MES data using ETL pipeline"""
        
        # Determine cache path based on date range
        cache_filename = f"{symbol.lower()}_{timeframe}_{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}.csv"
        cache_path = f"data/__cache__/{cache_filename}"
        
        # Determine if this is sample mode (small date range)
        date_diff = (end_date - start_date).days
        sample_mode = date_diff <= 10  # 10 days or less = sample mode
        
        # Initialize ETL pipeline
        pipeline = MESDataPipeline(
            csv_file_path=self.csv_file_path,
            cache_path=cache_path,
            sample_mode=sample_mode
        )
        
        # Run pipeline
        try:
            data = pipeline.run(
                start_date=start_date,
                end_date=end_date,
                target_timeframe=timeframe,
                force_refresh=False
            )
            
            return data
            
        except Exception as e:
            raise Exception(f"ETL Pipeline failed: {e}")
    
    def is_available(self) -> bool:
        """Check if Data Bento file exists"""
        import os
        return os.path.exists(self.csv_file_path)
    
    def get_provider_info(self) -> Dict[str, Any]:
        return {
            "name": "Data Bento MES Provider",
            "description": "Real institutional MES historical data",
            "cost": "$12 for 16 years",
            "real_time": False,
            "symbols_supported": ["MES"],
            "timeframes": ["1m", "5m"],
            "data_range": "2019-2026",
            "bars_available": "3.4M+ real market bars"
        }