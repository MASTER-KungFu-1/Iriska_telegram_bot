import emoji
from aiogram.utils.keyboard import InlineKeyboardBuilder
import callbackdata as cb
from config import variables
import methods

def menu():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Моя статистика', callback_data='mathme')
    keyboard.adjust(1)
    return keyboard.as_markup()


def chat_settings(chat,user_id):
    kb = InlineKeyboardBuilder()
    
    if chat.mathon:
        textmath_on = f'{emoji.emojize(":green_circle:")} Примеры включены'
    else:
        textmath_on = f'{emoji.emojize(":red_circle:")} Примеры выключены'

    kb.button(text=textmath_on, callback_data=cb.Chatsettings(user_id=user_id,action='mathon'))
    kb.button(text=f'Сообщений до примера: {chat.max_messages}', callback_data=cb.Chatsettings(user_id=user_id, action='messagecount'))
    kb.button(text=f'Настройка примеров', callback_data=cb.Chatsettings(user_id=user_id, action='mathlist'))
    kb.button(text=f'Автоудаление команд', callback_data=cb.Chatsettings(user_id=user_id, action='autodelete'))
    kb.button(text='Закрыть меню', callback_data=cb.Chatsettings(user_id=user_id, action='closemenu'))
    kb.adjust(1)
    return kb.as_markup()

def mathlist(chat,user_id):
    kb = InlineKeyboardBuilder()
    mathdisable = chat.mathdisable['disable']
    for i in variables:
        if i in mathdisable:
            kb.button(text=emoji.emojize(f':red_circle: {i}'), callback_data=cb.Chatsettings(user_id=user_id, action='mathchange',type=i))
        else:
            kb.button(text=emoji.emojize(f':green_circle: {i}'), callback_data=cb.Chatsettings(user_id=user_id, action='mathchange',type=i))
    kb.button(text='Назад', callback_data=cb.Chatsettings(user_id=user_id, action='cancel'))
    kb.adjust(3)
    return kb.as_markup()

def autodelete_settings(Chat,user_id):
    kb = InlineKeyboardBuilder()
    if Chat.autodelete_on:
        kb.button(text=emoji.emojize(f':green_circle: Включено'), callback_data=cb.Chatsettings(user_id=user_id, action='autodelete_change'))
    else:
        kb.button(text=emoji.emojize(f':red_circle: Выключено'), callback_data=cb.Chatsettings(user_id=user_id, action='autodelete_change'))
    minutes = methods.declension(Chat.autodelete_minutes,"минута",'минуты','минут')
    kb.button(text=emoji.emojize(f':hourglass_not_done: {Chat.autodelete_minutes} {minutes}'), callback_data=cb.Chatsettings(user_id=user_id, action='autodelete_minutes'))
    kb.button(text='Назад', callback_data=cb.Chatsettings(user_id=user_id, action='cancel'))
    kb.adjust(1)
    return kb.as_markup()

def cancel(user_id):
    kb = InlineKeyboardBuilder()
    kb.button(text='Отменить', callback_data=cb.Chatsettings(user_id=user_id,action='cancel'))
    return kb.as_markup()

def feedback_cancel():
    kb = InlineKeyboardBuilder()
    kb.button(text='Отменить', callback_data='feedback_cancel')
    return kb.as_markup()