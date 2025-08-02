import logging

import modules.constants as constants
import modules.functions as functions
import modules.classes as classes
import modules.database.query_api as database

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
