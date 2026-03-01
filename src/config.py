"""
Configuration settings for MES Price Action Chart Pack Generator
"""

# Chart Layout Configuration - 1x3 Vertical Stack Layout
CHARTS_PER_ROW = 1  # 1 chart horizontally (full width)
CHARTS_PER_COL = 3  # 3 rows vertically
CHARTS_PER_PAGE = CHARTS_PER_ROW * CHARTS_PER_COL  # = 3 charts per page

# Chart Technical Settings
BARS_PER_CHART = 192  # 16 hours (2am-6pm) of 5-minute data - extended sessions for more bars per chart
EMA_PERIOD = 20
EMA_COLOR = 'black'  # Black EMA line
EMA_ALPHA = 0.8

# Round Number Levels
ROUND_NUMBER_COLOR = 'gray'
ROUND_NUMBER_ALPHA = 0.15
ROUND_NUMBER_INTERVALS = [0.00, 0.50]  # '00 and '50 levels

# PDF Output Settings
DPI = 300
PAGE_SIZE = (27, 19)  # 27x19 inches (landscape) - larger to maintain bar spacing with 144 bars
FIGURE_SIZE = (27, 19)
MARGINS = {'top': 0.95, 'bottom': 0.05, 'left': 0.15, 'right': 0.85}  # Wide left/right margins, tight vertical for 3 charts
CHART_SPACING = {'hspace': 0.25, 'wspace': 0.1}  # Moderate spacing between 3 vertical charts

# Chart Styling - TradingView Style (Black & White)
CANDLESTICK_COLORS = {
    'up_color': 'black',      # Black for up candles
    'down_color': 'white',    # White for down candles  
    'up_wick': 'black',       # Black wicks for up
    'down_wick': 'black',     # Black wicks for down
    'edge_color': 'black'     # Black edges for all candles
}

GRID_STYLE = {
    'color': 'lightgray',
    'alpha': 0.3,
    'linestyle': '-',
    'linewidth': 0.5
}

# Font Settings
FONT_SIZES = {
    'title': 12,
    'axis_label': 8,
    'tick_label': 7
}