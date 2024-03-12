from aiogram import F, Router
from aiogram.filters import Command, and_f
from langs import langs_manager as lm
from aiogram import types
import gui
from config import admin_ids
from handlers.math_game import maths, mathstop
import sys
from create_bot import bot
router = Router()
router.message.filter(F.chat.type == "private")

startstats = {'allcount': 0, 'unique_users':[]}

#------------Админ команды--------------

#Статистика команды start
@router.message(Command(commands=['stats']))
async def stats(message: types.Message):
    if message.from_user.id in admin_ids:
        await message.answer(f'Всего: {startstats["allcount"]}\nУникальных: {len(startstats["unique_users"])}')


#Выключение бота       
@router.message(Command(commands=['irisstop']))
async def irisstop(message: types.Message):
    if message.from_user.id in admin_ids:
        math_list = [True for math in maths.values() if math.math() == True]
        mathstop['istrue'] = 1
        mathstop['user_id'] = message.from_user.id
        
        mathstop['count'] = len(math_list)
        if mathstop['count'] == 0:
            await message.answer(f'Нет примеров')
            sys.exit()
        else:
            message2 = await message.answer(f'Примеры выключены\nОжидаю решения {len(math_list)} примеров')
            mathstop['message_id'] = message2.message_id
#---------------------------------------


# Хэндлер на команду /start
@router.message(Command(commands=['start']))
async def commands(message: types.Message):
    #lang = lm.load(message.from_user.language_code)
    startstats['allcount'] += 1
    if not message.from_user.id in startstats['unique_users']:
        startstats['unique_users'].append(message.from_user.id)
    await message.answer('Приветствую👋\nЭтот бот сделан для групповых чатов. Добавьте меня туда и разрешите доступ к переписке. Затем каждые 50 сообщений я буду туда отправлять математический пример. Кто первый решит тот и победит. Все команды работают только в групповых чатах, а в личной переписке с ботом вы можете посмотреть статистику решенных примеров', reply_markup=gui.menu())



# @router.message(Command(commands=['ban']))
# async def ban(message: types.Message):
#     if message.from_user.id in admin_ids:
#         args = message.text.split(' ')
#         args.pop(0)
#         if len(args) <= 1:
#             await message.answer('Команде необходимы аргументы\n/ban [пользователь] [причина]')
#         elif len(args) == 2:
#             await message.answer(str(args))

@router.message(F.text.startswith('/'))
async def commands(message: types.Message):
    lang = lm.load(message.from_user.language_code)
    await message.answer(lang.chat_command, reply_markup=gui.menu())


@router.message(and_f(F.reply_to_message, F.from_user.id == 312731525))
async def reply_text(message: types.Message):
    forward_id = message.reply_to_message.chat.id
    await bot.forward_message(forward_id, message.chat.id,message.message_id)
    #await message.reply_to_message.forward(forward_id,)
    #await message.answer(message.text, reply_markup=gui.menu())
