# History and News Extractor Documentation

## Overview
The `history-news` workflow extracts historical data and related news for ForexFactory calendar events. This complements the details workflow by capturing time-series data and related articles.

## Features

### 📊 Historical Data Extraction
Extracts past releases of each economic indicator with:
- **Date**: Release date of historical data
- **Date URL**: Link to that specific calendar day
- **Actual**: The actual value released
- **Forecast**: The forecasted value before release
- **Previous**: The previous period's value

### 📰 Related News Extraction
Extracts news and related content with:
- **Title**: News article or link title
- **URL**: Full URL to the news/article
- **Snippet**: Brief excerpt or context (when available)
- **Link Type**: Classification (`news`, `related`, etc.)

## HTML Structure

The extractor targets the right panel of the event detail overlay:

```html
<div class="overlay__content">
    <div class="half details">
        <!-- Left panel: specs and full detail url -->
    </div>
    <div class="half last details">
        <!-- Right panel: history table and related news -->
        <table><!-- History data --></table>
        <div class="ff_taglist"><!-- Related news --></div>
    </div>
</div>
```

## Installation

Use the standard project install:

```bash
pip install -e .
python3 -m playwright install chromium
```

## Usage

### Basic Usage
```bash
# Use the default date parameter
python3 -m forexcalendar_scraper history-news

# Specify a custom date parameter
python3 -m forexcalendar_scraper history-news --date-param day=oct22.2025
```

Installed-package equivalent:

```bash
forexcalendar-history-news-extract --date-param day=oct22.2025
```

### Command-line Arguments

| Argument | Description | Default | Example |
|----------|-------------|---------|---------|
| `--csv-file` | Input CSV with events and detail IDs | `outputs/<date-folder>/{date_param}.csv` | `outputs/oct-22-2025/day=oct22.2025.csv` |
| `--date-param` | Date parameter for URL construction | `day=oct6.2025` | `day=oct22.2025` |

## Generation Order

Run the `scrape` workflow first. That creates the base `day=...csv` file that this extractor reads.

```bash
python3 -m forexcalendar_scraper scrape --date-param day=oct22.2025
python3 -m forexcalendar_scraper history-news --date-param day=oct22.2025
```

The `history-news` workflow does **not** require `day=oct22.2025_details.csv`. The details file is optional and only needed if you also want the event specification output from the `details` workflow.

If you want all four files for a date, a recommended sequence is:

```bash
python3 -m forexcalendar_scraper scrape --date-param day=oct22.2025
python3 -m forexcalendar_scraper details --date-param day=oct22.2025
python3 -m forexcalendar_scraper history-news --date-param day=oct22.2025
```

## Output Files

### History CSV: `outputs/<date-folder>/{date_param}_history.csv`

**Columns:**
- `detail_id` - Event detail ID
- `event_name` - Name of the economic event
- `event_date` - Scheduled event date
- `event_currency` - Currency affected
- `date` - Historical release date
- `date_url` - URL to that calendar day
- `actual` - Actual value released
- `forecast` - Forecasted value
- `previous` - Previous period value

**Example:**
```csv
detail_id,event_name,event_date,event_currency,date,date_url,actual,forecast,previous
144521,Trade Balance,Wed Oct 22,JPY,"Sep 17, 2025",https://www.forexfactory.com/calendar?day=sep17.2025#detail=144520,-0.15T,-0.37T,-0.29T
144521,Trade Balance,Wed Oct 22,JPY,"Aug 20, 2025",https://www.forexfactory.com/calendar?day=aug20.2025#detail=144519,-0.30T,-0.07T,-0.25T
```

### News CSV: `outputs/<date-folder>/{date_param}_news.csv`

**Columns:**
- `detail_id` - Event detail ID
- `event_name` - Name of the economic event
- `event_date` - Scheduled event date
- `event_currency` - Currency affected
- `title` - News article title
- `url` - Full URL to the article
- `snippet` - Brief excerpt (when available)
- `link_type` - Type of link (`news`, `related`, etc.)

**Example:**
```csv
detail_id,event_name,event_date,event_currency,title,url,snippet,link_type
144726,API Weekly Statistical Bulletin,Wed Oct 22,USD,News,https://www.forexfactory.com/news,,news
```

### What The Files Mean Together

- `day=oct22.2025.csv`: master event list from the `scrape` workflow.
- `day=oct22.2025_details.csv`: optional event specification file from the `details` workflow.
- `day=oct22.2025_history.csv`: historical release values from the `history-news` workflow.
- `day=oct22.2025_news.csv`: related news links from the `history-news` workflow.

## Technical Details

### Browser Configuration
- **Headless mode**: Enabled for performance
- **Fresh session per event**: Prevents caching issues
- **Conservative delays**: 3s between events, 5s every 5 events

### Extraction Logic

#### History Data
1. Locates the history table in the right panel (`.half.last.details table`)
2. Extracts header row to identify columns
3. Processes each data row:
   - Column 0: Date (with potential link)
   - Column 1: Actual value
   - Column 2: Forecast value
   - Column 3: Previous value
4. Captures date URLs for direct navigation to historical calendar days

#### Related News
1. Searches for news container (`.ff_taglist` or similar)
2. Extracts all links from the right panel
3. Filters out short date links (history navigation)
4. Captures:
   - Link title
   - Full URL (converts relative to absolute)
   - Parent element context as snippet
   - Link classification based on URL pattern

### Selectors Used

**History Table:**
- `.half.last.details table`
- `.overlay__content .half.last table`
- `[class*='history'] table`
- `.calendar__history table`

**News Container:**
- `.half.last.details .ff_taglist`
- `.overlay__content .half.last .ff_taglist`
- `[class*='news']`
- `.calendar__news`

## Testing Results

### Test Date: October 22, 2025
- **Events Tested**: 2 events
- **Success Rate**: 100% (2/2)
- **History Records Extracted**: 6 records
- **News Items Extracted**: 2 items

**Sample Output:**
```
✅ Extracted 6 history records and saved to outputs/oct-22-2025/day=oct22.2025_history.csv
✅ Extracted 2 news items and saved to outputs/oct-22-2025/day=oct22.2025_news.csv
```

## Workflow Integration

### Complete Data Collection Pipeline

1. **Main Calendar Scraper** (`scrape`)
   ```bash
   python3 -m forexcalendar_scraper scrape --date-param day=oct22.2025
   ```
   Output: `outputs/oct-22-2025/day=oct22.2025.csv` (basic event data with detail IDs)

2. **Detail Specifications** (`details`)
   ```bash
   python3 -m forexcalendar_scraper details --date-param day=oct22.2025
   ```
   Output: `outputs/oct-22-2025/day=oct22.2025_details.csv` (specs, descriptions, full detail URLs)

3. **History and News** (`history-news`)
   ```bash
   python3 -m forexcalendar_scraper history-news --date-param day=oct22.2025
   ```
   Output: 
   - `outputs/oct-22-2025/day=oct22.2025_history.csv` (historical values)
   - `outputs/oct-22-2025/day=oct22.2025_news.csv` (related news)

### File Relationships

```
outputs/
└── oct-22-2025/
   ├── day=oct22.2025.csv (master)
   ├── day=oct22.2025_details.csv (linked by detail_id)
   ├── day=oct22.2025_history.csv (linked by detail_id)
   └── day=oct22.2025_news.csv (linked by detail_id)
```

All files can be joined using the `detail_id` field.

## Use Cases

### Historical Analysis
- Track how actual values compare to forecasts over time
- Analyze forecast accuracy
- Study value trends and volatility

### News Correlation
- Find related articles for each economic indicator
- Research context around specific releases
- Build automated news aggregation

### Data Science Applications
- Time series analysis of economic indicators
- Forecast model training and validation
- Sentiment analysis of related news

## Error Handling

### Graceful Degradation
- Events without history tables: Skipped, logged
- Events without news: Logged, no error
- Missing columns: Uses positional extraction as fallback

### Logging
- **Debug level**: Detailed extraction progress
- **Info level**: Major milestones and counts
- **Error level**: Critical failures only
- **Log file**: `outputs/logs/history_news_extractor.log`

## Known Limitations

1. **History Table Variations**: Some events have different table structures
2. **News Detection**: Generic news links may need manual review
3. **Date Formats**: Various date formats may require parsing
4. **Limited News Metadata**: Snippets not always available

## Future Enhancements

Potential improvements:
- Add date parsing for standardized formats
- Expand news metadata extraction (author, publish date, category)
- Create consolidated database with all data sources
- Add historical trend visualization
- Implement incremental updates (only fetch new history)
- Add news content scraping (full article text)

## Support for Related News Fields

### Recommended News Fields to Extract:
Based on typical ForexFactory structure, the extractor captures:

✅ **Currently Extracted:**
- Title
- URL
- Link type (news/related)
- Basic snippet (when available)

💡 **Can be Added (if needed):**
- News source/publisher
- Publication date
- Article category/tags
- Thumbnail image URL
- Author information

Let me know if you need additional fields extracted from news items!

---

**Last Updated**: October 13, 2025  
**Status**: ✅ Implemented and Tested  
**Version**: 1.0
