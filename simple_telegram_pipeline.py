#!/usr/bin/env python3
"""
Simplified Telegram Bidding Clothing Pipeline

This version works without Prefect and can be used immediately.
You can enhance it later with Prefect for better orchestration.
"""

import asyncio
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from datetime import datetime, timedelta
import json
import os
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging
import pandas as pd
from config.secrets import t_api, t_hash

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MessageData:
    """Data class to store message information"""
    id: int
    date: datetime
    text: str
    channel: str
    media_type: Optional[str] = None
    file_path: Optional[str] = None

def initialize_client() -> TelegramClient:
    """Initialize and return Telegram client"""
    logger.info("Initializing Telegram client...")
    client = TelegramClient('anon_session', t_api, t_hash)
    return client

async def get_messages_from_channel(
    client: TelegramClient, 
    channel: str, 
    start_date: datetime,
    end_date: Optional[datetime] = None
) -> List[MessageData]:
    """Get all messages from a channel within the specified date range"""
    if end_date is None:
        end_date = datetime.now()
    
    messages_data = []
    
    try:
        # Get messages from the channel - now properly awaited
        messages = await client.get_messages(channel, limit=None)
        
        for msg in messages:
            if msg.date >= start_date and msg.date <= end_date:
                media_type = None
                if msg.media:
                    if isinstance(msg.media, MessageMediaPhoto):
                        media_type = "photo"
                    elif isinstance(msg.media, MessageMediaDocument):
                        media_type = "document"
                
                message_data = MessageData(
                    id=msg.id,
                    date=msg.date,
                    text=msg.text or "",
                    channel=channel,
                    media_type=media_type
                )
                messages_data.append(message_data)
        
        logger.info(f"Retrieved {len(messages_data)} messages from {channel}")
        
    except Exception as e:
        logger.error(f"Error getting messages from {channel}: {str(e)}")
    
    return messages_data

async def download_media_files(
    client: TelegramClient,
    messages: List[MessageData],
    save_dir: str = "media"
) -> List[MessageData]:
    """Download media files for messages that have media"""
    logger.info(f"Downloading media files to {save_dir}...")
    
    os.makedirs(save_dir, exist_ok=True)
    
    for msg_data in messages:
        if msg_data.media_type:
            try:
                # Get the actual message object to download media - now properly awaited
                messages_from_channel = await client.get_messages(msg_data.channel, ids=msg_data.id)
                if messages_from_channel:
                    msg = messages_from_channel[0]
                    if msg.media:
                        file_path = await client.download_media(msg.media, file=save_dir)
                        msg_data.file_path = file_path
                        logger.info(f"Downloaded media: {file_path}")
            except Exception as e:
                logger.error(f"Error downloading media for message {msg_data.id}: {str(e)}")
    
    return messages

def is_bidding_message(text: str) -> bool:
    """
    Detect if a message contains bidding-related content.
    TODO: You can enhance this function with your own logic.
    """
    if not text:
        return False
    
    # Convert to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Keywords that indicate bidding
    bidding_keywords = [
        'bid', 'bidding', 'auction', 'offer', 'price', 'cost',
        'starting bid', 'current bid', 'highest bid', 'minimum bid',
        'sold for', 'winning bid', 'place bid', 'make offer',
        'negotiable', 'best offer', 'final price', 'buy now'
    ]
    
    # Check for bidding patterns
    bidding_patterns = [
        r'\$\d+',  # Dollar amounts
        r'\d+\s*(?:dollars?|bucks?|usd)',  # Amount with currency
        r'starting\s+at\s+\$?\d+',  # Starting prices
        r'current\s+bid\s*:\s*\$?\d+',  # Current bid indicators
        r'minimum\s+bid\s*:\s*\$?\d+',  # Minimum bid indicators
    ]
    
    # Check for bidding keywords
    for keyword in bidding_keywords:
        if keyword in text_lower:
            return True
    
    # Check for bidding patterns
    for pattern in bidding_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False

def is_clothing_related(text: str) -> bool:
    """
    Detect if a message is related to clothing.
    TODO: You can enhance this function with your own logic.
    """
    if not text:
        return False
    
    # Convert to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Clothing-related keywords
    clothing_keywords = [
        # General clothing
        'shirt', 'pants', 'jeans', 'dress', 'skirt', 'jacket', 'coat',
        'sweater', 'hoodie', 'sweatshirt', 't-shirt', 'tshirt', 'blouse',
        'tank top', 'tanktop', 'shorts', 'leggings', 'jumpsuit',
        
        # Footwear
        'shoes', 'sneakers', 'boots', 'sandals', 'heels', 'flats',
        'loafers', 'oxfords', 'trainers', 'athletic shoes',
        
        # Accessories
        'hat', 'cap', 'beanie', 'scarf', 'belt', 'bag', 'purse',
        'wallet', 'jewelry', 'necklace', 'bracelet', 'earrings',
        'watch', 'sunglasses', 'glasses',
        
        # Materials and brands (common in clothing sales)
        'cotton', 'denim', 'leather', 'suede', 'wool', 'silk',
        'polyester', 'nike', 'adidas', 'puma', 'under armour',
        'levi', 'calvin klein', 'tommy hilfiger', 'ralph lauren',
        
        # Clothing-related terms
        'fashion', 'style', 'outfit', 'ensemble', 'garment',
        'apparel', 'clothing', 'wear', 'attire', 'dress code',
        'size', 'xs', 's', 'm', 'l', 'xl', 'xxl', 'small', 'medium', 'large'
    ]
    
    # Check for clothing keywords
    for keyword in clothing_keywords:
        if keyword in text_lower:
            return True
    
    # Check for size patterns
    size_patterns = [
        r'\b(?:xs|s|m|l|xl|xxl|xxxl)\b',  # Size abbreviations
        r'\b(?:small|medium|large|extra\s+small|extra\s+large)\b',  # Size words
        r'size\s*[:\-]?\s*\d+',  # Size with numbers
    ]
    
    for pattern in size_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False

def extract_price_info(text: str) -> Dict:
    """
    Extract price information from text.
    Returns a dictionary with extracted prices and bidding info.
    """
    text_lower = text.lower()
    
    # Price patterns
    price_patterns = [
        r'\$(\d+(?:\.\d{2})?)',  # $50, $50.00
        r'(\d+(?:\.\d{2})?)\s*(?:dollars?|bucks?|usd)',  # 50 dollars, 50 bucks
        r'starting\s+(?:bid|price|at)\s*\$?(\d+(?:\.\d{2})?)',  # starting bid $50
        r'current\s+bid\s*:\s*\$?(\d+(?:\.\d{2})?)',  # current bid: $50
        r'minimum\s+bid\s*:\s*\$?(\d+(?:\.\d{2})?)',  # minimum bid: $50
        r'sold\s+for\s*\$?(\d+(?:\.\d{2})?)',  # sold for $50
        r'winning\s+bid\s*:\s*\$?(\d+(?:\.\d{2})?)',  # winning bid: $50
    ]
    
    prices = []
    for pattern in price_patterns:
        matches = re.findall(pattern, text_lower)
        prices.extend([float(price) for price in matches])
    
    # Determine price type
    price_type = "unknown"
    if any(word in text_lower for word in ['starting bid', 'starting price', 'minimum bid']):
        price_type = "starting_price"
    elif any(word in text_lower for word in ['current bid', 'highest bid']):
        price_type = "current_bid"
    elif any(word in text_lower for word in ['sold for', 'winning bid', 'final price']):
        price_type = "final_price"
    elif any(word in text_lower for word in ['buy now', 'price']):
        price_type = "asking_price"
    
    return {
        "prices": prices,
        "min_price": min(prices) if prices else None,
        "max_price": max(prices) if prices else None,
        "price_type": price_type,
        "has_multiple_prices": len(prices) > 1
    }

def filter_messages(messages: List[MessageData]) -> List[MessageData]:
    """Filter messages to only include bidding and clothing-related ones"""
    logger.info("Filtering messages for bidding and clothing content...")
    
    filtered_messages = []
    
    for msg in messages:
        is_bidding = is_bidding_message(msg.text)
        is_clothing = is_clothing_related(msg.text)
        
        if is_bidding and is_clothing:
            filtered_messages.append(msg)
            logger.info(f"Found bidding clothing message: {msg.text[:100]}...")
    
    logger.info(f"Filtered {len(filtered_messages)} bidding clothing messages from {len(messages)} total messages")
    return filtered_messages

def save_results_csv(messages: List[MessageData], output_file: str = "clothing_bidding_dataset.csv"):
    """Save filtered messages to CSV format suitable for CNN training"""
    logger.info(f"Saving results to {output_file}...")
    
    # Convert messages to structured data for CNN training
    dataset_rows = []
    
    for msg in messages:
        price_info = extract_price_info(msg.text)
        
        row = {
            'message_id': msg.id,
            'date': msg.date.isoformat(),
            'text': msg.text,
            'channel': msg.channel,
            'media_type': msg.media_type,
            'media_path': msg.file_path,
            
            # Price information
            'min_price': price_info['min_price'],
            'max_price': price_info['max_price'],
            'price_type': price_info['price_type'],
            'has_multiple_prices': price_info['has_multiple_prices'],
            'all_prices': str(price_info['prices']),
            
            # Text features for NLP
            'text_length': len(msg.text),
            'has_media': msg.media_type is not None,
            
            # Labels (you can enhance these)
            'is_bidding': is_bidding_message(msg.text),
            'is_clothing': is_clothing_related(msg.text),
        }
        
        dataset_rows.append(row)
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(dataset_rows)
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    logger.info(f"Saved {len(messages)} records to {output_file}")
    return df

def save_results_json(messages: List[MessageData], output_file: str = "filtered_messages.json"):
    """Save filtered messages to JSON format (backup)"""
    logger.info(f"Saving backup results to {output_file}...")
    
    # Convert messages to dictionary format for JSON serialization
    messages_dict = []
    for msg in messages:
        msg_dict = {
            'id': msg.id,
            'date': msg.date.isoformat(),
            'text': msg.text,
            'channel': msg.channel,
            'media_type': msg.media_type,
            'file_path': msg.file_path
        }
        messages_dict.append(msg_dict)
    
    # Save to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(messages_dict, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved {len(messages)} filtered messages to {output_file}")

def create_summary_report(messages: List[MessageData]) -> Dict:
    """Create a summary report of the filtered messages"""
    if not messages:
        return {"total_messages": 0, "channels": [], "date_range": None, "channel_counts": {}, "media_counts": {}}
    
    # Get unique channels
    channels = list(set(msg.channel for msg in messages))
    
    # Get date range
    dates = [msg.date for msg in messages]
    min_date = min(dates)
    max_date = max(dates)
    
    # Count by channel
    channel_counts = {}
    for msg in messages:
        channel_counts[msg.channel] = channel_counts.get(msg.channel, 0) + 1
    
    # Count media types
    media_counts = {}
    for msg in messages:
        if msg.media_type:
            media_counts[msg.media_type] = media_counts.get(msg.media_type, 0) + 1
    
    summary = {
        "total_messages": len(messages),
        "channels": channels,
        "channel_counts": channel_counts,
        "date_range": {
            "start": min_date.isoformat(),
            "end": max_date.isoformat()
        },
        "media_counts": media_counts
    }
    
    logger.info(f"Summary: {len(messages)} messages from {len(channels)} channels")
    return summary

async def telegram_bidding_clothing_pipeline(
    channels: List[str],
    start_date: str,
    end_date: Optional[str] = None,
    save_media: bool = True,
    output_csv: str = "clothing_bidding_dataset.csv",
    output_json: str = "filtered_messages.json"
):
    """
    Main pipeline for scraping Telegram messages and filtering for bidding clothing items.
    
    Args:
        channels: List of channel usernames to scrape
        start_date: Start date in ISO format (e.g., "2024-01-01")
        end_date: End date in ISO format (e.g., "2024-12-31"), defaults to now
        save_media: Whether to download media files
        output_csv: Output CSV file name for CNN training
        output_json: Backup JSON file name
    """
    logger.info(f"Starting pipeline for {len(channels)} channels from {start_date}")
    
    # Parse dates
    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date) if end_date else datetime.now()
    
    # Initialize client
    client = initialize_client()
    
    all_messages = []
    
    try:
        # Start the client - now properly awaited
        await client.start()
        
        # Get messages from each channel
        for channel in channels:
            logger.info(f"Processing channel: {channel}")
            channel_messages = await get_messages_from_channel(client, channel, start_dt, end_dt)
            all_messages.extend(channel_messages)
        
        # Download media if requested
        if save_media:
            all_messages = await download_media_files(client, all_messages)
        
        # Filter messages
        filtered_messages = filter_messages(all_messages)
        
        # Save results in both formats
        df = None
        if filtered_messages:
            df = save_results_csv(filtered_messages, output_csv)
            save_results_json(filtered_messages, output_json)
        else:
            logger.warning("No filtered messages to save")
        
        # Create summary report
        summary = create_summary_report(filtered_messages)
        
        logger.info("Pipeline completed successfully!")
        return {
            "total_messages": len(all_messages),
            "filtered_messages": len(filtered_messages),
            "summary": summary,
            "dataset_shape": df.shape if df is not None else (0, 0)
        }
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise
    finally:
        # Disconnect the client - now properly awaited
        await client.disconnect()

async def main():
    """Main async function to run the pipeline"""
    # Example usage
    channels = ["edermelonzzzz"]  # Add your channel usernames here
    start_date = "2024-01-01"
    
    result = await telegram_bidding_clothing_pipeline(
        channels=channels,
        start_date=start_date,
        save_media=True
    )
    
    print("\n" + "="*50)
    print("PIPELINE RESULTS")
    print("="*50)
    print(f"Total messages processed: {result['total_messages']}")
    print(f"Filtered bidding clothing messages: {result['filtered_messages']}")
    print(f"Dataset shape: {result['dataset_shape']}")
    
    if result['summary']['total_messages'] > 0:
        print("\nSUMMARY:")
        print(f"Channels: {result['summary']['channels']}")
        print(f"Date range: {result['summary']['date_range']}")
        print(f"Channel counts: {result['summary']['channel_counts']}")
        print(f"Media counts: {result['summary']['media_counts']}")
    else:
        print("\nNo messages found matching criteria.")

if __name__ == "__main__":
    # Run the async pipeline
    asyncio.run(main()) 