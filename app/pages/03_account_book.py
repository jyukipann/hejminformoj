import os
import streamlit as st  # type: ignore
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from models.about_account_book import Category, Payer, FinancialTransaction
Base = declarative_base()
import pandas as pd


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

st.title('家計簿')
# データベースエンジンとセッションの取得
engine, SessionLocal = get_engine()

# データベースのテーブルを作成
Base.metadata.create_all(bind=engine)

# セッションの作成
session = SessionLocal()

# ORMによりクエリ文を生成
query = (
    session.query(FinancialTransaction)
    .options(
        joinedload(FinancialTransaction.category), 
        joinedload(FinancialTransaction.payer))
    .limit(100)
)

# as dataframe
df = pd.read_sql(query.statement, query.session.bind)

# セッションのクローズ
session.close()

st.dataframe(
    df,
    hide_index=True,
)