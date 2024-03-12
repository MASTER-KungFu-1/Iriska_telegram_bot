import aiomysql
import asyncio
import config
from langs import langs_manager as lm
from datetime import datetime, timedelta
from handlers.math_game import get_math, mathstop
from methods import declension
import json



async def connect():
    global pool
    loop = asyncio.get_event_loop()
    pool = await aiomysql.create_pool(
        host=config.bd['host'], 
        port=3306,user=config.bd['user'],
        password=config.bd['password'],
        db=config.bd['database'],
        loop=loop)


class Chat:
    def __init__(self, chat_id):
        self.chat_id = chat_id
    async def load(self):
        sql = f'SELECT * FROM chats WHERE chat_id = {self.chat_id}'
        async with pool.acquire() as con:
            async with con.cursor() as cur:
                await cur.execute(sql)
                curresult = await cur.fetchall()
        for chat in curresult:
            result = chat
            self.iscreate = True
            self.mathdisable = json.loads(result[5])
            
            break
        else:
            result = config.default_chat(self.chat_id)
            self.iscreate = False
            self.mathdisable = result[5]
        self.mathon = result[2]
        self.max_messages = result[3]
        self.autodelete_on = result[6]
        self.autodelete_minutes = result[7]
        
        
    async def save(self):
        if self.iscreate:
            sql = f'''UPDATE chats SET
            mathon = {self.mathon},
            max_messages = {self.max_messages},
            mathdisable = %s,
            autodelete_on = {self.autodelete_on},
            autodelete_minutes = {self.autodelete_minutes}
            WHERE chat_id = {self.chat_id}
            '''
        else:
            sql = f'INSERT INTO chats (chat_id, mathon, max_messages, mathdisable, autodelete_on, autodelete_minutes) VALUES({self.chat_id}, {self.mathon}, {self.max_messages}, %s,{self.autodelete_on}, {self.autodelete_minutes})'
        data = (json.dumps(self.mathdisable),)
        async with pool.acquire() as con:
            async with con.cursor() as cur:
                await cur.execute(sql,data)
                await con.commit()
    async def win(self,user_id,chat_id,math_txt,answer,solution_time):
        sql = f"INSERT INTO maths (user_id,chat_id,math,answer,solution_time) VALUES({user_id}, {chat_id}, %s, %s, {solution_time})"
        async with pool.acquire() as con:
            async with con.cursor() as cur:
                await cur.execute(sql,(math_txt,answer,))
                if not self.iscreate:
                    await cur.execute(f'INSERT INTO chats (chat_id) VALUES({chat_id})')
                await con.commit()

async def ban_list():
    async with pool.acquire() as con:
        async with con.cursor() as cur:
            await cur.execute(f'SELECT user_id FROM user WHERE isban = 1')
            return await cur.fetchall()


async def math(chat_id,lang='ru'):
    lang = lm.load(lang)
    math = await get_math(chat_id)
    if math.mathon:
        messages_count = math.max_messages - math.messages_count
        if messages_count <= 0:
            text = f'{lang.unsolved_example}\n{math.math_txt}?'
        elif mathstop['istrue']:
            text = 'Бот готовится к рестарту. Примеры временно отключены'
        else:  
            txt = declension(messages_count,lang.message1,lang.message2,lang.message3)
            text = lang.math.format(str(messages_count),txt)
    else:
        text = 'Примеры выключены.\nЧтобы включить используйте команду /settings'
    return text

async def mathme(user_id,chat_id=0):
    async with pool.acquire() as con:
        async with con.cursor() as cur:
            #await cur.execute(f'SELECT chat_id, times FROM maths WHERE user_id = {user_id}')
            sql = f"""SELECT user_id as id, count(*)as count FROM maths where user_id = {user_id}
            union
            select chat_id, count(*) from maths where user_id = {user_id} and chat_id = {chat_id}
            union
            select user_id, count(*) from  maths where user_id = {user_id} and times >= CURDATE();"""
            await cur.execute(sql)
            result = await cur.fetchall()
            return result

# async def mathme_txt(user_id,chat_id=0,lang='ru'):
#     maths = await mathme(user_id,chat_id)
#     day_count = maths[2][1]
#     #Решено за день
#     #day_count = len([True for row in maths if datetime.now().date() == row[1].date()])
#     math_count = len(maths)
#     if chat_id:
#         local_count = math_count
#     else:
#         local_count = len([True for math in maths if math[0] == chat_id])
#     lang = lm.load(lang)
#     if math_count > 0:          
#         example_local = declension(local_count,lang.example,lang.example2,lang.example3)
#         text = lang.mathme.format(str(local_count),example_local)
#         if day_count > 0:
#             dec_count = declension(day_count,lang.example,lang.example2,lang.example3)
#             text += lang.decided_today.format(day_count,dec_count)

#         if not math_count == local_count:
#             example_all = declension(math_count,lang.example,lang.example2,lang.example3)
#             text += lang.mathmeall.format(str(math_count),example_all) 
#         global_users = await globaltop()
#         for num, user in enumerate(global_users,1):
#             if user[0] == user_id:
#                 global_top = num
#                 break
#         text += lang.globalcount.format(str(global_top))
        
#     else:
#         text = lang.no_mathme
#     return text

async def mathme_txt(user_id,chat_id=0):
    maths = await mathme(user_id,chat_id)
    
    if len(maths) == 1:
        text = 'Вы не решили ни одного примера'
        return text
    elif len(maths) == 2:
        all_count = maths[0][1]
        day_count = maths[1][1]
        local_count = all_count
    else:
        all_count = maths[0][1]
        local_count = maths[1][1]
        day_count = maths[2][1]
        if not chat_id:
            local_count = all_count
    local_variant =  declension(local_count,'пример','примера','примеров')
    text = f'Вы решили {local_count} {local_variant}'
    if day_count > 0:
        day_variant = declension(day_count,'пример','примера','примеров')
        text += f'\nЗа сегодня {day_count} {day_variant}'
    if not local_count == all_count:
        all_variant =  declension(all_count,'пример','примера','примеров')
        text += f'\n\nВсего решено {all_count} {all_variant}'
    global_users = await globaltop()
    for num, user in enumerate(global_users,1):
        if user[0] == user_id:
            global_top = num
            break
    text += f'\nВ глобальном топе вы на {global_top} месте'
    return text

async def mathtop(chat_id):
    async with pool.acquire() as con:
        async with con.cursor() as cur:
            sql = f'select user_id, count(user_id) as count from maths group by user_id, chat_id having chat_id = {chat_id} ORDER BY count desc limit 5;'
            await cur.execute(sql)  
            return await cur.fetchall()


async def globaltop():
    global last_time, last_globaltop
    if (datetime.now() - last_time).total_seconds() > 5:
        async with pool.acquire() as con:
            async with con.cursor() as cur:
                await cur.execute(f'SELECT user_id, count(user_id) AS count FROM maths group BY user_id ORDER BY count DESC;')
                curresult = await cur.fetchall()
        last_time = datetime.now()
        last_globaltop = curresult
        return last_globaltop
    else:
        return last_globaltop

last_time = datetime.now() - timedelta(days=1)
# if __name__ == '__main__':
#     cur.execute('SELECT * FROM iris_tg.maths where chat_id = -73852374430;')
#     result = cur.fetchall()
#     for i in result:
#         print(i['times'].day, type(i['times']))