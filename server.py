from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
import base64
import os
import subprocess
import threading
import signal
import psutil

class MainProcess:
    def __init__(self):
        self.process = None
        self.should_run = True

    def start(self):
        if self.process is None or self.process.poll() is not None:
            self.process = subprocess.Popen(["python3", "main.py"])

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.send_signal(signal.SIGTERM)
            self.process.wait()
        self.should_run = False

    def restart(self):
        self.stop()
        self.should_run = True
        self.start()
        print("顔認識スクリプトをi再起動しました。")

main_process = MainProcess()

@asynccontextmanager
async def lifespan(app: FastAPI):
    main_process.start()
    yield
    main_process.stop()

app = FastAPI(lifespan=lifespan)

class ImageData(BaseModel):
    name: str
    data_url: str

@app.post("/upload")
async def upload_image(image_data: ImageData):
    try:
        # Data URLからbase64部分を抽出
        base64_data = image_data.data_url.split(',')[1]
        
        # base64をデコード
        image_bytes = base64.b64decode(base64_data)
        
        # ファイル名を作成（拡張子はjpgとする）
        filename = f"{image_data.name}.jpg"
        filepath = os.path.join('/data/input', filename)
        
        # 画像を保存
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
            
        # main.pyをリスタート
        main_process.restart()
        
        return {"message": "画像がアップロードされ、認識プロセスを再起動しました"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000) 