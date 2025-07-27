import logging
import sqlite3
import enum
import os
from typing import Any

class CommandSQL(enum.Enum):
    """Перечисление с типами запросов к БД"""
    CREATE = 1
    INSERT = 2
    DELETE = 3
    SELECT = 4

class Database(object):
    """Класс для работы с БД (только SQLite3)"""
    def __init__(self):
        try:
            db_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__), 
                '..',  
                '..',
                '..',
                '..',
                'data',  
                'database.db'  
            ))
            print(db_path)
            self.__connection = sqlite3.connect(db_path, check_same_thread=False)
        except (Exception, sqlite3.Error) as error:
            logging.critical("Ошибка при создании объекта: %s", error)
            self.__connection = None
            

    def __del__(self):
        if self.__connection is not None:
            try:
                if self.__connection:
                    self.__connection.close()
            except Exception as e:
                logging.error("Ошибка при закрытии соединения: %s", e)

    def get_cursor(self) -> sqlite3.Cursor:
        if self.__connection is None:
            raise sqlite3.Error("Соединение с базой данных не установлено")
        return self.__connection.cursor()

    def execute_sql(self, query: str, parameters: tuple[Any], command: CommandSQL) -> list[Any] | None:
        cursor = None
        try:
            cursor = self.get_cursor()
            cursor.execute(query, parameters)
            match command:
                case CommandSQL.SELECT:
                    record = cursor.fetchall()
                    return record
                case _:
                    self.__connection.commit()
                    return None
        except (Exception, sqlite3.Error) as error:
            logging.critical("Ошибка при выполнении запроса: %s", error)
        finally:
            if cursor:
                cursor.close()
