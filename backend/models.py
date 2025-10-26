from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, relationship

from .database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    risk_level: Mapped[str] = Column(String(32), default="unknown")

    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[int] = Column(Integer, ForeignKey("conversations.id"))
    sender: Mapped[str] = Column(String(16))
    text: Mapped[str] = Column(Text)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)

    conversation: Mapped[Conversation] = relationship("Conversation", back_populates="messages")
