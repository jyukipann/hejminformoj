import os
from sqlalchemy.orm import sessionmaker # type: ignore
from sqlalchemy import create_engine, text # type: ignore
from models.about_account_book import Category, Payer, TransactionType, FinancialTransaction
from models.about_users import User, Passkey
from models.base_model import Base

# docker container exec -it hejminformoj-db-1 bash
# mysql -u root -p$MYSQL_ROOT_PASSWORD
# DROP DATABASE household_accounts;

# データベースの設定と初期化
def get_engine():
    DB_HOST = "db"  # Dockerのホスト名
    DB_USER = "root"
    DB_PASSWORD = os.environ.get("MYSQL_ROOT_PASSWORD")
    DB_NAME = "household_accounts"
    
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
    Base.metadata.create_all(bind=engine)
    return engine, SessionLocal