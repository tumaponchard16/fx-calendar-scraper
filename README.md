# ForexFactory Calendar Scraper

A Python web scraper that extracts economic events data from ForexFactory's economic calendar using Playwright automation.

## ⚠️ Educational Purpose Only

**IMPORTANT**: This project is for educational purposes only. Use responsibly and respect website terms of service.

## 🚀 Quick Start

### Python Environment

Create and activate a virtual environment before installing dependencies or running the scraper:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you already have the virtual environment, activate it with:

```bash
source .venv/bin/activate
```

### Output Layout

Generated files are stored under `outputs/` and grouped by date:

```text
outputs/
├── oct-18-2025/
│   ├── day=oct18.2025.csv
│   └── day=oct18.2025_details.csv
└── logs/
  ├── scraper.log
  └── detail_extractor.log
```

### Run Tests

Run the standard unit test suite with:

```bash
python3 -m unittest discover -s tests
```

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
Generates: `outputs/oct-18-2025/day=oct18.2025.csv` with basic event data

### Step 2: Extract Detailed Specifications  
```bash
python3 detail_extractor.py --date-param "day=oct18.2025"
```
Generates: `outputs/oct-18-2025/day=oct18.2025_details.csv` with comprehensive specifications for all events

## 🧭 Generation Order

For a specific date such as `day=oct22.2025`, the sequence is:

1. Run `scraper.py` first. This creates the base CSV that contains the event rows and `detail` IDs.
2. After that, `detail_extractor.py`, `history_extractor.py`, and `news_extractor.py` can be run in any order.
3. `history_news_extractor.py` is an alternative to running `history_extractor.py` and `news_extractor.py` separately.

Required first step:

```bash
python3 scraper.py --url-params "day=oct22.2025"
```

Then any of these follow-up commands are valid:

```bash
python3 detail_extractor.py --date-param "day=oct22.2025"
python3 history_extractor.py --date-param "day=oct22.2025"
python3 news_extractor.py --date-param "day=oct22.2025"
```

Or run the combined history/news extractor:

```bash
python3 history_news_extractor.py --date-param "day=oct22.2025"
```

### Recommended Sequences

To generate **all four files**:

```bash
python3 scraper.py --url-params "day=oct22.2025"
python3 detail_extractor.py --date-param "day=oct22.2025"
python3 history_news_extractor.py --date-param "day=oct22.2025"
```

To generate **all four files with separate history/news commands**:

```bash
python3 scraper.py --url-params "day=oct22.2025"
python3 detail_extractor.py --date-param "day=oct22.2025"
python3 history_extractor.py --date-param "day=oct22.2025"
python3 news_extractor.py --date-param "day=oct22.2025"
```

To generate **only history and news**:

```bash
python3 scraper.py --url-params "day=oct22.2025"
python3 history_news_extractor.py --date-param "day=oct22.2025"
```

## 📚 Documentation

- [docs/README.md](docs/README.md) - Documentation index
- [docs/extractors/history-news-quick-start.md](docs/extractors/history-news-quick-start.md) - Combined history/news quick start
- [docs/extractors/history-news-extractor.md](docs/extractors/history-news-extractor.md) - Combined history/news extractor reference
- [docs/extractors/extractors-quick-ref.md](docs/extractors/extractors-quick-ref.md) - Separate history/news extractor quick reference
- [docs/extractors/separated-extractors.md](docs/extractors/separated-extractors.md) - Separate extractor workflow details

Sample CSVs used for manual checks live under `samples/`.

## 📊 Features

- ✅ **Playwright automation** - Fast and reliable browser automation
- ✅ **Flexible date targeting** - Command line arguments for any date or week
- ✅ **Event detail IDs** - Capture unique detail IDs for each event
- ✅ **Dynamic header capture** - Automatically extracts ALL unique specification fields
- ✅ **Detailed specifications extraction** - Extract complete event specifications
- ✅ **Single file output** - All events with all unique headers in one CSV
- ✅ **Organized outputs** - Generated files are grouped in `outputs/<date>/`
- ✅ **Comprehensive logging** - Debug and track scraping progress
- ✅ **CSV export** - Clean, structured data output
- ✅ **Complete event details**: Date, time, currency, impact, actual/forecast/previous values, detail IDs

## 🎯 How Different Event Headers Are Handled

**The detail extractor preserves event-specific fields without requiring a fixed schema:**

- **Example**: If Event A has 7 spec fields and Event B has 9 spec fields, both events are still stored in the same details file.
- **Long format**: Each event is written as its own block of `field_name` and `field_value` rows instead of forcing every event into one wide row.
- **No empty cells**: Missing fields are simply absent from that event's block.
- **Single file**: All events are saved in one CSV (for example, `outputs/oct-18-2025/day=oct18.2025_details.csv`).
- **No pre-configuration needed**: The extractor reads whatever specification fields are present for that event.

For additional extractor guides, see [docs/README.md](docs/README.md).

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

# Default: use the dated CSV inside outputs/
python3 detail_extractor.py --date-param "day=oct6.2025"

# Custom CSV file
python3 detail_extractor.py --csv-file my_events.csv

# Custom date parameter
python3 detail_extractor.py --date-param "day=oct2.2025"

# Both custom
python3 detail_extractor.py --csv-file events.csv --date-param "day=nov15.2025"
```

### Configuration

### Headless Mode

Enable headless mode by changing `headless=True` in `extractor_common.py`:

```python
headless=True  # Set to True for headless mode
```

## 📄 Output

The scraper generates dated output folders under `outputs/` based on your URL parameters:

### What Each Generated File Means

- **`day=oct22.2025.csv`**: the master event list from the calendar scraper. This file must exist before the other extractors can run.
- **`day=oct22.2025_details.csv`**: event specifications such as description, source, speaker, and other metadata from `detail_extractor.py`.
- **`day=oct22.2025_history.csv`**: historical releases, dates, actual values, forecasts, previous values, and date URLs from `history_extractor.py` or `history_news_extractor.py`.
- **`day=oct22.2025_news.csv`**: related article links and snippets from `news_extractor.py` or `history_news_extractor.py`.

The `details`, `history`, and `news` files all depend on the base `day=...csv` file from `scraper.py`, but they do **not** depend on each other.

**Basic Scraper Output:**
- **`outputs/oct-18-2025/day=oct18.2025.csv`** - Basic economic events data
- **`outputs/oct-21-2025/week=oct21.2025.csv`** - Week's events (if using week parameter)
- **`outputs/logs/scraper.log`** - Main scraper execution logs

**Detail Extractor Output:**
- **`outputs/oct-18-2025/day=oct18.2025_details.csv`** - Detailed event specifications with all unique headers
- **`outputs/logs/detail_extractor.log`** - Detail extraction logs

**Optional History and News Output:**
- **`outputs/oct-18-2025/day=oct18.2025_history.csv`** - Historical event values
- **`outputs/oct-18-2025/day=oct18.2025_news.csv`** - Related news links and snippets
- **`outputs/logs/history_extractor.log`**, **`outputs/logs/news_extractor.log`** - Extractor logs

### Basic Events CSV
```csv
date,time,currency,impact,event,actual,forecast,previous,detail
Sat Oct 18,12:15am,USD,Low Impact,FOMC Member Musalem Speaks,,,,,148482
Sat Oct 18,12:30am,GBP,Low Impact,MPC Member Breeden Speaks,,,,,148483
Sat Oct 18,Tentative,USD,Low Impact,Federal Budget Balance,,,,,141671
```

### Detailed Specifications CSV (All Unique Headers Captured)

**Long / vertical block format**: Each row represents one field of one event, making it easy to see exactly which specifications each event has.

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

# Query a specific details file from outputs/
python3 query_details.py --file outputs/oct-18-2025/day=oct18.2025_details.csv
```

**Note**: The details CSV uses **long format** where each row represents one field of one event. `query_details.py` searches `outputs/*/*_details.csv` by default and still accepts a custom `--file` path.

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

## ✅ Testing

- Unit tests cover shared path/output helpers and the details CSV query parser.
- Run them with `python3 -m unittest discover -s tests` or `python3 -m unittest discover -s tests -v` for verbose output.
- Browser scraping changes should still be validated by running the affected script for a concrete date param and checking the generated files under `outputs/`.

## 🚨 Troubleshooting

1. **Browser installation issues**:
   ```bash
   python3 -m playwright install chromium
   ```

2. **Missing CSV file error**: Run the main scraper first to generate `outputs/<date>/<date_param>.csv`
3. **Permission errors**: Ensure proper file permissions
4. **Debug info**: Check files in `outputs/logs/` for detailed error information

## � License

Educational use only. Users are responsible for complying with website terms of service and using the software ethically.

---

**Remember**: Always scrape responsibly. This tool is for educational purposes only.