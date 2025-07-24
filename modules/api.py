import logging

from fastapi import APIRouter, HTTPException, Request

import modules.constants as constants
import modules.functions as functions
import modules.classes as classes

router = APIRouter(prefix="/api")


@router.get("/")
async def read_root():
    return {"message": "Добро пожаловать на бекенд INSUGPT!"}

@router.post("/generate/text")
async def generate_text(
        request: Request, # TO DO: auth
        prompt: classes.Prompt
):
    if prompt.model not in constants.text_models:
        raise HTTPException(status_code=400, detail="Неверная модель")

    response = functions.generate_text(prompt.used_prompt, prompt.model)
    return {
        "used_prompt": prompt.used_prompt,
        "response": response
    }

@router.post("/generate/image")
async def generate_image(
        request: Request, # TO DO: auth
        prompt: classes.Prompt
):
    pass


@router.post("/generate/")
async def generate(prompt: str, model: str, smart_prompt: bool = False):
    if model not in constants.available_models:
        raise HTTPException(status_code=400, detail="Неверная модель")

    if model in constants.text_models:
        result = functions.generate_text(prompt, model)
        return {"response": result}

    elif model in constants.image_models:
        used_prompt = prompt
        if smart_prompt:
            try:
                translated_topic = functions.translate_to_english(prompt)
                smart_prompt_text = f"Generate a detailed and high-quality MidJourney prompt based on this idea: {translated_topic}. Do not add any explanations or introduction. Only output the prompt."
                prompt = functions.generate_text(smart_prompt_text, "gpt-4o")
                logging.info(f"Умный промпт: {prompt}")
                used_prompt = prompt
            except Exception as e:
                logging.error(f"Ошибка умного промпта: {str(e)}")

        result = functions.generate_image(prompt, model)
        return {
            "image_url": result,
            "used_prompt": used_prompt
        }

    else:
        raise HTTPException(status_code=400, detail="Ошибка выбора модели")
