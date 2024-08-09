from aiogram import Router, F
from aiogram.filters.callback_data import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.inline_query import InlineQuery
from aiogram.types.inline_query_result_article import InlineQueryResultArticle
from aiogram.types.input_text_message_content import InputTextMessageContent
from aiogram.enums.parse_mode import ParseMode
from test import *
from callbacks import GameCallback
from test import RoomsList

router = Router()
    
@router.inline_query(F.query=='joinRoom')
async def JoinRoom(inq: InlineQuery):
    query = inq.query.strip()
    results = []
    rooms = RoomsList(inq.from_user.id)
    if query:
        for room in rooms:
            playerId = room[1] if room[1] else room[3]
            playerChat = await inq.bot.get_chat(playerId)
            playerName = playerChat.username
            results.append(
                    InlineQueryResultArticle(
                        id=str(room[0]),
                        title=f'Комната игрока - {playerName}',
                        input_message_content=InputTextMessageContent(
                            message_text=f'/join Комната игрока - @{playerName}',
                            parse_mode=ParseMode.HTML
                        ),
                        #reply_markup=markup,
                        #thumb_url=photo_url,
                        #description=f""
                    )
                )
    await inq.answer(results=results, cache_time=10)
