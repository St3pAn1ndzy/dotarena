
from sqlalchemy import BigInteger, Column, DateTime, Integer, String, func

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    steam_id = Column(BigInteger, nullable=True)
    nickname = Column(String(255), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
