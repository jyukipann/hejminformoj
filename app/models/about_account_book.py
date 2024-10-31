from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.orm import relationship # type: ignore

Base = declarative_base()

# データベースモデル
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)

class Payer(Base):
    __tablename__ = "payers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)

class TransactionType(Base):
    __tablename__ = "transaction_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)

class FinancialTransaction(Base):
    __tablename__ = "financial_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    description = Column(String(255), nullable=False)
    amount = Column(Integer, nullable=False)
    is_split_bill = Column(Boolean, default=False, nullable=False)
    
    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False)
    payer_id = Column(
        Integer,
        ForeignKey("payers.id"),
        nullable=False)
    transaction_type_id = Column(
        Integer,
        ForeignKey("transaction_types.id"),
        nullable=False)
    
    category = relationship(
        "Category",
        back_populates="transactions")
    payer = relationship(
        "Payer",
        back_populates="transactions")
    transaction_type = relationship(
        "TransactionType",
        back_populates="transactions")

Category.transactions = relationship(
    "FinancialTransaction", back_populates="category")
Payer.transactions = relationship(
    "FinancialTransaction", back_populates="payer")
TransactionType.transactions = relationship(
    "FinancialTransaction", back_populates="transaction_type")