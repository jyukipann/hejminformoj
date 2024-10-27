import os
import streamlit as st  # type: ignore
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# データベースの設定と初期化
def get_engine():
    DB_HOST = "db"  # Dockerのホスト名
    DB_USER = "root"
    DB_PASSWORD = os.environ.get("MYSQL_ROOT_PASSWORD")
    DB_NAME = "household_accounts_db"
    
    # ベースとなるURL (データベース指定なし)
    BASE_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}"
    
    # データベースが存在しない場合に作成する
    engine = create_engine(BASE_DATABASE_URL)
    with engine.connect() as connection:
        connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
    
    # データベースを指定したURLにエンジンを再設定
    DATABASE_URL = f"{BASE_DATABASE_URL}/{DB_NAME}"
    engine = create_engine(DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal

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

# データベース初期化
engine, SessionLocal = get_engine()
Base.metadata.create_all(bind=engine)

# Streamlitアプリ
st.title("家計簿管理システム")

# セッションの取得
session = SessionLocal()

# カテゴリと支払者のリストを取得
def get_categories():
    return session.query(Category).all()

def get_payers():
    return session.query(Payer).all()

# 新しいカテゴリや支払者を追加するヘルパー関数
def add_category(name):
    category = Category(name=name)
    session.add(category)
    session.commit()

def add_payer(name):
    payer = Payer(name=name)
    session.add(payer)
    session.commit()

# フォームの作成
with st.form("financial_transaction_form"):
    st.header("新しい取引を追加")

    # 日付、金額、カテゴリ、支払者、取引タイプ、説明、分割支払いの入力
    date = st.date_input("日付")
    amount = st.number_input("金額", min_value=0, step=1)
    category_options = [c.name for c in get_categories()]
    category_name = st.selectbox("カテゴリ", options=category_options)
    payer_options = [p.name for p in get_payers()]
    payer_name = st.selectbox("支払者", options=payer_options)
    transaction_type = st.selectbox("取引タイプ", options=["収入", "支出"])
    description = st.text_input("説明（任意）")
    is_split_bill = st.checkbox("割り勘ですか？")

    submit_button = st.form_submit_button("取引を追加")

    # フォームの送信が行われた場合の処理
    if submit_button:
        # 選択したカテゴリと支払者のIDを取得
        category = session.query(Category).filter_by(name=category_name).first()
        payer = session.query(Payer).filter_by(name=payer_name).first() if payer_name else None
        
        # 取引をデータベースに追加
        transaction = FinancialTransaction(
            date=date,
            amount=amount,
            category_id=category.id,
            payer_id=payer.id if payer else None,
            description=description,
            transaction_type=transaction_type,
            is_split_bill=is_split_bill
        )
        session.add(transaction)
        session.commit()
        st.success("取引が追加されました！")

# カテゴリや支払者を追加するフォーム
with st.expander("カテゴリの追加"):
    new_category = st.text_input("新しいカテゴリ名")
    if st.button("カテゴリを追加"):
        add_category(new_category)
        st.success(f"カテゴリ '{new_category}' が追加されました！")

with st.expander("支払者の追加"):
    new_payer = st.text_input("新しい支払者名")
    if st.button("支払者を追加"):
        add_payer(new_payer)
        st.success(f"支払者 '{new_payer}' が追加されました！")