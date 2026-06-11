"""
应用配置
"""
import os
from dotenv import load_dotenv

load_dotenv(override=False)

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_API_KEY") or "your-api-key-here"

# === 诊断：打印所有环境变量中以 DEEPSEEK 开头的 ===
import sys
print(f"[诊断] DEEPSEEK_API_KEY 值: '{DEEPSEEK_API_KEY[:15]}...' 长度:{len(DEEPSEEK_API_KEY)}", file=sys.stderr)
for k, v in sorted(os.environ.items()):
    if 'DEEP' in k.upper() or 'KEY' in k.upper() or 'API' in k.upper():
        print(f"[诊断] 环境变量: {k} = {v[:20]}...", file=sys.stderr)

DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

SECRET_KEY = os.getenv("SECRET_KEY", "lovementor-secret-key-change-me")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))

SENTIMENT_TEMPERATURE = 0.3
RESPONSE_TEMPERATURE = 0.8
MAX_HISTORY = 100
