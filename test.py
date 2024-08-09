import psycopg2 as pg
from random import choice, randint
from datetime import date, time, datetime
from aiogram.filters.callback_data import CallbackQuery
from aiogram.types import Message
from keyboards import GenerateKeyBoard
from random import randint

try:
    conn = pg.connect(
        host='localhost',
        database='dokuzutesuto',
        port=5432,
        user='Admin',
        password='dokuzu_desu'
    )

except Exception as err:
    print(err)
    
async def ShowError(cb, moveTo, btnText='Попробовать снова'):
    if isinstance(cb, CallbackQuery):
        await cb.message.edit_text(text='Произошла осибка \nしつれい 、かみました!', reply_markup=GenerateKeyBoard({btnText:moveTo}))
    elif isinstance(cb, Message):
        await cb.edit_text(text='Произошла осибка \nしつれい 、かみました!', reply_markup=GenerateKeyBoard({btnText:moveTo}))

def CheckInDB(userName, userId):
    try:
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM users WHERE userid = %s;''', (userId, ))
        if not cursor.fetchone():
            cursor.execute('''INSERT INTO users (username, userid) 
                        VALUES (%s, %s)''', (userName, userId))
            conn.commit()
    except Exception as exp:
        print(exp)
    finally:
        cursor.close()

def CreateRoom(playerId, messageId):
    try:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO playerSessions (firstPlayerId, firstPlayerMessageId) 
                        VALUES (%s, %s)''', (playerId, messageId))
        conn.commit()
        cursor.execute('''SELECT * FROM playersessions WHERE firstPlayerid = %s;''', (playerId, ))
        return cursor.fetchone()[0]
    except Exception as exp:
        print(exp)
        return -1
    finally:
        cursor.close()
        
def LeaveRoom(playerId, sessionId):
    try:
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM playersessions WHERE id = %s;''', (str(sessionId), ))
        result = cursor.fetchone()
        ids = [result[1], result[3]]
        if all(ids):
            if ids[0] == playerId:
                cursor.execute('''UPDATE playersessions SET firstplayerid = %s, firstplayermessageid = %s WHERE id = %s;''', (None, None, str(sessionId)))
            elif ids[1] == playerId:
                cursor.execute('''UPDATE playersessions SET secondplayerid = %s, secondplayermessageid = %s WHERE id = %s;''', (None, None, str(sessionId)))
        else:
            cursor.execute('''DELETE FROM playersessions WHERE id = %s''', (str(sessionId), ))
        conn.commit()
        return (result[2], result[3], result[4]) if ids[0] == playerId else (result[4], result[1], result[2]) if ids[1] == playerId else -1
    except Exception as exp:
        print(exp)
        return -1
    finally:
        cursor.close()

def RoomsList(userId):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM playersessions WHERE firstplayerid is null or secondplayerid is null;')
        result = cursor.fetchall()
        result = filter(lambda x: x[1]!=userId and x[3]!=userId, result)
        return result
    except Exception as exp:
        print(exp)
        return []
    finally:
        cursor.close()
        
def JoinRoom(userId, hostUsername):
    try:
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM users WHERE username = %s;''', (hostUsername, ))
        hostUserId = cursor.fetchone()[2]
        cursor.execute('''SELECT * FROM playersessions WHERE (firstplayerid = %s and secondplayerid is null) or (secondplayerid = %s and firstplayerid is null);''', (hostUserId, hostUserId))
        result = cursor.fetchone()
        if not result[1]:
            cursor.execute('''UPDATE playersessions SET firstplayerid = %s WHERE id = %s;''', (userId, result[0]))
        elif not result[3]:
            cursor.execute('''UPDATE playersessions SET secondplayerid = %s WHERE id = %s;''', (userId, result[0]))
        else:
            return -10
        conn.commit()
        return result[0]
    except Exception as exp:
        print(exp)
        return -1
    finally:
        cursor.close()

def StartGame(messageId, sessionId):
    try:
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM playersessions WHERE id = %s;''', (sessionId, ))
        result = cursor.fetchone()
        if not result[2]:
            cursor.execute('''UPDATE playersessions SET firstplayermessageid = %s WHERE id = %s;''', (messageId, sessionId))
        elif not result[4]:
            cursor.execute('''UPDATE playersessions SET secondplayermessageid = %s WHERE id = %s;''', (messageId, sessionId))
        else:
            return -10
        conn.commit()
        return result[0]
    except Exception as exp:
        print(exp)
        return -1
    finally:
        cursor.close()
        
def RoomInfo(sessionId):
    try:
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM playersessions WHERE id = %s;''', (sessionId, ))
        return cursor.fetchone()
    except Exception as exp:
        print(exp)
        return -1
    finally:
        cursor.close()

def EndGame(matrix):
    x = []
    o = []
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if matrix[i][j]=='X':
                x.append(f'{i}{j}')
            elif matrix[i][j]=='O':
                o.append(f'{i}{j}')
    
    if len(list(filter(lambda a: int(a[0])+int(a[1])==2, x)))==3 or \
        len(list(filter(lambda a: a[0]==a[1], x)))==3:
        return 'X'
    if len(list(filter(lambda a: int(a[0])+int(a[1])==2, o)))==3 or \
        len(list(filter(lambda a: a[0]==a[1], o)))==3:
        return 'O'
    
    def AllEqual(list):
        for i in range(len(list)):
            for j in range(len(list)):
                if list[i]!=list[j]:
                    break
            else:
                continue
            break
        else:
            return True
        return False

    for i in range(len(matrix)):
        asd = []
        for j in range(len(matrix)):
            asd.append(matrix[j][i])
        if not None in asd and AllEqual(asd):
            return asd[0]

    for i in matrix:
        if not None in i and AllEqual(i):
            return i[0]

    return -1

#############################################Bot AI

def draw(board):
    for i in range(3):
        for j in range(3):
            if(board[i][j]==None):
                return 0
    return 1

def BotGame(board, dif):
    def comp_play(board):
        worst=100
        x=0
        y=0
        for i in range(3):
            for j in range(3):
                if board[i][j]==None:
                    board[i][j]='X'
                    score=minimax(board,0,True)
                    board[i][j]=None
                    if score < worst :
                        worst=score
                        x,y=i,j
        board[x][y]='X'
        return board

    def minimax(board,depth,isMaximizing):
        z=EndGame(board)
        if z=='O' :
            return 1
        if z=='X' :
            return -1
        if draw(board) :
            return 0
        
        if isMaximizing :
            best= -100
            for i in range(3):
                for j in range(3):
                    if board[i][j]==None:
                        board[i][j]='O'
                        score=minimax(board,depth+1,False)
                        board[i][j]=None
                        if score>best :
                            best=score
            return best
        if not isMaximizing :
            worst=100
            for i in range(3):
                for j in range(3):
                    if board[i][j]==None:
                        board[i][j]= 'X'
                        score=minimax(board,depth+1,True)
                        board[i][j]=None
                        if score<worst :
                            worst=score
            return worst
        
    def RandomTurn(board):
        num = []
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] == None:
                    num.append([i, j])
        asd = num[randint(0, len(num)-1)]
        board[asd[0]][asd[1]] = 'X'
        return board

    if dif == 'hard':
        return comp_play(board)
    elif dif == 'mid':
        if randint(0, 100) > 70:
            return RandomTurn(board)
        else:
            return comp_play(board)
    else:
        if randint(0, 100) > 50:
            return RandomTurn(board)
        else:
            return comp_play(board)











        

        
        
        
        
