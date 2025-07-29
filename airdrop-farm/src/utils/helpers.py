import asyncio
import random
import json
import os
from typing import List, Optional
import aiofiles

async def delay(seconds: float):
    """Асинхронная задержка"""
    await asyncio.sleep(seconds)

def get_random_user_agent(user_agents: List[str]) -> str:
    """Получить случайный User-Agent"""
    return random.choice(user_agents)

def get_random_email() -> str:
    """Генерировать случайный email"""
    return f"user{random.randint(1000, 9999)}@gmail.com"

def get_random_feedback() -> str:
    """Получить случайный отзыв"""
    feedbacks = [
        'Great platform!',
        'Love the features!',
        'Very user-friendly.',
        'Excellent service!',
        'Amazing experience!',
        'Highly recommended!',
        'Outstanding quality!',
        'Perfect interface!'
    ]
    return random.choice(feedbacks)

async def read_file_lines(file_path: str) -> List[str]:
    """Читать файл и возвращать список строк"""
    try:
        if not os.path.exists(file_path):
            return []
        
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            content = await file.read()
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            return lines
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []

async def load_config(config_path: str = "config.json") -> dict:
    """Загрузить конфигурацию из JSON файла"""
    try:
        async with aiofiles.open(config_path, 'r', encoding='utf-8') as file:
            content = await file.read()
            return json.loads(content)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def truncate_token(token: str, length: int = 8) -> str:
    """Обрезать токен для отображения"""
    if len(token) <= length:
        return token
    return f"{token[:length]}..."

def format_number(number) -> str:
    """Форматировать число для отображения"""
    if isinstance(number, (int, float)):
        return f"{number:,}"
    return str(number)