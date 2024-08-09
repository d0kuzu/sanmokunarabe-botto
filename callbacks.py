from aiogram.filters.callback_data import CallbackData

class GameCallback(CallbackData, prefix='game'):
    action:str

class GameboardCallback(CallbackData, prefix='gameboard'):
    action:str
    x:int
    y:int