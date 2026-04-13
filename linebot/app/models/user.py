# use sqlite
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from typing import Optional


class User(Base):
    __tablename__ = "users"

    line_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    conversation_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    bed_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # 床號
    diagnosis: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # 診斷
    attending_physician: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )  # 主治醫師
    dialysis_reason: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )  # 洗腎原因

    def __repr__(self):
        return f"<User line_id={self.line_id} conversation_id={self.conversation_id} bed_number={self.bed_number} diagnosis={self.diagnosis} attending_physician={self.attending_physician} dialysis_reason={self.dialysis_reason}>"
