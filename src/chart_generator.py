"""
Chart Generation Module for MES Price Action Chart Pack Generator
Creates individual price action charts with technical overlays
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import pandas as pd
import numpy as np
from src.config import *

class ChartGenerator:
    def __init__(self):
        plt.style.use('default')
        self.setup_matplotlib_params()
    
    def setup_matplotlib_params(self):
        """Configure matplotlib for high-quality chart output"""
        plt.rcParams.update({
            'figure.dpi': DPI,
            'savefig.dpi': DPI,
            'font.size': TICK_SIZE,
            'axes.labelsize': LABEL_SIZE,
            'axes.titlesize': TITLE_SIZE,
            'xtick.labelsize': TICK_SIZE,
            'ytick.labelsize': TICK_SIZE,
            'legend.fontsize': TICK_SIZE,
            'figure.titlesize': TITLE_SIZE
        })
    
    def create_candlestick_chart(self, ax, data, title=""):
        """Create a TradingView-style candlestick chart"""
        # Clear the axis and set white background
        ax.clear()
        ax.set_facecolor('white')
        
        # Prepare data
        dates = data.index
        opens = data['open'].values
        highs = data['high'].values
        lows = data['low'].values
        closes = data['close'].values
        
        # Create candlesticks manually for TradingView style
        for i, (date, o, h, l, c) in enumerate(zip(dates, opens, highs, lows, closes)):
            # All wicks are black (drawn on top of EMA)
            ax.plot([i, i], [l, h], color='black', linewidth=0.6, alpha=0.8, zorder=5)
            
            # Draw the body (open-close rectangle)
            body_height = abs(c - o)
            body_bottom = min(o, c)
            
            if body_height < 0.01:  # Doji - draw as thin line
                ax.plot([i-0.35, i+0.35], [o, c], color='black', linewidth=1.0, zorder=5)
            else:
                if c >= o:  # Up candle - opaque white body, black edge (drawn on top)
                    rect = Rectangle((i-0.4, body_bottom), 0.8, body_height, 
                                   facecolor='white', edgecolor='black', linewidth=0.6, 
                                   alpha=1.0, zorder=5)
                else:  # Down candle - black body (drawn on top)
                    rect = Rectangle((i-0.4, body_bottom), 0.8, body_height, 
                                   facecolor='black', edgecolor='black', linewidth=0.6, 
                                   alpha=1.0, zorder=5)
                ax.add_patch(rect)
        
        return ax
    
    def add_ema_overlay(self, ax, data):
        """Add EMA overlays to the chart (20 EMA and 80 EMA)"""
        x_positions = range(len(data))

        # Add 80 EMA (slower, lighter) - drawn first so it's behind
        if len(data) >= EMA_80:
            ema_slow = data['close'].ewm(span=EMA_80).mean()
            ax.plot(x_positions, ema_slow.values, color=EMA_80_COLOR,
                   alpha=EMA_80_ALPHA, linewidth=1.0, label=f'{EMA_80} EMA', zorder=1)

        # Add 20 EMA (faster, darker) - drawn second so it's on top
        if len(data) >= EMA_20:
            ema_fast = data['close'].ewm(span=EMA_20).mean()
            ax.plot(x_positions, ema_fast.values, color=EMA_20_COLOR,
                   alpha=EMA_20_ALPHA, linewidth=1.0, label=f'{EMA_20} EMA', zorder=2)
    
    def format_chart_axes(self, ax, data, chart_index):
        """Format chart axes with TradingView-style formatting and compressed Y-axis"""
        # Set date in top center with very light font for subtle reference
        chart_date = data.index[0].strftime('%m/%d/%Y')
        ax.text(0.5, 0.95, chart_date,
               transform=ax.transAxes, fontsize=TITLE_SIZE,
               ha='center', va='top', color='#ccc', weight='normal', alpha=0.7)
        
        # Auto-fit Y-axis to each day's actual price range (normalizes volatility)
        y_min, y_max = data['low'].min(), data['high'].max()
        day_range = y_max - y_min
        padding = day_range * 0.08  # 8% padding above and below
        y_bottom = y_min - padding
        y_top = y_max + padding
        
        ax.set_ylim(y_bottom, y_top)
        
        # Y-axis ticks at '00 and '50 round number levels (every 25 points)
        y_tick_spacing = 25  # Show both '00 and '50 levels (25-point intervals)
        
        # Find '00 and '50 levels within our range
        tick_start = int((y_bottom - 25) // y_tick_spacing) * y_tick_spacing
        y_ticks = []
        current_tick = tick_start
        while current_tick <= y_top + 25:
            if y_bottom - 10 <= current_tick <= y_top + 10:  # Include nearby ticks
                y_ticks.append(current_tick)
            current_tick += y_tick_spacing
        
        # Force matplotlib to use our custom ticks
        ax.set_yticks(y_ticks)
        # Clean formatting for round numbers: "4,800" instead of "4,800.0000"
        ax.set_yticklabels([f'{int(tick):,}' for tick in y_ticks])  # Format: "4,800", "4,825", etc.
        ax.yaxis.set_major_locator(plt.FixedLocator(y_ticks))
        ax.tick_params(axis='y', colors='#666', labelsize=TICK_SIZE)
        
        # Move Y-axis to the right side
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position('right')
        
        # X-axis with hourly labels and 30-minute tick marks
        bars_per_hour = 12  # 60 minutes / 5 minutes per bar = 12 bars per hour
        bars_per_30min = 6  # 30 minutes / 5 minutes per bar = 6 bars per 30min
        
        # Find hourly positions and labels
        hourly_positions = []
        hourly_labels = []
        
        for i in range(0, len(data), bars_per_hour):
            if i < len(data):
                hourly_positions.append(i)
                hour_time = data.index[i].strftime('%H:%M')
                hourly_labels.append(hour_time)
        
        # Set major ticks at hourly intervals
        ax.set_xticks(hourly_positions)
        ax.set_xticklabels(hourly_labels, color='#666', fontsize=TICK_SIZE)
        ax.tick_params(axis='x', which='major', colors='#666', length=5, width=1)
        
        # Add minor tick marks at 30-minute intervals on the X-axis itself
        thirty_min_positions = []
        for i in range(bars_per_30min, len(data), bars_per_hour):  # 30min marks: 6, 18, 30, 42...
            if i < len(data):
                thirty_min_positions.append(i)
        
        # Set minor ticks at 30-minute intervals (small marks on axis line)
        ax.set_xticks(thirty_min_positions, minor=True)
        ax.tick_params(axis='x', which='minor', length=3, width=0.5, colors='#666')
        
        # Light horizontal grid lines only at '00 and '50 levels (not '25 or '75)
        ax.grid(False)  # Turn off automatic grid
        
        # Add horizontal lines only at major '00 and '50 round number levels
        major_start = int((y_bottom - 25) // ROUND_NUMBER_SPACING) * ROUND_NUMBER_SPACING
        current_major = major_start
        while current_major <= y_top + 25:
            if y_bottom <= current_major <= y_top:
                # Light horizontal lines only at '00 and '50 levels
                ax.axhline(y=current_major, color=ROUND_NUMBER_COLOR, alpha=ROUND_NUMBER_ALPHA, linewidth=0.4, zorder=0)
            current_major += ROUND_NUMBER_SPACING
        
        # Set axis limits
        ax.set_xlim(0, len(data) - 1)
        
        # Remove top and left spines, style right spine for Y-axis
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_color('#ddd')
        ax.spines['bottom'].set_color('#ddd')
    
    def create_individual_chart(self, data_segment, chart_index):
        """Create a complete individual chart with all overlays"""
        fig, ax = plt.subplots(1, 1, figsize=(15, 4))
        
        # Create the candlestick chart
        self.create_candlestick_chart(ax, data_segment)
        
        # Add technical overlays
        self.add_ema_overlay(ax, data_segment)
        
        # Format the chart (includes round number levels and other formatting)
        self.format_chart_axes(ax, data_segment, chart_index)
        
        plt.tight_layout()
        return fig, ax

def chunk_data_into_segments(data, bars_per_chart=BARS_PER_CHART):
    """
    Chunk data into 6am-4pm Eastern time sessions
    Each chart shows the regular trading session from 6:00 AM to 4:00 PM ET (10 hours)
    """
    segments = []
    
    # Group data by date
    data_by_date = data.groupby(data.index.date)
    
    for date, day_data in data_by_date:
        # Find 6am start for this date (Eastern Time)
        start_time = pd.Timestamp(date).replace(hour=6, minute=0)
        # Find 4pm end for this date (Eastern Time)
        end_time = pd.Timestamp(date).replace(hour=16, minute=0)

        # Filter to 6am-4pm window only
        session_data = day_data[(day_data.index >= start_time) & (day_data.index < end_time)]
        
        # Split long sessions into multiple charts if needed for more charts per day
        if len(session_data) > bars_per_chart:
            # Split into multiple segments within the trading day
            for start_idx in range(0, len(session_data), bars_per_chart):
                end_idx = min(start_idx + bars_per_chart, len(session_data))
                segment = session_data.iloc[start_idx:end_idx]
                
                if len(segment) >= bars_per_chart * 0.5:
                    segments.append(segment)
        else:
            # Single chart per trading day
            if len(session_data) >= bars_per_chart * 0.5:
                segments.append(session_data)
    
    return segments