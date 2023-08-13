from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


async def get_client_kb():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("Поменять собеседника🔁")
    keyboard.add(button1)
    return keyboard


async def get_companion_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [InlineKeyboardButton("⬅️", callback_data="prev"),
         InlineKeyboardButton("➡️", callback_data="next")],
        [InlineKeyboardButton("Выбрать", callback_data="select")]
    ])
    return keyboard
