import streamlit as st  # type: ignore
from models.about_account_book import Category, Payer, TransactionType, FinancialTransaction
import pandas as pd # type: ignore
from tools.db_init import get_engine
import datetime
from sqlalchemy import func
from tools.simple_auth import check_password
if not check_password():
    st.stop()

st.title('家計簿')
st.sidebar.link_button('DB', url='http://jyukipann.com:7611', icon=":material/database:")

# データベースエンジンとセッションの取得
engine, SessionLocal = get_engine()

with SessionLocal() as session:
    # データベースにデータがあるか確認
    if not session.query(FinancialTransaction).first():
        st.write('データがありません')
        st.stop()

if 'search_filters' not in st.session_state:
    today = datetime.date.today()
    start_data = today.replace(day=1)
    end_data = (
        today.replace(day=1, month=today.month+1) - datetime.timedelta(days=1))
    st.session_state['search_filters'] = {
        'is_filter_by_date': False,
        'date': (start_data, end_data), # start to end
        'categories': [],
        'payers': [],
        'transaction_types': [],
        'is_split_bill': [],
        'limit': 50,
    }

with st.expander('Filters', expanded=True):
    filters = st.session_state['search_filters']
    filters['is_filter_by_date'] = st.checkbox('Filter by date', value=False)
    start_date = st.date_input(
        'start date', 
        filters['date'][0],
        disabled= not filters['is_filter_by_date'])
    end_date = st.date_input(
        'end date', 
        filters['date'][1],
        disabled=not filters['is_filter_by_date'])
    
    with SessionLocal() as session:
    # 各フィルターの選択項目を定義
        category_options = [c.name for c in session.query(Category).all()]
        payer_options = [p.name for p in session.query(Payer).all()]
        transaction_type_options = [t.name for t in session.query(TransactionType).all()]
    
    categories = st.multiselect('categories', category_options)
    filters['categories'] = categories

    payers = st.multiselect('Payer', payer_options, payer_options)
    filters['payers'] = payers

    transaction_types = st.multiselect('取引種別', transaction_type_options)
    filters['transaction_types'] = transaction_types

    split_bill_options = ["割り勘", "not割り勘"]
    split_bill_options = st.multiselect('割り勘', split_bill_options, split_bill_options)
    filters['is_split_bill'] = split_bill_options

    limit = st.selectbox("最大数件数", [50, 100, 200, 300, "あるだけ全部", ])
    filters['limit'] = limit

# st.write(filters)

# フィルターを適用する関数
@st.cache_data
def filter_account_book(filters):
    with SessionLocal() as session:
        # ベースクエリを作成
        FT = FinancialTransaction
        query = (
            session.query(
                FT.id,
                FT.description,
                FT.date,
                Category.name.label('category'),
                FT.amount,
                Payer.name.label('payer'),
                FT.is_split_bill,
                TransactionType.name.label('transaction_type'),
            )
            .join(Category, FT.category_id == Category.id)
            .join(Payer, FT.payer_id == Payer.id)
            .join(TransactionType, FT.transaction_type_id == TransactionType.id)
        )
        
        if filters.get('date') and filters['is_filter_by_date']:
            query = query.filter(FT.date.between(*filters['date']))

        if filters.get('categories'):
            query = query.filter(Category.name.in_(filters['categories']))

        if filters.get('payers'):
            query = query.filter(Payer.name.in_(filters['payers']))

        if filters.get('transaction_types'):
            query = query.filter(TransactionType.name.in_(filters['transaction_types']))

        if filters.get('is_split_bill'):
            if "割り勘" in filters['is_split_bill'] and "not割り勘" not in filters['is_split_bill']:
                query = query.filter(FT.is_split_bill == True)
            elif "not割り勘" in filters['is_split_bill'] and "割り勘" not in filters['is_split_bill']:
                query = query.filter(FT.is_split_bill == False)

        # dateでソート
        query = query.order_by(FT.date.desc())

        if isinstance(filters.get('limit'), int):  # "あるだけ全部" 以外の時
            query = query.limit(filters['limit'])

        df = pd.read_sql(query.statement, query.session.bind)
    return df


df = filter_account_book(filters)

selected = st.dataframe(
    df.drop(columns=['id']),
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

# chart space
st.markdown('---')
st.markdown('## Chart')
st.markdown('### 総支出')
@st.cache_data
def get_total_amount():
    with SessionLocal() as session:
        query = session.query(func.sum(FinancialTransaction.amount))
        total_amount = query.scalar()
    return total_amount
total_amount = get_total_amount()
st.markdown(f'総支出: {total_amount}円')

left_column, right_column = st.columns(2)
# データの読み込み
# 棒グラフ（支払者別）カテゴリも考慮したい
with left_column:
    st.markdown('### 支払者別 (カテゴリ別)')
    @st.cache_data
    def get_payer_category_total_amount():
        with SessionLocal() as session:
            query = (
                session.query(
                    Payer.name,
                    Category.name.label('category'),
                    func.sum(FinancialTransaction.amount).label('total_amount')
                )
                .join(Payer, FinancialTransaction.payer_id == Payer.id)
                .join(Category, FinancialTransaction.category_id == Category.id)
                .group_by(Payer.name, Category.name)
            )
            df = pd.read_sql(query.statement, query.session.bind)
            df.sort_values('name', ascending=False, inplace=True)
        return df
    df = get_payer_category_total_amount()
    
    st.bar_chart(df, x='name', y='total_amount', color='category')
    with st.expander('Data'):
        st.write(df)
    # st.bar_chart(df.set_index(['name', 'category']).unstack())
with right_column:
    # 割り勘を考慮した棒グラフ（支払者別）　カテゴリも考慮したい
    st.markdown('### 割り勘 (カテゴリ別)')
    @st.cache_data
    def get_split_bill_payer_category_total_amount():
        with SessionLocal() as session:
            query = (
                session.query(
                    Payer.name,
                    Category.name.label('category'),
                    func.sum(FinancialTransaction.amount).label('total_amount')
                )
                .join(Category, FinancialTransaction.category_id == Category.id)
                .join(Payer, FinancialTransaction.payer_id == Payer.id)
                .filter(FinancialTransaction.is_split_bill == True)
                .group_by(Payer.name, Category.name)
            )
            df = pd.read_sql(query.statement, query.session.bind)
            df.sort_values('name', ascending=False, inplace=True)
        return df
    df = get_split_bill_payer_category_total_amount()
    st.bar_chart(df, x='name', y='total_amount', color='category')
    with st.expander('Data'):
        st.write(df)

# 月ごとの支出 カテゴリごとにしたい
st.markdown('### 月ごとの支出 (カテゴリ別)')
@st.cache_data
def get_monthly_category_total_amount():
    with SessionLocal() as session:
        query = (
            session.query(
                func.date_format(FinancialTransaction.date, '%Y-%m').label('month'),
                Category.name.label('category'),
                func.sum(FinancialTransaction.amount).label('total_amount')
            )
            .join(Category, FinancialTransaction.category_id == Category.id)
            .group_by('month', 'category')
        )
        df = pd.read_sql(query.statement, query.session.bind)
    df['month'] = pd.to_datetime(df['month'])
    # format yyyy-mm-dd to yyyy-mm
    df['month'] = df['month'].dt.strftime('%Y-%m')
    # sort by month
    df = df.sort_values('month')
    df = df.set_index('month')
    return df
@st.cache_data
def sum_by_month(df):
    df = df.groupby('month').sum()
    df.drop(columns=['category'], inplace=True)
    return df

df = get_monthly_category_total_amount()
# st.write(df)
# st.write(df.index)
st.bar_chart(df, y='total_amount', color='category',horizontal=True)
with st.expander('Data'):
    st.write(sum_by_month(df))

