from datetime import datetime, timezone
from sqlalchemy import BigInteger, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Link(Base):
    """Модель сокращенной ссылки в базе данных."""

    __tablename__ = "links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    clicks: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<Link code={self.code} url={self.url[:30]} clicks={self.clicks}>"
