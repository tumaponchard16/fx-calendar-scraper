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
python3 scraper.py --url-params "day=oct18.2025"
```
Generates: `day=oct18.2025.csv` with basic event data (filename matches URL params)

### Step 2: Extract Detailed Specifications  
```bash
python3 detail_extractor.py --csv-file "day=oct18.2025.csv" --date-param "day=oct18.2025"
```
Generates: `day=oct18.2025_details.csv` with comprehensive specifications for ALL events in a single file

## 📊 Features

- ✅ **Playwright automation** - Fast and reliable browser automation
- ✅ **Flexible date targeting** - Command line arguments for any date or week
- ✅ **Event detail IDs** - Capture unique detail IDs for each event
- ✅ **Dynamic header capture** - Automatically extracts ALL unique specification fields
- ✅ **Detailed specifications extraction** - Extract complete event specifications
- ✅ **Single file output** - All events with all unique headers in one CSV
- ✅ **Dynamic filenames** - Organized by URL parameters (e.g., `day=oct18.2025.csv`)
- ✅ **Comprehensive logging** - Debug and track scraping progress
- ✅ **CSV export** - Clean, structured data output
- ✅ **Complete event details**: Date, time, currency, impact, actual/forecast/previous values, detail IDs

## 🎯 How Different Event Headers Are Handled

**The detail extractor automatically captures ALL unique specification headers across different events:**

- **Example**: If Event A has 7 spec fields and Event B has 9 spec fields, the output CSV will contain **all unique columns** (potentially 9+)
- **Single file**: All events are saved in one CSV (e.g., `day=oct18.2025_details.csv`)
- **Empty cells**: Events missing certain fields show as empty cells
- **No pre-configuration needed**: The system dynamically detects and includes all specification headers

For detailed information about header handling, see [DETAILS_EXTRACTION_INFO.md](DETAILS_EXTRACTION_INFO.md)

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

The scraper generates dynamically named files based on your URL parameters:

**Basic Scraper Output:**
- **`day=oct18.2025.csv`** - Basic economic events data (filename = URL params)
- **`week=oct21.2025.csv`** - Week's events (if using week parameter)
- **`scraper.log`** - Main scraper execution logs

**Detail Extractor Output:**
- **`day=oct18.2025_details.csv`** - Detailed event specifications with ALL unique headers
- **`detail_extractor.log`** - Detail extraction logs

### Basic Events CSV
```csv
date,time,currency,impact,event,actual,forecast,previous,detail
Sat Oct 18,12:15am,USD,Low Impact,FOMC Member Musalem Speaks,,,,,148482
Sat Oct 18,12:30am,GBP,Low Impact,MPC Member Breeden Speaks,,,,,148483
Sat Oct 18,Tentative,USD,Low Impact,Federal Budget Balance,,,,,141671
```

### Detailed Specifications CSV (All Unique Headers Captured)

**New Long Format**: Each row represents one field of one event, making it easy to see exactly which specifications each event has.

```csv
event_id,field_name,field_value
1,detail_id,148482
1,event_date,Sat Oct 18
1,event_time,12:15am
1,event_currency,USD
1,event_name,FOMC Member Musalem Speaks
1,description,"Due to participate in a moderated discussion..."
1,source,Federal Reserve Bank of St. Louis
1,speaker,Federal Reserve Bank of St. Louis President Alberto Musalem
1,usual_effect,More hawkish than expected is good for currency
1,ff_notes,FOMC voting member 2025
1,why_traderscare,Federal Reserve FOMC members vote on where to set...
1,acro_expand,Federal Open Market Committee (FOMC)
2,detail_id,148483
2,event_date,Sat Oct 18
2,event_time,12:30am
2,event_currency,GBP
2,event_name,MPC Member Breeden Speaks
2,description,"Different event with its own specifications..."
```

**Benefits of Long Format**:
- ✅ Each event has its own individual headers (field_name column)
- ✅ Easy to see which fields each event has
- ✅ No empty cells for missing fields
- ✅ Perfect for events with different specifications
- ✅ Simple to query specific events or fields

### Query Tool

Use the included query tool to easily access event details:

```bash
# List all events
python3 query_details.py

# Show all fields for event 1
python3 query_details.py --event 1

# Show 'description' field for all events
python3 query_details.py --field description

# Show specific field for specific event
python3 query_details.py --event 2 --field speaker

# List all unique fields
python3 query_details.py --list-fields
```

**Note**: The details CSV uses **long format** where each row represents one field of one event. This ensures each event has its own individual headers, making it perfect for events with different specifications. Events with different numbers of specification fields are all included without any empty cells.

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
- **Detail Extractor**: 
  - Extracts comprehensive event specifications
  - **Fresh browser session per event** - prevents caching issues
  - Conservative delays (3s between events, 5s every 5 events)
  - Ensures each event gets unique, correct data
  - Safe for extracting large numbers of events without rate limiting
- **Default Target**: October 2, 2025 (configurable via command line)
- **Performance**: ~11-13 seconds per event for detail extraction

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