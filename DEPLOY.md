# 🚀 部署指南 — 让其他用户访问你的情感良师

---

## 方法一：ngrok 隧道（最快 · 免费 · 适合演示）

**原理**：ngrok 在本机和你电脑之间建立加密隧道，生成一个临时公网 URL。

**优点**：30 秒搞定，无需服务器，无需配置  
**缺点**：你的电脑必须保持开机；免费版链接会变化、有访问限制

### 步骤

```bash
# 1. 安装 ngrok Python 包
pip install pyngrok

# 2. 注册 ngrok 账号（免费）: https://dashboard.ngrok.com/signup
# 3. 获取你的 authtoken: https://dashboard.ngrok.com/get-started/your-authtoken
# 4. 配置 authtoken（仅首次需要）
ngrok config add-authtoken 你的authtoken

# 5. 一键启动分享
python share.py
```

生成的链接类似 `https://xxxx.ngrok-free.app`，发给任何人即可访问。

---

## 方法二：Railway 部署（免费 · 持久 · 推荐）

**原理**：代码推送到 GitHub → Railway 自动构建并部署到云端。

**优点**：免费额度够用，链接永久不变，无需维护服务器  
**缺点**：首次配置约需 10 分钟

### 步骤

```bash
# 1. 初始化 git 仓库（如果还没有）
cd lovementor
git init
git add .
git commit -m "Initial commit"

# 2. 推送到 GitHub（新建一个仓库）
#    在 github.com 创建新仓库，然后：
git remote add origin https://github.com/你的用户名/lovementor.git
git push -u origin main

# 3. 登录 Railway: https://railway.app
#    用 GitHub 账号登录
#
# 4. 点击 "New Project" → "Deploy from GitHub repo"
#    选择 lovementor 仓库
#
# 5. 添加环境变量（Settings → Variables）:
#    DEEPSEEK_API_KEY = sk-你的apikey
#
# 6. 等待自动部署完成，Railway 会给你一个域名：
#    https://lovementor.up.railway.app
```

### 需要上传的文件已就绪

| 文件 | 用途 |
|------|------|
| `Procfile` | 告诉 Railway 如何启动服务 |
| `runtime.txt` | 指定 Python 版本 |
| `requirements.txt` | 自动安装依赖 |

---

## 方法三：Render 部署（免费 · 持久 · 备选）

与 Railway 类似，也是 GitHub 连接自动部署。

1. 登录 [render.com](https://render.com)，GitHub 登录
2. New → Web Service → 连接你的 lovementor 仓库
3. 设置：
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`
4. 添加环境变量 `DEEPSEEK_API_KEY`
5. 部署，获得 `https://lovementor.onrender.com`

> ⚠️ Render 免费版 15 分钟无访问会自动休眠，下次访问需等 30-60 秒唤醒。

---

## 方法四：国内服务器部署（腾讯云/阿里云）

如果你有国内云服务器（学生优惠通常 10 元/月）：

```bash
# 1. SSH 登录服务器
ssh root@你的服务器IP

# 2. 安装 Python 和 git
yum install python3 python3-pip git -y  # CentOS
# 或
apt install python3 python3-pip git -y  # Ubuntu

# 3. 克隆代码
git clone https://github.com/你的用户名/lovementor.git
cd lovementor

# 4. 安装依赖
pip3 install -r requirements.txt

# 5. 配置环境变量
echo 'DEEPSEEK_API_KEY=sk-你的key' > .env

# 6. 后台运行
nohup gunicorn app:app --bind 0.0.0.0:80 --workers 2 --daemon &

# 7. 防火墙开放 80 端口
# 在云控制台安全组中添加规则：入方向 TCP 80

# 现在用 http://服务器IP 即可访问
```

---

## 方案选择建议

| 你的情况 | 推荐方案 |
|---------|---------|
| 给老师同学演示一下 | **方法一 ngrok** |
| 课程展示，需要长期可访问链接 | **方法二 Railway** |
| 有 GitHub 账号，不想装东西 | **方法二 Railway** |
| 有国内服务器 | **方法四 云服务器** |

---

## 安全提醒

- `.env` 文件包含 API Key，**不要提交到 git 仓库**（已在 `.gitignore` 中排除）
- Railway/Render 上通过环境变量设置 API Key，而不是上传 `.env`
- 如果发现 API Key 泄露，立即去 [platform.deepseek.com](https://platform.deepseek.com) 重置
