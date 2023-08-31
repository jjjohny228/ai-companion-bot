from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from keyboards.admin_kb import *
from data_base.db_functions import add_open_ai_key, add_elevenlabs_key, show_all_keys, change_open_ai_current_key
from keyboards.client_kb import get_main_kb


class OpenAiStatesGroup(StatesGroup):
    key = State()


class ElevenlabsStatesGroup(StatesGroup):
    key = State()


async def cancel_command(message: types.Message, state: FSMContext):
    if state is None:
        await message.answer("Успешная отмена", reply_markup=await get_change_keys_kb())
        return
    await state.finish()
    await message.answer("Успешная отмена", reply_markup=await get_change_keys_kb())


async def add_key_oa(message: types.Message):
    await message.answer("Вставте новый ключ Open Ai", reply_markup=await get_cancel_kb())
    await OpenAiStatesGroup.key.set()


async def not_right_openai_key(message: types.Message):
    await message.answer("Вы ввели неправильный ключ. Попробуйте еще раз")


async def key_adding(message: types.Message, state: FSMContext):
    await add_open_ai_key(message.text)
    await message.answer("Ключ был успешно добавлен", reply_markup=await get_main_kb(message))
    await state.finish()


async def add_key_el(message: types.Message):
    await message.answer("Вставте новый ключ Elevenlabs", reply_markup=await get_cancel_kb())
    await ElevenlabsStatesGroup.key.set()


async def not_right_elevenlabs_key(message: types.Message):
    await message.answer("Вы ввели неправильный ключ. Попробуйте еще раз")


async def elevenlabs_key_adding(message: types.Message, state: FSMContext):
    await add_elevenlabs_key(message.text)
    await message.answer("Ключ был успешно добавлен", reply_markup=await get_main_kb(message))
    await state.finish()


async def add_keys(message: types.Message):
    await message.answer("Выберите тип ключа:", reply_markup=await get_change_keys_kb())


async def show_keys(message: types.Message):
    await message.answer(await show_all_keys())


async def home_command(message: types.Message):
        await message.answer('🏠', reply_markup=await get_main_kb(message))


async def change_open_ai_key_command(message: types.Message):
    await change_open_ai_current_key(message.from_user.id)
    await message.answer("Ключ был изменен")


async def clear_chat_history(memory):
    memory.clear()


async def keys_menu_command(message: types.Message):
    await message.answer('🗝️', reply_markup=await get_keys_menu())


async def back_command(message: types.Message):
    await keys_menu_command(message)


def register_admin_handlers(disp: Dispatcher):
    disp.register_message_handler(cancel_command, Text("Отмена"), state='*')
    disp.register_message_handler(add_key_oa, Text("Open Ai"))
    disp.register_message_handler(not_right_openai_key,
                                  lambda c: not c.text.startswith('sk') and len(c.text) != 51,
                                  state=OpenAiStatesGroup.key)
    disp.register_message_handler(key_adding, state=OpenAiStatesGroup.key)
    disp.register_message_handler(add_key_el, Text("Elevenlabs"))
    disp.register_message_handler(not_right_elevenlabs_key,
                                  lambda c: len(c.text) != 32, state=ElevenlabsStatesGroup.key)
    disp.register_message_handler(elevenlabs_key_adding, state=ElevenlabsStatesGroup.key)
    disp.register_message_handler(add_keys, Text("Добавить ключ🗝️"))
    disp.register_message_handler(show_keys, Text("Всего ключей🗝️🗝️"))
    disp.register_message_handler(home_command, Text("Главное меню🏠"))
    disp.register_message_handler(change_open_ai_key_command, Text("Поменять ключ Open Ai🔁"))
    disp.register_message_handler(keys_menu_command, Text("Ключи🗝️"))
    disp.register_message_handler(back_command, Text("Назад⬅️"))