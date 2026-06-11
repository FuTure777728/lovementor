"""
星座分析服务 — 匹配度分析 + 运势生成
"""
from data.zodiac_data import (
    ZODIAC_SIGNS, ZODIAC_NAMES,
    get_zodiac_by_name, get_compatibility
)
from services.deepseek_client import get_client

ZODIAC_SYSTEM_PROMPT = """你是一位精通星座与情感关系的占星师，你的语气温暖亲切、有洞察力。

## 你的背景
- 深谙占星学，了解星座元素（火土风水）与情感模式的关联
- 但你不迷信，你会结合现实情感智慧给出建议
- 你相信星座是了解自己和伴侣的工具，而非绝对的命运判决书

## 你的风格
- 有趣但不轻浮，专业但不死板
- 可以用星座视角解读情感，但始终落脚到温暖的实际建议
- 回复简洁有料，控制在 200-350 字
- 可以适当使用 emoji 增加趣味"""


def get_zodiac_list() -> list:
    """获取所有星座列表"""
    return ZODIAC_SIGNS


def analyze_compatibility(sign1: str, sign2: str, context: str = "") -> dict:
    """
    分析两个星座的恋爱匹配度

    Args:
        sign1: 星座1名称
        sign2: 星座2名称
        context: 可选的额外背景描述

    Returns:
        包含匹配度分数、分析、建议等的字典
    """
    # 参数验证
    if sign1 not in ZODIAC_NAMES:
        return {"error": f"未知星座: {sign1}", "valid_signs": ZODIAC_NAMES}
    if sign2 not in ZODIAC_NAMES:
        return {"error": f"未知星座: {sign2}", "valid_signs": ZODIAC_NAMES}

    # 获取基础匹配度数据
    base = get_compatibility(sign1, sign2)

    # 调用 AI 进行深度分析
    client = get_client()

    prompt = f"""请分析 {sign1} 和 {sign2} 这两个星座在恋爱中的匹配情况。

基础信息：
- {sign1}：元素{base['sign1']['element']}象星座，性格{', '.join(base['sign1']['traits'])}
  恋爱风格：{base['sign1']['love_style']}
- {sign2}：元素{base['sign2']['element']}象星座，性格{', '.join(base['sign2']['traits'])}
  恋爱风格：{base['sign2']['love_style']}
- 基础匹配度：{base['score']}/100 分

"""

    if context:
        prompt += f"用户补充信息：{context}\n\n"

    prompt += """请以 JSON 格式返回你的分析：
{
    "analysis": "200-350字的整体匹配分析",
    "strengths": ["这个组合的3个优势"],
    "challenges": ["可能需要磨合的2-3个点"],
    "advice": "给这对情侣的具体相处建议",
    "romance_tip": "一个浪漫的约会/相处小建议"
}"""

    try:
        ai_result = client.chat_json(
            user_message=prompt,
            system_prompt=ZODIAC_SYSTEM_PROMPT,
            temperature=0.7
        )

        # 合并基础数据和 AI 分析
        result = {
            "sign1": sign1,
            "sign2": sign2,
            "sign1_emoji": base["sign1"]["emoji"],
            "sign2_emoji": base["sign2"]["emoji"],
            "compatibility_score": base["score"],
            "level": base["level_name"],
            "level_desc": base["level_desc"],
        }
        result.update(ai_result)
        return result

    except Exception as e:
        # AI 降级：返回基础数据
        return {
            "sign1": sign1,
            "sign2": sign2,
            "sign1_emoji": base["sign1"]["emoji"],
            "sign2_emoji": base["sign2"]["emoji"],
            "compatibility_score": base["score"],
            "level": base["level_name"],
            "level_desc": base["level_desc"],
            "analysis": f"{sign1}和{sign2}的组合属于{base['level_name']}。"
                        f"两个{base['sign1']['element']}象星座和{base['sign2']['element']}象星座的相遇，"
                        f"既有互补也有挑战。建议多沟通、多理解对方的表达方式。",
            "strengths": ["彼此吸引", "可以互补成长"],
            "challenges": ["需要时间磨合", "沟通方式不同"],
            "advice": "爱情需要用心经营，星座只是参考。真诚和理解才是最重要的。",
            "romance_tip": "一起去看星空吧，在浩瀚宇宙中感受彼此的渺小与珍贵。"
        }


def get_daily_fortune(sign: str, mood: str = "") -> dict:
    """
    获取星座今日爱情运势

    Args:
        sign: 星座名称
        mood: 可选，用户当前情绪状态

    Returns:
        运势分析 dict
    """
    if sign not in ZODIAC_NAMES:
        return {"error": f"未知星座: {sign}", "valid_signs": ZODIAC_NAMES}

    zodiac = get_zodiac_by_name(sign)
    client = get_client()

    mood_context = ""
    if mood:
        mood_context = f"\n此外，用户当前的情绪状态偏向「{mood}」，请结合这个情绪状态给出更有针对性的建议。"

    prompt = f"""请为{zodiac['emoji']} {sign} 生成今日爱情运势。

星座信息：
- 元素：{zodiac['element']}象星座
- 性格：{', '.join(zodiac['traits'])}
- 恋爱风格：{zodiac['love_style']}
{mood_context}

请以 JSON 格式返回：
{{
    "fortune_summary": "一句话运势总结",
    "love_index": "1-5星的爱情指数，如'⭐⭐⭐⭐'",
    "today_tip": "今天的爱情小贴士",
    "lucky_color": "幸运颜色",
    "lucky_number": "1-99的幸运数字",
    "mood_advice": "结合情绪状态的建议（如果提供了情绪）"
}}

注意：运势要温暖正向，给人希望感，但不要过度承诺。强调"主动创造好运"的理念。"""

    try:
        result = client.chat_json(
            user_message=prompt,
            system_prompt=ZODIAC_SYSTEM_PROMPT,
            temperature=0.8
        )

        result["sign"] = sign
        result["emoji"] = zodiac["emoji"]
        result["element"] = zodiac["element"]
        return result

    except Exception as e:
        return {
            "sign": sign,
            "emoji": zodiac["emoji"],
            "element": zodiac["element"],
            "fortune_summary": "今天适合顺其自然，相信自己的直觉",
            "love_index": "⭐⭐⭐",
            "today_tip": "多关注自己的内心感受，爱情需要先爱自己",
            "lucky_color": "粉色",
            "lucky_number": "7",
            "mood_advice": "每一天都是新的开始，带着希望前行吧"
        }
