from typing import Callable, Awaitable, Dict, Any, cast

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from cachetools import TTLCache
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from database.requests import upsert_user  # Make sure this path matches your project

class TrackAllUsersMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.cache = TTLCache(
            maxsize=1000,
            ttl=60 * 60 * 6,  # 6 hours cache
        )
        self.logger = structlog.getLogger()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        await self.logger.debug('TrackAllUsersMiddleware begun')
        # Only process if event has a user (like Message)
        if not hasattr(event, "from_user") or event.from_user is None:
            await self.logger.debug('TrackAllUsersMiddleware: NO attribute "from_user"')
            return await handler(event, data)

        event = cast(Message, event)
        user_id = event.from_user.id

        data["user_cache"] = self.cache

        if user_id not in self.cache:
            session: AsyncSession = data.get("session")

            await upsert_user(
                session=session,
                telegram_id=event.from_user.id,
                lang=event.from_user.language_code or "en"
            )
            self.cache[user_id] = None
        await self.logger.debug('TrackAllUsersMiddleware end')

        self.cache[user_id] = None


        return await handler(event, data)
