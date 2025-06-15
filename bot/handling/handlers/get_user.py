from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from sqlalchemy import select

get_user_router = Router()


@get_user_router.message(Command("get_user"))
async def get_user_handler(msg: Message, i18n: TranslatorRunner, session: AsyncSession):
    #user = await session.get(User, msg.from_user.id)
    result = await session.execute(select(User).where(User.telegram_id == msg.from_user.id))
    user = result.scalar_one_or_none()
    if user is None:
        await msg.answer("User data not found")
    else:
        user_id = f"ID: {user.telegram_id}"
        await msg.answer(i18n.db_get_user(user=user_id))
