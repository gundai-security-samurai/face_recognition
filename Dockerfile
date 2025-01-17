# Pythonの軽量イメージを使用
FROM python:3.10.3-slim-bullseye

# 必要なシステムパッケージをインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-base-dev \
    libavcodec-dev \
    libavformat-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    software-properties-common \
    libgl1-mesa-glx \
    zip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# dlibのインストール
RUN git clone -b 'v19.9' --single-branch https://github.com/davisking/dlib.git /tmp/dlib && \
    cd /tmp/dlib && \
    python3 setup.py install --yes USE_AVX_INSTRUCTIONS && \
    rm -rf /tmp/dlib

# # アプリケーションコードをコンテナ内にコピー
WORKDIR /app
COPY . /app

# 必要なPythonパッケージをインストール
RUN pip3 install --no-cache-dir -r requirements.txt

# アプリケーションのエントリーポイントを設定
CMD ["python3", "server.py"]