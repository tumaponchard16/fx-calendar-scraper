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
        
        # Navigate to the detail URL - don't wait for networkidle as fragment changes don't trigger network requests
        page.goto(detail_url, wait_until="domcontentloaded")
        
        # Wait for JavaScript to process the URL fragment and load the detail
        time.sleep(2)
        
        # Wait for the detail overlay/modal to appear
        # Try multiple possible selectors for the detail container
        detail_selectors = [
            f"[data-event-id='{detail_id}']",
            ".calendar__detail",
            ".calendar-detail",
            "#detail",
            "[id*='detail']"
        ]
        
        detail_found = False
        for selector in detail_selectors:
            try:
                page.wait_for_selector(selector, timeout=3000)
                detail_found = True
                logger.debug(f"Found detail container with selector: {selector}")
                break
            except:
                continue
        
        if not detail_found:
            logger.debug(f"Could not find detail container for ID {detail_id}, waiting extra time...")
        
        # Wait for the page to fully render the detail content
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
        
        # Extract the full details URL from calendardetails__solo div
        try:
            solo_div = page.locator(".calendardetails__solo").first
            if solo_div.count() > 0:
                # Try to find the anchor tag within the solo div
                link = solo_div.locator("a").first
                if link.count() > 0:
                    full_details_url = link.get_attribute("href")
                    if full_details_url:
                        # If it's a relative URL, make it absolute
                        if full_details_url.startswith("/"):
                            full_details_url = f"https://www.forexfactory.com{full_details_url}"
                        specs_data["full_details_url"] = full_details_url
                        logger.debug(f"Extracted full details URL: {full_details_url}")
                    
                    # Also extract the link text if available
                    link_text = (link.text_content() or "").strip()
                    if link_text:
                        specs_data["full_details_link_text"] = link_text
        except Exception as url_error:
            logger.debug(f"Could not extract full details URL: {url_error}")
        
        field_names = [k for k in specs_data.keys() if k != 'detail_id']
        logger.debug(f"Successfully extracted {len(field_names)} spec fields for detail ID {detail_id}: {field_names}")
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
    
    # Process each event with a fresh browser session
    base_url = f"https://www.forexfactory.com/calendar?{base_date_param}"
    all_specs = []
    processed_count = 0
    failed_count = 0
    
    try:
        for i, event in enumerate(events):
            detail_id = event.get('detail', '').strip()
            
            if not detail_id:
                logger.debug(f"Event {i+1}: No detail ID, skipping")
                failed_count += 1
                continue
            
            # Create a fresh browser session for each event to avoid caching issues
            logger.debug(f"Creating new browser session for event {i+1}/{len(events)}")
            playwright, browser, context, page = setup_browser(logger)
            
            try:
                # Extract specs for this event with fresh session
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
            
            finally:
                # Always close the browser session
                try:
                    context.close()
                    browser.close()
                    playwright.stop()
                except:
                    pass
            
            # Delay between requests to prevent rate limiting
            # Longer delay every 5 events to be extra respectful
            if (i + 1) % 5 == 0:
                delay = 5  # 5 seconds every 5 events
                logger.info(f"Waiting {delay} seconds (batch delay to prevent rate limiting)...")
                time.sleep(delay)
            else:
                delay = 3  # 3 seconds between events
                logger.debug(f"Waiting {delay} seconds...")
                time.sleep(delay)
        
        
        logger.info(f"Detail extraction completed. Processed: {processed_count}, Failed: {failed_count}")
        
        # Save detailed specs to CSV with filename based on date parameter
        if all_specs:
            output_file = f"{base_date_param}_details.csv"
            logger.info(f"Saving detailed specifications to {output_file} (vertical block format)...")
            
            # Create vertical block format: each event as a self-contained block
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write each event as a block
                for event_num, spec in enumerate(all_specs, start=1):
                    # Event header
                    writer.writerow(['event_id', event_num])
                    
                    # Write all fields for this event
                    for field_name, field_value in spec.items():
                        writer.writerow([field_name, field_value])
                    
                    # Separator line between events (except after last event)
                    if event_num < len(all_specs):
                        writer.writerow(['---', '---'])
            
            logger.info(f"✅ Successfully saved {len(all_specs)} events (vertical block format) to {output_file}")
            print(f"✅ Extracted {len(all_specs)} event details and saved to {output_file}")
        else:
            logger.warning("⚠️ No event details found to save")
            print("⚠️ No event details found to save")
    
    except Exception as e:
        logger.error(f"❌ An error occurred during detail extraction: {str(e)}")
        raise
    finally:
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