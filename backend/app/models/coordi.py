"""
코디(Coordi) 엔티티 모델.

`Coordis` 테이블은 시즌, 스타일 정보와 자유 텍스트 설명을 보관한다.
"""

from sqlalchemy import BigInteger, Column, DateTime, Enum, Index, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Coordi(Base):
    """`Coordis` 테이블 모델."""

    __tablename__ = "Coordis"

    coordi_id = Column(BigInteger, primary_key=True, autoincrement=True)
    season = Column(
        Enum("SPRING", "SUMMER", "FALL", "WINTER", name="coordi_season_enum")
    )
    style = Column(
        Enum("CASUAL", "STREET", "SPORTY", "MINIMAL", name="coordi_style_enum")
    )
    gender = Column(
        Enum("MALE", "FEMALE", name="coordi_gender_enum"),
        comment="코디 대상 성별",
    )
    description = Column(Text, comment="태그 포함 설명 문구")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_coordis_season_style", "season", "style"),
        Index("idx_coordis_style", "style"),
    )

    images = relationship(
        "CoordiImage",
        back_populates="coordi",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    coordi_items = relationship(
        "CoordiItem",
        back_populates="coordi",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    interactions = relationship(
        "UserCoordiInteraction",
        back_populates="coordi",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    view_logs = relationship(
        "UserCoordiViewLog",
        back_populates="coordi",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"Coordi(coordi_id={self.coordi_id}, style={self.style})"

