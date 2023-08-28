from handlers.client_handlers import register_client_handlers
from handlers.admin_handlers import register_admin_handlers
from callbacks.client_callbacks import register_client_callbacks
from create_bot import dp
from aiogram import executor
from data_base.db_functions import *


async def on_startup(_):
    await start_db()
    print("Бот запущен")

register_admin_handlers(dp)
register_client_handlers(dp)
register_client_callbacks(dp)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)