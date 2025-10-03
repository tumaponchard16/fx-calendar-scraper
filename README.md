# ForexFactory Calendar Scraper

A Python web scraper that extracts economic events data from ForexFactory's economic calendar using Playwright automation.

## ⚠️ Educational Purpose Only

**IMPORTANT**: This project is for educational purposes only. Use responsibly and respect website terms of service.

## 🚀 Quick Start

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
- ✅ **Event detail IDs** - Capture unique detail IDs for each event
- ✅ **Comprehensive logging** - Debug and track scraping progress
- ✅ **CSV export** - Clean, structured data output
- ✅ **Complete event details**: Date, time, currency, impact, actual/forecast/previous values, detail IDs

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
date,time,currency,impact,event,actual,forecast,previous,detail
Mon Oct 6,All Day,AUD,Non-Economic,Bank Holiday,,,,140544
Mon Oct 6,8:00am,AUD,Low Impact Expected,MI Inflation Gauge m/m,,,-0.3%,144102
Mon Oct 6,3:00pm,CHF,Low Impact Expected,Unemployment Rate,,2.9%,2.9%,140797
```

### Detail URLs
Use the detail ID to access specific event details:
```
https://www.forexfactory.com/calendar?day=oct6.2025#detail=140544
```

## 🔧 Technical Details

- **Browser**: Playwright Chromium automation
- **Dependencies**: `playwright>=1.55.0`
- **Compatibility**: Linux, macOS, Windows
- **Default Target**: October 2, 2025 (configurable via command line)
- **Event Detail IDs**: Extracts unique detail identifiers for direct event access

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