import logging

import modules.constants as constants
import modules.functions as functions
import modules.classes as classes
import modules.database.query_api as database

from fastapi import APIRouter, HTTPException, Header
from typing import Optional

router = APIRouter(
    prefix="/api",
    tags=["api"]
)

@router.get("/")
def read_root():
    return {"message": "Добро пожаловать на бекенд INSUGPT!"}

@router.post("/generate/text", response_model=classes.ResponsePrompt)
def generate_text(
    prompt: classes.Prompt,
    user_id: Optional[str] = Header(None)
) -> classes.ResponsePrompt:
    if not user_id:
        raise HTTPException(status_code=400, detail="Требуется user_id в загаловке")

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
    database.create_row(user_id, answer.used_prompt, answer.response, "text")
    return answer

@router.post("/generate/image", response_model=classes.ResponsePrompt)
def generate_image(
    prompt: classes.Prompt,
    user_id: Optional[str] = Header(None)
) -> classes.ResponsePrompt:
    if not user_id:
        raise HTTPException(status_code=400, detail="Требуется user_id в загаловке")

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
    database.create_row(user_id, answer.used_prompt, answer.response, "image")
    return answer

@router.get("/history_chat", response_model=list[classes.HistoryResponse])
def get_history(
    chat_type: str = "text",
    limit: int = 5,
    offset: int = 0,
    user_id: Optional[str] = Header(None)
) -> list[classes.HistoryResponse]:
    if not user_id:
        raise HTTPException(status_code=400, detail="Требуется user_id в заголовке")

    resp = database.get_prompt_by_user(user_id, chat_type, limit, offset)

    if resp is None or len(resp) == 0:
        raise HTTPException(status_code=400, detail="Здесь пусто.")

    response = []
    for i in resp:
        response.append(classes.HistoryResponse(
            id=i[0],
            user_id=i[1],
            request_type=i[2],
            request_datetime=i[3],
            prompt=i[4],
            response=i[5]
        ))
    return response
