import os
import streamlit as st  # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore
from sqlalchemy import create_engine, text # type: ignore
from models.about_account_book import (
    Category, Payer, TransactionType, FinancialTransaction)
import pandas as pd # type: ignore
from tools.db_init import get_engine

# csv_upload
# csv_download
# csv parse and arrange data
# data to db

# 各カテゴリのマッピング用辞書を作成
def get_or_create_id(session, model, name):
    """名前でモデルを検索し、存在しなければ新規作成してIDを返す。"""
    instance = session.query(model).filter_by(name=name).first()
    if instance is None:
        instance = model(name=name)
        session.add(instance)
        session.commit()  # 新しいインスタンスをDBに保存してID取得
    return instance.id

st.title("家計簿のCSVデータの入出力")

# csv_upload
st.header("Upload CSV file")
uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=['csv'],
    disabled=True
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    engine, SessionLocal = get_engine()
    session = SessionLocal()
    # 外部キーとして存在していないデータを追加(_idを追加)
    # payer category transaction_type
    # それぞれ名前を_idに変換
    # カラム名に_idを追加
    
    # 外部キーを新しい列に変換する処理
    df['payer_id'] = df['payer'].apply(lambda x: get_or_create_id(session, Payer, x))
    df['category_id'] = df['category'].apply(lambda x: get_or_create_id(session, Category, x))
    df['transaction_type_id'] = df['transaction_type'].apply(lambda x: get_or_create_id(session, TransactionType, x))

    # 元のカラムを削除して_idカラムに置き換えたデータフレームを作成
    df.drop(columns=['payer', 'category', 'transaction_type'], inplace=True)

    # DataFrameをデータベースに保存
    df.to_sql('financial_transactions', engine, if_exists='append', index=False)

    st.success("CSVデータがデータベースにインポートされました。")
    session.close()



#cached
@st.cache_data
def dump_account_book()->pd.DataFrame:
    engine, SessionLocal = get_engine()
    session = SessionLocal()
    if not session.query(FinancialTransaction).first():
        df = pd.DataFrame()
    else:
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
                TransactionType.name.label("取引種別"),
            )
            .join(
                Category,
                FinancialTransaction.category_id == Category.id
            )
            .join(
                Payer,
                FinancialTransaction.payer_id == Payer.id
            )
            .join(
                TransactionType,
                FinancialTransaction.transaction_type_id == TransactionType.id
            )
        )
        df = pd.read_sql(query.statement, query.session.bind)
        session.close()
    return df

# csv_download
st.header("Download CSV file")
st.download_button(
    label="Download CSV",
    data=dump_account_book().to_csv(index=False),
    file_name="account_book.csv",
    mime="text/csv"
)
