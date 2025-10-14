#!/usr/bin/env python3
"""
ForexFactory Event History Extractor

Extracts historical data for each event using detail IDs from the main CSV file.

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
import argparse
import sys
import os

def setup_browser(logger):
    """Setup Playwright browser with options"""
    
    logger.info("Initializing Playwright browser for history extraction...")
    
    try:
        playwright = sync_playwright().start()
        
        # Launch browser with options
        browser = playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
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

def extract_history_data(page, detail_id, logger):
    """
    Extract historical data for an event
    
    Returns:
        list: List of history records with date, url, actual, forecast, previous
    """
    history_records = []
    
    try:
        # Try multiple selectors for history table
        history_selectors = [
            ".half.last.details table",
            ".overlay__content .half.last table",
            "[class*='history'] table",
            ".calendar__history table"
        ]
        
        history_table = None
        for selector in history_selectors:
            try:
                page.wait_for_selector(selector, timeout=3000)
                tables = page.locator(selector).all()
                if tables:
                    # Usually the first table in the right panel is history
                    history_table = tables[0]
                    logger.debug(f"Found history table with selector: {selector}")
                    break
            except:
                continue
        
        if not history_table:
            logger.debug(f"No history table found for detail ID {detail_id}")
            return history_records
        
        # Extract header to identify columns
        header_row = history_table.locator("thead tr, tr:first-child").first
        headers = []
        if header_row.count() > 0:
            header_cells = header_row.locator("th, td").all()
            headers = [cell.text_content().strip().lower() for cell in header_cells]
            logger.debug(f"History table headers: {headers}")
        
        # Extract data rows
        rows = history_table.locator("tbody tr, tr").all()
        
        for row in rows:
            try:
                cells = row.locator("td").all()
                if len(cells) < 2:  # Skip header or empty rows
                    continue
                
                record = {
                    'detail_id': detail_id,
                    'date': '',
                    'date_url': '',
                    'actual': '',
                    'forecast': '',
                    'previous': ''
                }
                
                # Extract data based on position (typical order: Date, Actual, Forecast, Previous)
                for idx, cell in enumerate(cells):
                    cell_text = cell.text_content().strip()
                    
                    if idx == 0:  # Date column
                        record['date'] = cell_text
                        # Try to extract URL if date is a link
                        link = cell.locator("a").first
                        if link.count() > 0:
                            href = link.get_attribute("href")
                            if href:
                                if href.startswith("/"):
                                    record['date_url'] = f"https://www.forexfactory.com{href}"
                                else:
                                    record['date_url'] = href
                    elif idx == 1:  # Actual
                        record['actual'] = cell_text
                    elif idx == 2:  # Forecast
                        record['forecast'] = cell_text
                    elif idx == 3:  # Previous
                        record['previous'] = cell_text
                
                if record['date']:  # Only add if we have a date
                    history_records.append(record)
                    
            except Exception as row_error:
                logger.debug(f"Error processing history row: {row_error}")
                continue
        
        logger.debug(f"Extracted {len(history_records)} history records for detail ID {detail_id}")
        
    except Exception as e:
        logger.debug(f"Failed to extract history for detail ID {detail_id}: {str(e)}")
    
    return history_records

def extract_event_history(page, base_url, detail_id, logger):
    """
    Extract history for a single event
    
    Args:
        page: Playwright page object
        base_url: Base URL with date parameter
        detail_id: Event detail ID
        logger: Logger instance
        
    Returns:
        list: List of history records
    """
    try:
        if not detail_id:
            logger.debug(f"No detail ID provided, skipping")
            return None
        
        # Construct the detail URL
        detail_url = f"{base_url}#detail={detail_id}"
        logger.debug(f"Extracting history for detail ID {detail_id}")
        
        # Navigate to the detail URL
        page.goto(detail_url, wait_until="domcontentloaded")
        
        # Wait for JavaScript to process the URL fragment
        time.sleep(2)
        
        # Wait for the detail overlay to appear
        detail_selectors = [
            ".overlay__content",
            ".calendar__detail",
            f"[data-event-id='{detail_id}']"
        ]
        
        detail_found = False
        for selector in detail_selectors:
            try:
                page.wait_for_selector(selector, timeout=3000)
                detail_found = True
                logger.debug(f"Found detail overlay with selector: {selector}")
                break
            except:
                continue
        
        if not detail_found:
            logger.debug(f"Could not find detail overlay for ID {detail_id}, skipping to next event")
            return None
        
        # Wait for content to render
        time.sleep(2)
        
        # Extract history data
        history_records = extract_history_data(page, detail_id, logger)
        
        return history_records
        
    except Exception as e:
        logger.debug(f"Failed to extract history for detail ID {detail_id}: {str(e)}")
        return None

def extract_all_history(csv_file="forexfactory_calendar.csv", base_date_param="day=oct6.2025"):
    """
    Main function to extract history for all events
    
    Args:
        csv_file (str): Path to the main CSV file with events
        base_date_param (str): Date parameter for the base URL
    """
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('history_extractor.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        logger.error(f"❌ CSV file '{csv_file}' not found. Please run the main scraper first.")
        return
    
    logger.info(f"Starting history extraction from {csv_file}")
    
    # Read the main CSV file
    events = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [field.strip() if field else field for field in reader.fieldnames]
            for row in reader:
                cleaned_row = {key.strip(): value.strip() if value else value for key, value in row.items()}
                events.append(cleaned_row)
        logger.info(f"Found {len(events)} events to process")
    except Exception as e:
        logger.error(f"❌ Failed to read CSV file: {str(e)}")
        return
    
    # Process each event with fresh browser session
    base_url = f"https://www.forexfactory.com/calendar?{base_date_param}"
    all_history = []
    processed_count = 0
    failed_count = 0
    
    try:
        for i, event in enumerate(events):
            detail_id = event.get('detail', '').strip()
            
            if not detail_id:
                logger.debug(f"Event {i+1}: No detail ID, skipping")
                failed_count += 1
                continue
            
            # Create fresh browser session for each event
            logger.debug(f"Creating new browser session for event {i+1}/{len(events)}")
            playwright, browser, context, page = setup_browser(logger)
            
            try:
                # Extract history with fresh session
                history_records = extract_event_history(page, base_url, detail_id, logger)
                
                if history_records:
                    event_name = event.get('event', 'Unknown')
                    event_date = event.get('date', '')
                    event_currency = event.get('currency', '')
                    
                    # Add event context to history records
                    for history_record in history_records:
                        history_record.update({
                            'event_name': event_name,
                            'event_date': event_date,
                            'event_currency': event_currency
                        })
                        all_history.append(history_record)
                    
                    processed_count += 1
                    
                    # Log progress
                    if processed_count % 5 == 0:
                        logger.info(f"Processed {processed_count} events so far...")
                else:
                    failed_count += 1
            
            finally:
                # Always close the browser session
                try:
                    context.close()
                    browser.close()
                    playwright.stop()
                except:
                    pass
            
            # Delay between requests
            if (i + 1) % 5 == 0:
                delay = 5
                logger.info(f"Waiting {delay} seconds (batch delay)...")
                time.sleep(delay)
            else:
                delay = 3
                logger.debug(f"Waiting {delay} seconds...")
                time.sleep(delay)
        
        logger.info(f"History extraction completed. Processed: {processed_count}, Failed: {failed_count}")
        logger.info(f"Total history records: {len(all_history)}")
        
        # Save history to CSV
        if all_history:
            history_file = f"{base_date_param}_history.csv"
            logger.info(f"Saving history data to {history_file}...")
            
            with open(history_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['detail_id', 'event_name', 'event_date', 'event_currency', 
                             'date', 'date_url', 'actual', 'forecast', 'previous']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_history)
            
            logger.info(f"✅ Successfully saved {len(all_history)} history records to {history_file}")
            print(f"✅ Extracted {len(all_history)} history records and saved to {history_file}")
        else:
            logger.warning("⚠️ No history data found to save")
            print("⚠️ No history data found to save")
    
    except Exception as e:
        logger.error(f"❌ An error occurred during extraction: {str(e)}")
        raise
    finally:
        logger.info("History extractor finished")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ForexFactory Event History Extractor - Educational purposes only",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 history_extractor.py
  python3 history_extractor.py --csv-file events.csv
  python3 history_extractor.py --date-param "day=oct22.2025"
  python3 history_extractor.py --csv-file day=oct22.2025.csv --date-param "day=oct22.2025"
        """
    )
    
    parser.add_argument(
        '--csv-file',
        type=str,
        help='Path to the CSV file containing events with detail IDs',
        default="forexfactory_calendar.csv"
    )
    
    parser.add_argument(
        '--date-param',
        type=str,
        help='Date parameter for constructing detail URLs (e.g., "day=oct22.2025")',
        default="day=oct6.2025"
    )
    
    args = parser.parse_args()
    
    # Run the extractor
    extract_all_history(csv_file=args.csv_file, base_date_param=args.date_param)
