import os
import openai
from aiogram.types import InputFile
from langchain import OpenAI, PromptTemplate
from dotenv import find_dotenv, load_dotenv
import requests
from openai.error import RateLimitError
from create_bot import bot, dp
from aiogram import types, Dispatcher
from config import HOST
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from aiogram.dispatcher.filters import Text
from keyboards.admin_kb import get_admin_kb
from keyboards.client_kb import get_client_kb, get_companion_keyboard
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


# @dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    first_name = message.from_user.first_name if message.from_user.first_name is not None else ''
    last_name = message.from_user.last_name if message.from_user.last_name is not None else ''
    if message.from_user.id == HOST:
        keyboard = await get_admin_kb()
    else:
        keyboard = await get_client_kb()

    await message.answer(f'Добро пожаловать в бот, {first_name} {last_name}\n\nВыберите собеседника:',
                         reply_markup=keyboard)
    await change_companion_command(message)


async def talk_function(message: types.Message):
    text_answer = await get_response_from_ai(message.text)
    voice_answer = await get_voice_message(text_answer)
    try:
        audio = MP3(BytesIO(voice_answer))
        duration = int(audio.info.length)
        await bot.send_voice(chat_id=message.from_user.id, voice=voice_answer, duration=duration)
    except (BadRequest, HeaderNotFoundError):
        if voice_answer is None:
            await db_functions.change_elevenlabs_current_key(message.from_user.id)
        await message.answer("Попробуйте еще раз отправить сообщение")


# Обработчик команды Text("Поменять собеседника🔁
@dp.message_handler(Text("Поменять собеседника🔁"))
async def change_companion_command(message: types.Message):
    # Отправка текущего компаньона
    name, description, photo, prompt, voice = db_functions.companion.values()
    await bot.send_photo(message.chat.id,
                         InputFile(db_functions.companion['photo']),
                         caption=f"{name}\n{description}",
                         reply_markup=await get_companion_keyboard())


# Обработчик callback_query
@dp.callback_query_handler(lambda c: c.data == "select")
async def select_callback(callback: types.CallbackQuery):
    all_companions = await db_functions.show_all_companions()
    current_index = int(os.getenv('CURRENT_COMPANION_INDEX'))
    await db_functions.change_companion(dict(zip(['name', 'description', 'photo', 'prompt', 'voice'], all_companions[current_index])))
    print(await db_functions.show_current_companion())
    await bot.answer_callback_query(callback.id, text="Компаньон выбран!")


# @dp.callback_query_handler(lambda c: c.data == ("prev", "next"))
async def prev_and_next_callback(callback: types.CallbackQuery):
    all_companions = await db_functions.show_all_companions()
    current_companion_index = int(os.getenv('CURRENT_COMPANION_INDEX'))
    if current_companion_index > 0 and callback.data == "prev":
        new_index = await db_functions.change_current_companion_index(-1)
        await update_companion(callback, new_index, all_companions)
        await callback.answer()

    elif current_companion_index < len(all_companions) - 1 and callback.data == "next":
        new_index = await db_functions.change_current_companion_index(1)
        await update_companion(callback, new_index, all_companions)
        await callback.answer()

    else:
        await callback.answer(text="Больше вариантов нет", show_alert=True)


async def update_companion(callback, new_index, companions):
    # Получаем информацию о текущем компаньоне
    name, description, photo, prompt, voice = companions[new_index]

    # Обновляем фото и описание компаньона в существующем сообщении
    await callback.message.edit_media(types.InputMedia(media=InputFile(photo),
                                                       type="photo",
                                                       caption=f"{name}\n{description}"),
                                      reply_markup=await get_companion_keyboard())


# Функция для обработки голосовых в текст через whisper
async def voice_command(message: types.Message):
    await message.voice.download('voice_message2.ogg')
    with open('voice_message2.ogg', 'rb') as media_file:
        response = openai.Audio.translate(
            api_key=os.getenv('OPENAI_API_KEY'),
            model='whisper-1',
            file=media_file,
            prompt=''
        )
    print(response)

    text_answer = await get_response_from_ai(response['text'])
    voice_answer = await get_voice_message(text_answer)
    try:
        audio = MP3(BytesIO(voice_answer))
        duration = int(audio.info.length)
        await bot.send_voice(chat_id=message.from_user.id, voice=voice_answer, duration=duration)
    except (BadRequest, HeaderNotFoundError):
        if voice_answer is None:
            await db_functions.change_elevenlabs_current_key(message.from_user.id)
        await message.answer("Попробуйте еще раз отправить сообщение")


def register_client_handlers(disp: Dispatcher):
    disp.register_message_handler(start_command, commands=['start'])
    disp.register_message_handler(change_companion_command, Text("Поменять собеседника🔁"))
    disp.register_callback_query_handler(select_callback, lambda c: c.data == "select")
    disp.register_callback_query_handler(prev_and_next_callback, lambda c: c.data in ("prev", "next"))
    # disp.register_callback_query_handler(next_callback, lambda c: c.data == "next")
    disp.register_message_handler(talk_function)
    disp.register_message_handler(voice_command, content_types=types.ContentType.VOICE)