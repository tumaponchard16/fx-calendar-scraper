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

# Extract detailed specifications
python3 detail_extractor.py --date-param "day=oct6.2025"
```

## 📋 Two-Step Process

### Step 1: Extract Basic Events
```bash
python3 scraper.py --url-params "day=oct6.2025"
```
Generates: `forexfactory_calendar.csv` with basic event data

### Step 2: Extract Detailed Specifications  
```bash
python3 detail_extractor.py --date-param "day=oct6.2025"
```
Generates: `forexfactory_event_details.csv` with comprehensive specifications

## 📊 Features

- ✅ **Playwright automation** - Fast and reliable browser automation
- ✅ **Flexible date targeting** - Command line arguments for any date or week
- ✅ **Event detail IDs** - Capture unique detail IDs for each event
- ✅ **Detailed specifications extraction** - Extract complete event specifications
- ✅ **Comprehensive logging** - Debug and track scraping progress
- ✅ **CSV export** - Clean, structured data output
- ✅ **Complete event details**: Date, time, currency, impact, actual/forecast/previous values, detail IDs

## ⚙️ Usage Examples

### Command Line Options

#### Main Scraper
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

#### Detail Extractor
```bash
# Show help for detail extractor
python3 detail_extractor.py --help

# Default: Use forexfactory_calendar.csv with day=oct6.2025
python3 detail_extractor.py

# Custom CSV file
python3 detail_extractor.py --csv-file my_events.csv

# Custom date parameter
python3 detail_extractor.py --date-param "day=oct2.2025"

# Both custom
python3 detail_extractor.py --csv-file events.csv --date-param "day=nov15.2025"
```

### Configuration

### Headless Mode

Enable headless mode by changing in `setup_browser()`:

```python
headless=True  # Set to True for headless mode
```

## 📄 Output

The scraper generates:
- **`forexfactory_calendar.csv`** - Basic economic events data
- **`forexfactory_event_details.csv`** - Detailed event specifications
- **`scraper.log`** - Main scraper execution logs
- **`detail_extractor.log`** - Detail extraction logs

### Basic Events CSV
```csv
date,time,currency,impact,event,actual,forecast,previous,detail
Mon Oct 6,All Day,AUD,Non-Economic,Bank Holiday,,,,140544
Mon Oct 6,8:00am,AUD,Low Impact Expected,MI Inflation Gauge m/m,,,-0.3%,144102
Mon Oct 6,3:00pm,CHF,Low Impact Expected,Unemployment Rate,,2.9%,2.9%,140797
```

### Detailed Specifications CSV
```csv
detail_id,event_date,event_time,event_currency,event_name,description,ff_notes,next_release,usual_effect,why_traderscare
140544,Mon Oct 6,All Day,AUD,Bank Holiday,"Banks closed for Labor Day","Forex brokers remain open","Dec 25, 2025","Low liquidity","Banks facilitate majority of FX volume"
144102,Mon Oct 6,8:00am,AUD,MI Inflation Gauge m/m,"Monthly inflation measurement","Leading indicator of CPI","Nov 6, 2025","Currency volatility","Inflation impacts central bank policy"
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
- **Main Scraper**: Extracts basic event data with detail IDs
- **Detail Extractor**: Extracts comprehensive event specifications
- **Default Target**: October 2, 2025 (configurable via command line)

## 🚨 Troubleshooting

1. **Browser installation issues**:
   ```bash
   python3 -m playwright install chromium
   ```

2. **Missing CSV file error**: Run the main scraper first to generate `forexfactory_calendar.csv`
3. **Permission errors**: Ensure proper file permissions
4. **Debug info**: Check `scraper.log` and `detail_extractor.log` for detailed error information

## � License

Educational use only. Users are responsible for complying with website terms of service and using the software ethically.

---

**Remember**: Always scrape responsibly. This tool is for educational purposes only.