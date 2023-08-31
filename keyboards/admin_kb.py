from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


async def get_change_keys_kb():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("Open Ai")
    button2 = KeyboardButton("Elevenlabs")
    button3 = KeyboardButton("Назад⬅️")
    keyboard.add(button1, button2).add(button3)
    return keyboard


async def get_keys_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("Добавить ключ🗝️")
    button2 = KeyboardButton("Всего ключей🗝️🗝️")
    button3 = KeyboardButton("Поменять ключ Open Ai🔁")
    button4 = KeyboardButton("Главное меню🏠")
    keyboard.add(button1, button2).add(button3).add(button4)
    return keyboard


async def get_cancel_kb():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("Отмена")
    keyboard.add(button1)
    return keyboard