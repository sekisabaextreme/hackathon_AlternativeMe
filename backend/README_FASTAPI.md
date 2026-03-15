# FastAPI + htmx 構成

このディレクトリは、FastAPI + htmx と OpenAI API で人生分岐シミュレーターを動かすための実装です。

## 起動方法

1. Python 仮想環境を作成
2. `pip install -r backend/requirements.txt`
3. `.env.local` または環境変数に `OPENAI_API_KEY` を設定
4. 必要なら `OPENAI_MODEL` を設定
5. `uvicorn backend.app.main:app --reload --env-file .env.local`

## 主な責務

- `backend/app/main.py`
  - FastAPI 本体の起動設定
- `backend/app/routes/pages.py`
  - 画面遷移と htmx 更新
- `backend/app/services/simulator.py`
  - シミュレーターの状態管理
- `backend/app/services/openai_service.py`
  - OpenAI API 呼び出し
- `backend/app/templates/`
  - HTML テンプレート
- `backend/app/static/`
  - 静的ファイル
