import logging
import random
import modules.constants as constants
from g4f.client import Client
from g4f.Provider import PollinationsAI 

client = Client(
    provider=PollinationsAI,
    api_key=constants.API_KEY
)

def generate_text(prompt: str, model: str) -> str:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error("Ошибка генерации текста: %s", e)
        return "Не удалось получить ответ."


def generate_image(prompt: str, model: str) -> str:
    try:
        response = client.images.generate(
            model=model,
            prompt=prompt,
            seed=random.randint(0, 10 ** 9),
            response_format="url"
        )
        return response.data[0].url
    except Exception as e:
        logging.error("Ошибка генерации изображения: %s", e)
        return "Ошибка генерации изображения."
