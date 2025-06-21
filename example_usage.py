#!/usr/bin/env python3
"""
Example usage of the Telegram Bidding Clothing Pipeline

This script demonstrates how to use the Prefect pipeline to scrape
Telegram messages and filter for bidding clothing items.
"""

from telegram_pipeline import telegram_bidding_clothing_pipeline
from datetime import datetime, timedelta

def main():
    # Define your channels (replace with actual channel usernames)
    channels = [
        "edermelonzzzz"  # Replace with your actual channel
        # "another_channel",
        # "third_channel"
    ]
    
    # Define date range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Run the pipeline
    result = telegram_bidding_clothing_pipeline(
        channels=channels,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        save_media=True,
        output_file="bidding_clothing_messages.json"
    )
    
    print("Pipeline Results:")
    print(f"Total messages processed: {result['total_messages']}")
    print(f"Filtered bidding clothing messages: {result['filtered_messages']}")
    print("\nSummary:")
    print(f"Channels: {result['summary']['channels']}")
    print(f"Date range: {result['summary']['date_range']}")
    print(f"Channel counts: {result['summary']['channel_counts']}")
    print(f"Media counts: {result['summary']['media_counts']}")

if __name__ == "__main__":
    main() 