"""
快速分享工具 — 一键生成公网链接

用法：
    python share.py          # 启动服务并尝试生成公网链接

前置条件（二选一）：
    A. 安装 ngrok: pip install pyngrok
    B. 安装 Cloudflare Tunnel: https://developers.cloudflare.com/cloudflare-one/

公网链接生成后，把链接发给任何人即可访问你的情感良师！
"""
import sys
import subprocess
import time

HAS_NGROK = False
try:
    from pyngrok import ngrok
    HAS_NGROK = True
except ImportError:
    pass


def start_share():
    print("""
╔══════════════════════════════════════════════╗
║     🚀 情感良师 · 一键分享工具              ║
╚══════════════════════════════════════════════╝
    """)

    # 检查 API Key
    from config import DEEPSEEK_API_KEY
    if DEEPSEEK_API_KEY == "your-api-key-here":
        print("⚠️  警告: 未配置 DeepSeek API Key")
        print("   编辑 .env 文件，填入你的 API Key 以获得完整体验")
        print()

    if HAS_NGROK:
        share_via_ngrok()
    else:
        print("未安装 pyngrok，仅启动本地服务。")
        print()
        print("📌 快速分享方案：")
        print("   方法1: pip install pyngrok && python share.py")
        print("   方法2: 参考 DEPLOY.md 部署到云端")
        print()
        print("启动本地服务 (仅本机访问)...")
        start_local_only()


def share_via_ngrok():
    """通过 ngrok 生成公网链接"""
    print("[*] 正在启动 ngrok 隧道...")

    # 启动 ngrok 隧道
    public_url = ngrok.connect(5000, "http")
    print(f"""
✅ 公网链接已生成！把这个链接发给任何人即可访问：

    👉 {public_url}

📌 按 Ctrl+C 停止服务

注意事项:
  - 链接在程序关闭后失效（免费版）
  - 你的电脑需要保持开机和联网
  - 如需长期稳定链接，请参考 DEPLOY.md
    """)

    # 启动 Flask
    try:
        from app import app
        app.run(host="0.0.0.0", port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n[*] 正在关闭...")
        ngrok.disconnect(public_url)
        ngrok.kill()


def start_local_only():
    """仅启动本地服务"""
    try:
        from app import app
        app.run(host="0.0.0.0", port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n[*] 服务已停止")


if __name__ == "__main__":
    start_share()
