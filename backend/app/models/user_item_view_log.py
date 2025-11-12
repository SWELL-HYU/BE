"""
사용자 아이템 조회 로그(UserItemViewLog) 엔티티 모델.

아이템 상세 화면에서의 체류 시간을 기록한다.
"""

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class UserItemViewLog(Base):
    """`User_Item_View_Logs` 테이블 모델."""

    __tablename__ = "User_Item_View_Logs"
    __table_args__ = (Index("idx_user_item", "user_id", "item_id"),)

    log_id = Column(BigInteger, autoincrement=True, primary_key=True)
    user_id = Column(
        BigInteger,
        ForeignKey("Users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    item_id = Column(
        BigInteger,
        ForeignKey("Items.item_id", ondelete="CASCADE"),
        nullable=False,
        comment="조회한 아이템 ID",
    )
    view_started_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="조회 시작 시간",
    )
    duration_seconds = Column(
        Integer,
        nullable=False,
        comment="머무른 시간 (초)",
    )

    user = relationship(
        "User",
        back_populates="item_view_logs",
        passive_deletes=True,
    )
    item = relationship(
        "Item",
        back_populates="view_logs",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"UserItemViewLog(log_id={self.log_id}, user_id={self.user_id}, item_id={self.item_id})"

