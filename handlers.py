from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.filters.command import Command
from test import *
from keyboards import startKeyboard, GenerateKeyBoard, GetGameboard
from random import randint

router = Router()

@router.message(Command("start"))
async def Start(msg: types.Message, state: FSMContext):
    CheckInDB(msg.from_user.username, msg.from_user.id)
    
    data = await state.get_data()
    if data.get('sessionId'):
        await msg.answer(text='Вы уже находитесь в игре', reply_markup=GenerateKeyBoard({'Покинуть игру':'leaveExistRoom'}))
    else:
        await msg.answer("Выберите игру", reply_markup=startKeyboard)

@router.message(Command('join'))
async def Join(msg: types.Message, state: FSMContext):
    text = msg.text.split('/join Комната игрока - @')[-1]
    roomId = JoinRoom(msg.from_user.id, text)
    if roomId == -10:
        await msg.answer("Комната переполнена \nВыберите игру", reply_markup=startKeyboard)
    elif roomId == -1:
        await msg.answer("Произошла ощибка \nしつれい 、かみました! \nВыберите игру", reply_markup=startKeyboard)
    else:
        result = RoomInfo(roomId)
        side = randint(0, 1)
        if result[1] != msg.from_user.id:
            opponentId = result[1]
            opponentMessageId = result[2]
        elif result[3] != msg.from_user.id:
            opponentId = result[3]
            opponentMessageId = result[4]
        matrix, gameboard, invalidGameboard = GetGameboard([[None, None, None], [None, None, None], [None, None, None]])

        storageKey = StorageKey(msg.bot.id, opponentId, opponentId)
        opponentState = FSMContext(storage=state.storage, key=storageKey)
        await state.update_data(matrix=matrix, sessionId=roomId, side=("O" if side==0 else "X"), turn=(True if side==0 else False))
        await opponentState.update_data(matrix=matrix, sessionId=roomId, side=("X" if side==0 else "O"), turn=(False if side==0 else True))

        await msg.bot.edit_message_text(chat_id=opponentId, message_id=opponentMessageId, text=f'Вы {"крестик" if side==0 else "нолик"} \n{"Ваш ход                      ⠀" if side==1 else "Ход второго игрока"}', reply_markup=(gameboard if side == 1 else invalidGameboard))
        lastMessage = await msg.answer(f'Вы {"нолик" if side==0 else "крестик"} \n{"Ваш ход                      ⠀" if side==0 else "Ход второго игрока"}', reply_markup=(gameboard if side == 0 else invalidGameboard))
        StartGame(lastMessage.message_id, roomId)
        
@router.message()
async def echo_message(msg: types.Message):
    await msg.answer("baaaka")
