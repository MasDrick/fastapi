import logging
import psycopg2
import enum

from ..constants import USER, PASSWORD, HOST, PORT, DBNAME  
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from typing import Any

class CommandSQL(enum.Enum):
    """Перечисление с типами запросов к БД"""
    CREATE = 1
    INSERT = 2
    DELETE = 3
    SELECT = 4

class Database(object):
    """Класс для работы с БД (только PostgreSQL)"""
    def __init__(self):
        try:
            self.__connection = psycopg2.connect(
                user=USER,
                password=PASSWORD,
                host=HOST,
                port=PORT,
                dbname=DBNAME
            )
            self.__connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        except (Exception, psycopg2.Error) as error:
            logging.critical("Ошибка при создании объекта: %s", error)
            self.__connection = None
            

    def __del__(self):
        if self.__connection:
            self.__connection.close()

    def get_cursor(self):
        return self.__connection.cursor()

    def execute_sql(self, query: str, command: CommandSQL) -> list[tuple[Any, ...]] | None:
        try:
            cursor = self.get_cursor()
            cursor.execute(query)
            match command:
                case CommandSQL.SELECT:
                    record = cursor.fetchall()
                    return record
                case _:
                    return None

            return None
        except (Exception, psycopg2.Error) as error:
            logging.critical("Ошибка при выполнении запроса: %s", error)
        finally:
            if cursor:
                cursor.close()
