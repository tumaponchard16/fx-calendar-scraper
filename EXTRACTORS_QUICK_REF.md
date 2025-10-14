# Quick Reference: History and News Extractors

## Two Separate Scripts

### 📊 History Extractor
```bash
python3 history_extractor.py --csv-file day=oct22.2025.csv --date-param "day=oct22.2025"
```
**Output:** `day=oct22.2025_history.csv`  
**Data:** date, date_url, actual, forecast, previous

### 📰 News Extractor
```bash
python3 news_extractor.py --csv-file day=oct22.2025.csv --date-param "day=oct22.2025"
```
**Output:** `day=oct22.2025_news.csv`  
**Data:** title, url, snippet, link_type

## Run Both
```bash
python3 history_extractor.py --csv-file day=oct22.2025.csv --date-param "day=oct22.2025" && \
python3 news_extractor.py --csv-file day=oct22.2025.csv --date-param "day=oct22.2025"
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

See `SEPARATED_EXTRACTORS.md` for full documentation.
