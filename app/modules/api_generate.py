import logging

import modules.constants as constants
import modules.functions as functions
import modules.classes as classes
import modules.database.query_api as database
import modules.database.database as db

from fastapi import APIRouter, HTTPException, Header
from typing import Optional

router = APIRouter(
    prefix="/generate",
    tags=["generate"]
)

@router.post("/text", response_model=classes.ResponsePrompt)
def generate_text(
    prompt: classes.Prompt,
    chat_id: Optional[str] = Header(None)
) -> classes.ResponsePrompt:
    if not chat_id:
        raise HTTPException(status_code=400, detail="Требуется chat_id в заголовке")
    
    # Проверяем соответствие типа сообщения типу чата
    if get_type(chat_id) == 'image':
        raise HTTPException(status_code=500, detail=f"Чат {chat_id} поддерживает только изображения")
    
    if prompt.model not in constants.text_models:
        raise HTTPException(status_code=400, detail="Неверная модель")

    try:
        response = functions.generate_text(prompt.used_prompt, prompt.model)
    except Exception as e:
        logging.critical("Ошибка при генерации текста: %s", e)
        raise HTTPException(status_code=500, detail=f"Ошибка при генерации текста: {e}")

    answer = classes.ResponsePrompt(
        used_prompt=prompt.used_prompt,
        response=response
    )

    if len(answer.response.strip()) == 0:
        raise HTTPException(status_code=400, detail="Ответ есть, но кажется он пуст. Видимо модели нужен отдых, выбери пока другую")
    database.create_message(chat_id, answer.used_prompt, answer.response, "text")
    return answer

@router.post("/image", response_model=classes.ResponsePrompt)
def generate_image(
    prompt: classes.Prompt,
    chat_id: Optional[str] = Header(None)
) -> classes.ResponsePrompt:
    if not chat_id:
        raise HTTPException(status_code=400, detail="Требуется chat_id в заголовке")

    # Проверяем соответствие типа сообщения типу чата
    if get_type(chat_id) == 'text':
        raise HTTPException(status_code=500, detail=f"Чат {chat_id} поддерживает только текстовые сообщения")

    if prompt.model not in constants.image_models:
        raise HTTPException(status_code=400, detail="Неверная модель")

    try:
        response = functions.generate_image(prompt.used_prompt, prompt.model)
    except Exception as e:
        logging.critical("Ошибка при генерации изображения: %s", e)
        raise HTTPException(status_code=500, detail=f"Ошибка при генерации изображения: {e}")

    answer = classes.ResponsePrompt(
        used_prompt=prompt.used_prompt,
        response=response
    )

    if len(answer.response.strip()) == 0:
        raise HTTPException(status_code=400, detail="Ответ есть, но кажется он пуст. Видимо модели нужен отдых, выбери пока другую")
    database.create_message(chat_id, answer.used_prompt, answer.response, "image")
    return answer

def get_type(chat_id: str) -> str:
    # Сначала проверяем тип чата
    chat_info = database.database.execute_sql(
        "SELECT chat_type FROM chats WHERE chat_id = ?",
        (chat_id,),
        db.CommandSQL.SELECT
    )
    
    if not chat_info:
        logging.error(f"Чат {chat_id} не найден")
        return False
        
    return chat_info[0][0]