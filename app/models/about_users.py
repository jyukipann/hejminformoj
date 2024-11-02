from sqlalchemy import Column, Integer, String, ForeignKey # type: ignore
from sqlalchemy.orm import relationship # type: ignore
from .base_model import Base
import uuid

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False, unique=True)
    # email = Column(String(255), nullable=False, unique=True)
    passkeys = relationship("Passkey", back_populates="user")
    uuid = Column(
        String(255), 
        nullable=False, 
        unique=True, 
        default=lambda: str(uuid.uuid4())
    )

class Passkey(Base):
    __tablename__ = "passkeys"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False)
    passkey = Column(String(255), nullable=False, unique=True)
    credential_id = Column(String(128), unique=True, nullable=False)  # クレデンシャルID
    public_key = Column(String(256), nullable=False)  # 公開鍵

    user = relationship(
        "User",
        back_populates="passkeys")