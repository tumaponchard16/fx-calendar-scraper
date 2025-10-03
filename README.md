# ForexFactory Calendar Scraper

A Python web scraper that extracts economic events data from ## 🔧 Technical Details

- **Browser**: Playwright Chromium automation
- **Dependencies**: `playwright>=1.55.0`
- **Compatibility**: Linux, macOS, Windows
- **Default Target**: October 2, 2025 (configurable via command line)actory's economic calendar using Playwright automation.

## ⚠️ Educational Purpose Only

**IMPORTANT**: This project is for educational purposes only. Use responsibly and respect website terms of service.

## � Quick Start

### Prerequisites
- Python 3.7+
- Internet connection

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd forexcalendar-scraper
   ```

2. **Install dependencies**:
   ```bash
   pip install playwright
   python3 -m playwright install chromium
   ```

3. **Run the scraper**:
   ```bash
   # Default (October 2, 2025)
   python3 scraper.py
   
   # Specific date
   python3 scraper.py --url-params "day=oct6.2025"
   
   # Entire week
   python3 scraper.py --url-params "week=oct2.2025"
   ```

## 📊 Features

- ✅ **Playwright automation** - Fast and reliable browser automation
- ✅ **Flexible date targeting** - Command line arguments for any date or week
- ✅ **Comprehensive logging** - Debug and track scraping progress
- ✅ **CSV export** - Clean, structured data output
- ✅ **Complete event details**: Date, time, currency, impact, actual/forecast/previous values

## ⚙️ Usage Examples

### Command Line Options

```bash
# Show help and available options
python3 scraper.py --help

# Default: October 2, 2025
python3 scraper.py

# Specific date
python3 scraper.py --url-params "day=oct6.2025"

# Different date formats
python3 scraper.py --url-params "day=nov15.2025"
python3 scraper.py --url-params "day=dec25.2025"

# Entire week
python3 scraper.py --url-params "week=oct2.2025"
```

### Configuration

### Headless Mode

Enable headless mode by changing in `setup_browser()`:

```python
headless=True  # Set to True for headless mode
```

## � Output

The scraper generates:
- **`forexfactory_calendar.csv`** - Economic events data
- **`scraper.log`** - Execution logs

### Sample CSV Output
```csv
date,time,currency,impact,event,actual,forecast,previous
Thu Oct 2,12:15am,USD,Low Impact Expected,FOMC Member Barkin Speaks,,,
Thu Oct 2,1:30am,CAD,Low Impact Expected,BOC Summary of Deliberations,,,
Thu Oct 2,5:00am,USD,Low Impact Expected,FOMC Member Goolsbee Speaks,,,
```

## � Technical Details

- **Browser**: Playwright Chromium automation
- **Dependencies**: `playwright>=1.55.0`
- **Compatibility**: Linux, macOS, Windows
- **Event Capture**: 20 events from October 2, 2025

## 🚨 Troubleshooting

1. **Browser installation issues**:
   ```bash
   python3 -m playwright install chromium
   ```

2. **Permission errors**: Ensure proper file permissions
3. **Debug info**: Check `scraper.log` for detailed error information

## � License

Educational use only. Users are responsible for complying with website terms of service and using the software ethically.

---

**Remember**: Always scrape responsibly. This tool is for educational purposes only.