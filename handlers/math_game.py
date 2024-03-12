from aiogram import types, Dispatcher
from aiogram.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from create_bot import bot, dp
from langs import langs_manager as lm
import random
import dbmanager as db
from aiogram import Router, F
import random
from datetime import datetime
from config import variables
import sys


router = Router()
router.message.filter(F.chat.type == "supergroup")

mathstop = {'istrue':0,'user_id':None,'message_id':None, 'count':0}

class Math:
    def __init__(self,chat_id):
        self.last_user = None
        self.messages_count = 0
        self.chat_id = chat_id
    async def load(self):
        chat = db.Chat(self.chat_id)
        await chat.load()
        self.mathon = chat.mathon
        self.max_messages = chat.max_messages
        self.mathdisable = chat.mathdisable
    def generate(self):
        allow_var = [i for i in variables if not i in self.mathdisable['disable']]
        operation = random.choice(allow_var)
        if operation == '+':
            one = random.randint(0, 9000)
            two = random.randint(0, 9000)
            self.answer = str(one + two)
            self.math_txt = f'{one} + {two}'
        elif operation == '-':
            one = random.randint(0, 9000)
            two = random.randint(0, 9000)
            self.answer = str(one - two)
            self.math_txt = f'{one} - {two}'
        elif operation == '*':
            one = random.randint(0, 200)
            two = random.randint(0, 20)
            self.answer = str(one * two)
            self.math_txt = f'{one} * {two}'
        elif operation == '/':
            answer = random.randint(0, 40)
            two = random.randint(0, 40)
            one = two * answer
            self.answer = str(answer)
            self.math_txt = f'{one} / {two}'
        elif operation == '2':
            answer = random.randint(2, 10)
            one = answer ** 2
            self.answer = str(answer)
            self.math_txt = f'Корень из {one}'
            lang = lm.load(language)
            self.createdate = datetime.now()
            return self.math_txt+'?'
        elif operation == '3':
            answer = random.randint(2, 10)
            one = answer ** 3
            self.answer = str(answer)
            self.math_txt = f'Кубический корень из {one}'
            lang = lm.load(language)
            self.createdate = datetime.now()
            return self.math_txt+'?'
        elif operation == 'log':
            num = {2:"₂",3:"₃",4:"₄",5:"₅",6:"₆",7:"₇",8:"₈",9:"₉"}
            one = random.randint(2,10)
            answer = random.randint(0,4)
            self.answer = str(answer)
            if one == 10:
                self.math_txt = f'lg{one**answer}'
            else:
                self.math_txt = f'log{num[one]}{one**answer}'
        self.createdate = datetime.now()
        lang = lm.load(language)
        return lang.math_question.format(self.math_txt)
    def math(self):
        if self.max_messages - self.messages_count > 0:
            return False
        else:
            return True



maths = dict()

async def get_math(chat_id):
    if maths.get(chat_id):
        return maths[chat_id]
    else:
        math = Math(chat_id)
        await math.load()
        maths.update({chat_id:math})
        return math

language = 'ru'
#message.from_user.locale

@router.message(F.text)
async def main(message: types.Message):
    math = await get_math(message.chat.id)
    if math.mathon and not mathstop['istrue'] and not message.from_user.id == math.last_user:
        math.messages_count += 1
        math.last_user = message.from_user.id
    elif not math.mathon:
        return
    if math.messages_count == math.max_messages:
        math_question = math.generate()
        math.messages_count += 1
        await message.answer(math_question)
    elif math.messages_count >= math.max_messages and message.text == math.answer:
        math.messages_count = 0
        lang = lm.load(language)
        text = lang.math_answer.format(math.math_txt,math.answer,message.from_user.full_name)
        chat = db.Chat(message.chat.id)
        await chat.load()
        solution_time = (datetime.now() - math.createdate).seconds
        await chat.win(message.from_user.id,message.chat.id,math.math_txt,math.answer,solution_time)
        await message.answer(text)   
        if mathstop['istrue']:
            mathstop['count'] -=1
            await bot.edit_message_text(f'Примеры выключены\nОжидаю решения {mathstop["count"]} примеров',mathstop['user_id'],mathstop['message_id'])
            if mathstop['count'] == 0:
                await bot.send_message(mathstop['user_id'],'Все примеры решены')
                sys.exit()
    elif math.messages_count > math.max_messages*2:
        math.messages_count = 0

# def register_handlers_math(dp: Dispatcher):
#     dp.register_message_handler(main,content_types=['text'])