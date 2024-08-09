from aiogram import Router, F
import logging
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.filters.callback_data import CallbackQuery
from test import *
from keyboards import startKeyboard, singleplayerKeyboard, multiplayerKeyboard, friendsKeyboard, GenerateKeyBoard, GetGameboard
from callbacks import GameCallback, GameboardCallback
from random import randint

router = Router()

##################################### menu    
@router.callback_query(GameCallback.filter(F.action=='singleplayer'))
async def Singleplayer(cb: CallbackQuery, callback_data: GameCallback):
    await cb.message.edit_text(text='Выберите действие', reply_markup=singleplayerKeyboard)
    

@router.callback_query(GameCallback.filter(F.action=='multiplayer'))
async def Multiplayer(cb: CallbackQuery, callback_data: GameCallback):
    await cb.message.edit_text(text='Выберите действие', reply_markup=multiplayerKeyboard)
    

@router.callback_query(GameCallback.filter(F.action=='friends'))
async def Friends(cb: CallbackQuery, callback_data: GameCallback):
    await cb.message.edit_text(text='Выберите действие', reply_markup=friendsKeyboard)

###################################### multiplayer
@router.callback_query(GameCallback.filter(F.action=='createRoom'))
async def CreateRoomHandler(cb: CallbackQuery, callback_data: GameCallback, state: FSMContext):
    sessionId = CreateRoom(cb.from_user.id, cb.message.message_id)
    if not sessionId:
        await ShowError(cb, 'createRoom')
    else:
        await state.update_data(sessionId=sessionId)
        await cb.message.edit_text(text='Ожидание опонента', reply_markup=GenerateKeyBoard({'Покинуть комнату':'leaveRoom'}))
        

@router.callback_query(GameCallback.filter(F.action=='leaveRoom'))
async def LeaveRoomHandler(cb: CallbackQuery, callback_data: GameCallback, state: FSMContext):
    data = await state.get_data()
    if data['sessionId']!='botGame':
        msgId, opponentId, opponentMessageId = LeaveRoom(cb.from_user.id, data['sessionId'])
        print(msgId, opponentId, opponentMessageId)
        if msgId:
            await cb.message.edit_text(text='Выберите игру', reply_markup=startKeyboard)

            await state.clear()
        if opponentId:
            await cb.bot.edit_message_text(chat_id=opponentId, message_id=opponentMessageId, text='Вас покинули, поиск оппонента', reply_markup=GenerateKeyBoard({'Покинуть комнату':'leaveRoom'}))
        if msgId is None:
            await ShowError(cb, 'leaveRoom')
    else:
        await cb.message.edit_text(text='Выберите игру', reply_markup=startKeyboard)
        await state.clear()



@router.callback_query(GameCallback.filter(F.action=='leaveExistRoom'))
async def LeaveExistRoom(cb: CallbackQuery, callback_data: GameCallback, state: FSMContext):
    data = await state.get_data()
    if data['sessionId']!='botGame':
        msgId, opponentId, opponentMessageId = LeaveRoom(cb.from_user.id, data['sessionId'])
        if msgId:
            await cb.bot.delete_message(cb.from_user.id, msgId)

            await state.clear()

            await cb.message.esit_text(text='Выберите игру', reply_markup=startKeyboard)
            
            if opponentId:
                await cb.bot.edit_message_text(chat_id=opponentId, message_id=opponentMessageId, text='Вас покинули, поиск оппонента', reply_markup=GenerateKeyBoard({'Покинуть комнату':'leaveRoom'}))
        else:
            await ShowError(cb, 'leaveExistRoom')
    else:
        await cb.bot.delete_message(cb.from_user.id, data['msgId'])
        await cb.message.edit_text(text='Выберите игру', reply_markup=startKeyboard)
        await state.clear()
            

@router.callback_query(GameboardCallback.filter(F.action=='game'))
async def GameHandler(cb: CallbackQuery, callback_data: GameboardCallback, state: FSMContext):
    data = await state.get_data()
    matrix, gameboard, invalidGameboard = GetGameboard(data['matrix'], callback_data.x, callback_data.y, data['side'])
    result = RoomInfo(data['sessionId'])
    if result[1] != cb.from_user.id:
        opponentId = result[1]
        opponentMessageId = result[2]
    elif result[3] != cb.from_user.id:
        opponentId = result[3]
        opponentMessageId = result[4]

    text = f'Вы {"крестик" if data["side"]=="O" else "нолик"} \n{"Ваш ход                      ⠀" if data["turn"] else "Ход второго игрока"}'
    await cb.bot.edit_message_text(chat_id=opponentId, message_id=opponentMessageId, text=text, reply_markup=(gameboard if data['turn'] else invalidGameboard))
    text = f'Вы {"нолик" if data["side"]=="O" else "крестик"} \n{"Ваш ход                      ⠀" if not data["turn"] else "Ход второго игрока"}'
    await cb.message.edit_text(text=text, reply_markup=(gameboard if not data['turn'] else invalidGameboard))
    

    storageKey = StorageKey(cb.bot.id, opponentId, opponentId)
    opponentState = FSMContext(storage=state.storage, key=storageKey)
    await state.update_data(matrix=matrix, turn=not data['turn'])
    await opponentState.update_data(matrix=matrix, turn=data['turn'])

    for i in matrix:
        if None in i:
            result = EndGame(matrix)
            if result != -1:
                await cb.message.edit_text(text='Вы победили' if data["side"]==result else 'Вы проиграли', reply_markup=invalidGameboard)
                await cb.bot.edit_message_text(chat_id=opponentId, message_id=opponentMessageId, text='Вы проиграли' if data["side"]==result else 'Вы победили', reply_markup=invalidGameboard)
            break
    else:
        result = EndGame(matrix)
        if result == -1:
            text = 'Ничья'
            await cb.bot.edit_message_text(chat_id=opponentId, message_id=opponentMessageId, text=text, reply_markup=invalidGameboard)
            await cb.message.edit_text(text=text, reply_markup=invalidGameboard)
        else:
            await cb.message.edit_text(text='Вы победили' if data["side"]==result else 'Вы проиграли', reply_markup=invalidGameboard)
            await cb.bot.edit_message_text(chat_id=opponentId, message_id=opponentMessageId, text='Вы проиграли' if data["side"]==result else 'Вы победили', reply_markup=invalidGameboard)
        

@router.callback_query(GameCallback.filter(F.action=='playAgain'))
async def PlayAgainHandler(cb: CallbackQuery, callback_data: GameCallback, state: FSMContext):
    data = await state.get_data()
    if data['sessionId']!='botGame':    
        matrix, gameboard, invalidGameboard = GetGameboard([[None, None, None], [None, None, None], [None, None, None]])
        result = RoomInfo(data['sessionId'])
        side = randint(0, 1)
        if result[1] != cb.from_user.id:
            opponentId = result[1]
            opponentMessageId = result[2]
        elif result[3] != cb.from_user.id:
            opponentId = result[3]
            opponentMessageId = result[4]

        storageKey = StorageKey(cb.bot.id, opponentId, opponentId)
        opponentState = FSMContext(storage=state.storage, key=storageKey)
        await state.update_data(matrix=matrix, side=("O" if side==0 else "X"), turn=(True if side==0 else False))
        await opponentState.update_data(matrix=matrix, side=("X" if side==0 else "O"), turn=(False if side==0 else True))

        await cb.bot.edit_message_text(chat_id=opponentId, message_id=opponentMessageId, text=f'Вы {"крестик" if side==0 else "нолик"} \n{"Ваш ход                      ⠀" if side==1 else "Ход второго игрока"}', reply_markup=(gameboard if side == 1 else invalidGameboard))
        await cb.message.edit_text(f'Вы {"нолик" if side==0 else "крестик"} \n{"Ваш ход                      ⠀" if side==0 else "Ход второго игрока"}', reply_markup=(gameboard if side == 0 else invalidGameboard))
    else:
        await StartHardGame(cb, callback_data, state)


###################################### singleplayer
@router.callback_query(GameCallback.filter(F.action=='hard'))
async def StartHardGame(cb: CallbackQuery, callback_data: GameCallback, state: FSMContext):
    matrix, gameboard, invalidGameboard = GetGameboard([[None, None, None], [None, None, None], [None, None, None]], botGame=True)
    
    await state.update_data(matrix=matrix, sessionId='botGame', dif='hard', side="O", msgId=cb.message.message_id)
    await cb.message.edit_text(f'Вы нолик \nВаш ход', reply_markup=gameboard)


@router.callback_query(GameCallback.filter(F.action=='mid'))
async def StartHardGame(cb: CallbackQuery, callback_data: GameCallback, state: FSMContext):
    matrix, gameboard, invalidGameboard = GetGameboard([[None, None, None], [None, None, None], [None, None, None]], botGame=True)
    
    await state.update_data(matrix=matrix, sessionId='botGame', dif='mid', side="O", msgId=cb.message.message_id)
    await cb.message.edit_text(f'Вы нолик \nВаш ход', reply_markup=gameboard)


@router.callback_query(GameCallback.filter(F.action=='easy'))
async def StartHardGame(cb: CallbackQuery, callback_data: GameCallback, state: FSMContext):
    matrix, gameboard, invalidGameboard = GetGameboard([[None, None, None], [None, None, None], [None, None, None]], botGame=True)
    
    await state.update_data(matrix=matrix, sessionId='botGame', dif='easy', side="O", msgId=cb.message.message_id)
    await cb.message.edit_text(f'Вы нолик \nВаш ход', reply_markup=gameboard)


@router.callback_query(GameboardCallback.filter(F.action=='botGame'))
async def BotGameHandler(cb: CallbackQuery, callback_data: GameboardCallback, state: FSMContext):
    data = await state.get_data()
    matrix, gameboard, invalidGameboard = GetGameboard(data['matrix'], callback_data.x, callback_data.y, data['side'], botGame=True)
    print('player')
    print(matrix)
    await cb.message.edit_text(f'Вы нолик \nХод бота', reply_markup=invalidGameboard)
    await state.update_data(matrix=matrix)

    result = EndGame(matrix)
    from aiogram.types import InlineKeyboardButton
    invalidGameboard.inline_keyboard[-1] = [InlineKeyboardButton(text='Выйти', callback_data=GameCallback(action='leaveRoom').pack()), 
                        InlineKeyboardButton(text='Играть снова', callback_data=GameCallback(action='playAgain').pack())]
    if result != -1:
        await cb.message.edit_text(text='Вы победили' if data['side']==result else 'Вы проиграли', reply_markup=invalidGameboard)
    elif draw(matrix):
        await cb.message.edit_text(text='Ничья', reply_markup=invalidGameboard)
    else:
        botMatrix = BotGame(matrix, data['dif'])
        matrix, gameboard, invalidGameboard = GetGameboard(botMatrix, botGame=True)
        print(botMatrix)

        await cb.message.edit_text(f'Вы нолик \nВаш ход', reply_markup=gameboard)
        await state.update_data(matrix=matrix)

        result = EndGame(matrix)
        if result != -1:
            await cb.message.edit_text(text='Вы победили' if data['side']==result else 'Вы проиграли', reply_markup=invalidGameboard)
        elif draw(matrix):
            await cb.message.edit_text(text='Ничья', reply_markup=invalidGameboard)

    

###################################### tadanonanimo

@router.callback_query(GameboardCallback.filter(F.action=='nanimo'))
async def SkipHandler(cb: CallbackQuery, callback_data: GameboardCallback, state: FSMContext):
    await cb.answer('')

@router.callback_query(GameCallback.filter(F.action=='waitBot'))
async def SkipHandler(cb: CallbackQuery, callback_data: GameCallback, state: FSMContext):
    await cb.answer('Дождитесь хода бота')
    
    
    
    
    
    