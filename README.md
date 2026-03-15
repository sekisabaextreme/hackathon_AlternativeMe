# FastAPI + htmx Life Branches

FastAPI と htmx で動く人生分岐シミュレーターです。設定画面で `OpenAI` と `Gemini` のどちらを使うか選べます。

## 起動方法

1. 依存関係をインストールします。

```bash
python -m pip install -r backend/requirements.txt
```

2. `.env.local` に使いたい API キーを設定します。

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4.1-mini

GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash
```

3. 開発サーバーを起動します。

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload --env-file .env.local
```

4. ブラウザで `http://127.0.0.1:8000` を開きます。

## 構成

- `backend/app/main.py`
  - FastAPI のエントリポイント
- `backend/app/routes/pages.py`
  - 画面ルーティングと htmx 更新
- `backend/app/services/simulator.py`
  - シミュレーション状態管理と LLM 呼び出し振り分け
- `backend/app/services/openai_service.py`
  - OpenAI API 呼び出し
- `backend/app/services/gemini_service.py`
  - Gemini API 呼び出し
- `backend/app/templates/`
  - HTML テンプレート
- `backend/app/static/`
  - CSS などの静的ファイル

## API キー管理

`.env.local` は `.gitignore` で除外されているため、API キーは GitHub に含まれません。
