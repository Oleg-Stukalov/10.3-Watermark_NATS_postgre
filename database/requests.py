from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


async def upsert_user(session: AsyncSession, telegram_id: int, lang: str = "en"):
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            telegram_id=telegram_id,
            lang=lang,
        )
        session.add(user)
        await session.commit()
    else:
        # Optional: update lang if changed
        if user.lang != lang:
            user.lang = lang
            await session.commit()
