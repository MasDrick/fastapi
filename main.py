from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
import g4f
from g4f.client import Client
import random
import logging
import re
from io import BytesIO
from docx import Document
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://gpt-front-ashy.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)

available_models = ["gpt-4o", "gpt-4o-mini", "deepseek-r1", "deepseek-v3", "evil", "flux", "dall-e-3", "midjourney"]
image_models = ["flux", "dall-e-3", "midjourney"]
text_models = [model for model in available_models if model not in image_models]
user_models = {}


def ask_gpt(prompt: str, model: str) -> str:
    system_message = {"role": "system", "content": "Пожалуйста, отвечай на русском языке, грамотно."}
    try:
        response = g4f.ChatCompletion.create(
            model=model,
            messages=[system_message, {"role": "user", "content": prompt}],
            stream=False,
        )
        
        if isinstance(response, str):
            return response
        elif isinstance(response, list):
            return " ".join([msg.get("content", "") for msg in response if isinstance(msg, dict)])
        return str(response)
    except Exception as e:
        logging.error(f"Ошибка при использовании GPT: {str(e)}")
        return "Не удалось получить ответ от GPT."


def gen_img(prompt: str, model: str) -> str:
    try:
        client = Client()
        response = client.images.generate(
            model=model,
            prompt=prompt,
            seed=random.randint(0, 10**9),
            response_format="url"
        )
        image_url = response.data[0].url
        logging.info(f"Изображение сгенерировано: {image_url}")
        return image_url
    except Exception as e:
        logging.error(f"Ошибка генерации изображения: {str(e)}")
        return f"Ошибка при генерации: {str(e)}"


@app.post("/generate/")
async def generate(url: str, method: str, prompt: str, model: str, user_id: str):
    user_models[user_id] = model  # Запоминаем модель для пользователя
    
    if method.lower() == "text":
        if model not in text_models:
            raise HTTPException(status_code=400, detail="Выбрана неверная модель для генерации текста.")
        response = ask_gpt(prompt, model)
        return {"url": url, "method": method, "response": response, "model": model, "user_id": user_id}
    
    elif method.lower() == "image":
        if model not in image_models:
            raise HTTPException(status_code=400, detail="Выбрана неверная модель для генерации изображений.")
        image_url = gen_img(prompt, model)
        return {"url": url, "method": method, "image_url": image_url, "model": model, "user_id": user_id}
    
    else:
        raise HTTPException(status_code=400, detail="Некорректный метод запроса.")


@app.post("/set_model/")
async def set_model(user_id: str, model: str):
    if model not in available_models:
        raise HTTPException(status_code=400, detail="Недопустимая модель")
    user_models[user_id] = model
    return {"status": "success", "message": f"Модель {model} установлена!"}


@app.get("/")
async def root():
    return {"message": "Добро пожаловать в GPT Backend!"}
