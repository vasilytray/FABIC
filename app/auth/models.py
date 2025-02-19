from sqlalchemy import text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.dao.database import Base, str_uniq
from datetime import datetime


class Role(Base):
    name: Mapped[str_uniq]
    users: Mapped[list["User"]] = relationship(back_populates="role")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"


class User(Base):
    phone_number: Mapped[str_uniq]
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str_uniq]
    password: Mapped[str]
    email_verified: Mapped[bool] = mapped_column(default=False, server_default=text("false"))
    phone_verified: Mapped[bool] = mapped_column(default=False, server_default=text("false"))
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), default=1, server_default=text("1"))
    telegram_chat_id: Mapped[Optional[str]] = mapped_column(nullable=True)
    role: Mapped["Role"] = relationship("Role", back_populates="users", lazy="joined")
    verification_codes: Mapped[list["VerificationCode"]] = relationship(back_populates="user")

class VerificationCode(Base):
    __tablename__ = "verification_codes"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    code: Mapped[str]
    type: Mapped[str]  # 'email' или 'phone'
    expires_at: Mapped[datetime]
    
    user: Mapped["User"] = relationship("User", back_populates="verification_codes")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"
