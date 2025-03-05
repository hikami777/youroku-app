FROM ubuntu:latest

#COPY colors.sh /home/render/colors.sh

# ベースイメージを指定
FROM python:3.9

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリのコードをコピー
COPY . /app/

# ポートを指定
EXPOSE 5000


# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    ncurses-bin \
    && rm -rf /var/lib/apt/lists/*

# アプリケーションのコードをコピー
COPY . /app
WORKDIR /app

# gunicorn のインストール
RUN pip install gunicorn


# colors.sh を修正
#RUN sed -i 's/$(tput setaf 1)/\\033[31m/g' /home/render/colors.sh && \
#    sed -i 's/$(tput setaf 2)/\\033[32m/g' /home/render/colors.sh && \
#    sed -i 's/$(tput sgr0)/\\033[0m/g' /home/render/colors.sh

# アプリケーションのセットアップ
COPY . /app
WORKDIR /app
#RUN ./setup.sh

# gunicorn を使って Flask アプリケーションを実行
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
