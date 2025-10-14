#!/usr/bin/env python3
"""
Query tool for long format event details CSV

Usage examples:
  python3 query_details.py --event 1                    # Show all fields for event 1
  python3 query_details.py --field description          # Show description for all events
  python3 query_details.py --event 2 --field speaker    # Show speaker for event 2
"""

import csv
import argparse
import sys
from collections import defaultdict

def load_details(filename):
    """Load the vertical block format CSV into a structured format"""
    events = defaultdict(dict)
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            current_event_id = None
            
            for row in reader:
                if len(row) < 2:
                    continue
                
                field_name = row[0].strip()
                field_value = row[1].strip()
                
                # Check for separator or event_id
                if field_name == '---':
                    continue  # Skip separator lines
                elif field_name == 'event_id':
                    current_event_id = field_value
                    events[current_event_id] = {}
                elif current_event_id:
                    events[current_event_id][field_name] = field_value
                    
    except FileNotFoundError:
        print(f"❌ File '{filename}' not found.")
        sys.exit(1)
    
    return events

def show_event(events, event_id):
    """Display all fields for a specific event"""
    if event_id not in events:
        print(f"❌ Event ID {event_id} not found.")
        return
    
    event = events[event_id]
    event_name = event.get('event_name', 'Unknown Event')
    
    print(f"\n📋 Event {event_id}: {event_name}")
    print("=" * 80)
    
    # Show basic info first
    basic_fields = ['event_date', 'event_time', 'event_currency', 'detail_id']
    for field in basic_fields:
        if field in event:
            print(f"{field:20s}: {event[field]}")
    
    print("\n📊 Specifications:")
    print("-" * 80)
    
    # Show specification fields
    for field_name, field_value in sorted(event.items()):
        if field_name not in basic_fields + ['event_name']:
            # Truncate long values
            display_value = field_value if len(field_value) <= 60 else field_value[:57] + "..."
            print(f"{field_name:20s}: {display_value}")
    
    print("=" * 80 + "\n")

def show_field_across_events(events, field_name):
    """Display a specific field for all events"""
    print(f"\n🔍 Field '{field_name}' across all events:")
    print("=" * 80)
    
    found_any = False
    for event_id in sorted(events.keys(), key=int):
        event = events[event_id]
        if field_name in event:
            found_any = True
            event_name = event.get('event_name', 'Unknown')
            value = event[field_name]
            
            # Truncate long values
            display_value = value if len(value) <= 50 else value[:47] + "..."
            print(f"Event {event_id:2s}: {event_name[:30]:30s} | {display_value}")
    
    if not found_any:
        print(f"⚠️ Field '{field_name}' not found in any event.")
    
    print("=" * 80 + "\n")

def show_specific_field(events, event_id, field_name):
    """Display a specific field for a specific event"""
    if event_id not in events:
        print(f"❌ Event ID {event_id} not found.")
        return
    
    event = events[event_id]
    event_name = event.get('event_name', 'Unknown')
    
    if field_name not in event:
        print(f"⚠️ Field '{field_name}' not found in event {event_id}.")
        print(f"Available fields: {', '.join(sorted(event.keys()))}")
        return
    
    print(f"\n📋 Event {event_id}: {event_name}")
    print(f"Field: {field_name}")
    print("=" * 80)
    print(event[field_name])
    print("=" * 80 + "\n")

def list_all_events(events):
    """List all events with their IDs and names"""
    print(f"\n📊 All Events ({len(events)} total):")
    print("=" * 80)
    
    for event_id in sorted(events.keys(), key=int):
        event = events[event_id]
        event_name = event.get('event_name', 'Unknown')
        event_date = event.get('event_date', 'N/A')
        event_time = event.get('event_time', 'N/A')
        field_count = len(event)
        
        print(f"Event {event_id:2s}: {event_name[:40]:40s} | {event_date:12s} {event_time:10s} | {field_count} fields")
    
    print("=" * 80 + "\n")

def list_all_fields(events):
    """List all unique fields across all events"""
    all_fields = set()
    for event in events.values():
        all_fields.update(event.keys())
    
    print(f"\n🔍 All Unique Fields ({len(all_fields)} total):")
    print("=" * 80)
    
    for field in sorted(all_fields):
        # Count how many events have this field
        count = sum(1 for event in events.values() if field in event)
        print(f"{field:25s} (present in {count}/{len(events)} events)")
    
    print("=" * 80 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Query tool for long format event details CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 query_details.py                                      # List all events
  python3 query_details.py --list-fields                        # List all unique fields
  python3 query_details.py --event 1                            # Show all fields for event 1
  python3 query_details.py --field description                  # Show description for all events
  python3 query_details.py --event 2 --field speaker            # Show speaker for event 2
  python3 query_details.py --file day=oct18.2025_details.csv    # Use specific CSV file
        """
    )
    
    parser.add_argument('--file', type=str, help='CSV file to query (default: most recent *_details.csv)')
    parser.add_argument('--event', type=str, help='Event ID to query')
    parser.add_argument('--field', type=str, help='Field name to query')
    parser.add_argument('--list-fields', action='store_true', help='List all unique fields')
    
    args = parser.parse_args()
    
    # Find the CSV file
    if args.file:
        filename = args.file
    else:
        import glob
        import os
        details_files = glob.glob("*_details.csv")
        if not details_files:
            print("❌ No details CSV files found. Please specify with --file or run detail extractor first.")
            sys.exit(1)
        filename = max(details_files, key=os.path.getmtime)
        print(f"🔍 Using most recent file: {filename}\n")
    
    # Load the data
    events = load_details(filename)
    
    if not events:
        print("❌ No events found in the CSV file.")
        sys.exit(1)
    
    # Execute the query
    if args.list_fields:
        list_all_fields(events)
    elif args.event and args.field:
        show_specific_field(events, args.event, args.field)
    elif args.event:
        show_event(events, args.event)
    elif args.field:
        show_field_across_events(events, args.field)
    else:
        list_all_events(events)
