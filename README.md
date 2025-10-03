# ForexFactory Calendar Scraper

A Python web scraper that extracts economic events data from ForexFactory's economic calendar using Playwright automation.

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
   python3 scraper.py
   ```

## 📊 Features

- ✅ **Playwright automation** - Fast and reliable browser automation
- ✅ **Date-specific scraping** - Currently configured for October 2, 2025
- ✅ **Comprehensive logging** - Debug and track scraping progress
- ✅ **CSV export** - Clean, structured data output
- ✅ **Complete event details**: Date, time, currency, impact, actual/forecast/previous values

## ⚙️ Configuration

### Change Target Date

Modify the URL in `scraper.py` to target different dates:

```python
# Current setting (October 2, 2025)
url = "https://www.forexfactory.com/calendar?day=oct2.2025"

# For different dates
url = "https://www.forexfactory.com/calendar?day=oct15.2025"  # October 15
url = "https://www.forexfactory.com/calendar?week=oct2.2025"  # Entire week
```

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