# Daraz Product Scraper

A modern, modular web scraper for Daraz.com.np with live updates and clean UI.

## Features

- **Live Progress Updates** - See real-time scraping status
- **Modular Architecture** - Clean, maintainable code
- **Smart Filtering** - Filter results after scraping
- **CSV Export** - Download data for analysis
- **Beautiful UI** - Modern, intuitive interface

## Project Structure

```
Daraz_webscraper/
├── app.py              # Main Streamlit application (entry point)
├── scraper.py          # Web scraping logic with Selenium
├── ui_components.py    # Reusable UI components (NEW!)
├── requirements.txt    # Python dependencies
├── runtime.txt         # Python version
└── packages.txt        # System packages
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app:**
   ```bash
   streamlit run app.py
   ```

3. **Use the app:**
   - Enter product name in sidebar
   - Select number of pages (2-3 recommended)
   - Click "Search Products"
   - Watch live updates!

## Modular Components

### `app.py` - Main Application
- Clean entry point
- Orchestrates UI components
- Handles scraping with live callbacks

### `scraper.py` - Scraping Logic
- Selenium-based scraper
- Support for progress callbacks
- Multi-page navigation
- Duplicate detection

### `ui_components.py` - UI Components
- `apply_custom_css()` - Custom styling
- `render_header()` - App header
- `render_sidebar()` - Settings sidebar
- `render_statistics()` - Metrics display
- `render_results_table()` - Data table with filters
- `render_download_button()` - CSV export
- `render_welcome_screen()` - Landing page

## Usage Tips

- **Start small:** Use 2-3 pages for quick results
- **Filter results:** Use the search box to find specific products
- **Export data:** Download CSV for Excel/analysis
- **Watch progress:** Live updates show current status

## Technical Details

- **Framework:** Streamlit
- **Scraping:** Selenium + ChromeDriver
- **Data:** Pandas DataFrames
- **UI:** Custom CSS + Streamlit components

## Sample Output

The scraper extracts:
- Product names
- Prices (in NPR)
- Sales information
- All data exportable to CSV

---

Built with for e-commerce analysis
