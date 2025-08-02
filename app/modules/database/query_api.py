# coding=utf-8
import logging
 
import pytz

from datetime import datetime
from .database import CommandSQL, Database
from typing import Any


tz_ekb = pytz.timezone('Asia/Yekaterinburg')
database = Database()

def create_table():
    """
    Создаёт необходимые таблицы в БД
    """

    tables = [
    """ -- создание таблиц чатов
    CREATE TABLE IF NOT EXISTS chats (
        chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        chat_type TEXT CHECK (chat_type IN ('mixed', 'text', 'image')) NOT NULL DEFAULT 'mixed',
        chat_name TEXT DEFAULT 'Новый чат',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );""",

    """ -- создание таблицы для отслеживания истории
    CREATE TABLE IF NOT EXISTS messages (
        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL,
        request_type TEXT CHECK (request_type IN ('text', 'image')) NOT NULL,
        prompt TEXT NOT NULL,
        response TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chat_id) REFERENCES chats(chat_id) ON DELETE CASCADE
    );""",

    """ -- создание таблицы для отслеживания избранных моделей
    CREATE TABLE IF NOT EXISTS user_favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        model_name TEXT NOT NULL,
        UNIQUE(user_id, model_name)
    );"""
    ]

    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_user_favorites ON user_favorites(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_chats_user ON chats(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages(chat_id)",
        "CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(created_at)"
    ]

    for table in tables:
        try:
            database.execute_sql(table, (), CommandSQL.CREATE)
        except Exception as e:
            logging.error(f"Ошибка при создании таблицы: {e}")

    for index in indexes:
        try:
            database.execute_sql(index, (), CommandSQL.CREATE)
        except Exception as e:
            logging.error(f"Ошибка при создании индекса: {e}")

def get_prompt_by_user(chat_id: int, limit: int = 5, offset: int = 0) -> list[Any] | None:
    query = """
        SELECT *
        FROM messages
        WHERE chat_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        OFFSET ?
    """
    return database.execute_sql(query, (chat_id, limit, offset), CommandSQL.SELECT)

def create_message(chat_id: int, prompt: str, response: str, request_type: str) -> None:
    current_time_ekb = datetime.now(tz_ekb)
    query = """
        INSERT INTO messages (chat_id, request_type, prompt, response, created_at)
        VALUES (?, ?, ?, ?, ?)
    """
    database.execute_sql(query, (chat_id, request_type, prompt, response, current_time_ekb.isoformat()), CommandSQL.INSERT)

def create_chat(user_id: int, chat_name: str = "Новый чат", chat_type: str = "mixed") -> int:
    query = """
        INSERT INTO chats (user_id, chat_type, chat_name)
        VALUES (?, ?, ?)
    """
    try:
        database.execute_sql(query, (user_id, chat_type, chat_name), CommandSQL.INSERT)
        
        query = "SELECT last_insert_rowid()"  # Получаем ID созданного чата
        result = database.execute_sql(query, (), CommandSQL.SELECT)
        return result[0][0] if result else None
    except Exception as e:
        logging.error(f"Ошибка при создании чата: {e}")
        return None

def delete_chat(chat_id: int) -> bool:
    """
    Удаляет чат по его ID
    """

    query = """
        DELETE FROM chats 
        WHERE chat_id = ?
    """
    try:
        database.execute_sql(
            "DELETE FROM messages WHERE chat_id = ?",
            (chat_id,),
            CommandSQL.DELETE
        )

        database.execute_sql(query, (chat_id,), CommandSQL.DELETE)
        return True
    except Exception as e:
        logging.error(f"Ошибка при удалении чата: {e}")
        return False
    

def add_favorite_model(user_id: int, model_name: str) -> bool:
    query = """
        INSERT OR IGNORE INTO user_favorites (user_id, model_name)
        VALUES (?, ?)
    """
    try:
        database.execute_sql(query, (user_id, model_name), CommandSQL.INSERT)
        return True
    except Exception as e:
        logging.error(f"Ошибка при добавлении в избранное: {e}")
        return False

def get_user_favorites(user_id: int) -> list[str]:
    """
    Получает список избранных моделей пользователя
    """

    query = """
        SELECT model_name 
        FROM user_favorites 
        WHERE user_id = ? 
    """
    try:
        result = database.execute_sql(query, (user_id,), CommandSQL.SELECT)
        return [row[0] for row in result] if result else []
    except Exception as e:
        logging.error(f"Ошибка при получении избранного: {e}")
        return []

def del_model(user_id: int, model_name: str):
    """
    Удаляет модель из избранного пользователя
    """
    query = """
        DELETE FROM user_favorites 
        WHERE user_id = ? AND model_name = ?
    """
    try:
        database.execute_sql(query, (user_id, model_name), CommandSQL.DELETE)
        return True
    except Exception as e:
        logging.error(f"Ошибка при удалении модели: {e}")
        return False

def get_chats_by_user(user_id: int, chat_type: str = None) -> list[dict]:
    """
    Получает список чатов пользователя с возможной фильтрацией по типу
    """
    query = """
        SELECT chat_id, chat_name, chat_type, created_at
        FROM chats
        WHERE user_id = ?
    """
    params = [user_id]
    
    if chat_type:
        query += " AND chat_type = ?"
        params.append(chat_type)
    
    query += " ORDER BY created_at DESC"
    
    try:
        result = database.execute_sql(query, tuple(params), CommandSQL.SELECT)
        return [
            {
                'chat_id': row[0],
                'chat_type': row[2],
                'chat_name': row[1],
                'created_at': row[3]
            }
            for row in result
        ] if result else []
    except Exception as e:
        logging.error(f"Ошибка при получении чатов: {e}")
        return []