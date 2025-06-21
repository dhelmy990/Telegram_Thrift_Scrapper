#!/usr/bin/env python3
"""
Test script to verify the setup and dependencies
"""

def test_imports():
    """Test if all required packages can be imported"""
    try:
        import prefect
        print(f"✓ Prefect imported successfully (version: {prefect.__version__})")
    except ImportError as e:
        print(f"✗ Failed to import prefect: {e}")
        return False
    
    try:
        import telethon
        print(f"✓ Telethon imported successfully (version: {telethon.__version__})")
    except ImportError as e:
        print(f"✗ Failed to import telethon: {e}")
        return False
    
    try:
        import pandas
        print(f"✓ Pandas imported successfully (version: {pandas.__version__})")
    except ImportError as e:
        print(f"✗ Failed to import pandas: {e}")
        return False
    
    try:
        import nltk
        print(f"✓ NLTK imported successfully (version: {nltk.__version__})")
    except ImportError as e:
        print(f"✗ Failed to import nltk: {e}")
        return False
    
    try:
        import textblob
        print(f"✓ TextBlob imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import textblob: {e}")
        return False
    
    return True

def test_config():
    """Test if configuration can be loaded"""
    try:
        from config.secrets import t_api, t_hash
        print(f"✓ Configuration loaded successfully")
        print(f"  API ID: {t_api}")
        print(f"  API Hash: {'*' * len(t_hash)}")  # Don't print the actual hash
        return True
    except ImportError as e:
        print(f"✗ Failed to load configuration: {e}")
        return False

def test_pipeline_import():
    """Test if the pipeline can be imported"""
    try:
        from telegram_pipeline import telegram_bidding_clothing_pipeline
        print("✓ Pipeline imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import pipeline: {e}")
        return False

def main():
    print("Testing Telegram Bidding Clothing Pipeline Setup")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test imports
    print("\n1. Testing package imports:")
    if not test_imports():
        all_tests_passed = False
    
    # Test configuration
    print("\n2. Testing configuration:")
    if not test_config():
        all_tests_passed = False
    
    # Test pipeline import
    print("\n3. Testing pipeline import:")
    if not test_pipeline_import():
        all_tests_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("✓ All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Update your channel list in example_usage.py")
        print("2. Run: python example_usage.py")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Check your config/secrets.py file")
        print("3. Verify your Telegram API credentials")

if __name__ == "__main__":
    main() 