# coding=utf-8
import logging
from .database import CommandSQL, Database
from typing import Any

database = Database()

def create_table():
    table = """ -- создание таблицы для отслеживания истории
        CREATE TABLE history_prompt (
        id SERIAL PRIMARY KEY,
        request_type TEXT CHECK (request_type IN ('text', 'image')) NOT NULL,
        request_datetime TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        prompt TEXT NOT NULL,
        response TEXT
    );"""
    try:
        database.execute_sql(table, CommandSQL.CREATE)
    except Exception as e:
        logging.info("Таблица уже создана")

def get_prompy_by_user(user_id: int, limit: int = 5, offset: int = 0) -> list[tuple[Any, ...]] | None:
    query = f"""
        SELECT *
        FROM history_prompt
        WHERE id = {user_id}
        ORDER BY request_datetime
        LIMIT {limit}
        OFFSET {offset}
    """
    return database.execute_sql(query, CommandSQL.SELECT)


