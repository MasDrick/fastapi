from fastapi import APIRouter, HTTPException, Request

import modules.constants as constants
import modules.functions as functions
import modules.classes as classes

router = APIRouter(prefix="/api")


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

    response = functions.generate_text(prompt.used_prompt, prompt.model)
    answer = classes.ResponsePrompt(
        used_prompt=prompt.used_prompt,
        response=response
    )
    return answer

@router.post("/generate/image", response_model=classes.ResponsePrompt)
def generate_image(
        request: Request, # TO DO: auth
        prompt: classes.Prompt
) -> classes.ResponsePrompt:
    if prompt.model not in constants.image_models:
        raise HTTPException(status_code=400, detail="Неверная модель")

    response = functions.generate_image(prompt.used_prompt, prompt.model)
    answer = classes.ResponsePrompt(
        used_prompt=prompt.used_prompt,
        response=response
    )
    return answer

