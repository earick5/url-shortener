import re
from datetime import datetime, timezone
from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator


class LinkCreate(BaseModel):
    """Схема запроса для создания короткой ссылки."""

    url: AnyHttpUrl = Field(
        ...,
        description="Длинный URL-адрес для сокращения",
        examples=["https://example.com/some/very/long/link"],
    )
    custom_alias: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        description="Пользовательский псевдоним (буквы, цифры, дефис, подчеркивание)",
        examples=["my-alias"],
    )
    expires_at: datetime | None = Field(
        default=None,
        description="Время истечения срока действия ссылки в формате ISO (UTC)",
        examples=["2026-03-01T00:00:00Z"],
    )

    @field_validator("custom_alias")
    @classmethod
    def validate_alias(cls, v: str | None) -> str | None:
        if v is not None:
            # Запрещаем зарезервированные системные слова
            reserved = {"api", "docs", "redoc", "openapi.json", "health", "metrics"}
            if v.lower() in reserved:
                raise ValueError(f"Псевдоним '{v}' зарезервирован системой.")
            if not re.match(r"^[a-zA-Z0-9_-]+$", v):
                raise ValueError(
                    "Псевдоним может содержать только латинские буквы, цифры, '-' и '_'."
                )
        return v

    @field_validator("expires_at")
    @classmethod
    def validate_expires(cls, v: datetime | None) -> datetime | None:
        if v is not None:
            # Проверяем, что срок истечения в будущем
            now = datetime.now(timezone.utc)
            if v.tzinfo is None:
                # Если таймзона не передана, считаем что это UTC
                v = v.replace(tzinfo=timezone.utc)
            if v <= now:
                raise ValueError("Срок истечения ссылки (expires_at) должен быть в будущем.")
        return v


class LinkResponse(BaseModel):
    """Схема ответа с данными о ссылке и статистикой."""

    code: str
    url: str
    created_at: datetime
    expires_at: datetime | None = None
    clicks: int = 0

    model_config = ConfigDict(from_attributes=True)
