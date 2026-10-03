import os
from dotenv import load_dotenv

# Load environment variables from .env file (if running locally)
load_dotenv()

class Config:
    LEETCODE_USERNAME = os.getenv('LEETCODE_USERNAME')
    LEETCODE_PASSWORD = os.getenv('LEETCODE_PASSWORD')
    AI_API_KEY = os.getenv('AI_API_KEY')
    
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    AUTO_SUBMIT = os.getenv('AUTO_SUBMIT', 'false').lower() == 'true'
    HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'

config = Config()
