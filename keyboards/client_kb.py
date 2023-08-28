import os
from config import HOST
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


async def get_main_kb(message):
    if str(message.from_user.id) == HOST:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = KeyboardButton("Добавить ключ🗝️")
        button2 = KeyboardButton("Всего ключей🗝️🗝️")
        button3 = KeyboardButton("Поменять собеседника🔁")
        button4 = KeyboardButton("Поменять тип ответов🔁")
        keyboard.add(button1, button2).add(button3, button4)
    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = KeyboardButton("Поменять собеседника🔁")
        button2 = KeyboardButton("Поменять тип ответов🔁")
        keyboard.add(button1, button2)
    return keyboard


async def get_companion_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [InlineKeyboardButton("⬅️", callback_data="prev"),
         InlineKeyboardButton("➡️", callback_data="next")],
        [InlineKeyboardButton("Выбрать", callback_data="select")]
    ])
    return keyboard


async def get_change_answer_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("Текст✍️")
    button2 = KeyboardButton("Голосовые🎙️")
    keyboard.add(button1, button2)
    return keyboard
