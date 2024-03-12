import create_bot
import asyncio
from handlers import commands_chat, commands_ls, math_game, inline
from middlewares.bancheck import isban
from dbmanager import connect
from middlewares.bancheck import banlist_load
import logging



async def main():
    bot = create_bot.bot
    dp = create_bot.dp
    
    print('Bot online')
    await connect()
    await banlist_load()
    #Проверка на бан для соообщений и колбэков
    #dp.message.outer_middleware(updates())
    -1001607078902
    dp.message.outer_middleware(isban())
    dp.callback_query.middleware(isban())
    #Инициализация роутеров
    dp.include_router(commands_chat.router)
    dp.include_router(commands_ls.router)
    dp.include_router(inline.router)
    dp.include_router(math_game.router)
    await bot.delete_webhook()
    await dp.start_polling(bot)




    '''
    @dp.message_handler(commands=['name'],state=None)
    async def set_name(message: types.Message):
        await FSM.name.set()
        await message.answer("Введи свое имя")



    @dp.message_handler(state=FSM.name)
    async def set_name_2(message:types.Message, state:FSMContext):
        if message.text[0] == '/':
            await message.answer('Давай по новой')
        else:
            await message.answer(f'Имя {message.text} сохранено')
            await state.finish()'''

   


if __name__ == "__main__":
    logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger('main')
    asyncio.run(main())