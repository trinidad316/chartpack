"""
ETL Extractors - Raw Data Extraction Module
Handles reading raw data from various sources
"""
import pandas as pd
from typing import Optional


class DataBentoExtractor:
    """
    Extract raw 1-minute OHLCV data from Data Bento CSV files
    """
    
    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path
    
    def extract(self, sample_mode: bool = False, sample_rows: int = 50000) -> pd.DataFrame:
        """
        Extract raw data from CSV file
        
        Args:
            sample_mode: If True, only load first N rows for fast processing
            sample_rows: Number of rows to load in sample mode
            
        Returns:
            Raw DataFrame with timestamp index
        """
        print("=" * 60)
        print("📊 EXTRACT PHASE - Raw Data Loading")
        print("=" * 60)
        
        try:
            if sample_mode:
                print(f"🚀 Sample Mode: Loading first {sample_rows:,} rows only...")
                df = pd.read_csv(self.csv_file_path, nrows=sample_rows)
                print(f"✅ Extracted {len(df):,} raw bars (sample subset)")
            else:
                print("📂 Production Mode: Loading full dataset...")
                df = pd.read_csv(self.csv_file_path)
                print(f"✅ Extracted {len(df):,} raw bars (complete dataset)")
            
            # Convert timestamp and set as index
            print("🕒 Converting timestamps to datetime index...")
            df['ts_event'] = pd.to_datetime(df['ts_event'])
            df.set_index('ts_event', inplace=True)
            
            # Keep only OHLCV columns
            df = df[['open', 'high', 'low', 'close', 'volume']].copy()
            
            print(f"📅 Data range: {df.index.min()} to {df.index.max()}")
            print(f"📊 Columns: {list(df.columns)}")
            print("✅ Extract phase complete")
            
            return df
            
        except Exception as e:
            raise Exception(f"❌ Extract failed: {e}")


class RawDataValidator:
    """
    Validate raw extracted data before processing
    """
    
    @staticmethod
    def validate(df: pd.DataFrame) -> bool:
        """
        Validate raw data structure and basic integrity
        """
        print("\n🔍 VALIDATION - Raw Data Integrity Check")
        print("-" * 50)
        
        checks_passed = 0
        total_checks = 0
        
        # Check 1: Required columns
        total_checks += 1
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if all(col in df.columns for col in required_cols):
            print("✅ All required OHLCV columns present")
            checks_passed += 1
        else:
            print("❌ Missing required OHLCV columns")
            
        # Check 2: DateTime index
        total_checks += 1
        if isinstance(df.index, pd.DatetimeIndex):
            print("✅ Valid datetime index")
            checks_passed += 1
        else:
            print("❌ Invalid datetime index")
            
        # Check 3: Data not empty
        total_checks += 1
        if len(df) > 0:
            print(f"✅ Non-empty dataset ({len(df):,} rows)")
            checks_passed += 1
        else:
            print("❌ Empty dataset")
            
        # Check 4: No all-null columns
        total_checks += 1
        null_cols = df.columns[df.isnull().all()].tolist()
        if not null_cols:
            print("✅ No completely null columns")
            checks_passed += 1
        else:
            print(f"❌ Completely null columns: {null_cols}")
            
        print(f"\n📊 Validation Result: {checks_passed}/{total_checks} checks passed")
        
        if checks_passed == total_checks:
            print("✅ Raw data validation passed")
            return True
        else:
            print("❌ Raw data validation failed")
            return False