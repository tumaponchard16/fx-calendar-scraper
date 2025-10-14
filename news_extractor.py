#!/usr/bin/env python3
"""
ForexFactory Event News Extractor

Extracts related news for each event using detail IDs from the main CSV file.

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
    
    logger.info("Initializing Playwright browser for news extraction...")
    
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

def extract_related_news(page, detail_id, logger):
    """
    Extract related news for an event
    
    Returns:
        list: List of news items with title, url, snippet, link_type
    """
    news_items = []
    
    try:
        # Try multiple selectors for news section
        news_selectors = [
            ".half.last.details .ff_taglist",
            ".overlay__content .half.last .ff_taglist",
            "[class*='news']",
            ".calendar__news"
        ]
        
        news_container = None
        for selector in news_selectors:
            try:
                page.wait_for_selector(selector, timeout=3000)
                news_container = page.locator(selector).first
                if news_container.count() > 0:
                    logger.debug(f"Found news container with selector: {selector}")
                    break
            except:
                continue
        
        if not news_container:
            # Try to find any links or news items in the right panel
            try:
                right_panel = page.locator(".half.last.details").first
                if right_panel.count() > 0:
                    news_links = right_panel.locator("a").all()
                    logger.debug(f"Found {len(news_links)} links in right panel")
                    
                    for link in news_links:
                        try:
                            title = link.text_content().strip()
                            href = link.get_attribute("href")
                            
                            if title and href and len(title) > 5:  # Filter out short/empty links
                                # Skip if it's a history date link (usually short dates)
                                if len(title) < 15 and any(char.isdigit() for char in title):
                                    continue
                                
                                news_url = href
                                if href.startswith("/"):
                                    news_url = f"https://www.forexfactory.com{href}"
                                
                                # Try to extract date/metadata from parent element
                                parent = link.locator("xpath=..").first
                                parent_text = parent.text_content().strip() if parent.count() > 0 else ""
                                
                                news_items.append({
                                    'detail_id': detail_id,
                                    'title': title,
                                    'url': news_url,
                                    'snippet': parent_text[:200] if len(parent_text) > len(title) else '',
                                    'link_type': 'news' if 'news' in href or 'article' in href else 'related'
                                })
                        except Exception as link_error:
                            logger.debug(f"Error processing news link: {link_error}")
                            continue
            except:
                pass
        else:
            # Extract news from structured container
            news_links = news_container.locator("a").all()
            
            for link in news_links:
                try:
                    title = link.text_content().strip()
                    href = link.get_attribute("href")
                    
                    if title and href:
                        news_url = href
                        if href.startswith("/"):
                            news_url = f"https://www.forexfactory.com{href}"
                        
                        news_items.append({
                            'detail_id': detail_id,
                            'title': title,
                            'url': news_url,
                            'snippet': '',
                            'link_type': 'news' if 'news' in href or 'article' in href else 'related'
                        })
                except Exception as link_error:
                    logger.debug(f"Error processing news link: {link_error}")
                    continue
        
        if not news_items:
            logger.debug(f"No related news found for detail ID {detail_id}")
        else:
            logger.debug(f"Extracted {len(news_items)} news items for detail ID {detail_id}")
        
    except Exception as e:
        logger.debug(f"Failed to extract news for detail ID {detail_id}: {str(e)}")
    
    return news_items

def extract_event_news(page, base_url, detail_id, logger):
    """
    Extract news for a single event
    
    Args:
        page: Playwright page object
        base_url: Base URL with date parameter
        detail_id: Event detail ID
        logger: Logger instance
        
    Returns:
        list: List of news items
    """
    try:
        if not detail_id:
            logger.debug(f"No detail ID provided, skipping")
            return None
        
        # Construct the detail URL
        detail_url = f"{base_url}#detail={detail_id}"
        logger.debug(f"Extracting news for detail ID {detail_id}")
        
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
        
        # Extract related news
        news_items = extract_related_news(page, detail_id, logger)
        
        return news_items
        
    except Exception as e:
        logger.debug(f"Failed to extract news for detail ID {detail_id}: {str(e)}")
        return None

def extract_all_news(csv_file="forexfactory_calendar.csv", base_date_param="day=oct6.2025"):
    """
    Main function to extract news for all events
    
    Args:
        csv_file (str): Path to the main CSV file with events
        base_date_param (str): Date parameter for the base URL
    """
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('news_extractor.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        logger.error(f"❌ CSV file '{csv_file}' not found. Please run the main scraper first.")
        return
    
    logger.info(f"Starting news extraction from {csv_file}")
    
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
    all_news = []
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
                # Extract news with fresh session
                news_items = extract_event_news(page, base_url, detail_id, logger)
                
                if news_items:
                    event_name = event.get('event', 'Unknown')
                    event_date = event.get('date', '')
                    event_currency = event.get('currency', '')
                    
                    # Add event context to news items
                    for news_item in news_items:
                        news_item.update({
                            'event_name': event_name,
                            'event_date': event_date,
                            'event_currency': event_currency
                        })
                        all_news.append(news_item)
                    
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
        
        logger.info(f"News extraction completed. Processed: {processed_count}, Failed: {failed_count}")
        logger.info(f"Total news items: {len(all_news)}")
        
        # Save news to CSV
        if all_news:
            news_file = f"{base_date_param}_news.csv"
            logger.info(f"Saving news data to {news_file}...")
            
            with open(news_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['detail_id', 'event_name', 'event_date', 'event_currency',
                             'title', 'url', 'snippet', 'link_type']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_news)
            
            logger.info(f"✅ Successfully saved {len(all_news)} news items to {news_file}")
            print(f"✅ Extracted {len(all_news)} news items and saved to {news_file}")
        else:
            logger.warning("⚠️ No news data found to save")
            print("⚠️ No news data found to save")
    
    except Exception as e:
        logger.error(f"❌ An error occurred during extraction: {str(e)}")
        raise
    finally:
        logger.info("News extractor finished")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ForexFactory Event News Extractor - Educational purposes only",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 news_extractor.py
  python3 news_extractor.py --csv-file events.csv
  python3 news_extractor.py --date-param "day=oct22.2025"
  python3 news_extractor.py --csv-file day=oct22.2025.csv --date-param "day=oct22.2025"
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
    extract_all_news(csv_file=args.csv_file, base_date_param=args.date_param)
