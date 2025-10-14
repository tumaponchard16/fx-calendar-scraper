
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

from playwright.sync_api import sync_playwright
import time
import csv
import logging
import subprocess
import sys
import re
import argparse

import logging
import subprocess
import sys

def setup_browser(logger):
    """Setup Playwright browser with options"""
    
    logger.info("Initializing Playwright browser...")
    
    try:
        playwright = sync_playwright().start()
        
        # Launch browser with options
        browser = playwright.chromium.launch(
            headless=True,  # Set to True for headless mode
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--disable-infobars",
                "--disable-extensions",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        
        # Create a new context (like an incognito window)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Create a new page
        page = context.new_page()
        
        logger.info("✅ Playwright browser initialized successfully")
        return playwright, browser, context, page
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Playwright browser: {str(e)}")
        logger.error("Make sure you have installed the browser with: python3 -m playwright install chromium")
        raise Exception(f"Failed to initialize Playwright browser: {str(e)}")

def scrape_forexfactory_calendar(url_params=None):
    """
    Main scraping function that extracts ForexFactory calendar events.
    
    Args:
        url_params (str): URL parameters to append to the base URL (e.g., "day=oct6.2025")
    
    This function:
    1. Sets up logging
    2. Initializes Playwright browser 
    3. Navigates to ForexFactory calendar
    4. Extracts event data with dates
    5. Saves results to CSV file
    
    Educational purpose only - use responsibly!
    """
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG,  # Changed to DEBUG to see what's being skipped
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    # Build URL with custom parameters or default
    base_url = "https://www.forexfactory.com/calendar"
    if url_params:
        url = f"{base_url}?{url_params}"
        filename = f"{url_params}.csv"
    else:
        url_params = "day=oct2.2025"  # Default to October 2, 2025
        url = f"{base_url}?{url_params}"
        filename = f"{url_params}.csv"
    
    logger.info(f"Starting scraper for URL: {url}")
    logger.info(f"Output will be saved to: {filename}")

    logger.info("Initializing Playwright browser...")
    playwright, browser, context, page = setup_browser(logger)

    try:
        logger.info("Navigating to ForexFactory calendar page...")
        page.goto(url)

        # Wait for the calendar table to load
        logger.info("Waiting for calendar table to load...")
        page.wait_for_selector("table.calendar__table tbody", timeout=15000)
        logger.info("Calendar table loaded successfully")

        # Grab all rows from the calendar table
        rows = page.locator("table.calendar__table tbody tr").all()
        logger.info(f"Found {len(rows)} rows in the calendar table")

        events = []
        processed_count = 0
        skipped_count = 0
        current_date = None
        
        for i, row in enumerate(rows):
            try:
                # Check if this row contains a date (check for day-breaker class)
                row_classes = row.get_attribute("class") or ""
                
                if "day-breaker" in row_classes:
                    # This is a date header row - extract the date
                    try:
                        # Try to get date from the cell content
                        date_cell = row.locator("td").first
                        date_text = date_cell.text_content() or ""
                        
                        if not date_text:
                            # If no text, try getting inner HTML and extract date
                            cell_html = date_cell.inner_html()
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
                try:
                    # Get the event detail ID from the row's data-event-id attribute
                    detail_id = row.get_attribute("data-event-id") or ""
                    
                    time_cell = row.locator(".calendar__time")
                    currency_cell = row.locator(".calendar__currency")
                    impact_cell = row.locator(".calendar__impact span")
                    event_cell = row.locator(".calendar__event")
                    actual_cell = row.locator(".calendar__actual")
                    forecast_cell = row.locator(".calendar__forecast")
                    previous_cell = row.locator(".calendar__previous")

                    event_data = {
                        "date": current_date if current_date else "Unknown",
                        "time": (time_cell.text_content() or "").strip(),
                        "currency": (currency_cell.text_content() or "").strip(),
                        "impact": (impact_cell.get_attribute("title") or "").strip(),
                        "event": (event_cell.text_content() or "").strip(),
                        "actual": (actual_cell.text_content() or "").strip(),
                        "forecast": (forecast_cell.text_content() or "").strip(),
                        "previous": (previous_cell.text_content() or "").strip(),
                        "detail": detail_id,
                    }
                    
                    events.append(event_data)
                    processed_count += 1
                    
                    # Log progress every 10 events
                    if processed_count % 10 == 0:
                        logger.info(f"Processed {processed_count} events so far...")
                        
                except Exception as event_error:
                    # Try alternative approach for rows that might have different structure
                    try:
                        # Check if this row has any event-related content
                        all_cells = row.locator("td").all()
                        if len(all_cells) >= 7:  # Should have at least 7 columns for a valid event
                            # Extract data using more flexible approach
                            time_text = ""
                            currency_text = ""
                            impact_text = ""
                            event_text = ""
                            actual_text = ""
                            forecast_text = ""
                            previous_text = ""
                            
                            # Try to find time cell
                            time_elements = row.locator(".calendar__time")
                            if time_elements.count() > 0:
                                time_text = (time_elements.first.text_content() or "").strip()
                            
                            # Try to find currency cell
                            currency_elements = row.locator(".calendar__currency")
                            if currency_elements.count() > 0:
                                currency_text = (currency_elements.first.text_content() or "").strip()
                            
                            # Try to find impact cell
                            impact_elements = row.locator(".calendar__impact span")
                            if impact_elements.count() > 0:
                                impact_text = (impact_elements.first.get_attribute("title") or impact_elements.first.text_content() or "").strip()
                            
                            # Try to find event cell
                            event_elements = row.locator(".calendar__event")
                            if event_elements.count() > 0:
                                event_text = (event_elements.first.text_content() or "").strip()
                            
                            # Try to find actual cell
                            actual_elements = row.locator(".calendar__actual")
                            if actual_elements.count() > 0:
                                actual_text = (actual_elements.first.text_content() or "").strip()
                            
                            # Try to find forecast cell
                            forecast_elements = row.locator(".calendar__forecast")
                            if forecast_elements.count() > 0:
                                forecast_text = (forecast_elements.first.text_content() or "").strip()
                            
                            # Try to find previous cell
                            previous_elements = row.locator(".calendar__previous")
                            if previous_elements.count() > 0:
                                previous_text = (previous_elements.first.text_content() or "").strip()
                            
                            # Only add if we found at least an event name or currency
                            if event_text or currency_text:
                                # Get the event detail ID from the row's data-event-id attribute
                                detail_id = row.get_attribute("data-event-id") or ""
                                
                                event_data = {
                                    "date": current_date if current_date else "Unknown",
                                    "time": time_text,
                                    "currency": currency_text,
                                    "impact": impact_text,
                                    "event": event_text,
                                    "actual": actual_text,
                                    "forecast": forecast_text,
                                    "previous": previous_text,
                                    "detail": detail_id,
                                }
                                
                                events.append(event_data)
                                processed_count += 1
                                logger.debug(f"Recovered event from row {i+1}: {event_text}")
                                
                                # Log progress every 10 events
                                if processed_count % 10 == 0:
                                    logger.info(f"Processed {processed_count} events so far...")
                            else:
                                skipped_count += 1
                                logger.debug(f"Skipped row {i+1}: No event content found")
                        else:
                            skipped_count += 1
                            logger.debug(f"Skipped row {i+1}: Insufficient columns ({len(all_cells)})")
                    except Exception as fallback_error:
                        skipped_count += 1
                        logger.debug(f"Skipped row {i+1}: {str(event_error)} | Fallback failed: {str(fallback_error)}")
                    
            except Exception as e:
                # Some rows may be headers/separators or completely unrelated content
                skipped_count += 1
                logger.debug(f"Skipped row {i+1} entirely: {str(e)}")
                continue

        logger.info(f"Scraping completed. Processed: {processed_count} events, Skipped: {skipped_count} rows")

        # Save to CSV
        if events:
            logger.info("Saving events to CSV file...")
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=events[0].keys())
                writer.writeheader()
                writer.writerows(events)

            logger.info(f"✅ Successfully saved {len(events)} events to {filename}")
            print(f"✅ Scraped {len(events)} events and saved to {filename}")
        else:
            logger.warning("⚠️ No events found to save")
            print("⚠️ No events found to save")

    except Exception as e:
        logger.error(f"❌ An error occurred during scraping: {str(e)}")
        raise
    finally:
        logger.info("Closing browser...")
        time.sleep(2)
        context.close()
        browser.close()
        playwright.stop()
        logger.info("Scraper finished")

if __name__ == "__main__":
    # Set up command line argument parser
    parser = argparse.ArgumentParser(
        description="ForexFactory Calendar Scraper - Educational purposes only",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scraper.py                           # Default: October 2, 2025
  python3 scraper.py --url-params "day=oct6.2025"     # October 6, 2025
  python3 scraper.py --url-params "week=oct2.2025"    # Entire week of October 2, 2025
  python3 scraper.py --url-params "day=nov15.2025"    # November 15, 2025
        """
    )
    
    parser.add_argument(
        '--url-params',
        type=str,
        help='URL parameters for ForexFactory calendar (e.g., "day=oct6.2025", "week=oct2.2025")',
        default=None
    )
    
    args = parser.parse_args()
    
    # Run the scraper with provided parameters
    scrape_forexfactory_calendar(url_params=args.url_params)
