# ForexFactory Calendar Scraper

A Python web scraper that extracts economic events data from ForexFactory's economic calendar for educational purposes.

## ⚠️ Educational Purpose Only

**IMPORTANT DISCLAIMER**: This project is created for educational purposes only. It is designed to demonstrate web scraping techniques, data extraction, and automation concepts. 

- **Not for commercial use**
- **Respect website terms of service**
- **Use responsibly and ethically**
- **Do not overload servers with excessive requests**

## 📋 Features

- ✅ **Automated Chrome WebDriver setup** with fallback options
- ✅ **Date-categorized events** - Each event includes its occurrence date
- ✅ **Comprehensive logging** - Track scraping progress and debug issues
- ✅ **Robust error handling** - Multiple Chrome/ChromeDriver setup methods
- ✅ **CSV export** - Clean, structured data output
- ✅ **Event details extraction**:
  - Date and time
  - Currency affected
  - Event impact level
  - Event description
  - Actual, forecast, and previous values

## 🚀 Installation

### Prerequisites

- Python 3.7+
- Google Chrome browser
- Internet connection

### Setup

1. **Clone or download the project**:
   ```bash
   git clone <repository-url>
   cd forexcalendar-scraper
   ```

2. **Create a virtual environment (recommended)**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install selenium webdriver-manager
   ```

4. **Install Google Chrome** (if not already installed):
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install google-chrome-stable
   
   # Or install Chromium
   sudo apt install chromium-browser
   ```

## 📖 Usage

### Basic Usage

Run the scraper with default settings:

```bash
python scraper.py
```

### Output

The scraper generates two files:

1. **`forexfactory_calendar.csv`** - Main data output
2. **`scraper.log`** - Detailed execution logs

### Sample CSV Output

```csv
date,time,currency,impact,event,actual,forecast,previous
Mon Oct 7,4:30pm,GBP,Low Impact Expected,M4 Money Supply m/m,0.4%,0.2%,0.1%
Mon Oct 7,5:00pm,EUR,Low Impact Expected,German Buba President Nagel Speaks,,,
Tue Oct 8,7:01am,GBP,Low Impact Expected,BRC Shop Price Index y/y,1.4%,1.2%,0.9%
Wed Oct 9,1:30am,USD,Low Impact Expected,FOMC Member Goolsbee Speaks,,,
```

## ⚙️ Configuration

### Customizing the Date Range

The scraper can be configured to target specific weeks by modifying the URL in `scraper.py`:

```python
# Current week
url = "https://www.forexfactory.com/calendar"

# Specific week (example)
url = "https://www.forexfactory.com/calendar?week=oct8.2025"
```

### Headless Mode

To run Chrome in headless mode (no GUI), uncomment this line in `setup_webdriver()`:

```python
options.add_argument("--headless=new")
```

### Logging Level

Adjust logging verbosity in `scrape_forexfactory_calendar()`:

```python
logging.basicConfig(level=logging.DEBUG)  # More detailed logs
logging.basicConfig(level=logging.WARNING)  # Less verbose
```

## 🔧 Technical Details

### Architecture

The scraper uses several key components:

1. **Chrome WebDriver Management**: Automatic setup with multiple fallback options
2. **Date Detection**: Identifies date headers using CSS class analysis
3. **Event Extraction**: Parses economic event details from table rows
4. **Error Handling**: Robust exception handling for missing elements
5. **Data Cleaning**: Removes extra whitespace and formats dates consistently

### Dependencies

- **Selenium**: Web automation and browser control
- **webdriver-manager**: Automatic ChromeDriver management
- **Chrome/Chromium**: Web browser for automation

### Compatibility

- **OS**: Linux, macOS, Windows
- **Python**: 3.7+
- **Browsers**: Google Chrome, Chromium

## 📊 Data Fields

Each scraped event contains the following fields:

| Field | Description | Example |
|-------|-------------|---------|
| `date` | Event occurrence date | "Mon Oct 7" |
| `time` | Event time | "4:30pm" |
| `currency` | Affected currency | "USD", "EUR", "GBP" |
| `impact` | Expected market impact | "High Impact Expected" |
| `event` | Event description | "Non-Farm Payrolls" |
| `actual` | Actual released value | "150K" |
| `forecast` | Forecasted value | "145K" |
| `previous` | Previous period value | "140K" |

## 🚨 Troubleshooting

### Common Issues

1. **Chrome not found**:
   ```bash
   sudo apt install google-chrome-stable
   ```

2. **ChromeDriver issues**:
   - The scraper automatically handles ChromeDriver setup
   - If issues persist, install webdriver-manager: `pip install webdriver-manager`

3. **Permission errors**:
   ```bash
   chmod +x scraper.py
   ```

4. **Import errors**:
   ```bash
   pip install -r requirements.txt
   ```

### Debug Mode

For detailed troubleshooting, check the `scraper.log` file which contains:
- Chrome browser detection
- WebDriver initialization steps
- Date detection progress
- Event processing details
- Error messages and stack traces

## 📄 License & Legal

### Educational Use Only

This software is provided for educational purposes only. Users are responsible for:

- Complying with ForexFactory's terms of service
- Respecting rate limits and not overloading servers
- Using the data ethically and responsibly
- Not using for commercial purposes without proper authorization

### Disclaimer

The authors are not responsible for:
- Any misuse of this software
- Violations of website terms of service
- Any damages or legal issues arising from use
- Data accuracy or completeness

## 🤝 Contributing

This is an educational project. If you'd like to contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📚 Learning Resources

This project demonstrates several important concepts:

- **Web Scraping**: Using Selenium for dynamic content
- **Data Extraction**: Parsing HTML structures and extracting meaningful data
- **Error Handling**: Implementing robust fallback mechanisms
- **Logging**: Creating comprehensive logs for debugging
- **Data Processing**: Cleaning and structuring scraped data
- **Automation**: Setting up automated browser interactions

## 📞 Support

For educational questions or issues:

1. Check the `scraper.log` file for detailed error information
2. Review the troubleshooting section above
3. Ensure all dependencies are properly installed
4. Verify Chrome browser is accessible

---

**Remember**: Always scrape responsibly and respect website terms of service. This tool is for learning purposes only.