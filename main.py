from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
import g4f
from g4f.client import Client
import random
import logging
import re
from io import BytesIO
from docx import Document
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware



# Инициализация FastAPI
app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",

]

app.add_middleware(  
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Доступные модели
available_models = ["gpt-4o", "gpt-4o-mini", "deepseek-r1", "deepseek-v3", "evil", "flux", "dall-e-3", "midjourney"]
image_models = ["flux", "dall-e-3", "midjourney"]
text_models = [model for model in available_models if model not in image_models]

# Хранение выбранных моделей для пользователей
user_models = {}

# Функция для генерации текста
def ask_gpt(prompt: str, user_id: str) -> str:
    system_message = {"role": "system", "content": "Пожалуйста, отвечай на русском языке, грамотно."}
    model = user_models.get(user_id, "gpt-4o")  # Используем модель по умолчанию, если нет выбора
    
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

# Функция для генерации изображений
def gen_img(prompt: str, user_id: str) -> str:
    try:
        client = Client()
        response = client.images.generate(
            model=user_models.get(user_id),
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

# Форматирование ответов
def format_answer(answer: str) -> str:
    formatted_answer = answer
    formatted_answer = re.sub(r'```.*?\n', r'```', formatted_answer, flags=re.DOTALL)  # Удаляем информацию о языке
    formatted_answer = re.sub(r'```(.*?)```', r'\1', formatted_answer, flags=re.DOTALL)
    formatted_answer = re.sub(r'#+\s*(.*)', r'\1', formatted_answer)  # Преобразуем заголовки
    formatted_answer = re.sub(r'\*\*(.*?)\*\*', r'\1', formatted_answer)  # Преобразуем жирный текст
    formatted_answer = re.sub(r'`(.*?)`', r'\1', formatted_answer)  # Преобразуем курсив
    return formatted_answer

# Эндпоинт для генерации текста
@app.post("/generate_text/")
async def generate_text(prompt: str, user_id: str):
    model = user_models.get(user_id, "gpt-4o-mini")
    if model in image_models:
        raise HTTPException(status_code=400, detail="Выбрана модель для генерации изображений. Пожалуйста, выберите текстовую модель.")
    
    response = ask_gpt(prompt, user_id)
    formatted_response = format_answer(response)
    return {"response": formatted_response}

# Эндпоинт для генерации изображений
@app.post("/generate_image/")
async def generate_image(prompt: str, user_id: str):
    model = user_models.get(user_id)
    if model not in image_models:
        raise HTTPException(status_code=400, detail="Выбрана текстовая модель. Пожалуйста, выберите модель для генерации изображений.")
    
    image_url = gen_img(prompt, user_id)
    return {"image_url": image_url}

# Эндпоинт для установки модели
@app.post("/set_model/")
async def set_model(user_id: str, model: str):
    if model not in available_models:
        raise HTTPException(status_code=400, detail="Недопустимая модель")
    
    user_models[user_id] = model
    return {"status": "success", "message": f"Модель {model} установлена!"}

# Эндпоинт для обработки документов
@app.post("/process_document/")
async def process_document(file: UploadFile = File(...), user_query: str = "", user_id: str = ""):
    content = await file.read()
    doc_text = ""
    
    if file.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        doc = Document(BytesIO(content))
        doc_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    elif file.content_type == 'text/plain':
        doc_text = content.decode('utf-8')
    else:
        raise HTTPException(status_code=400, detail="Поддерживаются только .docx и .txt файлы")
    
    combined_text = f"{user_query}\n\n{doc_text}" if user_query else doc_text
    response = ask_gpt(combined_text, user_id)
    formatted_response = format_answer(response)
    return {"response": formatted_response}

# Корневой эндпоинт
@app.get("/")
async def root():
    return {"message": "Добро пожаловать в GPT Backend!"}

# Эндпоинт для документации
@app.get("/docs")
async def docs():
    return JSONResponse(content={"message": "Документация доступна по адресу /openapi.json yea"}) 

