"""
사용자 엔티티 모델.

`Users` 테이블과 1:N 관계를 맺는 종속 엔티티와의 연동을 담당한다.
"""

from sqlalchemy import BigInteger, Column, DateTime, Enum, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class User(Base):
    """`Users` 테이블 모델."""

    __tablename__ = "Users"

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    gender = Column(
        Enum("MALE", "FEMALE", name="user_gender_enum"),
        comment="사용자 성별",
    )
    preferred_tags = Column(Text, comment="사용자 선호 태그 (콤마 구분 텍스트)")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 종속 엔티티들과의 양방향 관계 설정
    fitting_results = relationship(
        "FittingResult",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    images = relationship(
        "UserImage",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    coordi_interactions = relationship(
        "UserCoordiInteraction",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    coordi_view_logs = relationship(
        "UserCoordiViewLog",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    closet_items = relationship(
        "UserClosetItem",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    item_view_logs = relationship(
        "UserItemViewLog",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"User(user_id={self.user_id}, email={self.email})"

