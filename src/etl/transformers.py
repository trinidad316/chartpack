"""
Clean ETL Transformers - Preserving Natural Price Action
Rebuilt from scratch based on systematic testing and validation
"""
import pandas as pd
import numpy as np


class CleanContractSelector:
    """Select single primary contract, remove spread contracts"""
    
    @staticmethod
    def transform(df: pd.DataFrame) -> pd.DataFrame:
        print(f"\n🔍 TRANSFORM - Clean Contract Selection")
        print("-" * 50)
        
        original_count = len(df)
        
        if 'symbol' not in df.columns:
            print("⚠️  No symbol column found, skipping contract selection")
            return df
        
        # Remove spread contracts
        df = df[~df['symbol'].str.contains('-', na=False)]
        
        # Select most active contract by volume
        if len(df) > 0:
            contract_volumes = df.groupby('symbol')['volume'].sum()
            primary_contract = contract_volumes.idxmax()
            df = df[df['symbol'] == primary_contract]
            
            print(f"✅ Selected contract: {primary_contract}")
            print(f"   Volume: {contract_volumes[primary_contract]:,.0f}")
        
        final_count = len(df)
        print(f"📊 Records: {original_count:,} → {final_count:,}")
        
        return df


class CleanBasicFilter:
    """Remove only obvious bad data - minimal intervention"""
    
    @staticmethod  
    def transform(df: pd.DataFrame) -> pd.DataFrame:
        print(f"\n🧹 TRANSFORM - Basic Data Filter")
        print("-" * 50)
        
        original_count = len(df)
        
        # Remove nulls
        df = df.dropna()
        
        # Remove extreme price outliers (clearly corrupt data only)
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            df = df[(df[col] >= 100) & (df[col] <= 10000)]
        
        # Remove duplicate timestamps (keep highest volume)
        if df.index.duplicated().any():
            df = df.sort_values('volume', ascending=False)
            df = df[~df.index.duplicated(keep='first')]
        
        final_count = len(df)
        removed = original_count - final_count
        
        print(f"📊 Bad data removed: {removed:,}")
        print(f"📊 Records retained: {final_count:,}")
        
        return df


class CleanTimezoneConverter:
    """Clean timezone conversion with minimal side effects"""
    
    @staticmethod
    def transform(df: pd.DataFrame, source_tz: str = 'UTC', target_tz: str = 'US/Eastern') -> pd.DataFrame:
        print(f"\n🕒 TRANSFORM - Timezone Conversion")
        print("-" * 50)
        
        if df.index.tz is None:
            df.index = df.index.tz_localize(source_tz)
        df.index = df.index.tz_convert(target_tz)
        
        print(f"✅ Converted {source_tz} → {target_tz}")
        return df


class CleanResampler:
    """Clean resampling with quality preservation"""
    
    @staticmethod
    def transform(df: pd.DataFrame, target_timeframe: str = "5min") -> pd.DataFrame:
        print(f"\n📊 TRANSFORM - Clean Resampling to {target_timeframe}")
        print("-" * 50)
        
        if target_timeframe in ["1min", "1m"]:
            print("⚡ Target timeframe is 1min - no resampling needed")
            return df
        
        before_count = len(df)
        before_range = df[['open', 'high', 'low', 'close']].min().min(), df[['open', 'high', 'low', 'close']].max().max()
        
        # Convert legacy frequency strings to pandas-compatible format
        pandas_freq = target_timeframe
        if target_timeframe == "5m":
            pandas_freq = "5min"
        elif target_timeframe == "15m":
            pandas_freq = "15min"
        elif target_timeframe == "30m":
            pandas_freq = "30min"
        elif target_timeframe == "1h":
            pandas_freq = "1h"
        
        # Simple OHLCV resampling
        resampled = df.resample(pandas_freq, label='left', closed='left').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min', 
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        after_count = len(resampled)
        after_range = resampled[['open', 'high', 'low', 'close']].min().min(), resampled[['open', 'high', 'low', 'close']].max().max()
        
        print(f"📊 {before_count:,} 1-min → {after_count:,} {target_timeframe} bars")
        print(f"📈 Range: ${before_range[0]:.2f}-${before_range[1]:.2f} → ${after_range[0]:.2f}-${after_range[1]:.2f}")
        
        # Quality check
        range_preservation = (after_range[1] - after_range[0]) / (before_range[1] - before_range[0])
        print(f"📊 Range preservation: {range_preservation:.1%}")
        
        return resampled


class CleanFinalProcessor:
    """Final processing with validation"""
    
    @staticmethod
    def transform(df: pd.DataFrame) -> pd.DataFrame:
        print(f"\n🎯 TRANSFORM - Final Processing")
        print("-" * 50)
        
        # Sort by timestamp
        df = df.sort_index()
        
        # Remove timezone for chart compatibility
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        
        # Calculate final statistics
        if len(df) > 0:
            df['bar_range'] = df['high'] - df['low']
            avg_range = df['bar_range'].mean()
            max_range = df['bar_range'].max()
            
            print(f"📊 Final stats: {len(df):,} bars")
            print(f"📈 Avg range: ${avg_range:.2f}")
            print(f"📈 Max range: ${max_range:.2f}")
            
            df = df.drop('bar_range', axis=1)  # Remove temp column
        
        return df


# Legacy aliases for backward compatibility
TimezoneTransformer = CleanTimezoneConverter
TimeframeResampler = CleanResampler  
FinalProcessor = CleanFinalProcessor