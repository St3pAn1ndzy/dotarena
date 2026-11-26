from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class BattleMatchEvent(Base):
    __tablename__ = "battle_match_events"
    __table_args__ = (UniqueConstraint("battle_id", "match_id", name="uq_battle_match"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    battle_id: Mapped[int] = mapped_column(ForeignKey("battles.id", ondelete="CASCADE"))
    match_id: Mapped[int]
    account_id: Mapped[int]
    hero_id: Mapped[int]
    kills: Mapped[int] = mapped_column(default=0)
    deaths: Mapped[int] = mapped_column(default=0)
    assists: Mapped[int] = mapped_column(default=0)
    win: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"<BattleMatchEvent id={self.id} match_id={self.match_id}>"
