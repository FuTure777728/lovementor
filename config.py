"""
应用配置
"""
import os
from dotenv import load_dotenv

load_dotenv(override=False)

DEEPSEEK_API_KEY = "sk-00fa4d9dbc7b4b1d8648526d97fba78e"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

SECRET_KEY = os.getenv("SECRET_KEY", "lovementor-secret-key-change-me")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))

SENTIMENT_TEMPERATURE = 0.3
RESPONSE_TEMPERATURE = 0.8
MAX_HISTORY = 100
