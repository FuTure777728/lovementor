"""
情感分析服务 — 调用 DeepSeek API 实现爱情领域细腻情感分析
"""
import json
from services.deepseek_client import get_client

# 良师益友 System Prompt
MENTOR_SYSTEM_PROMPT = """你是一位名叫"白开水"的情感小精灵，是用户身边那个古灵精怪又超懂感情的闺蜜/好哥们！✨

## 🎀 你的性格
- 俏皮可爱、元气满满，像一杯冒着泡泡的苏打水 🫧
- 有点小毒舌但绝不伤人，吐槽中带着关心
- 脑洞大开，喜欢用奇妙的比喻解释感情问题
- 表面嘻嘻哈哈，实际上看问题一针见血
- 爱用 emoji 和颜文字来表达情绪 (๑•̀ㅂ•́)و✧

## 💕 你的专业领域
- 爱情与两性关系的情感分析
- 用有趣的方式帮用户看清纠结的情感问题
- 给出不落俗套的建议，拒绝鸡汤套路

## 🎤 你的风格
- 先撒个娇或抛个梗拉近距离，再给出有洞察力的分析
- 用生活中有趣的比喻来解释情感道理（比如"感情就像奶茶，太甜会腻，太淡没味，三分糖刚刚好"）
- 偶尔自嘲或吐槽，让气氛轻松起来
- 适当使用"宝～""姐妹""兄dei""hhh"等活泼用语
- 善用 emoji 增加表现力，但不要泛滥 🎨
- 不要冷冰冰贴标签，不要高高在上说教
- 不要说"我理解你"这种老套开场白

## 📏 回复长度规则（重要！）
- 用户就一句话/抱怨很短 → 回 2-4 句话，俏皮点破即可
- 用户写了一大段、情绪复杂 → 认真展开，可以 200-400 字
- 用户像在聊天互动 → 保持简短，像朋友聊天一样自然
- 原则：用户说多少，你就回应多少，不要过度输出

## ⚠️ 注意事项
- 不要给出极端或有害的建议
- 遇到严重心理问题倾向时，先共情再温和建议寻求专业帮助
- 保持积极正向，但拒绝强行灌鸡汤
- 俏皮是风格，不是不认真——对用户的情绪始终保持真诚"""


def analyze_sentiment(user_text: str) -> dict:
    """
    情感分析 — 识别用户在爱情关系中的细腻情感

    Args:
        user_text: 用户输入的文本

    Returns:
        {
            "label": str,       # 主要情感标签
            "category": str,    # positive/negative/neutral
            "confidence": float,# 置信度 0-1
            "emotions": [str],  # 次要情绪列表
            "keywords": [str],  # 情感关键词
        }
    """
    client = get_client()

    sentiment_prompt = """请分析以下用户在爱情/情感方面的倾诉文本，识别其情感状态。

情感标签体系：
- 正面情绪：甜蜜、幸福、期待、感动、安心、满足、感恩
- 负面情绪：失落、焦虑、委屈、吃醋、心碎、纠结、愤怒、不安、孤独
- 中性情绪：迷茫、回忆、思考、好奇、观望

请以 JSON 格式返回分析结果：
{
    "label": "最主要的情感标签（从上述标签中选择）",
    "category": "positive/negative/neutral",
    "confidence": 0.0-1.0之间的数字,
    "emotions": ["次要情绪1", "次要情绪2"],
    "keywords": ["文本中关键的情感词汇1", "词汇2", "词汇3"],
    "brief_analysis": "1-2句话简短概括用户的情感状态"
}"""

    try:
        result = client.chat_json(
            user_message=f"请分析这段情感倾诉：\n\n{user_text}",
            system_prompt=sentiment_prompt,
            temperature=0.3
        )

        # 验证必要字段
        required_fields = ["label", "category", "confidence", "emotions", "keywords"]
        for field in required_fields:
            if field not in result:
                result[field] = "未知" if field in ["label", "category"] else []

        # 确保类型正确
        if not isinstance(result.get("emotions"), list):
            result["emotions"] = []
        if not isinstance(result.get("keywords"), list):
            result["keywords"] = []
        try:
            result["confidence"] = float(result["confidence"])
        except (ValueError, TypeError):
            result["confidence"] = 0.5

        return result

    except Exception as e:
        # 降级方案：返回一个基础分析
        return {
            "label": "思考",
            "category": "neutral",
            "confidence": 0.5,
            "emotions": [],
            "keywords": [],
            "brief_analysis": f"抱歉，分析过程中遇到了问题：{str(e)}"
        }


def generate_response(user_text: str, sentiment: dict, user: str = "") -> str:
    """
    根据情感分析结果，生成俏皮可爱风格的回应，长度自适应

    Args:
        user_text: 用户原始文本
        sentiment: 情感分析结果
        user: 当前用户身份 "水水" / "小白" / ""

    Returns:
        俏皮温暖的回应文本
    """
    client = get_client()

    # --- 用户身份适配 ---
    if user == "水水":
        user_hint = '当前和你聊天的是「水水」（男生），请用"水水～""兄dei""hhh"等亲切自然的称呼，带点兄弟式调侃风格。'
    elif user == "小白":
        user_hint = '当前和你聊天的是「小白」（女生），请用"小白宝～""姐妹""嘿嘿"等俏皮可爱的称呼，带点闺蜜分享风格。'
    else:
        user_hint = ""

    # --- 自适应长度策略 ---
    text_len = len(user_text)
    if text_len < 30:
        length_hint = "用户只说了一两句话，请回复 2-4 句即可，俏皮点破，不要长篇大论。"
        max_tokens = 300
    elif text_len < 150:
        length_hint = "用户说了中等篇幅，回复 100-200 字左右，保持轻松活泼。"
        max_tokens = 500
    elif text_len < 500:
        length_hint = "用户倾诉了比较多内容，可以展开到 200-350 字，认真但不啰嗦。"
        max_tokens = 800
    else:
        length_hint = "用户写了很多，说明情绪复杂或事情重要，请认真回应 300-500 字但保持你的俏皮风格。"
        max_tokens = 1000

    # --- 情感适配 ---
    category = sentiment.get("category", "neutral")
    if category == "positive":
        mood_hint = "用户情绪正面，可以一起开心、调侃、撒花庆祝～"
    elif category == "negative":
        mood_hint = "用户情绪低落，先给个温暖的抱抱再俏皮开解，幽默要轻柔不要显得不在乎。"
    else:
        mood_hint = "用户情绪中性或迷茫，可以轻松地帮TA理一理思路。"

    response_prompt = f"""用户刚刚向你倾诉了以下情感内容：
---
{user_text}
---

情感分析结果：主要情绪「{sentiment.get('label', '未知')}」，
类别为「{category}」，
次要情绪：「{', '.join(sentiment.get('emotions', []))}」

🎯 回应要求：
- {length_hint}
- {mood_hint}
- {user_hint}
- 以"白开水"的身份回应，个性要鲜明
- 不要提"你的情绪标签是xx"这种机器语言，要自然说出来"""

    try:
        response = client.chat(
            user_message=response_prompt,
            system_prompt=MENTOR_SYSTEM_PROMPT,
            temperature=0.85,
            max_tokens=max_tokens
        )
        return response.strip()
    except Exception as e:
        # 降级回应
        return _fallback_response(sentiment)


def _fallback_response(sentiment: dict) -> str:
    """当 API 不可用时的降级回应（俏皮版）"""
    category = sentiment.get("category", "neutral")
    label = sentiment.get("label", "思考")

    fallbacks = {
        "positive": f"哇哦～{label}的感觉也太棒了吧！✨ 看把你开心的，"
                    "我也跟着嘴角上扬了hhh。趁着心情好，"
                    "快去给TA发个可爱的表情包，把甜蜜传染过去～ (๑•̀ㅂ•́)و✧",
        "negative": f"哎哟喂，{label}这种情绪真的超难受的，先给你一个大大的抱抱 🫂！"
                    "不过宝，就像奶茶三分糖最好喝，感情里有点苦才知道甜有多珍贵。"
                    "先做点让自己开心的小事，没有什么是一顿火锅解决不了的～",
        "neutral": f"唔，感觉你心里正在酝酿什么小想法呢 🤔～"
                   "没关系不用急着下结论，感情这种事情啊，"
                   "有时候就像拆盲盒，耐心等等会有惊喜的！",
    }
    return fallbacks.get(category, fallbacks["neutral"])
