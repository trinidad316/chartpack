"""
PDF Assembly Module for MES Price Action Chart Pack Generator
Combines individual charts into printable pages and generates final PDF
"""
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
from datetime import datetime
from src.config import *
from src.chart_generator import ChartGenerator, chunk_data_into_segments

class PDFAssembler:
    def __init__(self):
        self.chart_generator = ChartGenerator()
        
    def create_page_with_charts(self, data_segments, page_number, start_chart_index):
        """
        Create a single page with up to 4 charts in 2x2 grid
        """
        # Create figure with TradingView-style clean layout
        fig = plt.figure(figsize=FIGURE_SIZE, facecolor='white')
        fig.patch.set_facecolor('white')
        
        # Add page header - centered
        page_title = f"Chart Pack - {page_number}"
        fig.text(0.5, 0.98, page_title, fontsize=FONT_SIZES['title'] + 2, 
                ha='center', va='top', transform=fig.transFigure)
        
        # Create subplots in 2x2 grid
        charts_on_page = min(len(data_segments), CHARTS_PER_PAGE)
        
        for i, segment in enumerate(data_segments[:CHARTS_PER_PAGE]):
            # Calculate subplot position for current layout
            subplot_index = i + 1
            
            # Create subplot (nrows=CHARTS_PER_COL, ncols=CHARTS_PER_ROW, index=subplot_index)
            ax = plt.subplot(CHARTS_PER_COL, CHARTS_PER_ROW, subplot_index)
            
            # Generate the chart
            self.chart_generator.create_candlestick_chart(ax, segment)
            self.chart_generator.add_ema_overlay(ax, segment)
            self.chart_generator.format_chart_axes(ax, segment, start_chart_index + i)
        
        # Adjust layout
        plt.subplots_adjust(
            top=MARGINS['top'], 
            bottom=MARGINS['bottom'],
            left=MARGINS['left'], 
            right=MARGINS['right'],
            hspace=CHART_SPACING['hspace'], 
            wspace=CHART_SPACING['wspace']
        )
        
        
        return fig
    
    def create_month_separator_page(self, month_date):
        """Create a dedicated month separator page"""
        fig = plt.figure(figsize=FIGURE_SIZE, facecolor='white')
        fig.patch.set_facecolor('white')
        
        # Create single large text area
        ax = plt.subplot(1, 1, 1)
        ax.axis('off')  # Remove axes
        
        # Format month and year
        month_name = month_date.strftime('%B %Y')
        
        # Add large centered text
        ax.text(0.5, 0.6, month_name, 
               transform=ax.transAxes, fontsize=48, weight='bold',
               ha='center', va='center', color='#333')
        
        # Add subtitle
        ax.text(0.5, 0.4, 'MES Price Action Analysis', 
               transform=ax.transAxes, fontsize=24,
               ha='center', va='center', color='#666')
        
        
        return fig
    
    def create_quarter_separator_page(self, quarter_date):
        """Create a dedicated quarter separator page"""
        fig = plt.figure(figsize=FIGURE_SIZE, facecolor='white')
        fig.patch.set_facecolor('white')
        
        # Create single large text area
        ax = plt.subplot(1, 1, 1)
        ax.axis('off')  # Remove axes
        
        # Calculate quarter
        quarter = (quarter_date.month - 1) // 3 + 1
        year = quarter_date.year
        
        # Add large centered text
        ax.text(0.5, 0.6, f'Q{quarter} {year}', 
               transform=ax.transAxes, fontsize=60, weight='bold',
               ha='center', va='center', color='#2c3e50')
        
        # Add subtitle
        ax.text(0.5, 0.4, 'Quarterly Price Action Review', 
               transform=ax.transAxes, fontsize=28,
               ha='center', va='center', color='#7f8c8d')
        
        # Add quarter months
        quarter_months = {
            1: 'January - February - March',
            2: 'April - May - June', 
            3: 'July - August - September',
            4: 'October - November - December'
        }
        ax.text(0.5, 0.25, quarter_months[quarter], 
               transform=ax.transAxes, fontsize=18,
               ha='center', va='center', color='#95a5a6')
        
        
        return fig
    
    def generate_chart_pack_pdf(self, data, output_filename):
        """
        Generate the complete chart pack PDF
        """
        print("Generating MES Price Action Chart Pack...")
        
        # Chunk data into chart segments
        print("Chunking data into chart segments...")
        segments = chunk_data_into_segments(data, BARS_PER_CHART)
        total_charts = len(segments)
        total_pages = (total_charts + CHARTS_PER_PAGE - 1) // CHARTS_PER_PAGE
        
        print(f"Creating {total_charts} charts across {total_pages} pages...")
        
        # Ensure output directory exists
        import os
        output_dir = os.path.dirname(output_filename)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Generate PDF with month and quarter separators
        with PdfPages(output_filename) as pdf:
            current_month = None
            current_quarter = None
            page_count = 0
            
            # Process segments with separator pages
            i = 0
            while i < len(segments):
                segment = segments[i]
                segment_date = segment.index[0]
                
                # Check for quarter change (insert before month check)
                quarter = (segment_date.month - 1) // 3 + 1
                if current_quarter != (segment_date.year, quarter):
                    if current_quarter is not None:  # Skip first quarter page
                        print(f"Adding Q{quarter} {segment_date.year} separator page...")
                        fig = self.create_quarter_separator_page(segment_date)
                        pdf.savefig(fig, dpi=DPI, facecolor='white', 
                                   edgecolor='none', bbox_inches='tight')
                        plt.close(fig)
                        page_count += 1
                    current_quarter = (segment_date.year, quarter)
                
                # Check for month change
                if current_month != (segment_date.year, segment_date.month):
                    print(f"Adding {segment_date.strftime('%B %Y')} separator page...")
                    fig = self.create_month_separator_page(segment_date)
                    pdf.savefig(fig, dpi=DPI, facecolor='white', 
                               edgecolor='none', bbox_inches='tight')
                    plt.close(fig)
                    current_month = (segment_date.year, segment_date.month)
                    page_count += 1
                
                # Collect segments for this page
                page_segments = []
                for j in range(CHARTS_PER_PAGE):
                    if i + j < len(segments):
                        page_segments.append(segments[i + j])
                
                # Create the regular chart page
                page_count += 1
                print(f"Generating page {page_count} (charts {i + 1}-{i + len(page_segments)})...")
                
                fig = self.create_page_with_charts(
                    page_segments, 
                    page_count, 
                    i
                )
                
                # Save to PDF
                pdf.savefig(fig, dpi=DPI, facecolor='white', 
                           edgecolor='none', bbox_inches='tight')
                plt.close(fig)
                
                i += len(page_segments)
            
            # Add metadata to PDF
            metadata = pdf.infodict()
            metadata['Title'] = 'MES Price Action Chart Pack'
            metadata['Author'] = 'MES Chart Pack Generator'
            metadata['Subject'] = 'Price Action Analysis Charts'
            metadata['Creator'] = 'Python matplotlib'
            metadata['CreationDate'] = datetime.now()
        
        print(f"✅ PDF generated successfully: {output_filename}")
        print(f"📊 Total charts: {total_charts}")
        print(f"📄 Total pages: {page_count} (including month/quarter separators)")
        print(f"🖨️  Recommended print size: {PAGE_SIZE[0]}\"x{PAGE_SIZE[1]}\" landscape")
        
        return output_filename
    
    def generate_sample_pages(self, data, num_pages=2):
        """
        Generate a few sample pages for preview including separator pages
        Use February 2026 data for sample
        """
        # Use provided data for sample generation
        print("Generating sample data...")
        feb_data = data[:1000]  # Use first 1000 bars for sample
        
        segments = chunk_data_into_segments(feb_data, BARS_PER_CHART)
        sample_filename = 'samples/sample_pages.pdf'
        
        print(f"Generating sample pages with month separators...")
        
        with PdfPages(sample_filename) as pdf:
            # Add a sample quarter separator page first
            if len(segments) > 0:
                print("Adding sample quarter separator page...")
                fig = self.create_quarter_separator_page(segments[0].index[0])
                pdf.savefig(fig, dpi=DPI, facecolor='white', 
                           edgecolor='none', bbox_inches='tight')
                plt.close(fig)
                
                print("Adding sample month separator page...")
                fig = self.create_month_separator_page(segments[0].index[0])
                pdf.savefig(fig, dpi=DPI, facecolor='white', 
                           edgecolor='none', bbox_inches='tight')
                plt.close(fig)
            
            # Add sample chart pages
            pages_generated = 0
            for page_num in range(min(num_pages, (len(segments) + CHARTS_PER_PAGE - 1) // CHARTS_PER_PAGE)):
                start_idx = page_num * CHARTS_PER_PAGE
                end_idx = min(start_idx + CHARTS_PER_PAGE, len(segments))
                page_segments = segments[start_idx:end_idx]
                
                fig = self.create_page_with_charts(page_segments, page_num + 1, start_idx)
                pdf.savefig(fig, dpi=DPI, facecolor='white', 
                           edgecolor='none', bbox_inches='tight')
                plt.close(fig)
                pages_generated += 1
        
        print(f"✅ Sample pages generated: {sample_filename}")
        print(f"📄 Includes: Q1 2026 + February 2026 separators + {pages_generated} chart pages")
        print(f"📅 Sample shows: One week in February 2024 (02/26-03/01)")
        print(f"📊 Charts: {len(segments)} trading day charts (Mon-Fri)")
        print(f"💡 Synthetic MES data provides realistic price action patterns for study!")
        return sample_filename

def create_chart_pack(data_file, output_file):
    """
    Main function to create the complete chart pack
    """
    # Load data
    print("Loading MES data...")
    data = pd.read_csv(data_file, index_col=0, parse_dates=True)
    
    # Create PDF assembler and generate chart pack
    assembler = PDFAssembler()
    return assembler.generate_chart_pack_pdf(data, output_file)