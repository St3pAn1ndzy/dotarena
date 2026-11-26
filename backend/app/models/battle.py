from datetime import datetime
from secrets import token_urlsafe

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import BattleStatus
from app.models.base import Base


class Battle(Base):
    __tablename__ = "battles"

    id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    opponent_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    invite_token: Mapped[str] = mapped_column(
        nullable=False, unique=True,
        default=lambda: token_urlsafe(16),
    )
    status: Mapped[str] = mapped_column(
        nullable=False,
        default=BattleStatus.pending.value,
        server_default=BattleStatus.pending.value,
    )
    winner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    last_polled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"<Battle id={self.id} status={self.status}>"
