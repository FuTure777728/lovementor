"""
情感良师 (LoveMentor) — Flask 主应用
爱情与两性关系情感分析系统
"""
from flask import Flask, request, jsonify, render_template
from datetime import datetime

from config import DEBUG, HOST, PORT, SECRET_KEY, DEEPSEEK_API_KEY
from services.sentiment import analyze_sentiment, generate_response
from services.zodiac import analyze_compatibility, get_daily_fortune, get_zodiac_list
from services.history import init_db, save_record, get_records, delete_all_records
from services.couple import (
    send_letter, get_inbox, get_unread_count, mark_read,
    submit_mediation, get_mediation_status, get_mediation_result, get_mediation_history
)

app = Flask(__name__)
app.secret_key = SECRET_KEY

# 启动时初始化数据库
init_db()

# 启动诊断
import sys
_key_ok = DEEPSEEK_API_KEY and DEEPSEEK_API_KEY != "your-api-key-here" and len(DEEPSEEK_API_KEY) > 10
print(f"[启动] DeepSeek API Key: {'已配置 ✅' if _key_ok else '未配置 ⚠️ 使用降级方案'}", file=sys.stderr)
if not _key_ok:
    print(f"[启动] 请在 Railway Variables 中设置 DEEPSEEK_API_KEY", file=sys.stderr)


# ============================================================
# 页面路由
# ============================================================

@app.route("/")
def index():
    """主页面"""
    return render_template("index.html")


# ============================================================
# API — 情感分析
# ============================================================

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """
    情感分析 + 良师益友回应

    Request:  { "text": "用户输入的文本", "user": "水水/小白（可选）" }
    Response: { "sentiment": {...}, "response": "...", "id": int }
    """
    data = request.get_json(silent=True)
    if not data or "text" not in data:
        return jsonify({"error": "请提供 text 字段"}), 400

    user_text = data["text"].strip()
    user = data.get("user", "").strip()
    if not user_text:
        return jsonify({"error": "text 不能为空"}), 400
    if len(user_text) > 2000:
        return jsonify({"error": "文本过长，请控制在2000字以内"}), 400

    # 情感分析
    sentiment = analyze_sentiment(user_text)

    # 生成良师益友回应（传入用户身份实现个性化）
    response = generate_response(user_text, sentiment, user=user)

    # 保存历史记录
    record_id = save_record(user_text, sentiment, response)

    return jsonify({
        "id": record_id,
        "sentiment": sentiment,
        "response": response,
        "timestamp": datetime.now().isoformat()
    })


# ============================================================
# API — 星座分析
# ============================================================

@app.route("/api/zodiac/list", methods=["GET"])
def api_zodiac_list():
    """获取所有星座列表"""
    signs = get_zodiac_list()
    return jsonify({"signs": signs})


@app.route("/api/zodiac/match", methods=["POST"])
def api_zodiac_match():
    """
    双星座匹配分析

    Request:  { "sign1": "天蝎座", "sign2": "双鱼座", "context": "可选" }
    Response: { "compatibility_score": 92, "analysis": "...", ... }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请提供请求数据"}), 400

    sign1 = data.get("sign1", "").strip()
    sign2 = data.get("sign2", "").strip()
    context = data.get("context", "").strip()

    if not sign1 or not sign2:
        return jsonify({"error": "请提供两个星座名称"}), 400

    result = analyze_compatibility(sign1, sign2, context)
    if "error" in result:
        return jsonify(result), 400

    return jsonify(result)


@app.route("/api/zodiac/fortune", methods=["POST"])
def api_zodiac_fortune():
    """
    星座今日爱情运势

    Request:  { "sign": "天蝎座", "mood": "可选的情绪状态" }
    Response: { "fortune_summary": "...", "love_index": "⭐⭐⭐⭐", ... }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请提供请求数据"}), 400

    sign = data.get("sign", "").strip()
    mood = data.get("mood", "").strip()

    if not sign:
        return jsonify({"error": "请提供星座名称"}), 400

    result = get_daily_fortune(sign, mood)
    if "error" in result:
        return jsonify(result), 400

    return jsonify(result)


# ============================================================
# API — 历史记录
# ============================================================

@app.route("/api/history", methods=["GET"])
def api_history():
    """获取历史记录"""
    limit = request.args.get("limit", 20, type=int)
    records = get_records(limit=min(limit, 50))
    return jsonify({"records": records, "count": len(records)})


@app.route("/api/history", methods=["DELETE"])
def api_history_clear():
    """清空历史记录"""
    delete_all_records()
    return jsonify({"message": "历史记录已清空"})


# ============================================================
# API — 情侣信箱
# ============================================================

@app.route("/api/mailbox/send", methods=["POST"])
def api_mailbox_send():
    """发送信件"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请提供请求数据"}), 400

    from_user = data.get("from_user", "").strip()
    message = data.get("message", "").strip()

    if not from_user or not message:
        return jsonify({"error": "请提供 from_user 和 message"}), 400

    result = send_letter(from_user, message)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@app.route("/api/mailbox/inbox", methods=["GET"])
def api_mailbox_inbox():
    """获取收件箱"""
    user = request.args.get("user", "").strip()
    if not user:
        return jsonify({"error": "请提供 user 参数"}), 400

    letters = get_inbox(user)
    return jsonify({"letters": letters, "count": len(letters)})


@app.route("/api/mailbox/unread", methods=["GET"])
def api_mailbox_unread():
    """获取未读数量"""
    user = request.args.get("user", "").strip()
    if not user:
        return jsonify({"count": 0})
    return jsonify({"count": get_unread_count(user)})


@app.route("/api/mailbox/read/<int:letter_id>", methods=["PUT"])
def api_mailbox_read(letter_id):
    """标记已读"""
    mark_read(letter_id)
    return jsonify({"ok": True})


# ============================================================
# API — 矛盾调解室
# ============================================================

@app.route("/api/mediation/submit", methods=["POST"])
def api_mediation_submit():
    """提交一方描述"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请提供请求数据"}), 400

    user = data.get("user", "").strip()
    message = data.get("message", "").strip()

    if not user or not message:
        return jsonify({"error": "请提供 user 和 message"}), 400

    result = submit_mediation(user, message)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@app.route("/api/mediation/status", methods=["GET"])
def api_mediation_status():
    """查看调解进度"""
    session_key = request.args.get("session", "").strip()
    if not session_key:
        return jsonify({"error": "请提供 session 参数"}), 400

    result = get_mediation_status(session_key)
    return jsonify(result)


@app.route("/api/mediation/result", methods=["GET"])
def api_mediation_result():
    """获取调解分析结果"""
    session_key = request.args.get("session", "").strip()
    if not session_key:
        return jsonify({"error": "请提供 session 参数"}), 400

    result = get_mediation_result(session_key)
    return jsonify(result)


@app.route("/api/mediation/history", methods=["GET"])
def api_mediation_history():
    """获取调解历史"""
    limit = request.args.get("limit", 10, type=int)
    records = get_mediation_history(limit=min(limit, 20))
    return jsonify({"records": records})


# ============================================================
# 健康检查
# ============================================================

@app.route("/api/health", methods=["GET"])
def api_health():
    """诊断 API 状态"""
    key_status = "ok" if DEEPSEEK_API_KEY and DEEPSEEK_API_KEY != "your-api-key-here" and len(DEEPSEEK_API_KEY) > 10 else "missing"
    return jsonify({
        "status": "running",
        "api_key_configured": key_status == "ok",
        "api_key_preview": DEEPSEEK_API_KEY[:10] + "..." if key_status == "ok" else "N/A",
    })


# ============================================================
# 错误处理
# ============================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "接口不存在"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "服务器内部错误，请稍后重试"}), 500


# ============================================================
# 启动入口
# ============================================================

if __name__ == "__main__":
    import sys
    # 设置 stdout 编码为 UTF-8，避免 Windows GBK 编码问题
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("""
+------------------------------------------+
|    LoveMentor 情感良师 v1.0              |
|    NLP 情感分析系统                       |
|                                          |
|    启动地址: http://localhost:{0}        |
|    按 Ctrl+C 停止服务                    |
+------------------------------------------+
    """.format(PORT))
    app.run(host=HOST, port=PORT, debug=DEBUG)
