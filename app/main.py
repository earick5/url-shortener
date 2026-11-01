from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api.endpoints import router as links_router
from app.database import engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Управление жизненным циклом приложения при старте и завершении."""
    # При запуске сервиса
    yield
    # При остановке сервиса освобождаем соединения пула БД
    await engine.dispose()


app = FastAPI(
    title="URL Shortener Service",
    description="Сервис для сокращения ссылок, перенаправления и сбора статистики переходов.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Подключаем маршруты API v1 с префиксом /api/v1
app.include_router(links_router, prefix="/api/v1")


@app.get(
    "/",
    response_class=HTMLResponse,
    tags=["UI"],
    summary="Веб-интерфейс сервиса",
)
async def root() -> HTMLResponse:
    """Главная страница с современным веб-интерфейсом."""
    html_path = Path(__file__).parent / "static" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/health", tags=["Служебные"], summary="Проверка работоспособности")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get(
    "/{code}",
    tags=["Редирект"],
    summary="Редирект по короткой ссылке",
    description="Перенаправляет на оригинальный URL и увеличивает счетчик кликов.",
    response_class=RedirectResponse,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
)
async def redirect_to_url(
    code: str,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    link = await crud.get_link_by_code(db, code)
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Короткая ссылка '{code}' не найдена.",
        )

    if crud.is_link_expired(link):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Срок действия этой ссылки истек.",
        )

    # Увеличиваем счетчик кликов
    await crud.increment_clicks(db, link.id)

    # Выполняем редирект (HTTP 307 сохраняет метод и не кэширует жестко в браузере)
    return RedirectResponse(
        url=link.url, status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )
