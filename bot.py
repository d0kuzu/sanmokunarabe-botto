import asyncio
import logging
from aiogram import Bot, Dispatcher, types
import handlers
import callbackHandlers
import inlineHandlers

import coloredlogs
import colored_traceback
colored_traceback.add_hook(always=True)
coloredlogs.install()


logging.basicConfig(level=logging.INFO)
level_styles = {
    'debug': {'color': 'blue'},
    'info': {'color': 'green'},
    'warning': {'color': 'yellow'},
    'error': {'color': 'red'},
    'critical': {'color': 'magenta'}
}

field_styles = {
    'asctime': {'color': 'cyan'},
    'name': {'color': 'white'},
    'levelname': {'color': 'yellow', 'bold': True},
    'module': {'color': 'magenta'},
    'message': {'color': 'white'}
}

coloredlogs.install(
    level='INFO',
    fmt='%(asctime)s:%(levelname)s:%(name)s:%(module)s:%(message)s',
    level_styles=level_styles,
    field_styles=field_styles
)
bot = Bot(token="7487870032:AAGqvwbK9xB91cMM9YriPEGHkdHiuW6u9bw")
dp = Dispatcher()

dp.include_routers(handlers.router, callbackHandlers.router, inlineHandlers.router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
