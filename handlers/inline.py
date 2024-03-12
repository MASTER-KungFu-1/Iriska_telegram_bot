from aiogram import Router, F
from aiogram import types
from create_bot import bot
import dbmanager as db
from handlers.math_game import get_math
import gui
from datetime import datetime
import callbackdata as cb
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from config import variables

router = Router()

class MessageCount(StatesGroup):
    message_id = State()
    count = State()

class AutoDeleteMinutes(StatesGroup):
    message_id = State()
    count = State()

class FeedBack(StatesGroup):
    text = State()
    main_message = State()


@router.callback_query(F.data=='mathme')
async def mathme(callback_query: types.CallbackQuery):
    text = await db.mathme_txt(callback_query.from_user.id)
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(text,callback_query.from_user.id,callback_query.message.message_id,reply_markup=gui.menu())

@router.callback_query(cb.Chatsettings.filter(F.action == 'mathon'))
async def mathon(callback: types.CallbackQuery, callback_data: cb.Chatsettings):
    if callback.from_user.id == callback_data.user_id:
        chat_id = callback.message.chat.id
        user_id = callback.from_user.id
        chat = db.Chat(chat_id)
        await chat.load()
        if chat.mathon:
            chat.mathon = 0
        else:
            chat.mathon = 1
        math = await get_math(chat_id)
        math.mathon = chat.mathon
        await chat.save()
        await bot.answer_callback_query(callback.id)
        await bot.edit_message_text(f'Настройка беседы - @{callback.from_user.username}',chat_id,callback.message.message_id,reply_markup=gui.chat_settings(chat,user_id))

@router.callback_query(cb.Chatsettings.filter(F.action=='messagecount'))
async def messagecount(callback: types.CallbackQuery, callback_data: cb.Chatsettings, state: FSMContext):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    await bot.answer_callback_query(callback.id)
    if callback.from_user.id == callback_data.user_id:
        await state.update_data(message_id=callback.message.message_id)
        await state.set_state(MessageCount.count)
        await bot.edit_message_text(f'Напишите через сколько сообщений бот будет отправлять пример - @{callback.from_user.username}',chat_id,callback.message.message_id,reply_markup=gui.cancel(user_id))

#Нажатие на кнопку настройка примеров
@router.callback_query(cb.Chatsettings.filter(F.action=='mathlist'))
async def mathlist(callback: types.CallbackQuery, callback_data: cb.Chatsettings, state: FSMContext):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    chat = db.Chat(chat_id)
    await chat.load()
    await bot.answer_callback_query(callback.id)
    if callback.from_user.id == callback_data.user_id:
        await bot.edit_message_text(f'Настройка примеров - @{callback.from_user.username}',chat_id,callback.message.message_id,reply_markup=gui.mathlist(chat,user_id))

#Нажатие включение или отключение примера
@router.callback_query(cb.Chatsettings.filter(F.action=='mathchange'))
async def mathchange(callback: types.CallbackQuery, callback_data: cb.Chatsettings, state: FSMContext):
    await bot.answer_callback_query(callback.id)
    if callback.from_user.id == callback_data.user_id and callback_data.type in variables:
        chat_id = callback.message.chat.id
        user_id = callback.from_user.id
        Chat = db.Chat(chat_id)
        await Chat.load()
        mathdisable = Chat.mathdisable['disable']
        mathdescription = {'+':'плюсом','-':'минусом','*':'умножением','/':'делением','2':'корнем','3':'кубическим корнем','log':'логарифмом'}
        if callback_data.type in mathdisable:
            mathdisable.remove(callback_data.type)
            text = f'Примеры с {mathdescription[callback_data.type]} включены'
        else:
            allow_var = [i for i in variables if not i in Chat.mathdisable['disable']]
            if len(allow_var) == 1:
                text = 'Должен быть активен хотя бы один тип примеров'
            else:
                mathdisable.append(callback_data.type)
                text = f'Примеры с {mathdescription[callback_data.type]} выключены'
        await Chat.save()
        await bot.edit_message_text(f'{text}\nНастройка примеров - @{callback.from_user.username}',chat_id,callback.message.message_id,reply_markup=gui.mathlist(Chat,user_id))

#Пользователь пишет число
@router.message(MessageCount.count)
async def message_count(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    user_id = message.from_user.id
    chat = db.Chat(chat_id)
    await chat.load()
    await message.delete()
    user_data = await state.get_data()
    if message.text.isdigit() and int(message.text) >= 20 and int(message.text) <= 1000:
        math = await get_math(chat_id)
        math.max_messages = int(message.text)
        if math.max_messages - math.messages_count <= 0:
            math.messages_count = math.max_messages - 1
        chat.max_messages = int(message.text)
        await chat.save()
        await bot.edit_message_text(f'Количество сообщений до примера - {message.text}\nНастройка беседы - @{message.from_user.username}',chat_id,user_data['message_id'],reply_markup=gui.chat_settings(chat,user_id))
        await state.clear()
    else:
        await bot.edit_message_text('Вы должны отправить число от 20 до 1000',chat_id,user_data['message_id'],reply_markup=gui.cancel(user_id))

#Автоудаление сообщений
@router.callback_query(cb.Chatsettings.filter(F.action=='autodelete'))
async def autodelete(callback: types.CallbackQuery, callback_data: cb.Chatsettings, state: FSMContext):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    await bot.answer_callback_query(callback.id)
    if user_id == callback_data.user_id:
        chat = db.Chat(chat_id)
        await chat.load()
        await bot.edit_message_text('Включив эту настройку бот будет удалять команды и ответы на них через заданный интервал времени',chat_id,callback.message.message_id,reply_markup=gui.autodelete_settings(chat,user_id))

#Автоудаление сообщений
@router.callback_query(cb.Chatsettings.filter(F.action=='autodelete_change'))
async def autodelete_change(callback: types.CallbackQuery, callback_data: cb.Chatsettings):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    await bot.answer_callback_query(callback.id)
    if user_id == callback_data.user_id:
        Chat = db.Chat(chat_id)
        await Chat.load()
        if Chat.autodelete_on:
            Chat.autodelete_on = 0
            text = 'Выключено автоудаление команд'
        else:
            Chat.autodelete_on = 1
            text = 'Включено автоудаление команд'
        await Chat.save()
        await bot.edit_message_text(text,chat_id,callback.message.message_id, reply_markup=gui.autodelete_settings(Chat,user_id))

@router.callback_query(cb.Chatsettings.filter(F.action=='autodelete_minutes'))
async def autodelete_minutes(callback: types.CallbackQuery, callback_data: cb.Chatsettings, state: FSMContext):
    await bot.answer_callback_query(callback.id)
    if callback.from_user.id == callback_data.user_id:
        chat_id = callback.message.chat.id
        user_id = callback.from_user.id
        Chat = db.Chat(chat_id)
        await Chat.load()
        await state.update_data(message_id=callback.message.message_id)
        await state.set_state(AutoDeleteMinutes.count)
        await bot.edit_message_text(f'Напишите сколько минут должно пройти для удаления команды (от 1 до 255) - @{callback.from_user.username}',chat_id,callback.message.message_id,reply_markup=gui.cancel(user_id))

#Пользователь пишет минуты
@router.message(AutoDeleteMinutes.count)
async def minute_count(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    user_id = message.from_user.id
    Chat = db.Chat(chat_id)
    await Chat.load()
    await message.delete()
    user_data = await state.get_data()
    if message.text.isdigit() and int(message.text) >= 1 and int(message.text) <= 255:
        Chat.autodelete_minutes = int(message.text)
        await Chat.save()
        await bot.edit_message_text(f'Количество минут до удаления - {message.text}\nНастройка беседы - @{message.from_user.username}',chat_id,user_data['message_id'],reply_markup=gui.autodelete_settings(Chat,user_id))
        await state.clear()
    else:
        await bot.edit_message_text('Вы должны отправить число от 1 до 255',chat_id,user_data['message_id'],reply_markup=gui.cancel(user_id))



@router.callback_query(cb.Chatsettings.filter(F.action=='cancel'))
async def messagecount(callback: types.CallbackQuery, callback_data: cb.Chatsettings, state: FSMContext):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    await bot.answer_callback_query(callback.id)
    if user_id == callback_data.user_id:
        chat = db.Chat(chat_id)
        await chat.load()
        await state.clear()
        await bot.edit_message_text(f'Настройка беседы - @{callback.from_user.username}',chat_id,callback.message.message_id,reply_markup=gui.chat_settings(chat,user_id))

@router.callback_query(cb.Chatsettings.filter(F.action=='closemenu'))
async def messagecount(callback: types.CallbackQuery, callback_data: cb.Chatsettings, state: FSMContext):
    user_id = callback.from_user.id
    await bot.answer_callback_query(callback.id)
    if user_id == callback_data.user_id:
        await callback.message.delete()

@router.callback_query(F.data=='feedback')
async def feedback(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(FeedBack.text)
    await callback.answer()
    await state.update_data(message_id=callback.message.message_id)
    await callback.message.edit_text('Здравствуйте! Чтобы связаться с администратором, воспользуйтесь данной функцией обратной связи. Опишите вашу проблему или вопрос максимально подробно, чтобы мы смогли вам помочь. Спасибо!',reply_markup=gui.feedback_cancel())
    #await bot.edit_message_text(f'123',callback.message.chat.id,callback.message.message_id,reply_markup=gui.menu())


@router.callback_query(F.data=='feedback_cancel')
async def feedback_cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Главное меню:',reply_markup=gui.menu())

@router.message(FeedBack.text)
async def feedback_send(message: types.Message, state: FSMContext):
    await message.answer('Сообщение отправлено и если потребуется администрация вам ответит. А пока вы можете продолжить пользоваться ботом',reply_markup=gui.menu())
    await bot.forward_message(312731525,message.from_user.id,message.message_id)
    await state.clear()
    


#antispam = {'time':datetime(1980,1,1)}
# @router.callback_query(F.data=='globaltop')
# async def process_callback_button(callback_query: types.CallbackQuery):
#     global antispam
#     seconds = (datetime.now() - antispam['time']).seconds
#     if seconds < 300:
#         await bot.edit_message_text(antispam['text'],callback_query.from_user.id,callback_query.message.message_id,reply_markup=gui.menu())
#         return
#     users = db.globaltop()
#     text = 'Топ лучших:\n'
#     for num, user_stat in enumerate(users):
#         if num == 0:
#             emotion = '👑'
#         else:
#             emotion = ''
#         try:
#             user = await bot.get_chat(user_stat['user_id'])
#             full_name = user.full_name
#         except exceptions.TelegramBadRequest:
#             full_name = 'Unknown'
#         text += f'{num+1}) {full_name}{emotion} - {user_stat["count"]}\n'
#     antispam = {'time':datetime.now(),'text':text}
#     await bot.answer_callback_query(callback_query.id)
#     await bot.edit_message_text(text,callback_query.from_user.id,callback_query.message.message_id,reply_markup=gui.menu())