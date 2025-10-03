#!/usr/bin/env python3
"""
ForexFactory Event Detail Extractor

Extracts detailed specifications for each event using the detail IDs from the main CSV file.

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
    
    logger.info("Initializing Playwright browser for detail extraction...")
    
    try:
        playwright = sync_playwright().start()
        
        # Launch browser with options
        browser = playwright.chromium.launch(
            headless=True,  # Use headless mode for detail extraction
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

def extract_event_specs(page, base_url, detail_id, logger):
    """
    Extract specifications for a single event
    
    Args:
        page: Playwright page object
        base_url: Base URL with date parameter
        detail_id: Event detail ID
        logger: Logger instance
        
    Returns:
        dict: Event specifications or None if failed
    """
    try:
        if not detail_id:
            logger.debug(f"No detail ID provided, skipping")
            return None
            
        # Construct the detail URL
        detail_url = f"{base_url}#detail={detail_id}"
        logger.debug(f"Extracting specs for detail ID {detail_id}")
        
        # Navigate to the detail URL
        page.goto(detail_url)
        
        # Wait a bit for the page to load and for any JavaScript to execute
        time.sleep(2)
        
        # Try multiple selectors for the specs table
        specs_selectors = [
            "table.calendarspecs",
            ".calendarspecs",
            "table.calendar-specs",
            ".calendar-specs",
            "[class*='specs']",
            ".calendar__detail table",
            ".calendar-detail table"
        ]
        
        specs_table = None
        for selector in specs_selectors:
            try:
                page.wait_for_selector(selector, timeout=5000)
                specs_table = page.locator(selector)
                if specs_table.count() > 0:
                    logger.debug(f"Found specs table with selector: {selector}")
                    break
            except:
                continue
        
        if not specs_table or specs_table.count() == 0:
            # Try to find any table in the detail section
            try:
                page.wait_for_selector("table", timeout=5000)
                all_tables = page.locator("table").all()
                logger.debug(f"Found {len(all_tables)} tables on page for detail ID {detail_id}")
                
                # Try the first table that has content
                for i, table in enumerate(all_tables):
                    rows = table.locator("tr").all()
                    if len(rows) > 1:  # Has header and at least one data row
                        specs_table = table
                        logger.debug(f"Using table {i+1} with {len(rows)} rows")
                        break
            except:
                pass
        
        if not specs_table or specs_table.count() == 0:
            logger.debug(f"No specs table found for detail ID {detail_id}")
            return None
        
        # Extract all rows from the specs table
        rows = specs_table.locator("tr").all()
        
        specs_data = {
            "detail_id": detail_id,
        }
        
        for row in rows:
            try:
                cells = row.locator("td").all()
                if len(cells) >= 2:
                    # Get the label (first cell) and value (second cell)
                    label = (cells[0].text_content() or "").strip()
                    value = (cells[1].text_content() or "").strip()
                    
                    if label and value:
                        # Clean up the label to make it a valid CSV column name
                        clean_label = label.lower().replace(" ", "_").replace(":", "").replace("/", "_").replace("(", "").replace(")", "")
                        specs_data[clean_label] = value
                        
            except Exception as row_error:
                logger.debug(f"Error processing row in specs table: {row_error}")
                continue
        
        logger.debug(f"Successfully extracted {len(specs_data)-1} spec fields for detail ID {detail_id}")
        return specs_data if len(specs_data) > 1 else None
        
    except Exception as e:
        logger.debug(f"Failed to extract specs for detail ID {detail_id}: {str(e)}")
        return None

def extract_event_details(csv_file="forexfactory_calendar.csv", base_date_param="day=oct6.2025"):
    """
    Main function to extract detailed specifications for all events
    
    Args:
        csv_file (str): Path to the main CSV file with events
        base_date_param (str): Date parameter for the base URL
    """
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG,  # Changed to DEBUG to see more details
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('detail_extractor.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        logger.error(f"❌ CSV file '{csv_file}' not found. Please run the main scraper first.")
        return
    
    logger.info(f"Starting detail extraction from {csv_file}")
    
    # Read the main CSV file
    events = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Clean up the fieldnames to remove extra spaces
            reader.fieldnames = [field.strip() if field else field for field in reader.fieldnames]
            for row in reader:
                # Clean up the row data
                cleaned_row = {key.strip(): value.strip() if value else value for key, value in row.items()}
                events.append(cleaned_row)
        logger.info(f"Found {len(events)} events to process")
    except Exception as e:
        logger.error(f"❌ Failed to read CSV file: {str(e)}")
        return
    
    # Setup browser
    playwright, browser, context, page = setup_browser(logger)
    
    try:
        base_url = f"https://www.forexfactory.com/calendar?{base_date_param}"
        all_specs = []
        processed_count = 0
        failed_count = 0
        
        for i, event in enumerate(events):
            detail_id = event.get('detail', '').strip()
            
            if not detail_id:
                logger.debug(f"Event {i+1}: No detail ID, skipping")
                failed_count += 1
                continue
            
            # Extract specs for this event
            specs = extract_event_specs(page, base_url, detail_id, logger)
            
            if specs:
                # Add basic event info to specs
                specs.update({
                    'event_date': event.get('date', ''),
                    'event_time': event.get('time', ''),
                    'event_currency': event.get('currency', ''),
                    'event_name': event.get('event', ''),
                })
                all_specs.append(specs)
                processed_count += 1
                
                # Log progress
                if processed_count % 5 == 0:
                    logger.info(f"Processed {processed_count} event details so far...")
            else:
                failed_count += 1
            
            # Small delay between requests to be respectful
            time.sleep(1)
        
        logger.info(f"Detail extraction completed. Processed: {processed_count}, Failed: {failed_count}")
        
        # Save detailed specs to CSV
        if all_specs:
            output_file = "forexfactory_event_details.csv"
            logger.info(f"Saving detailed specifications to {output_file}...")
            
            # Get all possible fieldnames from all specs
            all_fieldnames = set()
            for spec in all_specs:
                all_fieldnames.update(spec.keys())
            
            # Sort fieldnames for consistent ordering
            fieldnames = ['detail_id', 'event_date', 'event_time', 'event_currency', 'event_name'] + \
                        sorted([f for f in all_fieldnames if f not in ['detail_id', 'event_date', 'event_time', 'event_currency', 'event_name']])
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_specs)
            
            logger.info(f"✅ Successfully saved {len(all_specs)} detailed specifications to {output_file}")
            print(f"✅ Extracted {len(all_specs)} event details and saved to {output_file}")
        else:
            logger.warning("⚠️ No event details found to save")
            print("⚠️ No event details found to save")
    
    except Exception as e:
        logger.error(f"❌ An error occurred during detail extraction: {str(e)}")
        raise
    finally:
        logger.info("Closing browser...")
        context.close()
        browser.close()
        playwright.stop()
        logger.info("Detail extractor finished")

if __name__ == "__main__":
    # Set up command line argument parser
    parser = argparse.ArgumentParser(
        description="ForexFactory Event Detail Extractor - Educational purposes only",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 detail_extractor.py                                    # Use default CSV and date
  python3 detail_extractor.py --csv-file events.csv              # Custom CSV file
  python3 detail_extractor.py --date-param "day=oct2.2025"       # Custom date parameter
  python3 detail_extractor.py --csv-file events.csv --date-param "day=nov15.2025"
        """
    )
    
    parser.add_argument(
        '--csv-file',
        type=str,
        help='Path to the CSV file containing events with detail IDs (default: forexfactory_calendar.csv)',
        default="forexfactory_calendar.csv"
    )
    
    parser.add_argument(
        '--date-param',
        type=str,
        help='Date parameter for constructing detail URLs (e.g., "day=oct6.2025")',
        default="day=oct6.2025"
    )
    
    args = parser.parse_args()
    
    # Run the detail extractor
    extract_event_details(csv_file=args.csv_file, base_date_param=args.date_param)