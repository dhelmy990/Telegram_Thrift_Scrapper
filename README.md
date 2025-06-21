# Telegram Bidding Clothing Pipeline

A Prefect-based pipeline for scraping Telegram messages from multiple channels and filtering for bidding messages related to clothing items.

## Features

- **Multi-channel scraping**: Process multiple Telegram channels simultaneously
- **Date range filtering**: Specify start and end dates for message collection
- **Bidding detection**: Automatically identify messages containing bidding-related content
- **Clothing classification**: Filter messages related to clothing and fashion items
- **Media download**: Download associated media files (photos, documents)
- **Structured output**: Save results in JSON format with comprehensive metadata
- **Summary reporting**: Generate detailed reports of processed messages

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your Telegram API credentials in `config/secrets.py`:
```python
t_api = YOUR_API_ID
t_hash = 'YOUR_API_HASH'
```

## Usage

### Basic Usage

```python
from telegram_pipeline import telegram_bidding_clothing_pipeline

# Define channels to scrape
channels = ["channel1", "channel2", "channel3"]

# Run the pipeline
result = telegram_bidding_clothing_pipeline(
    channels=channels,
    start_date="2024-01-01",
    end_date="2024-12-31",
    save_media=True,
    output_file="filtered_messages.json"
)
```

### Example Script

Run the example script:
```bash
python example_usage.py
```

## Pipeline Components

### 1. Message Collection (`get_messages_from_channel`)
- Retrieves all messages from specified channels within date range
- Handles rate limiting and error recovery
- Extracts message metadata (ID, date, text, media type)

### 2. Media Download (`download_media_files`)
- Downloads associated media files (photos, documents)
- Organizes files in a structured directory
- Preserves file paths for reference

### 3. Bidding Detection (`is_bidding_message`)
**Helper function that you can enhance:**
- Detects bidding-related keywords (bid, auction, offer, price, etc.)
- Identifies price patterns ($XX, XX dollars, etc.)
- Recognizes bidding-specific phrases (starting bid, current bid, etc.)

### 4. Clothing Classification (`is_clothing_related`)
**Helper function that you can enhance:**
- Identifies clothing-related keywords (shirt, pants, shoes, etc.)
- Detects size patterns (S, M, L, XL, etc.)
- Recognizes fashion brands and materials

### 5. Message Filtering (`filter_messages`)
- Combines bidding and clothing detection
- Returns only messages that match both criteria
- Provides detailed logging of filtered results

### 6. Results Export (`save_results`)
- Saves filtered messages to JSON format
- Includes all metadata and file paths
- UTF-8 encoded for international character support

## Output Format

The pipeline generates a JSON file with the following structure:

```json
[
  {
    "id": 12345,
    "date": "2024-01-15T10:30:00",
    "text": "Nike Air Max shoes, starting bid $50",
    "channel": "fashion_auctions",
    "media_type": "photo",
    "file_path": "media/photo_12345.jpg"
  }
]
```

## Customization

### Enhancing Bidding Detection

You can improve the `is_bidding_message` function by:

1. Adding more bidding keywords:
```python
bidding_keywords.extend([
    'your_custom_keyword',
    'another_bidding_term'
])
```

2. Adding custom regex patterns:
```python
bidding_patterns.append(r'your_custom_pattern')
```

### Enhancing Clothing Classification

You can improve the `is_clothing_related` function by:

1. Adding more clothing keywords:
```python
clothing_keywords.extend([
    'your_clothing_item',
    'specific_brand'
])
```

2. Adding size patterns:
```python
size_patterns.append(r'your_size_pattern')
```

## Configuration

### Environment Variables

You can set the following environment variables:
- `TELEGRAM_API_ID`: Your Telegram API ID
- `TELEGRAM_API_HASH`: Your Telegram API Hash
- `SAVE_MEDIA_DIR`: Directory for saving media files (default: "media")

### Prefect Configuration

The pipeline uses Prefect for orchestration. You can configure:
- Logging levels
- Retry policies
- Resource limits
- Monitoring and alerting

## Error Handling

The pipeline includes comprehensive error handling:
- Network connection issues
- Rate limiting
- Invalid channel names
- Media download failures
- File system errors

## Monitoring

Prefect provides built-in monitoring:
- Real-time flow execution status
- Task-level metrics
- Error tracking and alerting
- Performance analytics

## Security Considerations

- Store API credentials securely
- Use environment variables for sensitive data
- Implement rate limiting to avoid API restrictions
- Monitor API usage to stay within limits

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed
2. **Authentication errors**: Verify API credentials in `config/secrets.py`
3. **Channel access errors**: Ensure you have access to the specified channels
4. **Rate limiting**: The pipeline includes built-in delays to respect API limits

### Debug Mode

Enable debug logging by setting the log level:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

To enhance the pipeline:

1. Fork the repository
2. Create a feature branch
3. Implement your improvements
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License. 