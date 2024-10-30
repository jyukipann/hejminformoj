import os
import streamlit as st  # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore
from sqlalchemy import create_engine, text # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from models.about_account_book import Category, Payer, TransactionType, FinancialTransaction

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
    Base = declarative_base()
    Base.metadata.create_all(bind=engine)
    return engine, SessionLocal

# データベース初期化
engine, SessionLocal = get_engine()

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
    
def add_transaction_type(name):
    transaction_type = TransactionType(name=name)
    session.add(transaction_type)
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
    
    transaction_type_options = [t.name for t in session.query(TransactionType).all()]
    transaction_type = st.selectbox("取引種別", options=transaction_type_options)
    
    description = st.text_input("説明（商品、サービス、その他）")
    
    is_split_bill = st.checkbox("割り勘ですか？")

    submit_button = st.form_submit_button("取引を追加")

    # フォームの送信が行われた場合の処理
    if submit_button:
        # 選択したカテゴリと支払者のIDを取得
        category = session.query(Category).filter_by(name=category_name).first()
        payer = session.query(Payer).filter_by(name=payer_name).first()
        transaction_type = session.query(TransactionType).filter_by(name=transaction_type).first()
        
        # 取引をデータベースに追加
        transaction = FinancialTransaction(
            date=date,
            amount=amount,
            category_id=category.id,
            payer_id=payer.id,
            transaction_type_id=transaction_type.id,
            description=description,
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
        
with st.expander("種別の追加"):
    new_transaction_type = st.text_input("新しい種別名")
    if st.button("種別を追加"):
        transaction_type = TransactionType(name=new_transaction_type)
        session.add(transaction_type)
        session.commit()
        st.success(f"種別 '{new_transaction_type}' が追加されました！")
