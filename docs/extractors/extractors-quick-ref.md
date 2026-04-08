# Quick Reference: History and News Extractors

## Two Separate Commands

### 📊 History Extractor
```bash
python3 -m forexcalendar_scraper history --date-param day=oct22.2025
```
**Output:** `outputs/oct-22-2025/day=oct22.2025_history.csv`  
**Data:** date, date_url, actual, forecast, previous

### 📰 News Extractor
```bash
python3 -m forexcalendar_scraper news --date-param day=oct22.2025
```
**Output:** `outputs/oct-22-2025/day=oct22.2025_news.csv`  
**Data:** title, url, snippet, link_type

## Run Both
```bash
python3 -m forexcalendar_scraper history --date-param day=oct22.2025
python3 -m forexcalendar_scraper news --date-param day=oct22.2025
```

Installed-package equivalents:

```bash
forexcalendar-history-extract --date-param day=oct22.2025
forexcalendar-news-extract --date-param day=oct22.2025
```

## Why Separate?

✅ **Faster** - Run only what you need  
✅ **Clearer** - Separate logs for debugging  
✅ **Flexible** - Independent updates  
✅ **Efficient** - Skip news if not needed  

## When to Use

**History Only:** Most common for data analysis  
**News Only:** When building news aggregation  
**Both:** Complete data collection  

---

Logs are written to `outputs/logs/`.

See [separated-extractors.md](separated-extractors.md) for full documentation.
