from collections.abc import Sequence
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.database import get_db
from app.schemas import LinkCreate, LinkResponse

router = APIRouter(prefix="/links", tags=["Ссылки (Links)"])


@router.post(
    "",
    response_model=LinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать короткую ссылку",
    description="Принимает длинный URL, опциональный кастомный псевдоним (custom_alias) и дату истечения (expires_at).",
)
async def create_short_link(
    link_in: LinkCreate,
    db: AsyncSession = Depends(get_db),
) -> LinkResponse:
    if link_in.custom_alias:
        existing = await crud.get_link_by_code(db, link_in.custom_alias)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Псевдоним '{link_in.custom_alias}' уже занят.",
            )

    link = await crud.create_link(db, link_in)
    return LinkResponse.model_validate(link)


@router.get(
    "",
    response_model=list[LinkResponse],
    summary="Получить список всех ссылок",
    description="Возвращает список сохраненных ссылок с поддержкой пагинации (limit и offset).",
)
async def list_links(
    limit: int = Query(50, ge=1, le=100, description="Количество записей"),
    offset: int = Query(0, ge=0, description="Смещение списка"),
    db: AsyncSession = Depends(get_db),
) -> Sequence[LinkResponse]:
    links = await crud.get_links(db, limit=limit, offset=offset)
    return [LinkResponse.model_validate(link) for link in links]


@router.get(
    "/{code}",
    response_model=LinkResponse,
    summary="Получить статистику по короткой ссылке",
    description="Возвращает информацию о ссылке, дату создания, срок действия и количество переходов.",
)
async def get_link_stats(
    code: str,
    db: AsyncSession = Depends(get_db),
) -> LinkResponse:
    link = await crud.get_link_by_code(db, code)
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ссылка не найдена.",
        )
    return LinkResponse.model_validate(link)


@router.delete(
    "/{code}",
    summary="Удалить короткую ссылку",
    description="Удаляет короткую ссылку из базы данных по её коду.",
)
async def delete_short_link(
    code: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    link = await crud.get_link_by_code(db, code)
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ссылка не найдена.",
        )

    await crud.delete_link(db, link)
    return {"detail": f"Ссылка с кодом '{code}' успешно удалена."}
