from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from flask import Flask, jsonify, request
from flask_cors import CORS

from .database import fetchall, fetchone, init_db, session_scope
from .support import RESOURCES, assess_risk, build_supportive_message, merge_risk_levels

app = Flask(__name__)
CORS(app)

init_db()


def _isoformat(timestamp: str) -> str:
    try:
        return datetime.fromisoformat(timestamp).isoformat()
    except ValueError:
        return timestamp


@app.get("/api/resources")
def list_resources():
    return jsonify({"resources": RESOURCES})


@app.post("/api/chat")
def chat():
    payload = request.get_json(force=True, silent=True) or {}
    user_message = (payload.get("message") or "").strip()
    conversation_id = payload.get("conversation_id")

    if not user_message:
        return jsonify({"error": "A message is required."}), 400

    with session_scope() as connection:
        current = None
        if conversation_id is not None:
            current = connection.execute(
                "SELECT id, risk_level FROM conversations WHERE id = ?",
                (conversation_id,),
            ).fetchone()

        if current is None:
            cursor = connection.execute(
                "INSERT INTO conversations (risk_level) VALUES (?)",
                ("unknown",),
            )
            conversation_id = cursor.lastrowid
            current_risk = "unknown"
        else:
            conversation_id = current["id"]
            current_risk = current["risk_level"]

        connection.execute(
            "INSERT INTO messages (conversation_id, sender, text) VALUES (?, ?, ?)",
            (conversation_id, "user", user_message),
        )

        risk_result = assess_risk(user_message)
        merged_risk = merge_risk_levels(current_risk, risk_result.level)

        connection.execute(
            "UPDATE conversations SET risk_level = ? WHERE id = ?",
            (merged_risk, conversation_id),
        )

        bot_text = build_supportive_message(risk_result)
        connection.execute(
            "INSERT INTO messages (conversation_id, sender, text) VALUES (?, ?, ?)",
            (conversation_id, "bot", bot_text),
        )

        response = {
            "conversation_id": conversation_id,
            "response": bot_text,
            "risk_level": merged_risk,
            "triggers": risk_result.triggers,
            "recommended_resources": risk_result.recommended_resources,
        }

    return jsonify(response)


@app.get("/api/conversations")
def list_conversations():
    rows = fetchall(
        """
        SELECT c.id, c.created_at, c.risk_level, COUNT(m.id) AS message_count
        FROM conversations AS c
        LEFT JOIN messages AS m ON m.conversation_id = c.id
        GROUP BY c.id
        ORDER BY c.created_at DESC
        """
    )

    result = [
        {
            "id": row["id"],
            "created_at": _isoformat(row["created_at"]),
            "risk_level": row["risk_level"],
            "message_count": row["message_count"],
        }
        for row in rows
    ]

    return jsonify({"conversations": result})


@app.get("/api/conversations/<int:conversation_id>")
def get_conversation(conversation_id: int):
    conversation = fetchone(
        "SELECT id, created_at, risk_level FROM conversations WHERE id = ?",
        (conversation_id,),
    )
    if conversation is None:
        return jsonify({"error": "Conversation not found."}), 404

    messages = fetchall(
        """
        SELECT id, sender, text, created_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY created_at ASC, id ASC
        """,
        (conversation_id,),
    )

    data = {
        "id": conversation["id"],
        "created_at": _isoformat(conversation["created_at"]),
        "risk_level": conversation["risk_level"],
        "messages": [
            {
                "id": message["id"],
                "sender": message["sender"],
                "text": message["text"],
                "created_at": _isoformat(message["created_at"]),
            }
            for message in messages
        ],
    }

    return jsonify(data)


@app.get("/api/conversations/<int:conversation_id>/analysis")
def analyze_conversation(conversation_id: int):
    conversation = fetchone(
        "SELECT id, created_at, risk_level FROM conversations WHERE id = ?",
        (conversation_id,),
    )
    if conversation is None:
        return jsonify({"error": "Conversation not found."}), 404

    messages = fetchall(
        """
        SELECT id, sender, text, created_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY created_at ASC, id ASC
        """,
        (conversation_id,),
    )

    keyword_flags: List[Dict[str, str]] = []
    last_message_at = None
    for message in messages:
        timestamp = _isoformat(message["created_at"])
        last_message_at = timestamp
        if message["sender"] != "user":
            continue
        risk = assess_risk(message["text"])
        if risk.triggers:
            keyword_flags.append(
                {
                    "message_id": message["id"],
                    "excerpt": message["text"][:120],
                    "triggers": risk.triggers,
                    "assessed_level": risk.level,
                }
            )

    data = {
        "conversation_id": conversation["id"],
        "created_at": _isoformat(conversation["created_at"]),
        "risk_level": conversation["risk_level"],
        "message_count": len(messages),
        "user_message_count": sum(1 for m in messages if m["sender"] == "user"),
        "bot_message_count": sum(1 for m in messages if m["sender"] == "bot"),
        "keyword_flags": keyword_flags,
        "last_message_at": last_message_at or datetime.utcnow().isoformat(),
    }

    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
