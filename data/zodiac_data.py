"""
12 星座基础数据与匹配度矩阵
"""

# 12 星座基础信息
ZODIAC_SIGNS = [
    {"name": "白羊座", "date_range": "3月21日-4月19日", "element": "火", "emoji": "♈",
     "traits": ["热情", "勇敢", "直率", "冲动", "竞争心强"],
     "love_style": "主动热烈，喜欢追逐，在爱情中充满激情和能量"},
    {"name": "金牛座", "date_range": "4月20日-5月20日", "element": "土", "emoji": "♉",
     "traits": ["稳重", "忠诚", "务实", "固执", "追求享受"],
     "love_style": "慢热但专一，重视稳定和物质安全感，用行动表达爱意"},
    {"name": "双子座", "date_range": "5月21日-6月21日", "element": "风", "emoji": "♊",
     "traits": ["聪明", "善变", "好奇", "健谈", "适应力强"],
     "love_style": "喜欢有趣的灵魂碰撞，需要精神层面的交流和新鲜感"},
    {"name": "巨蟹座", "date_range": "6月22日-7月22日", "element": "水", "emoji": "♋",
     "traits": ["温柔", "敏感", "顾家", "念旧", "保护欲强"],
     "love_style": "极度重视安全感，渴望被呵护也愿意全身心付出"},
    {"name": "狮子座", "date_range": "7月23日-8月22日", "element": "火", "emoji": "♌",
     "traits": ["自信", "大方", "骄傲", "忠诚", "爱表现"],
     "love_style": "喜欢被崇拜和关注，在爱情中慷慨热情但要面子"},
    {"name": "处女座", "date_range": "8月23日-9月22日", "element": "土", "emoji": "♍",
     "traits": ["细心", "理性", "追求完美", "可靠", "谨慎"],
     "love_style": "用细节表达爱，默默付出，但有时过于挑剔和理性"},
    {"name": "天秤座", "date_range": "9月23日-10月23日", "element": "风", "emoji": "♎",
     "traits": ["优雅", "公正", "社交能力强", "犹豫", "重视和谐"],
     "love_style": "追求和谐美好的关系，浪漫而有品位，但害怕冲突"},
    {"name": "天蝎座", "date_range": "10月24日-11月22日", "element": "水", "emoji": "♏",
     "traits": ["深情", "神秘", "意志坚定", "占有欲强", "洞察力强"],
     "love_style": "爱得深沉而极致，忠诚但占有欲强，需要绝对的信任"},
    {"name": "射手座", "date_range": "11月23日-12月21日", "element": "火", "emoji": "♐",
     "traits": ["乐观", "自由", "坦率", "爱冒险", "不喜欢束缚"],
     "love_style": "向往自由奔放的爱情，不喜欢被管控，需要共同成长的空间"},
    {"name": "摩羯座", "date_range": "12月22日-1月19日", "element": "土", "emoji": "♑",
     "traits": ["成熟", "负责", "务实", "有野心", "内敛"],
     "love_style": "认真负责的伴侣，用行动和承诺证明爱，但表达情感比较含蓄"},
    {"name": "水瓶座", "date_range": "1月20日-2月18日", "element": "风", "emoji": "♒",
     "traits": ["独立", "创新", "理性", "友善", "叛逆"],
     "love_style": "需要精神共鸣和独立空间，爱得有创意但有时显得疏离"},
    {"name": "双鱼座", "date_range": "2月19日-3月20日", "element": "水", "emoji": "♓",
     "traits": ["浪漫", "善良", "感性", "富有想象力", "易受影响"],
     "love_style": "浪漫到骨子里，为爱可以付出一切，但需要被温柔对待"},
]

# 星座名称索引
ZODIAC_NAMES = [s["name"] for s in ZODIAC_SIGNS]

# 星座匹配度矩阵 (12x12, 0-100)
# 基于星座元素和传统星座配对理论
COMPATIBILITY_MATRIX = [
    # 白  金  双  巨  狮  处  天  天  射  摩  水  双
    # 羊  牛  子  蟹  子  女  秤  蝎  手  羯  瓶  鱼
    [100, 70, 88, 62, 95, 55, 78, 75, 92, 65, 80, 68],  # 白羊
    [ 70,100, 58, 88, 65, 92, 75, 80, 60, 95, 62, 85],  # 金牛
    [ 88, 58,100, 65, 82, 62, 90, 68, 85, 55, 95, 72],  # 双子
    [ 62, 88, 65,100, 70, 82, 72, 95, 58, 85, 68, 92],  # 巨蟹
    [ 95, 65, 82, 70,100, 58, 85, 72, 90, 68, 78, 62],  # 狮子
    [ 55, 92, 62, 82, 58,100, 68, 78, 60, 88, 65, 75],  # 处女
    [ 78, 75, 90, 72, 85, 68,100, 72, 82, 65, 92, 70],  # 天秤
    [ 75, 80, 68, 95, 72, 78, 72,100, 65, 82, 60, 95],  # 天蝎
    [ 92, 60, 85, 58, 90, 60, 82, 65,100, 55, 85, 62],  # 射手
    [ 65, 95, 55, 85, 68, 88, 65, 82, 55,100, 58, 78],  # 摩羯
    [ 80, 62, 95, 68, 78, 65, 92, 60, 85, 58,100, 68],  # 水瓶
    [ 68, 85, 72, 92, 62, 75, 70, 95, 62, 78, 68,100],  # 双鱼
]

# 匹配度等级划分
COMPATIBILITY_LEVELS = [
    (90, "💖 天生一对", "你们是命中注定的组合，彼此理解和吸引"),
    (80, "💕 极佳匹配", "你们非常合拍，在一起会很幸福"),
    (70, "💛 良好默契", "有很好的相处基础，需要用心经营"),
    (60, "🤝 一般组合", "需要多一些理解和包容"),
    (0,  "🌱 需要磨合", "差异较大，但真爱可以跨越一切差异"),
]


def get_zodiac_by_name(name: str) -> dict | None:
    """按名称获取星座信息"""
    for sign in ZODIAC_SIGNS:
        if sign["name"] == name:
            return sign
    return None


def get_compatibility(sign1: str, sign2: str) -> dict:
    """
    获取两个星座的匹配度

    Args:
        sign1: 星座1名称
        sign2: 星座2名称

    Returns:
        {"score": int, "level": str, "description": str,
         "sign1_info": dict, "sign2_info": dict}
    """
    idx1 = ZODIAC_NAMES.index(sign1)
    idx2 = ZODIAC_NAMES.index(sign2)
    score = COMPATIBILITY_MATRIX[idx1][idx2]

    level = COMPATIBILITY_LEVELS[-1]
    for l in COMPATIBILITY_LEVELS:
        if score >= l[0]:
            level = l
            break

    return {
        "score": score,
        "level_name": level[1],
        "level_desc": level[2],
        "sign1": get_zodiac_by_name(sign1),
        "sign2": get_zodiac_by_name(sign2),
    }
