from datetime import datetime, timezone
from collections.abc import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Link
from app.schemas import LinkCreate
from app.utils import generate_short_code


async def get_link_by_code(db: AsyncSession, code: str) -> Link | None:
    """Поиск ссылки по короткому коду или псевдониму."""
    stmt = select(Link).where(Link.code == code)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_link(db: AsyncSession, link_in: LinkCreate) -> Link:
    """Создание новой короткой ссылки с проверкой коллизий."""
    if link_in.custom_alias:
        code = link_in.custom_alias
    else:
        # Генерируем уникальный код, проверяя отсутствие дубликатов
        while True:
            candidate = generate_short_code()
            existing = await get_link_by_code(db, candidate)
            if not existing:
                code = candidate
                break

    link = Link(
        code=code,
        url=str(link_in.url),
        expires_at=link_in.expires_at,
        clicks=0,
    )
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


async def increment_clicks(db: AsyncSession, link_id: int) -> None:
    """Атомарное увеличение счетчика переходов на 1."""
    stmt = update(Link).where(Link.id == link_id).values(clicks=Link.clicks + 1)
    await db.execute(stmt)
    await db.commit()


async def get_links(
    db: AsyncSession, limit: int = 50, offset: int = 0
) -> Sequence[Link]:
    """Получение списка ссылок с пагинацией (сортировка от новых к старым)."""
    stmt = (
        select(Link)
        .order_by(Link.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def delete_link(db: AsyncSession, link: Link) -> None:
    """Удаление ссылки из базы данных."""
    await db.delete(link)
    await db.commit()


def is_link_expired(link: Link) -> bool:
    """Проверка, истек ли срок жизни ссылки."""
    if link.expires_at is None:
        return False
    now = datetime.now(timezone.utc)
    return link.expires_at <= now
