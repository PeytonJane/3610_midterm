from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import select

from .database import Base, engine, session_scope
from .models import Conversation, Message
from .support import RESOURCES, assess_risk, build_supportive_message, merge_risk_levels

app = Flask(__name__)
CORS(app)

Base.metadata.create_all(bind=engine)


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

    with session_scope() as session:
        conversation: Conversation
        if conversation_id is not None:
            conversation = session.get(Conversation, conversation_id)  # type: ignore[arg-type]
            if conversation is None:
                conversation = Conversation(risk_level="unknown")
                session.add(conversation)
                session.flush()
        else:
            conversation = Conversation(risk_level="unknown")
            session.add(conversation)
            session.flush()

        user_entry = Message(conversation_id=conversation.id, sender="user", text=user_message)
        session.add(user_entry)

        risk_result = assess_risk(user_message)
        conversation.risk_level = merge_risk_levels(conversation.risk_level, risk_result.level)

        bot_text = build_supportive_message(risk_result)
        bot_entry = Message(conversation_id=conversation.id, sender="bot", text=bot_text)
        session.add(bot_entry)

        session.flush()

        response = {
            "conversation_id": conversation.id,
            "response": bot_text,
            "risk_level": conversation.risk_level,
            "triggers": risk_result.triggers,
            "recommended_resources": risk_result.recommended_resources,
        }

    return jsonify(response)


@app.get("/api/conversations")
def list_conversations():
    with session_scope() as session:
        conversations = session.execute(select(Conversation)).scalars().all()
        result = [
            {
                "id": conv.id,
                "created_at": conv.created_at.isoformat(),
                "risk_level": conv.risk_level,
                "message_count": len(conv.messages),
            }
            for conv in conversations
        ]
    return jsonify({"conversations": result})


@app.get("/api/conversations/<int:conversation_id>")
def get_conversation(conversation_id: int):
    with session_scope() as session:
        conversation = session.get(Conversation, conversation_id)
        if conversation is None:
            return jsonify({"error": "Conversation not found."}), 404

        messages = [
            {
                "id": message.id,
                "sender": message.sender,
                "text": message.text,
                "created_at": message.created_at.isoformat(),
            }
            for message in conversation.messages
        ]

        data = {
            "id": conversation.id,
            "created_at": conversation.created_at.isoformat(),
            "risk_level": conversation.risk_level,
            "messages": messages,
        }

    return jsonify(data)


@app.get("/api/conversations/<int:conversation_id>/analysis")
def analyze_conversation(conversation_id: int):
    with session_scope() as session:
        conversation = session.get(Conversation, conversation_id)
        if conversation is None:
            return jsonify({"error": "Conversation not found."}), 404

        keyword_flags: List[Dict[str, str]] = []
        for message in conversation.messages:
            if message.sender != "user":
                continue
            risk = assess_risk(message.text)
            if risk.triggers:
                keyword_flags.append(
                    {
                        "message_id": message.id,
                        "excerpt": message.text[:120],
                        "triggers": risk.triggers,
                        "assessed_level": risk.level,
                    }
                )

        data = {
            "conversation_id": conversation.id,
            "created_at": conversation.created_at.isoformat(),
            "risk_level": conversation.risk_level,
            "message_count": len(conversation.messages),
            "user_message_count": sum(1 for m in conversation.messages if m.sender == "user"),
            "bot_message_count": sum(1 for m in conversation.messages if m.sender == "bot"),
            "keyword_flags": keyword_flags,
            "last_message_at": max((m.created_at for m in conversation.messages), default=datetime.utcnow()).isoformat(),
        }

    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
