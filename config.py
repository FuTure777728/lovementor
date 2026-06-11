"""
应用配置
"""
import os
from dotenv import load_dotenv

# 只在本地开发时加载 .env 文件，生产环境（Railway）用系统环境变量
load_dotenv(override=False)

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_API_KEY") or "your-api-key-here"
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
