# ベースイメージ
FROM python:3.10.15

# 作業ディレクトリの設定
WORKDIR /app

RUN apt-get update && apt-get install -y cmake build-essential libboost-dev
RUN pip install --upgrade setuptools wheel
RUN pip install pyarrow --upgrade --prefer-binary
RUN pip install streamlit
RUN pip install mysql-connector-python
RUN pip install sqlalchemy pymysql cryptography
RUN pip install pandas

# ポートの指定
EXPOSE 8501