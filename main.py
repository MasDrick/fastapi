from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import random
import g4f
from g4f.client import Client

app = FastAPI()

# Настройка CORS
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

# Логирование
logging.basicConfig(level=logging.INFO)

# Доступные модели
available_models = ["gpt-4o", "gpt-4o-mini", "deepseek-r1", "deepseek-v3", "evil", "flux", "dall-e-3", "midjourney"]
image_models = ["flux", "dall-e-3", "midjourney"]
text_models = [model for model in available_models if model not in image_models]

# Генерация текста
def generate_text(prompt: str, model: str) -> str:
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
        logging.error(f"Ошибка генерации текста: {str(e)}")
        return "Не удалось получить ответ."

# Генерация изображения
def generate_image(prompt: str, model: str) -> str:
    try:
        client = Client()
        response = client.images.generate(
            model=model,
            prompt=prompt,
            seed=random.randint(0, 10**9),
            response_format="url"
        )
        return response.data[0].url
    except Exception as e:
        logging.error(f"Ошибка генерации изображения: {str(e)}")
        return "Ошибка генерации изображения."

# Эндпоинт генерации контента
@app.post("/generate/")
async def generate(prompt: str, model: str, smart_prompt: bool = False):
    if model not in available_models:
        raise HTTPException(status_code=400, detail="Неверная модель")

    # Если модель текстовая — просто вернуть ответ
    if model in text_models:
        result = generate_text(prompt, model)
        return {"response": result}
    
    # Если модель для изображения
    elif model in image_models:
        # Обработка умного промпта
        if smart_prompt:
            try:
                smart_prompt_text = f"Напиши промпт для миджорни без лишних слов, сразу промпт. {prompt}"
                prompt = generate_text(smart_prompt_text, "gpt-4o")
                logging.info(f"Умный промпт: {prompt}")
            except Exception as e:
                logging.error(f"Ошибка умного промпта: {str(e)}")

        result = generate_image(prompt, model)
        return {"image_url": result}
    
    else:
        raise HTTPException(status_code=400, detail="Ошибка выбора модели")
