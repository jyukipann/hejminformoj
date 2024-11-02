from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey # type: ignore
from sqlalchemy.orm import relationship # type: ignore
from .base_model import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True)
    name = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)