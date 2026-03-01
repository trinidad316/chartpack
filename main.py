#!/usr/bin/env python3
"""
MES Price Action Chart Pack Generator - Simplified Workflow
Separates data processing from chart generation for cleaner workflow
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.interfaces import DataProviderConfig
from src.data_service import MarketDataService
from src.pdf_assembler import PDFAssembler


def process_data(start_date: str, end_date: str, symbol: str = "MES", no_cache: bool = False):
    """Step 1: Process and cache market data"""
    print("=" * 60)
    print("📊 MES DATA PROCESSING")
    print("=" * 60)
    print()
    
    config = DataProviderConfig(
        provider_type="databento",
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        timeframe="5m",
        cache_enabled=not no_cache
    )
    
    try:
        data_service = MarketDataService(config)
        
        # Show provider info
        provider_info = data_service.get_provider_info()
        print(f"📈 Provider: {provider_info['name']}")
        print(f"💰 Cost: {provider_info.get('cost', 'Unknown')}")
        print(f"📅 Date Range: {start_date} to {end_date}")
        print()
        
        # Process the data
        data = data_service.get_market_data()
        
        print(f"\n✅ Data processing complete!")
        print(f"📊 Processed {len(data):,} bars")
        print(f"💾 Cache: {config.cache_path}")
        print(f"💡 Next step: python main.py --mode charts --start-date {start_date} --end-date {end_date}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Data processing failed: {e}")
        return 1


def generate_charts(start_date: str, end_date: str, symbol: str = "MES", output: str = None):
    """Step 2: Generate charts from cached data"""
    print("=" * 60)
    print("📚 MES CHART PACK GENERATION")
    print("=" * 60)
    print()
    
    config = DataProviderConfig(
        provider_type="databento",
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        timeframe="5m",
        cache_enabled=True
    )
    
    # Check if cache exists
    if not os.path.exists(config.cache_path):
        print(f"❌ No cached data found: {config.cache_path}")
        print(f"💡 Run data processing first:")
        print(f"   python main.py --mode data --start-date {start_date} --end-date {end_date}")
        return 1
    
    try:
        data_service = MarketDataService(config)
        data = data_service.get_market_data()
        
        print(f"📊 Using cached data: {len(data):,} bars")
        print(f"📅 Date Range: {start_date} to {end_date}")
        print()
        
        # Generate PDF
        assembler = PDFAssembler()
        
        if not output:
            # Create output folder if it doesn't exist
            os.makedirs("output", exist_ok=True)
            
            # Auto-generate filename based on date range
            start_str = start_date.replace('-', '')
            end_str = end_date.replace('-', '')
            output = f"output/MES_Chart_Pack_{start_str}_{end_str}.pdf"
        
        print("📚 Generating chart pack...")
        output_file = assembler.generate_chart_pack_pdf(data, output)
        
        print(f"\n✅ Chart pack generated: {output_file}")
        print(f"📊 Total bars: {len(data):,}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Chart generation failed: {e}")
        return 1


def sample_workflow():
    """Quick sample workflow: 1 week of data"""
    print("=" * 60)
    print("🚀 QUICK SAMPLE WORKFLOW")
    print("=" * 60)
    print()
    
    # Use a 1-week range for sample (fast processing)
    start_date = "2019-05-06"  # Monday  
    end_date = "2019-05-10"    # Friday (1 week for fast sample)
    
    print(f"📅 Sample Range: {start_date} to {end_date} (1 week)")
    print("⚡ Step 1: Processing sample data...")
    
    # Step 1: Process data (with caching for step 2)
    result = process_data(start_date, end_date, no_cache=False)
    if result != 0:
        return result
    
    print("\n" + "="*60)
    print("⚡ Step 2: Generating sample charts...")
    
    # Step 2: Generate charts  
    result = generate_charts(start_date, end_date, output="output/sample_pages.pdf")
    
    if result == 0:
        print("\n🎉 Sample complete!")
        print("📄 Check: output/sample_pages.pdf")
    
    return result


def main():
    parser = argparse.ArgumentParser(description='MES Chart Pack Generator - Simplified Workflow')
    
    # Mode selection
    parser.add_argument('--mode', choices=['data', 'charts', 'sample'], default='sample',
                       help='Mode: data (process data), charts (generate PDF), sample (quick test)')
    
    # Date range
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    
    # Options
    parser.add_argument('--symbol', default='MES', help='Trading symbol (default: MES)')
    parser.add_argument('--output', '-o', help='Output PDF filename (auto-generated if not provided)')
    parser.add_argument('--no-cache', action='store_true', help='Skip cache and process fresh data')
    
    args = parser.parse_args()
    
    # Ensure directories exist
    Path('data').mkdir(exist_ok=True)
    Path('samples').mkdir(exist_ok=True)
    
    if args.mode == 'sample':
        return sample_workflow()
    
    # Validate date arguments for data/charts modes
    if not args.start_date or not args.end_date:
        if args.mode in ['data', 'charts']:
            print("❌ --start-date and --end-date required for data/charts modes")
            print("💡 Example: python main.py --mode data --start-date 2024-02-01 --end-date 2024-02-07")
            return 1
    
    if args.mode == 'data':
        return process_data(args.start_date, args.end_date, args.symbol, args.no_cache)
    elif args.mode == 'charts':
        return generate_charts(args.start_date, args.end_date, args.symbol, args.output)


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code or 0)
    except KeyboardInterrupt:
        print("\n⚠️  Generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)