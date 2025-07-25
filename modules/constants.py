import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

text_models = [
    "gpt-4", "gpt-4o", "gpt-4.1-mini", "gpt-4o-mini",
    "gpt-4.1-nano", "gpt-4.1", "o4-mini",
    "qwen-2.5-coder-32b", "llama-3.3-70b", "llama-4-scout",
    "mistral-small-3.1-24b", "phi-4",
    "deepseek-r1", "deepseek-v3-0324", "deepseek-v3",
    "grok-3-mini", "grok-3-mini-high"
]

image_models = [
    "sdxl-turbo", "gpt-image", "flux-dev", "flux-schnell", "flux-pro", "flux"
]
