from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from callbacks import GameCallback, GameboardCallback

def GenerateButton(text, action, btnType='def'):
    if btnType=='def':
        button = InlineKeyboardButton(text=text, callback_data=GameCallback(action=action).pack())
    else:
        button = InlineKeyboardButton(text=text, switch_inline_query_current_chat=action)
    return button

def GenerateKeyBoard(values, listBtns=[]):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[GenerateButton(i, values[i], 'def' if not i in listBtns else 'list')] for i in values])
    return keyboard

def GetGameboard(matrix=[[None, None, None], [None, None, None], [None, None, None]], x=None, y=None, side=None, botGame=False):
    buttons = []
    invalidButtons = []
    for i in range(len(matrix)):
        buttons.append([])
        invalidButtons.append([])
        for j in range(len(matrix[i])):
            if x is not None and i==x and j==y:
                matrix[i][j]=side
            buttons[i].append(InlineKeyboardButton(text=f'{"X" if matrix[i][j]=="X" else "O" if matrix[i][j]=="O" else " "}', callback_data=GameboardCallback(action=('botGame' if botGame and not matrix[i][j] else 'game' if not matrix[i][j] and not botGame else 'nanimo'), x=i, y=j).pack()))
            invalidButtons[i].append(InlineKeyboardButton(text=f'{"X" if matrix[i][j]=="X" else "O" if matrix[i][j]=="O" else " "}', callback_data=GameboardCallback(action='nanimo', x=i, y=j).pack()))
    buttons.append([InlineKeyboardButton(text='Выйти', callback_data=GameCallback(action='waitBot' if side is not None and botGame else 'leaveRoom').pack()), 
                    InlineKeyboardButton(text='Играть снова', callback_data=GameCallback(action='waitBot' if side is not None and botGame else 'playAgain').pack())])
    invalidButtons.append([InlineKeyboardButton(text='Выйти', callback_data=GameCallback(action='waitBot' if side is not None and botGame else 'leaveRoom').pack()), 
                           InlineKeyboardButton(text='Играть снова', callback_data=GameCallback(action='waitBot' if side is not None and botGame else 'playAgain').pack())])
    workingKeyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    invalidGameboard = InlineKeyboardMarkup(inline_keyboard=invalidButtons)
    return (matrix, workingKeyboard, invalidGameboard)

startKeyboard = GenerateKeyBoard({'Бой с ботом':'singleplayer',
                                'Бой с игроком':'multiplayer'})

singleplayerKeyboard = GenerateKeyBoard({'Легкая':'easy',
                                        'Средняя':'mid',
                                        'Сложная':'hard'})

multiplayerKeyboard = GenerateKeyBoard({'Создать комнату':'createRoom',
                                        'Присоеденится к комнате':'joinRoom'}, ['Присоеденится к комнате'])

friendsKeyboard = GenerateKeyBoard({'Добавить друга':'addFriend',
                                    'Список друзей':'friendsList'})


