# 💌 情感良师 LoveMentor — NLP 情感分析系统

基于深度学习的爱情与两性关系情感分析 Web 应用。系统以"白开水"为良师益友身份，为用户提供温暖、有洞察力的情感分析回应，并集成星座分析等趣味功能。

## 功能概览

| 模块 | 功能 | 说明 |
|------|------|------|
| 💬 情感倾诉 | 输入心事 → 细腻情感分析 → 温暖回应 | 支持正向/负向/中性及 18 种细腻情绪标签 |
| ⭐ 星座分析 | 双人匹配度 + 今日爱情运势 | 基于 12×12 匹配度矩阵 + AI 深度解读 |
| 📜 心情记录 | 历史对话查看与管理 | SQLite 本地存储，支持查阅与清空 |

## 技术栈

- **后端**：Python 3.12 + Flask 3.x
- **前端**：原生 HTML/CSS/JS（单页应用，温暖治愈风格）
- **AI 引擎**：DeepSeek Chat API（支持降级运行）
- **数据库**：SQLite（历史记录持久化）
- **情感分析**：基于大模型 Prompt Engineering 的细腻情感识别

## 环境要求

- Python 3.9+
- 浏览器（Chrome / Edge / Safari 等现代浏览器）

## 快速启动

### 1. 克隆 / 解压项目

```bash
cd lovementor
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

编辑项目根目录下的 `.env` 文件，填入 DeepSeek API Key：

```
DEEPSEEK_API_KEY=sk-your-actual-api-key
```

> 📌 **获取 API Key**：访问 [platform.deepseek.com](https://platform.deepseek.com) 注册并获取。
>
> 📌 **无 API Key 也能运行**：系统内置了降级方案，未配置 API Key 时将使用本地回退逻辑，不影响整体功能演示。

### 4. 启动服务

```bash
python app.py
```

### 5. 访问应用

浏览器打开 [http://localhost:5000](http://localhost:5000)

## 项目结构

```
lovementor/
├── app.py                    # Flask 主应用入口（路由、错误处理）
├── config.py                 # 配置文件（API Key、端口等）
├── requirements.txt          # Python 依赖清单
├── .env                      # 环境变量（API Key 配置）
├── .gitignore
├── README.md                 # 本文件
├── services/
│   ├── __init__.py
│   ├── deepseek_client.py    # DeepSeek API 统一封装层
│   ├── sentiment.py          # 情感分析 + 良师益友回应生成
│   ├── zodiac.py             # 星座匹配分析 + 运势生成
│   └── history.py            # SQLite 历史记录服务
├── data/
│   └── zodiac_data.py        # 12 星座基础数据 + 匹配度矩阵
├── templates/
│   └── index.html            # 前端单页应用（三 Tab 布局）
└── static/
    ├── css/
    │   └── style.css         # 温暖治愈风格样式表
    └── js/
        └── app.js            # 前端交互逻辑
```

## API 接口

| 方法 | 路由 | 说明 |
|------|------|------|
| GET | `/` | 主页面 |
| POST | `/api/analyze` | 情感分析 + 良师益友回应 |
| GET | `/api/zodiac/list` | 获取 12 星座列表 |
| POST | `/api/zodiac/match` | 双星座恋爱匹配度分析 |
| POST | `/api/zodiac/fortune` | 单星座今日爱情运势 |
| GET | `/api/history` | 获取历史记录 |
| DELETE | `/api/history` | 清空历史记录 |

### 请求示例

```json
POST /api/analyze
{ "text": "他今天一整天都没回我消息，我是不是想太多了..." }

Response:
{
  "sentiment": {
    "label": "焦虑",
    "category": "negative",
    "confidence": 0.87,
    "emotions": ["不安", "期待关注"]
  },
  "response": "亲爱的朋友，你的心情我完全理解...（温暖回应）"
}
```

## 降级策略

当 DeepSeek API 不可用时（未配置 Key / 网络异常 / 超时），系统自动启用降级方案：

| 服务 | 降级行为 |
|------|---------|
| 情感分析 | 返回中性标签 + 通用回应模板 |
| 星座匹配 | 使用本地匹配度矩阵计算结果 |
| 星座运势 | 使用预置运势数据 |

降级运行不会导致系统报错或崩溃，确保基础功能始终可用。

## 许可证

本项目仅用于课程学习和学术交流目的。
