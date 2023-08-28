import os
from aiogram.types import InputFile
from keyboards.client_kb import get_companion_keyboard
from data_base import db_functions
from aiogram import types, Dispatcher
from create_bot import bot


async def select_callback(callback: types.CallbackQuery):
    all_companions = await db_functions.show_all_companions()
    current_index = int(os.getenv('CURRENT_COMPANION_INDEX'))
    await db_functions.change_companion(dict(zip(['name', 'description', 'photo', 'prompt', 'voice'], all_companions[current_index])))
    print(await db_functions.show_current_companion())
    await bot.answer_callback_query(callback.id, text="Компаньон выбран!")
    await bot.send_message(callback.from_user.id, text='Напишите сообщение или отправьте голосовое')


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


def register_client_callbacks(disp: Dispatcher):
    disp.register_callback_query_handler(select_callback, lambda c: c.data == "select")
    disp.register_callback_query_handler(prev_and_next_callback, lambda c: c.data in ("prev", "next"))