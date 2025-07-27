# coding=utf-8
import logging
from .database import CommandSQL, Database
from typing import Any

database = Database()

def create_table():
    table = """ -- создание таблицы для отслеживания истории
        CREATE TABLE IF NOT EXISTS history_prompt (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_type TEXT CHECK (request_type IN ('text', 'image')) NOT NULL,
        request_datetime DATETIME NOT NULL,
        prompt TEXT NOT NULL,
        response TEXT
    );"""
    try:
        database.execute_sql(table, (), CommandSQL.CREATE)
    except Exception as e:
        logging.info("Таблица уже создана")

def get_prompt_by_user(user_id: int, limit: int = 5, offset: int = 0) -> list[Any] | None:
    query = """
        SELECT *
        FROM history_prompt
        WHERE id = ?
        ORDER BY request_datetime
        LIMIT ?
        OFFSET ?
    """
    return database.execute_sql(query, (user_id, limit, offset), CommandSQL.SELECT)


