from asyncio import sleep
from aiogram import types
from aiogram import F, Router
from aiogram.filters import Command
from create_bot import bot, dp
import dbmanager as db
from langs import langs_manager as lm
from aiogram import exceptions
from datetime import datetime
from aiogram.fsm.context import FSMContext
import logging
import gui

logger = logging.getLogger('commands_chat')

router = Router()
router.message.filter(F.chat.type == "supergroup")
#router.message.middleware(isban)

antispam = {'time':datetime(1980,1,1)}

async def message_delete(message, answer):
    Chat = db.Chat(message.chat.id)
    await Chat.load()
    if Chat.autodelete_on:
        await sleep(Chat.autodelete_minutes*60)
        await message.delete()
        await bot.delete_message(message.chat.id, answer.message_id)



@router.message(Command(commands=['math']))
async def math(message: types.Message):
    text = await db.math(message.chat.id)
    answer = await message.answer(text)
    await message_delete(message, answer)
    

@router.message(Command(commands=['mathme']))
async def mathme(message: types.Message):
    text = await db.mathme_txt(message.from_user.id,message.chat.id)
    answer = await message.reply(text)
    await message_delete(message, answer)
    
@router.message(Command(commands=['mathtop']))
async def mathtop(message: types.Message):
    lang = lm.load()
    result = await db.mathtop(message.chat.id)
    text = 'Топ пользователей:\n'
    for num, user_stat in enumerate(result):
        try:
            user = await bot.get_chat_member(message.chat.id, user_stat[0])
            #user = await bot.get_chat(user_stat['user_id'])
            fullname = user.user.full_name
        except exceptions.TelegramBadRequest:
            fullname = 'Anonim'
        text += f'{num+1}) {fullname} - {user_stat[1]}\n'
    if not result:
        text = 'В этом диалоге еще никто не решал примеры'
    answer = await message.answer(text)
    await message_delete(message, answer)
    
@router.message(Command(commands=['settings']))
async def settings(message: types.Message):
    users = await bot.get_chat_administrators(message.chat.id)
    admin_ids = [user.user.id for user in users]
    user_id = message.from_user.id
    if user_id in admin_ids:
        chat = db.Chat(message.chat.id)
        await chat.load()
        try:
            await message.delete()
            error_txt = ''
        except exceptions.TelegramBadRequest as e:
            error_txt = 'Для корректной работы разрешите боту удалять сообщения\n'
        await message.answer(f'{error_txt}Настройка беседы - @{message.from_user.username}',reply_markup=gui.chat_settings(chat,user_id))

    else:
        await message.reply('Эту команду могут выполять только администраторы')
    
@router.message(Command(commands=['cancel']))
async def cancel(message: types.Message, state: FSMContext):
    data = await state.get_state()
    if data is None:
        answer = await message.answer('Нечего отменять')
    else:
        await state.clear()
        answer = await message.answer('Действие отменено')
    await message_delete(message, answer)

    #result = await bot.get_chat(message.from_user.id)
    #print(result)

# @router.message(Command(commands=['globaltop']))
# async def globaltop(message: types.Message):
#     global antispam
#     seconds = (datetime.now() - antispam['time']).seconds
#     if seconds < 300:
#         await message.answer(antispam['text'])
#         return
#     users = db.globaltop()
#     text = 'Топ лучших:\n'
#     for user_stat in users:
#         try:
#             user = await bot.get_chat(user_stat['user_id'])
#             text += f'{user.full_name} - {user_stat["count"]}\n'
#         except exceptions.TelegramBadRequest:
#             text += f'Unknown - {user_stat["count"]}\n'
#     antispam = {'time':datetime.now(),'text':text}
#     await message.answer(text)

