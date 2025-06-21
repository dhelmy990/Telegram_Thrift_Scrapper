from prefect import flow, task, get_run_logger
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from datetime import datetime, timedelta
import json
import os
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from textblob import TextBlob
import nltk
from config.secrets import t_api, t_hash

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

@dataclass
class MessageData:
    """Data class to store message information"""
    id: int
    date: datetime
    text: str
    channel: str
    media_type: Optional[str] = None
    file_path: Optional[str] = None

@task(name="Initialize Telegram Client")
def initialize_client() -> TelegramClient:
    """Initialize and return Telegram client"""
    logger = get_run_logger()
    client = TelegramClient('anon_session', t_api, t_hash)
    logger.info("Telegram client initialized")
    return client

# ... rest of the code remains unchanged ... 