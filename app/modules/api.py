from fastapi import APIRouter, HTTPException, Request
import logging
import modules.constants as constants
import modules.functions as functions
import modules.classes as classes

router = APIRouter(
    prefix="/api",
    tags=["api"]
)

@router.get("/")
def read_root():
    return {"message": "Добро пожаловать на бекенд INSUGPT!"}

@router.post("/generate/text", response_model=classes.ResponsePrompt)
def generate_text(
        request: Request, # TO DO: auth
        prompt: classes.Prompt
) -> classes.ResponsePrompt:
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
    return answer

@router.post("/generate/image", response_model=classes.ResponsePrompt)
def generate_image(
        request: Request, # TO DO: auth
        prompt: classes.Prompt
) -> classes.ResponsePrompt:
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
    return answer