import logging
import random

import g4f
from g4f.client import Client


def translate_to_english(text: str) -> str:
    try:
        translation_prompt = [
            {"role": "system",
             "content": "You are a professional translator. Translate everything into English without any comments or explanations."},
            {"role": "user", "content": text}
        ]
        translation = g4f.ChatCompletion.create(
            model="gpt-4o",
            messages=translation_prompt,
            stream=False
        )
        return translation if isinstance(translation, str) else str(translation)
    except Exception as e:
        logging.error(f"Ошибка перевода: {str(e)}")
        return text


def generate_text(prompt: str, model: str) -> str:
    try:
        response = g4f.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response
    except Exception as e:
        logging.error(f"Ошибка генерации текста: {str(e)}")
        return "Не удалось получить ответ."


def generate_image(prompt: str, model: str) -> str:
    try:
        client = Client()
        response = client.images.generate(
            model=model,
            prompt=prompt,
            seed=random.randint(0, 10 ** 9),
            response_format="url"
        )
        return response.data[0].url
    except Exception as e:
        logging.error(f"Ошибка генерации изображения: {str(e)}")
        return "Ошибка генерации изображения."
