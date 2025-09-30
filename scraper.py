
#!/usr/bin/env python3
"""
ForexFactory Calendar Scraper

A web scraper that extracts economic events data from ForexFactory's economic calendar.

EDUCATIONAL PURPOSE ONLY:
This script is created for educational purposes to demonstrate web scraping techniques.
Please respect website terms of service and use responsibly.

Author: Educational Project
License: Educational Use Only
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
import time
import csv
import logging
import subprocess
import sys
import re

import logging
import subprocess
import sys

def check_chrome_installation():
    """Check if Chrome/Chromium is installed and accessible"""
    chrome_commands = ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']
    
    for cmd in chrome_commands:
        try:
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return cmd, result.stdout.strip()
        except FileNotFoundError:
            continue
    
    return None, None

def setup_webdriver(logger):
    """Setup WebDriver with fallback options"""
    
    # Check Chrome installation first
    chrome_cmd, chrome_version = check_chrome_installation()
    if not chrome_cmd:
        logger.error("❌ Chrome/Chromium browser not found. Please install Chrome or Chromium:")
        logger.error("   Ubuntu/Debian: sudo apt update && sudo apt install google-chrome-stable")
        logger.error("   Or: sudo apt install chromium-browser")
        raise WebDriverException("Chrome/Chromium browser not found")
    
    logger.info(f"Found browser: {chrome_cmd} - {chrome_version}")
    
    # Setup Chrome options
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")  # Often needed on Linux
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    
    # Set binary location if using chromium
    if 'chromium' in chrome_cmd:
        options.binary_location = chrome_cmd
    
    # Uncomment to run headless
    # options.add_argument("--headless=new")
    
    try:
        # Try with automatic ChromeDriver management
        logger.info("Attempting to initialize ChromeDriver (auto-managed)...")
        driver = webdriver.Chrome(service=Service(), options=options)
        logger.info("✅ ChromeDriver initialized successfully")
        return driver
        
    except WebDriverException as e:
        logger.warning(f"Auto-managed ChromeDriver failed: {str(e)}")
        
        # Try with webdriver-manager
        try:
            logger.info("Trying webdriver-manager for automatic ChromeDriver setup...")
            from webdriver_manager.chrome import ChromeDriverManager
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            logger.info("✅ ChromeDriver initialized with webdriver-manager")
            return driver
            
        except ImportError:
            logger.warning("webdriver-manager not installed. Install with: pip install webdriver-manager")
        except Exception as e2:
            logger.warning(f"webdriver-manager failed: {str(e2)}")
        
        # Try with explicit ChromeDriver path (if available in PATH)
        try:
            logger.info("Trying explicit ChromeDriver path...")
            service = Service('chromedriver')
            driver = webdriver.Chrome(service=service, options=options)
            logger.info("✅ ChromeDriver initialized with explicit path")
            return driver
            
        except WebDriverException as e3:
            logger.error(f"❌ All ChromeDriver initialization attempts failed:")
            logger.error(f"   Error 1 (auto): {str(e)}")
            logger.error(f"   Error 2 (explicit): {str(e3)}")
            logger.error("\nTroubleshooting steps:")
            logger.error("1. Install webdriver-manager: pip install webdriver-manager")
            logger.error("2. Or manually download ChromeDriver from: https://chromedriver.chromium.org/")
            logger.error("3. Make sure Chrome and ChromeDriver versions are compatible")
            logger.error("4. Check if Chrome is properly installed")
            raise WebDriverException("Failed to initialize ChromeDriver")

def scrape_forexfactory_calendar():
    """
    Main scraping function that extracts ForexFactory calendar events.
    
    This function:
    1. Sets up logging
    2. Initializes Chrome WebDriver 
    3. Navigates to ForexFactory calendar
    4. Extracts event data with dates
    5. Saves results to CSV file
    
    Educational purpose only - use responsibly!
    """
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,  # Changed back to INFO for cleaner output
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    url = "https://www.forexfactory.com/calendar?week=oct8.2025"
    logger.info(f"Starting scraper for URL: {url}")

    logger.info("Initializing Chrome WebDriver...")
    driver = setup_webdriver(logger)

    try:
        logger.info("Navigating to ForexFactory calendar page...")
        driver.get(url)

        # Wait for the calendar table to load
        logger.info("Waiting for calendar table to load...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table.calendar__table tbody tr"))
        )
        logger.info("Calendar table loaded successfully")

        # Grab all rows from the calendar table
        rows = driver.find_elements(By.CSS_SELECTOR, "table.calendar__table tbody tr")
        logger.info(f"Found {len(rows)} rows in the calendar table")

        events = []
        processed_count = 0
        skipped_count = 0
        current_date = None
        
        for i, row in enumerate(rows):
            try:
                # Check if this row contains a date (check for day-breaker class)
                row_classes = row.get_attribute("class") or ""
                
                if "day-breaker" in row_classes or "new-day" in row_classes:
                    # This is a date header row - extract the date
                    try:
                        # Try to get date from the cell content
                        date_cell = row.find_element(By.CSS_SELECTOR, "td")
                        date_text = date_cell.text.strip()
                        
                        if not date_text:
                            # If no text, try getting inner HTML and extract date
                            cell_html = date_cell.get_attribute("innerHTML")
                            # Extract text that looks like a date
                            import re
                            date_match = re.search(r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+(\w+\s+\d+)', cell_html)
                            if date_match:
                                date_text = date_match.group(0)
                        
                        if date_text and len(date_text) > 3:
                            # Clean up the date text - remove extra whitespace and newlines
                            current_date = ' '.join(date_text.split())
                            logger.info(f"Found date section: {current_date}")
                    except Exception as e:
                        logger.debug(f"Error extracting date from row {i}: {e}")
                    continue
                
                # Try to extract event data
                time_cell = row.find_element(By.CSS_SELECTOR, ".calendar__time")
                currency_cell = row.find_element(By.CSS_SELECTOR, ".calendar__currency")
                impact_cell = row.find_element(By.CSS_SELECTOR, ".calendar__impact span")
                event_cell = row.find_element(By.CSS_SELECTOR, ".calendar__event")
                actual_cell = row.find_element(By.CSS_SELECTOR, ".calendar__actual")
                forecast_cell = row.find_element(By.CSS_SELECTOR, ".calendar__forecast")
                previous_cell = row.find_element(By.CSS_SELECTOR, ".calendar__previous")

                event_data = {
                    "date": current_date if current_date else "Unknown",
                    "time": time_cell.text.strip(),
                    "currency": currency_cell.text.strip(),
                    "impact": impact_cell.get_attribute("title"),
                    "event": event_cell.text.strip(),
                    "actual": actual_cell.text.strip(),
                    "forecast": forecast_cell.text.strip(),
                    "previous": previous_cell.text.strip(),
                }
                
                events.append(event_data)
                processed_count += 1
                
                # Log progress every 10 events
                if processed_count % 10 == 0:
                    logger.info(f"Processed {processed_count} events so far...")
                    
            except Exception as e:
                # Some rows may be headers/separators
                skipped_count += 1
                logger.debug(f"Skipped row {i+1}: {str(e)}")
                continue

        logger.info(f"Scraping completed. Processed: {processed_count} events, Skipped: {skipped_count} rows")

        # Save to CSV
        if events:
            logger.info("Saving events to CSV file...")
            with open("forexfactory_calendar.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=events[0].keys())
                writer.writeheader()
                writer.writerows(events)

            logger.info(f"✅ Successfully saved {len(events)} events to forexfactory_calendar.csv")
            print(f"✅ Scraped {len(events)} events and saved to forexfactory_calendar.csv")
        else:
            logger.warning("⚠️ No events found to save")
            print("⚠️ No events found to save")

    except Exception as e:
        logger.error(f"❌ An error occurred during scraping: {str(e)}")
        raise
    finally:
        logger.info("Closing WebDriver...")
        time.sleep(2)
        driver.quit()
        logger.info("Scraper finished")

if __name__ == "__main__":
    scrape_forexfactory_calendar()
