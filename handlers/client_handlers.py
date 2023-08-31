import os
import openai
from aiogram.types import InputFile
from langchain import OpenAI, PromptTemplate
from dotenv import load_dotenv
import requests
from create_bot import bot, dp
from aiogram import types, Dispatcher
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from aiogram.dispatcher.filters import Text
from keyboards.client_kb import get_main_kb, get_companion_keyboard, get_change_answer_keyboard
from data_base import db_functions
from aiogram.utils.exceptions import BadRequest
from mutagen.mp3 import MP3, HeaderNotFoundError
from io import BytesIO
load_dotenv()

memory = ConversationBufferMemory()


async def get_response_from_ai(human_input):
    template = f"""
    {db_functions.companion['prompt']}
    {{history}}

    Companion: {{input}}
    {db_functions.companion['name']}:
    """

    prompt = PromptTemplate(input_variables=["history", "input"], template=template)

    chatgpt_chain = ConversationChain(
        llm=OpenAI(temperature=0.2),
        prompt=prompt,
        verbose=True,
        memory=memory
    )
    output = chatgpt_chain.predict(input=human_input)

    return output


async def get_voice_message(message):
    payload = {
        "text": message,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    headers = {
        'accept': 'audio/mpeg',
        'xi-api-key': os.getenv('ELEVEN_LABS_API_KEY'),
        'Content-Type': 'application/json'
    }

    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{db_functions.companion['voice']}?optimize_streaming_latency=0",
        headers=headers, json=payload)
    print(response.status_code)
    if response.status_code == 200 and response.content:
        print("Прошла проверку")

        return response.content


async def start_command(message: types.Message):
    first_name = message.from_user.first_name if message.from_user.first_name is not None else ''
    last_name = message.from_user.last_name if message.from_user.last_name is not None else ''
    await message.answer(f'Добро пожаловать в бот, {first_name} {last_name}\n\nВыберите собеседника:',
                         reply_markup=await get_main_kb(message))
    await change_companion_command(message)


# Обработчик команды Text("Поменять собеседника🔁")
async def change_companion_command(message: types.Message):
    # Отправка текущего компаньона
    name, description, photo, prompt, voice = db_functions.companion.values()
    await bot.send_photo(message.chat.id,
                         InputFile(db_functions.companion['photo']),
                         caption=f"{name}\n{description}",
                         reply_markup=await get_companion_keyboard())


# Обработчик команды Text('Поменять тип ответов🔁'))
async def change_answer(message: types.Message):
    await message.answer("Выберите тип ответов", reply_markup=await get_change_answer_keyboard())


# Обработчик команды Text('Текст✍️'))
async def text_answer_type(message: types.Message):
    current_answer_type = os.getenv('ANSWER_TYPE')
    if current_answer_type == 'text':
        await message.answer("Текстовый тип уже выбран")
    else:
        await db_functions.change_answer_type('text')
        await message.answer("Тип сообщений изменен", reply_markup=await get_main_kb(message))


# Обработчик команды Text('Голосовые🎙️'))
async def voice_answer_type(message: types.Message):
    current_answer_type = os.getenv('ANSWER_TYPE')
    if current_answer_type == 'voice':
        await message.answer("Голосовые уже выбраны")
    else:
        await db_functions.change_answer_type('voice')
        await message.answer("Тип сообщений изменен", reply_markup=await get_main_kb(message))


# Функция для обработки голосовых сообщений
async def voice_command(message: types.Message):
    voice_bytes = await message.voice.download()
    print(voice_bytes.name)
    with open(voice_bytes.name, 'rb') as media_file:
        response = openai.Audio.translate(
            api_key=os.getenv('OPENAI_API_KEY'),
            model='whisper-1',
            file=media_file,
            prompt=''
        )

    await bot_response(message, response['text'])


async def text_command(message: types.Message):
    await bot_response(message, message.text)


async def bot_response(message, text):
    if os.getenv('ANSWER_TYPE') == 'text':
        text_answer = await get_response_from_ai(text)
        await message.answer(text_answer)
    elif os.getenv('ANSWER_TYPE') == 'voice':
        text_answer = await get_response_from_ai(text)
        voice_answer = await get_voice_message(text_answer)
        try:
            audio = MP3(BytesIO(voice_answer))
            duration = int(audio.info.length)
            await bot.send_voice(chat_id=message.from_user.id, voice=voice_answer, duration=duration)
        except (BadRequest, HeaderNotFoundError):
            if voice_answer is None:
                await db_functions.change_elevenlabs_current_key(message.from_user.id)
            await message.answer("Попробуйте еще раз отправить сообщение")


async def clear_chat_history(message: types.Message):
    memory.clear()
    await message.answer("История чата была удалена")


def register_client_handlers(disp: Dispatcher):
    disp.register_message_handler(start_command, commands=['start'])
    disp.register_message_handler(change_companion_command, Text("Поменять собеседника🔁"))
    disp.register_message_handler(change_answer, Text('Поменять тип ответов🔁'))
    disp.register_message_handler(text_answer_type, Text('Текст✍️'))
    disp.register_message_handler(voice_answer_type, Text('Голосовые🎙️'))
    disp.register_message_handler(voice_command, content_types=types.ContentType.VOICE)
    disp.register_message_handler(clear_chat_history, Text("Удалить память компаньена🗑"))

    disp.register_message_handler(text_command)