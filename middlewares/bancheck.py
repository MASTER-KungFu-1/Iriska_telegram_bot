from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message
from dbmanager import ban_list as bl
from aiomysql import InterfaceError
import dbmanager as db
from logging import getLogger

logger = getLogger('main')

async def banlist_load():
    global ban_list
    ban_list = [row['user_id'] for row in await bl()]
    print(ban_list)
class isban(BaseMiddleware):
    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message, data: Dict[str, Any]) -> Any:
        if not event.from_user.id in ban_list:
            try:
                return await handler(event, data)
            except InterfaceError as e:
                print(e)
                logger.exception(e)
                await db.connect()
                return await handler(event, data)
        return