"""
情侣功能服务层 — 信箱 + 矛盾调解
"""
import sqlite3
import os
import uuid
import json
from services.deepseek_client import get_client

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "lovementor.db")

VALID_USERS = {"水水", "小白"}


def _get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# 情侣信箱
# ============================================================

def send_letter(from_user: str, message: str) -> dict:
    """
    发送信件

    Args:
        from_user: 发送者 "水水" / "小白"
        message: 信件内容

    Returns:
        {"id": int, "to_user": str}
    """
    if from_user not in VALID_USERS:
        return {"error": f"无效用户: {from_user}"}

    to_user = "小白" if from_user == "水水" else "水水"

    conn = _get_db()
    cursor = conn.execute(
        "INSERT INTO couple_mailbox (from_user, to_user, message) VALUES (?, ?, ?)",
        (from_user, to_user, message[:1000])
    )
    conn.commit()
    letter_id = cursor.lastrowid
    conn.close()

    return {"id": letter_id, "to_user": to_user, "from_user": from_user}


def get_inbox(user: str, limit: int = 20) -> list:
    """
    获取收件箱（对方写给我的信）

    Args:
        user: 当前用户
        limit: 返回条数

    Returns:
        信件列表
    """
    if user not in VALID_USERS:
        return []

    conn = _get_db()
    rows = conn.execute(
        """SELECT * FROM couple_mailbox
           WHERE to_user = ?
           ORDER BY created_at DESC LIMIT ?""",
        (user, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_unread_count(user: str) -> int:
    """获取未读信件数"""
    if user not in VALID_USERS:
        return 0

    conn = _get_db()
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM couple_mailbox WHERE to_user = ? AND is_read = 0",
        (user,)
    ).fetchone()
    conn.close()
    return row["cnt"] if row else 0


def mark_read(letter_id: int) -> bool:
    """标记信件已读"""
    conn = _get_db()
    conn.execute("UPDATE couple_mailbox SET is_read = 1 WHERE id = ?", (letter_id,))
    conn.commit()
    conn.close()
    return True


# ============================================================
# 矛盾调解室
# ============================================================

MEDIATION_SYSTEM_PROMPT = """你是"白开水"，一位俏皮可爱的情感调解员。

现在有对情侣「水水」和「小白」因为某件事产生了矛盾，他们各自描述了事情的经过和感受。
你需要站在中立的第三方视角，帮他们分析问题并给出和解建议。

## 你的分析框架
1. 先轻松破冰，缓解紧张氛围
2. 客观总结双方各自的诉求和感受
3. 指出矛盾的**真正核心**（往往是沟通方式或未被满足的需求，而非表面事件）
4. 给出具体的和解步骤 + 一个甜蜜的修复行动建议

## 你的风格
- 俏皮可爱，但对待矛盾要认真
- 不站队、不评判谁对谁错
- 像好朋友一样劝和，不官方不说教
- 可以用有趣的比喻

## 输出格式（JSON）
{
    "ice_breaker": "一句俏皮的破冰语",
    "shuishui_view": "水水的核心感受和诉求（1-2句）",
    "xiaobai_view": "小白的核心感受和诉求（1-2句）",
    "core_issue": "矛盾的核心问题",
    "advice": "具体的和解建议（150-250字）",
    "sweet_action": "一个甜蜜的修复行动建议"
}"""


def submit_mediation(user: str, message: str) -> dict:
    """
    提交一方对矛盾的描述

    Args:
        user: "水水" / "小白"
        message: 矛盾描述

    Returns:
        {"session_key": str, "step": int, "waiting_for": str}
    """
    if user not in VALID_USERS:
        return {"error": f"无效用户: {user}"}

    conn = _get_db()

    # 查找是否有未完成的调解（对方已提交，本方未提交）
    other_user = "小白" if user == "水水" else "水水"
    pending = conn.execute(
        """SELECT session_key FROM mediation_sessions
           WHERE user = ? AND step = 1
           AND session_key NOT IN (
               SELECT session_key FROM mediation_sessions WHERE user = ?
           )
           ORDER BY created_at DESC LIMIT 1""",
        (other_user, user)
    ).fetchone()

    if pending:
        # 对方已提交，加入同一个 session
        session_key = pending["session_key"]
        conn.execute(
            "INSERT INTO mediation_sessions (session_key, user, message, step) VALUES (?, ?, ?, 2)",
            (session_key, user, message[:1500])
        )
        conn.commit()
        conn.close()
        return {
            "session_key": session_key,
            "step": 2,
            "both_ready": True,
            "message": f"双方都已提交，可以开始分析了！"
        }
    else:
        # 新建 session
        session_key = uuid.uuid4().hex[:12]
        conn.execute(
            "INSERT INTO mediation_sessions (session_key, user, message, step) VALUES (?, ?, ?, 1)",
            (session_key, user, message[:1500])
        )
        conn.commit()
        conn.close()
        return {
            "session_key": session_key,
            "step": 1,
            "both_ready": False,
            "waiting_for": other_user,
            "message": f"已记录你的描述，等{other_user}也提交后就能分析了～"
        }


def get_mediation_status(session_key: str) -> dict:
    """查看调解进度"""
    conn = _get_db()
    rows = conn.execute(
        "SELECT user, step, created_at FROM mediation_sessions WHERE session_key = ? ORDER BY step",
        (session_key,)
    ).fetchall()
    conn.close()

    users_submitted = [r["user"] for r in rows]
    steps = [r["step"] for r in rows]
    both_ready = len(users_submitted) >= 2

    return {
        "session_key": session_key,
        "both_ready": both_ready,
        "submitted_users": users_submitted,
        "steps": steps,
    }


def run_mediation_analysis(session_key: str) -> dict:
    """
    调用 AI 进行矛盾分析

    Args:
        session_key: 调解 session

    Returns:
        AI 分析结果 dict
    """
    conn = _get_db()
    rows = conn.execute(
        "SELECT * FROM mediation_sessions WHERE session_key = ? ORDER BY step",
        (session_key,)
    ).fetchall()

    if len(rows) < 2:
        conn.close()
        return {"error": "双方都还没提交完，请耐心等待～"}

    # 检查是否已有缓存结果
    if rows[0]["ai_result"]:
        conn.close()
        try:
            return json.loads(rows[0]["ai_result"])
        except (json.JSONDecodeError, TypeError):
            pass  # 缓存损坏，重新分析

    # 整理双方描述
    shuishui_msg = ""
    xiaobai_msg = ""
    for r in rows:
        if r["user"] == "水水":
            shuishui_msg = r["message"]
        elif r["user"] == "小白":
            xiaobai_msg = r["message"]

    client = get_client()
    prompt = f"""请分析这对情侣的矛盾：

【水水的描述】
{shuishui_msg}

【小白的描述】
{xiaobai_msg}

请按 JSON 格式返回分析结果。"""

    try:
        result = client.chat_json(
            user_message=prompt,
            system_prompt=MEDIATION_SYSTEM_PROMPT,
            temperature=0.7
        )

        # 缓存结果
        result_json = json.dumps(result, ensure_ascii=False)
        for r in rows:
            conn.execute(
                "UPDATE mediation_sessions SET ai_result = ? WHERE id = ?",
                (result_json, r["id"])
            )
        conn.commit()
        conn.close()

        return result

    except Exception as e:
        conn.close()
        return {
            "ice_breaker": "两个小可爱，先深呼吸一下～ 🫧",
            "shuishui_view": "水水觉得自己的感受没有被充分理解",
            "xiaobai_view": "小白也希望对方能更懂自己的心意",
            "core_issue": "沟通方式的错位——双方都在表达，但都没感觉到被真正听见",
            "advice": f"先各自冷静10分钟，然后轮流说'我听到你说的是...'来确认理解。注意：是复述对方的话，不是反驳！（分析出错: {e}）",
            "sweet_action": "一人写一句对方的优点贴在冰箱上，看着它吃一顿饭 🍜"
        }


def get_mediation_result(session_key: str) -> dict:
    """获取调解结果（优先缓存，没有则触发分析）"""
    conn = _get_db()
    rows = conn.execute(
        "SELECT * FROM mediation_sessions WHERE session_key = ? ORDER BY step",
        (session_key,)
    ).fetchall()

    if len(rows) < 2:
        conn.close()
        return {
            "ready": False,
            "session_key": session_key,
            "submitted": [r["user"] for r in rows],
            "message": "还在等待另一方提交..."
        }

    # 尝试读缓存
    if rows[0]["ai_result"]:
        conn.close()
        try:
            cached = json.loads(rows[0]["ai_result"])
            cached["ready"] = True
            cached["session_key"] = session_key
            return cached
        except (json.JSONDecodeError, TypeError):
            pass

    conn.close()
    # 触发分析
    result = run_mediation_analysis(session_key)
    result["ready"] = True
    result["session_key"] = session_key
    return result


def get_mediation_history(limit: int = 10) -> list:
    """获取调解历史列表（按 session 分组）"""
    conn = _get_db()
    rows = conn.execute(
        """SELECT session_key, GROUP_CONCAT(user, ' & ') as users,
                  MAX(created_at) as latest_time,
                  COUNT(*) as cnt,
                  MAX(CASE WHEN ai_result IS NOT NULL THEN 1 ELSE 0 END) as has_result
           FROM mediation_sessions
           GROUP BY session_key
           ORDER BY latest_time DESC LIMIT ?""",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
