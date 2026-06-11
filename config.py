"""
应用配置
"""
import os
from dotenv import load_dotenv

load_dotenv()

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your-api-key-here")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# Flask 配置
SECRET_KEY = os.getenv("SECRET_KEY", "lovementor-secret-key-change-me")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))

# 情感分析配置
SENTIMENT_TEMPERATURE = 0.3  # 分析用低温保证准确
RESPONSE_TEMPERATURE = 0.8   # 回应用稍高温更有温度
MAX_HISTORY = 100             # 最大历史记录数
