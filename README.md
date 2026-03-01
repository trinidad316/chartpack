# MES Price Action Chart Pack Generator

Generates printable PDF chart packs of MES (Micro E-mini S&P 500) 5-minute price action charts.

## Technical Specifications

### Chart Layout
- **Format**: 27"×19" landscape pages (300 DPI)
- **Grid**: 1×3 layout (3 charts stacked vertically per page)
- **Session**: 2am-6pm ET (192 bars per chart)
- **Time Axis**: Right-aligned price axis
- **Margins**: Wide left/right margins for annotation

### Chart Features
- **Candlestick Charts**: OHLC bars with black/white styling
- **20 EMA Overlay**: Black line  cfor trend reference
- **Round Numbers**: Horizontal lines at '00 and '50 levels
- **Date Labels**: MM/DD/YYYY format at top center

### Data Processing
- **Source**: Data Bento MES 1-minute OHLCV data
- **ETL Pipeline**: Extract → Transform → Load with data cleaning
- **Outlier Detection**: Range validation, statistical analysis, OHLC consistency
- **Timezone**: UTC → Eastern Time conversion
- **Caching**: Processed data cached for reuse

## Quick Start

### Installation
```bash
# Clone and setup
git clone [repository-url]
cd printout
make install
```

### Data Setup
The raw MES data files are not included in the repository due to GitHub's file size limits. You need to obtain and place them manually:

1. **Obtain the databento data file** (from your data provider):
   - `GLBX-20260301-5V5QDD9JH6.zip` (45MB compressed)
   - Contains MES 1-minute OHLCV data from 2010-2026

2. **Place and extract the data file**:
   ```bash
   # Place the zip file in the databento directory
   cp /path/to/your/GLBX-20260301-5V5QDD9JH6.zip data/databento/
   
   # Extract it
   cd data/databento
   unzip GLBX-20260301-5V5QDD9JH6.zip
   ```

3. **Verify the data structure**:
   ```
   data/
   └── databento/                                # ⚠️  Entire directory git-ignored
       ├── GLBX-20260301-5V5QDD9JH6.zip          # 45MB compressed file
       └── GLBX-20260301-5V5QDD9JH6/             # 365MB extracted folder
           └── glbx-mdp3-20100606-20260228.ohlcv-1m.csv
   ```

**Note**: All databento files are git-ignored to stay under GitHub's file size limits. You must provide the data files separately.

### Generate Chart Packs
```bash
# Generate a sample chart pack (1 week)
make sample

# Generate charts for any date range
make generate START=2019-05-06 END=2019-05-10

# Advanced: Separate data processing and chart generation  
make data START=2019-05-06 END=2019-05-10      # Process data (optional)
make charts START=2019-05-06 END=2019-05-10    # Generate charts (optional)
```

### Output
- **Chart Pack**: `output/MES_Chart_Pack_YYYYMMDD_YYYYMMDD.pdf`
- **Sample**: `output/sample_pages.pdf`
- **Print Settings**: 27"×19" landscape, 300 DPI

### Cleanup
```bash
make clean          # Remove generated PDFs
make clean-data     # Remove cached data files
make clean-all      # Clean everything
```

## Technical Implementation

### Required Libraries
```python
import pandas as pd            # Data manipulation
import matplotlib.pyplot as plt # Chart generation  
import numpy as np             # Numerical operations
from matplotlib.backends.backend_pdf import PdfPages
```

### Architecture
- **Data Providers**: Interface-based system for different data sources
- **ETL Pipeline**: Modular Extract, Transform, Load processing
- **Chart Generator**: Matplotlib-based candlestick chart creation
- **PDF Assembler**: Multi-page PDF generation with proper layout

### Configuration
Chart settings, layout parameters, and styling options are centralized in `src/config.py`.