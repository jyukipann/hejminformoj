from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# データベースモデル
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)

class Payer(Base):
    __tablename__ = "payers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)

class FinancialTransaction(Base):
    __tablename__ = "financial_transactions"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    payer_id = Column(Integer, ForeignKey("payers.id"), nullable=True)
    description = Column(String(255))
    transaction_type = Column(String(50), nullable=False)
    is_split_bill = Column(Boolean, default=False)
    category = relationship("Category", back_populates="transactions")
    payer = relationship("Payer", back_populates="transactions")

Category.transactions = relationship("FinancialTransaction", back_populates="category")
Payer.transactions = relationship("FinancialTransaction", back_populates="payer")