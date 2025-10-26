from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Iterator

DB_PATH = Path(__file__).resolve().parent.parent / "chatbot.db"


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    """Create database tables if they do not already exist."""

    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                risk_level TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                sender TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
            """
        )


@contextmanager
def session_scope() -> Iterator[sqlite3.Connection]:
    """Provide a transactional scope for database operations."""

    connection = _connect()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def fetchone(query: str, params: tuple) -> sqlite3.Row | None:
    with _connect() as connection:
        cursor = connection.execute(query, params)
        return cursor.fetchone()


def fetchall(query: str, params: tuple = ()) -> list[sqlite3.Row]:
    with _connect() as connection:
        cursor = connection.execute(query, params)
        return cursor.fetchall()
