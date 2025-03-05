FROM python:3.9

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリのコードをコピー
COPY . /app/

# 必要なパッケージをインストール（もし必要なパッケージがあれば）
RUN apt-get update && apt-get install -y ncurses-bin && rm -rf /var/lib/apt/lists/*

# ポートを指定
EXPOSE 5000

# gunicorn を使って Flask アプリケーションを実行
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

