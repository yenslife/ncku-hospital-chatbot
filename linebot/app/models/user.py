# use sqlite
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from typing import Optional


class User(Base):
    __tablename__ = "users"

    line_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    conversation_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    def __repr__(self):
        return f"<User line_id={self.line_id}>"
