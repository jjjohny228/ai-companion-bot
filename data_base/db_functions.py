import sqlite3 as sq
from prompts import prompts_dict
import asyncio
from create_bot import bot
from config import start_elevenlabs_keys, start_open_ai_keys
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

companion = dict()
current_companion_index = 0


async def start_db():
    global db, cursor, companion
    db = sq.connect('main_data_base.db')
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS companions "
                   "(id INTEGER PRIMARY KEY AUTOINCREMENT,"
                   "name TEXT, description TEXT, photo TEXT, prompt TEXT, voice TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS open_ai_keys "
                   "(id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS elevenlabs_keys "
                   "(id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT)")
    if cursor.execute("SELECT COUNT(*) FROM companions").fetchone()[0] == 0:
        for prompt in prompts_dict:
            cursor.execute("INSERT INTO companions (name, description, photo, prompt, voice) VALUES(?, ?, ?, ?, ?)",
                           tuple(prompt.values()))

        for key in start_open_ai_keys:
            cursor.execute(f"INSERT INTO open_ai_keys (key) VALUES('{key}')")

        for key in start_elevenlabs_keys:
            cursor.execute(f"INSERT INTO elevenlabs_keys (key) VALUES('{key}')")

    db.commit()
    companions = await show_all_companions()
    current_companion_index = int(os.getenv('CURRENT_COMPANION_INDEX'))
    companion = dict(zip(['name', 'description', 'photo', 'prompt', 'voice'], companions[current_companion_index]))
    # os.environ['OPENAI_API_KEY'] = cursor.execute("SELECT key FROM open_ai_keys ORDER BY id LIMIT 1").fetchone()[0]
    os.environ['ELEVEN_LABS_API_KEY'] = cursor.execute("SELECT key FROM elevenlabs_keys ORDER BY id LIMIT 1").fetchone()[0]


async def add_open_ai_key(key):
    cursor.execute(f"INSERT INTO open_ai_keys (key) VALUES('{key}')")
    db.commit()


async def add_elevenlabs_key(key):
    cursor.execute(f"INSERT INTO elevenlabs_keys (key) VALUES('{key}')")
    db.commit()


async def show_all_keys():
    open_ai_keys = cursor.execute("SELECT COUNT(*) FROM open_ai_keys").fetchone()[0]
    elevenlabs_keys = cursor.execute("SELECT COUNT(*) FROM elevenlabs_keys").fetchone()[0]
    return f"Open ai keys: {open_ai_keys}\nElevenlabs keys: {elevenlabs_keys}"


async def show_all_companions():
    return cursor.execute("SELECT name, description, photo, prompt, voice FROM companions").fetchall()


async def change_companion(new_companion):
    global companion
    companion = new_companion


async def change_current_companion_index(new_index):
    async with asyncio.Lock():
        old_companion_index = int(os.getenv('CURRENT_COMPANION_INDEX'))
        new_companion_index = old_companion_index + new_index
        os.environ['CURRENT_COMPANION_INDEX'] = str(new_companion_index)
    return new_companion_index


async def show_current_companion():
    return companion


async def show_current_companion_index():
    return int(os.getenv('CURRENT_COMPANION_INDEX'))


async def change_open_ai_current_key(chat_id):
    old_open_api_key = os.getenv('OPENAI_API_KEY')
    cursor.execute(f"DELETE FROM open_ai_keys WHERE key = '{old_open_api_key}'")
    db.commit()
    new_open_api_key = cursor.execute("SELECT key FROM open_ai_keys ORDER BY id LIMIT 1").fetchone()[0]
    if new_open_api_key is None:
        await bot.send_message(chat_id=chat_id, text="Ключи Open Ai зкончились. Обратитесь к администратору")
    else:
        os.environ['OPENAI_API_KEY'] = new_open_api_key


async def change_elevenlabs_current_key(chat_id):
    old_elevenlabs_api_key = os.getenv('ELEVEN_LABS_API_KEY')
    cursor.execute(f"DELETE FROM elevenlabs_keys WHERE key = '{old_elevenlabs_api_key}'")
    db.commit()
    new_elevenlabs_api_key = cursor.execute("SELECT key FROM elevenlabs_keys ORDER BY id LIMIT 1").fetchone()[0]
    if new_elevenlabs_api_key is None:
        await bot.send_message(chat_id=chat_id, text="Ключи ElevenLabs зкончились. Обратитесь к администратору")
    else:
        os.environ['ELEVEN_LABS_API_KEY'] = new_elevenlabs_api_key


async def change_answer_type(answer_type):
    os.environ['ANSWER_TYPE'] = answer_type
