"""役割: FastAPI アプリ本体を起動し、分割済みルーターを登録する。"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routes import router


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Life Branches FastAPI")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(router)
