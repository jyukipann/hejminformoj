import os
import streamlit as st  # type: ignore
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from models.about_account_book import Category, Payer, FinancialTransaction
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

# セッションの作成
session = SessionLocal()

# ORMによりクエリ文を生成
query = (
    session.query(
        FinancialTransaction.id,
        FinancialTransaction.description.label("メモ"),
        FinancialTransaction.date.label("日付"),
        Category.name.label("カテゴリ"),
        FinancialTransaction.amount.label("金額"),
        Payer.name.label("payer_name").label("支払者"),
        FinancialTransaction.is_split_bill.label("is割り勘"),
        FinancialTransaction.transaction_type.label("種類"),
    )
    .join(Category, FinancialTransaction.category_id == Category.id)
    .join(Payer, FinancialTransaction.payer_id == Payer.id)
    .limit(100)
)
# st.write(query)
# as dataframe
df = pd.read_sql(query.statement, query.session.bind)
# st.write(df.columns)

# セッションのクローズ
session.close()

selected = st.dataframe(
    df,
    hide_index=True,
    on_select='rerun',
    use_container_width=True,
    column_config={
        
    }
)

if st.button(
        'Delete selected rows', 
        disabled=selected["selection"]['rows'] == [], 
        use_container_width=True):
    for row in df.iloc[selected["selection"]['rows']].iterrows():
        transaction_id = row[1]['id']

        session = SessionLocal()
        session.query(FinancialTransaction).filter_by(id=transaction_id).delete()
        session.commit()
        session.close()
    st.rerun()