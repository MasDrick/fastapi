# coding=utf-8
import logging
 
import pytz

from datetime import datetime
from .database import CommandSQL, Database
from typing import Any


tz_ekb = pytz.timezone('Asia/Yekaterinburg')
database = Database()

def create_table():
    table = """ -- создание таблицы для отслеживания истории
        CREATE TABLE IF NOT EXISTS history_prompt (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        request_type TEXT CHECK (request_type IN ('text', 'image')) NOT NULL,
        request_datetime DATETIME NOT NULL,
        prompt TEXT NOT NULL,
        response TEXT
    );"""
    try:
        database.execute_sql(table, (), CommandSQL.CREATE)
    except Exception as e:
        logging.info("Таблица уже создана")

def get_prompt_by_user(user_id: int, chat_type: str = "text", limit: int = 5, offset: int = 0) -> list[Any] | None:
    query = """
        SELECT *
        FROM history_prompt
        WHERE id = ? AND request_type = ?
        ORDER BY request_datetime
        LIMIT ?
        OFFSET ?
    """
    return database.execute_sql(query, (user_id, chat_type, limit, offset), CommandSQL.SELECT)

def create_row(user_id: int, prompt: str, response: str, request_type: str) -> None:
    current_time_ekb = datetime.now(tz_ekb)
    query = """
        INSERT INTO history_prompt (user_id, request_type, request_datetime, prompt, response)
        VALUES (?, ?, ?, ?, ?)
    """
    database.execute_sql(query, (user_id, request_type, current_time_ekb.isoformat(), prompt, response), CommandSQL.INSERT)


