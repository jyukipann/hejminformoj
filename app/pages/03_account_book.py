import streamlit as st  # type: ignore
from models.about_account_book import Category, Payer, TransactionType, FinancialTransaction
import pandas as pd # type: ignore
from tools.db_init import get_engine

st.title('家計簿')
# データベースエンジンとセッションの取得
engine, SessionLocal = get_engine()

# セッションの作成
session = SessionLocal()

# データベースにデータがあるか確認
if not session.query(FinancialTransaction).first():
    st.write('データがありません')
    st.stop()

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
    .limit(100)
)

df = pd.read_sql(query.statement, query.session.bind)

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