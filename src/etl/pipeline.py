"""
ETL Pipeline Orchestrator - Clear Data Processing Pipeline
Coordinates the entire Extract → Transform → Load process
"""
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any

from .extractors import DataBentoExtractor, RawDataValidator
from .transformers import (
    CleanContractSelector,
    CleanBasicFilter,
    CleanTimezoneConverter,
    CleanResampler,
    CleanFinalProcessor
)
from .loaders import CacheLoader, DataExporter


class MESDataPipeline:
    """
    Complete ETL pipeline for MES market data processing
    
    Pipeline Steps:
    1. EXTRACT: Load raw data from source
    2. TRANSFORM: Clean, process, and aggregate data
    3. LOAD: Save processed data to cache
    """
    
    def __init__(self, 
                 csv_file_path: str,
                 cache_path: str,
                 sample_mode: bool = False):
        self.csv_file_path = csv_file_path
        self.cache_path = cache_path
        self.sample_mode = sample_mode
        
        # Initialize pipeline components
        self.extractor = DataBentoExtractor(csv_file_path)
        self.cache_loader = CacheLoader(cache_path)
        
        print("🏗️  MES Data Pipeline Initialized")
        print(f"📂 Source: {csv_file_path}")
        print(f"💾 Cache: {cache_path}")
        print(f"⚡ Mode: {'Sample' if sample_mode else 'Production'}")
    
    def run(self, 
            start_date: datetime, 
            end_date: datetime,
            target_timeframe: str = "5m",
            force_refresh: bool = False) -> pd.DataFrame:
        """
        Execute the complete ETL pipeline
        
        Args:
            start_date: Filter data from this date
            end_date: Filter data to this date  
            target_timeframe: Target timeframe (1m, 5m, etc.)
            force_refresh: Skip cache and reprocess everything
            
        Returns:
            Clean, processed DataFrame ready for charting
        """
        print("\n" + "=" * 80)
        print("🚀 STARTING MES DATA PIPELINE")
        print("=" * 80)
        print(f"📅 Date Range: {start_date.date()} to {end_date.date()}")
        print(f"📊 Target Timeframe: {target_timeframe}")
        print(f"⚡ Mode: {'Sample' if self.sample_mode else 'Production'}")
        print(f"🔄 Force Refresh: {force_refresh}")
        
        # Try loading from cache first (unless force refresh)
        if not force_refresh:
            cached_data = self.cache_loader.load()
            if cached_data is not None:
                # Filter cached data to requested date range
                filtered_data = self._filter_by_date_range(cached_data, start_date, end_date)
                if len(filtered_data) > 0:
                    print(f"\n✅ Using cached data ({len(filtered_data):,} bars)")
                    return filtered_data
        
        # No cache or force refresh - run full pipeline
        print(f"\n🔄 Running full ETL pipeline...")
        
        # PHASE 1: EXTRACT
        raw_data = self._extract_phase()
        
        # PHASE 2: TRANSFORM  
        clean_data = self._transform_phase(raw_data, target_timeframe)
        
        # PHASE 3: LOAD
        success = self._load_phase(clean_data)
        
        if success:
            # Filter to requested date range
            filtered_data = self._filter_by_date_range(clean_data, start_date, end_date)
            
            print(f"\n" + "=" * 80)
            print("🎉 PIPELINE COMPLETED SUCCESSFULLY")
            print("=" * 80)
            print(f"📊 Final Output: {len(filtered_data):,} bars")
            print(f"📅 Date Range: {filtered_data.index.min()} to {filtered_data.index.max()}")
            print(f"💾 Data cached for future use")
            
            return filtered_data
        else:
            raise Exception("❌ Pipeline failed during load phase")
    
    def _extract_phase(self) -> pd.DataFrame:
        """
        Phase 1: Extract raw data from source
        """
        print(f"\n" + "🔵" * 20 + " EXTRACT PHASE " + "🔵" * 20)
        
        # Extract raw data
        raw_data = self.extractor.extract(
            sample_mode=self.sample_mode,
            sample_rows=50000 if self.sample_mode else None
        )
        
        # Validate extracted data
        if not RawDataValidator.validate(raw_data):
            raise Exception("❌ Raw data validation failed")
        
        print(f"✅ Extract phase complete: {len(raw_data):,} raw bars")
        return raw_data
    
    def _transform_phase(self, raw_data: pd.DataFrame, target_timeframe: str) -> pd.DataFrame:
        """
        Phase 2: Clean transform pipeline - preserving natural price action
        """
        print(f"\n" + "🟡" * 20 + " CLEAN TRANSFORM PHASE " + "🟡" * 20)
        
        # Step 1: Contract Selection (remove spreads, select primary contract)
        data = CleanContractSelector.transform(raw_data)
        
        # Step 2: Basic Filtering (remove only obvious bad data)
        data = CleanBasicFilter.transform(data)
        
        # Step 3: Timezone Conversion
        data = CleanTimezoneConverter.transform(
            data, 
            source_tz='UTC', 
            target_tz='US/Eastern'
        )
        
        # Step 4: Timeframe Resampling
        data = CleanResampler.transform(data, target_timeframe)
        
        # Step 5: Final Processing
        data = CleanFinalProcessor.transform(data)
        
        print(f"✅ Clean transform phase complete: {len(data):,} bars")
        return data
    
    def _load_phase(self, clean_data: pd.DataFrame) -> bool:
        """
        Phase 3: Load processed data to cache
        """
        print(f"\n" + "🟢" * 20 + " LOAD PHASE " + "🟢" * 20)
        
        # Save to cache
        success = self.cache_loader.save(clean_data)
        
        if success:
            # Export summary (optional)
            summary_path = self.cache_path.replace('.csv', '_summary.txt')
            DataExporter.export_summary(clean_data, summary_path)
        
        return success
    
    def _filter_by_date_range(self, 
                            data: pd.DataFrame, 
                            start_date: datetime, 
                            end_date: datetime) -> pd.DataFrame:
        """
        Filter data to requested date range
        """
        print(f"\n🔍 FILTER - Date Range Selection")
        print("-" * 50)
        
        print(f"📅 Requested: {start_date.date()} to {end_date.date()}")
        print(f"📊 Available: {data.index.min().date()} to {data.index.max().date()}")
        
        # Create timezone-naive datetime range for filtering
        start_ts = pd.Timestamp(start_date).tz_localize(None)
        end_ts = pd.Timestamp(end_date).tz_localize(None)
        
        # Filter data
        mask = (data.index >= start_ts) & (data.index <= end_ts)
        filtered_data = data[mask].copy()
        
        print(f"📊 Filtered result: {len(filtered_data):,} bars")
        
        if len(filtered_data) == 0:
            print("⚠️  No data found for requested date range")
            print("💡 Try adjusting the date range or check data availability")
        
        return filtered_data
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get current pipeline status and metadata
        """
        cache_exists = self.cache_loader._validate_cache if hasattr(self.cache_loader, '_validate_cache') else False
        
        status = {
            'pipeline_mode': 'Sample' if self.sample_mode else 'Production',
            'source_file': self.csv_file_path,
            'cache_path': self.cache_path,
            'cache_exists': cache_exists,
            'components': {
                'extractor': 'DataBentoExtractor',
                'transformers': [
                    'CleanContractSelector',
                    'CleanBasicFilter',
                    'CleanTimezoneConverter',
                    'CleanResampler',
                    'CleanFinalProcessor'
                ],
                'loader': 'CacheLoader'
            }
        }
        
        return status
    
    def clear_cache(self) -> bool:
        """
        Clear pipeline cache
        """
        return self.cache_loader.clear()