import enum

from sqlalchemy import Boolean, Column, Enum, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True, nullable=False)

    hashed_password = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)

    is_admin = Column(Boolean, default=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.user)
    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
