# Face Recognition System

顔認識システムは、Webカメラを使用してリアルタイムで顔を検出し、登録された人物を識別するシステムです。

## 必要条件

- Docker
- Docker Compose
- Webカメラ

## 環境構築

1. リポジトリをクローン：

```bash
git clone https://github.com/gundai-security-samurai/face_recognition.git
cd face_recognition
```

2. 環境変数の設定：
`.env`ファイルを作成し、以下の内容を設定：

```env
API_ENDPOINT=<your-api-endpoint>
```

3. Dockerイメージのビルドと起動：

```bash
docker-compose up --build
```

## 使用方法

### 1. 顔画像の登録

1. `data/input` ディレクトリを作成
2. 登録したい人物の顔画像を配置
   - サポートする形式: `.jpg`, `.jpeg`, `.png`
   - ファイル名が人物名として使用されます（例：`yamada.jpg`）
   - 1枚の画像につき1つの顔を含むようにしてください

### 2. システムの実行

システムが起動すると、以下の処理が自動的に実行されます：

- Webカメラからのリアルタイム映像取得
- 顔の検出と登録済み人物との照合
- 人物を検出した場合、指定されたAPIエンドポイントに通知
  - 同一人物の検出は30秒間隔で制限されています

### 3. 表示設定

`main.py`の`DISPLAY_VIDEO`フラグを変更することで、映像表示の有無を制御できます：
- `True`: 検出結果を含む映像をリアルタイム表示
- `False`: バックグラウンドで実行（デフォルト）

### 4. システムの終了

1. Docker Composeを停止：

```bash
docker-compose down
```

## 注意事項

- Webカメラへのアクセス権限が必要です
- 十分な照明環境で使用してください
- プライバシーに配慮して使用してください

## 技術スタック

- Python 3.10
- face_recognition
- OpenCV
- Docker
- FastAPI