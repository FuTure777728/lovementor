"""
历史记录服务 — SQLite 存储
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "lovementor.db")


def _get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    conn = _get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_text TEXT NOT NULL,
            sentiment_label TEXT,
            sentiment_category TEXT,
            sentiment_data TEXT,
            ai_response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 情侣信箱表
    conn.execute("""
        CREATE TABLE IF NOT EXISTS couple_mailbox (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user TEXT NOT NULL,
            to_user TEXT NOT NULL,
            message TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 矛盾调解表
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mediation_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_key TEXT NOT NULL,
            user TEXT NOT NULL,
            message TEXT NOT NULL,
            step INTEGER DEFAULT 1,
            ai_result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_record(user_text: str, sentiment: dict, response: str) -> int:
    """
    保存一条分析记录

    Args:
        user_text: 用户输入文本
        sentiment: 情感分析结果
        response: AI 回应

    Returns:
        新记录的 ID
    """
    import json
    conn = _get_db()
    cursor = conn.execute(
        """INSERT INTO history (user_text, sentiment_label, sentiment_category, sentiment_data, ai_response)
           VALUES (?, ?, ?, ?, ?)""",
        (
            user_text[:500],
            sentiment.get("label", "未知"),
            sentiment.get("category", "neutral"),
            json.dumps(sentiment, ensure_ascii=False),
            response
        )
    )
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()

    # 限制历史记录数量
    _cleanup_old_records()
    return record_id


def get_records(limit: int = 20) -> list:
    """
    获取历史记录列表

    Args:
        limit: 返回条数上限

    Returns:
        记录列表
    """
    conn = _get_db()
    rows = conn.execute(
        "SELECT * FROM history ORDER BY created_at DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_all_records():
    """清空所有历史记录"""
    conn = _get_db()
    conn.execute("DELETE FROM history")
    conn.commit()
    conn.close()


def _cleanup_old_records():
    """保留最近 MAX_HISTORY 条记录"""
    from config import MAX_HISTORY
    conn = _get_db()
    count = conn.execute("SELECT COUNT(*) FROM history").fetchone()[0]
    if count > MAX_HISTORY:
        excess = count - MAX_HISTORY
        conn.execute(
            "DELETE FROM history WHERE id IN "
            "(SELECT id FROM history ORDER BY created_at ASC LIMIT ?)",
            (excess,)
        )
        conn.commit()
    conn.close()
