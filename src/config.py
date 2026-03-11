"""
MES Chart Pack Configuration
Simple settings you can adjust to customize your chart pack
"""

# =============================================================================
# CHART SETTINGS
# =============================================================================

# How many 5-minute bars to show per chart
# 160 bars = 13h20m (2:40am-4pm ET trading session)
BARS_PER_CHART = 160

# Moving Averages
EMA_20 = 20          # Fast EMA period
EMA_20_COLOR = 'black'       # Dark black line
EMA_20_ALPHA = 0.8           # Opacity (0.0-1.0)

EMA_80 = 80          # Slow EMA period
EMA_80_COLOR = "#DCDCDC"     # Light gray line
EMA_80_ALPHA = 0.5           # Opacity (0.0-1.0)


# =============================================================================
# PAGE LAYOUT
# =============================================================================

# How many charts per page
CHARTS_PER_PAGE = 2          # 2 charts stacked vertically

# Page dimensions (inches)
PAGE_WIDTH = 17              # 17 inches wide
PAGE_HEIGHT = 11             # 11 inches tall

# Print quality
DPI = 300                    # 300 DPI for high quality printing


# =============================================================================
# CHART STYLING
# =============================================================================

# Candlestick colors
UP_CANDLE = 'white'          # White body for bullish candles
DOWN_CANDLE = 'black'        # Black body for bearish candles
WICK_COLOR = 'black'         # Black wicks
EDGE_COLOR = 'black'         # Black edges

# Round number levels (horizontal lines at '00 and '50 prices)
ROUND_NUMBER_COLOR = '#d0d0d0'    # Light gray
ROUND_NUMBER_ALPHA = 0.6          # Opacity
ROUND_NUMBER_SPACING = 50         # Show lines every 50 points


# =============================================================================
# ADVANCED SETTINGS (usually don't need to change these)
# =============================================================================

# Font sizes
TITLE_SIZE = 12
LABEL_SIZE = 8
TICK_SIZE = 7

# Y-axis padding (% of day's range added above and below price action)
Y_AXIS_PADDING = 0.25        # 25% padding on each side

# Chart spacing and margins
CHART_SPACING = 1.0          # Annotation space between charts
LEFT_MARGIN = 0.15           # Wide margins for annotations
RIGHT_MARGIN = 0.85
TOP_MARGIN = 0.97            # (1 - 0.25/11 ≈ 0.977)
BOTTOM_MARGIN = 0.03         # (0.25/11 ≈ 0.023)
