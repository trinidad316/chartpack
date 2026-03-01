"""
ETL Loaders - Data Persistence and Cache Management Module
Handles saving and loading processed data
"""
import pandas as pd
import os
from typing import Optional


class CacheLoader:
    """
    Handle caching and loading of processed market data
    """
    
    def __init__(self, cache_path: str):
        self.cache_path = cache_path
    
    def load(self) -> Optional[pd.DataFrame]:
        """
        Load processed data from cache
        """
        print("\n💾 LOAD PHASE - Cache Management")
        print("-" * 50)
        
        if not os.path.exists(self.cache_path):
            print(f"📂 No cache found at: {self.cache_path}")
            return None
            
        try:
            print(f"📂 Loading cached data from: {self.cache_path}")
            
            # Load CSV with timestamp index
            df = pd.read_csv(self.cache_path, index_col=0, parse_dates=True)
            
            print(f"✅ Loaded {len(df):,} bars from cache")
            print(f"📅 Cached range: {df.index.min()} to {df.index.max()}")
            print(f"📊 Columns: {list(df.columns)}")
            
            # Validate cached data structure
            if self._validate_cache(df):
                print("✅ Cache validation passed")
                return df
            else:
                print("❌ Cache validation failed - will regenerate")
                return None
                
        except Exception as e:
            print(f"⚠️  Cache read error: {e}")
            print("🔄 Will regenerate fresh data")
            return None
    
    def save(self, df: pd.DataFrame) -> bool:
        """
        Save processed data to cache
        """
        print(f"\n💾 SAVE - Caching Processed Data")
        print("-" * 50)
        
        try:
            # Ensure cache directory exists
            cache_dir = os.path.dirname(self.cache_path)
            if cache_dir:
                os.makedirs(cache_dir, exist_ok=True)
                print(f"📁 Ensured cache directory exists: {cache_dir}")
            
            print(f"💾 Saving {len(df):,} processed bars to cache...")
            print(f"📂 Cache path: {self.cache_path}")
            
            # Save to CSV with timestamp index
            df.to_csv(self.cache_path)
            
            # Verify the save worked
            file_size = os.path.getsize(self.cache_path) / (1024 * 1024)  # MB
            print(f"✅ Cache saved successfully")
            print(f"📊 File size: {file_size:.2f} MB")
            print(f"📅 Data range: {df.index.min()} to {df.index.max()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Cache save error: {e}")
            return False
    
    def _validate_cache(self, df: pd.DataFrame) -> bool:
        """
        Validate cached data integrity
        """
        print("🔍 Validating cached data...")
        
        # Check required columns
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            print(f"❌ Missing required columns in cache")
            return False
            
        # Check datetime index
        if not isinstance(df.index, pd.DatetimeIndex):
            print(f"❌ Invalid datetime index in cache")
            return False
            
        # Check for empty data
        if len(df) == 0:
            print(f"❌ Empty cache file")
            return False
            
        # Check for excessive null values
        null_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        if null_pct > 5:  # More than 5% null values
            print(f"❌ Too many null values in cache ({null_pct:.1f}%)")
            return False
            
        return True
    
    def clear(self) -> bool:
        """
        Clear cached data
        """
        print(f"\n🗑️  CLEAR - Removing Cache")
        print("-" * 50)
        
        if os.path.exists(self.cache_path):
            try:
                os.remove(self.cache_path)
                print(f"✅ Cache cleared: {self.cache_path}")
                return True
            except Exception as e:
                print(f"❌ Failed to clear cache: {e}")
                return False
        else:
            print(f"ℹ️  No cache to clear: {self.cache_path}")
            return True


class DataExporter:
    """
    Export processed data to various formats
    """
    
    @staticmethod
    def export_summary(df: pd.DataFrame, output_path: str) -> bool:
        """
        Export data summary and statistics
        """
        print(f"\n📋 EXPORT - Data Summary")
        print("-" * 50)
        
        try:
            summary = {
                'Dataset Summary': {
                    'Total Bars': len(df),
                    'Date Range': f"{df.index.min()} to {df.index.max()}",
                    'Timespan (Days)': (df.index.max() - df.index.min()).days,
                    'Columns': list(df.columns)
                },
                'Price Statistics': {
                    'Price Range': f"{df[['open','high','low','close']].min().min():.2f} - {df[['open','high','low','close']].max().max():.2f}",
                    'Average Close': f"{df['close'].mean():.2f}",
                    'Price Std Dev': f"{df['close'].std():.2f}",
                    'Total Volume': f"{df['volume'].sum():,.0f}"
                },
                'Data Quality': {
                    'Null Values': df.isnull().sum().sum(),
                    'Duplicate Timestamps': df.index.duplicated().sum(),
                    'Missing Bars': 'TODO: Calculate expected vs actual bars'
                }
            }
            
            # Write summary to file
            with open(output_path, 'w') as f:
                for section, data in summary.items():
                    f.write(f"\n{section}:\n")
                    f.write("-" * len(section) + "\n")
                    for key, value in data.items():
                        f.write(f"{key}: {value}\n")
            
            print(f"✅ Summary exported to: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False