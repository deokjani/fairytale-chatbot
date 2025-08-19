import random
import string
import aioredis
from src.v3.params import REDIS_URL
import json

async def init_redis():
    return await aioredis.from_url(REDIS_URL)

async def generate_session_id(length=8):
    characters = string.ascii_lowercase + string.digits  # 대문자와 숫자
    return ''.join(random.choice(characters) for _ in range(length))

async def create_unique_session_id(length=8, ttl=3600) -> str:
    while True:
        store = await init_redis()
        session_id = await generate_session_id(length)
        if not await store.exists(session_id):  # 중복 확인
            await store.setex(session_id, ttl, '')
            return session_id

def get_characters(book_id):
    roles = []

    try:
        with open(f'ebook/{book_id}/common/data/ebook_character.json', 'r', encoding='utf-8') as file:
            character_info = json.load(file)
            return list(character_info.keys())
    except:
        print("-------------------Something is happend where get_character_-------------------")
        return []

def get_character_description(book_id, character):
    try:
        with open(f'ebook/{book_id}/common/data/ebook_character.json', 'r', encoding='utf-8') as file:
            character_info = json.load(file)
        
        return character_info[character]
    except:
        print("-------------------Something is happend where get_character_description-------------------")
        return ""


with open("data/ebook_list.txt", "r", encoding="utf-8") as file:
    ebook_lists = [line.strip() for line in file]
