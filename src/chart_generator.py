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
            'font.size': FONT_SIZES['tick_label'],
            'axes.labelsize': FONT_SIZES['axis_label'],
            'axes.titlesize': FONT_SIZES['title'],
            'xtick.labelsize': FONT_SIZES['tick_label'],
            'ytick.labelsize': FONT_SIZES['tick_label'],
            'legend.fontsize': FONT_SIZES['tick_label'],
            'figure.titlesize': FONT_SIZES['title']
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
    
    def add_ema_overlay(self, ax, data, period=EMA_PERIOD):
        """Add EMA overlay to the chart"""
        if len(data) >= period:
            ema = data['close'].ewm(span=period).mean()
            x_positions = range(len(data))
            ax.plot(x_positions, ema.values, color=EMA_COLOR, 
                   alpha=EMA_ALPHA, linewidth=1.0, label=f'{period} EMA', zorder=2)
    
    def format_chart_axes(self, ax, data, chart_index):
        """Format chart axes with TradingView-style formatting and compressed Y-axis"""
        # Set date in top center with very light font for subtle reference
        chart_date = data.index[0].strftime('%m/%d/%Y')
        ax.text(0.5, 0.95, chart_date, 
               transform=ax.transAxes, fontsize=FONT_SIZES['title'], 
               ha='center', va='top', color='#ccc', weight='normal', alpha=0.7)
        
        # Calculate Y-axis range based on desired number of '00/'50 round number levels
        y_min, y_max = data['low'].min(), data['high'].max()
        price_center = (y_min + y_max) / 2
        
        # Show 2 levels of '00/'50 round numbers (each level = 50 points)
        desired_levels = 2.0  # 2 levels for maximum tall candles
        level_spacing = 50    # '00 and '50 levels are 50 points apart
        target_range = desired_levels * level_spacing  # 3.5 * 50 = 175 points
        
        # Center the range around the price action
        y_bottom = price_center - target_range / 2
        y_top = price_center + target_range / 2
        
        # Ensure we don't cut off actual price action (small buffer only if needed)
        actual_buffer = 5  # Small buffer to avoid clipping
        if y_bottom > y_min - actual_buffer:
            y_bottom = y_min - actual_buffer
        if y_top < y_max + actual_buffer:
            y_top = y_max + actual_buffer
        
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
        ax.tick_params(axis='y', colors='#666', labelsize=FONT_SIZES['tick_label'])
        
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
        ax.set_xticklabels(hourly_labels, color='#666', fontsize=FONT_SIZES['tick_label'])
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
        major_spacing = 50  # Major round numbers (50-point intervals for '00 and '50 levels)
        major_start = int((y_bottom - 25) // major_spacing) * major_spacing
        current_major = major_start
        while current_major <= y_top + 25:
            if y_bottom <= current_major <= y_top:
                # Light horizontal lines only at '00 and '50 levels
                ax.axhline(y=current_major, color='#d0d0d0', alpha=0.6, linewidth=0.4, zorder=0)
            current_major += major_spacing
        
        # Set axis limits
        ax.set_xlim(0, len(data) - 1)
        
        # Remove top and left spines, style right spine for Y-axis
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_color('#ddd')
        ax.spines['bottom'].set_color('#ddd')
    
    def create_individual_chart(self, data_segment, chart_index):
        """Create a complete individual chart with all overlays"""
        fig, ax = plt.subplots(1, 1, figsize=(9, 6))
        
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
    Chunk data into 2am-6pm Eastern time extended sessions
    Each chart shows extended trading segments from 2:00 AM to 6:00 PM ET (16 hours)
    """
    segments = []
    
    # Group data by date
    data_by_date = data.groupby(data.index.date)
    
    for date, day_data in data_by_date:
        # Find 2am start for this date (Eastern Time)
        start_time = pd.Timestamp(date).replace(hour=2, minute=0)
        # Find 6pm end for this date (Eastern Time)  
        end_time = pd.Timestamp(date).replace(hour=18, minute=0)
        
        # Filter to 2am-6pm window only
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