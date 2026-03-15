"""役割: ルーティング共通の状態管理とテンプレート描画をまとめる。"""

from __future__ import annotations

from pathlib import Path
import uuid
from typing import Any

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..services.simulator import build_tree_view_model, initial_state


BASE_DIR = Path(__file__).resolve().parents[1]
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
SESSION_COOKIE_NAME = "life_branches_session_id"
SESSION_STORE: dict[str, dict[str, Any]] = {}

PROVIDER_OPTIONS = [
    {"value": "openai", "label": "OpenAI"},
    {"value": "gemini", "label": "Gemini"},
]

INTEREST_OPTIONS = [
    "研究",
    "安定",
    "ものづくり",
    "芸術",
    "スポーツ",
    "起業",
    "社会貢献",
    "国際交流",
    "教育",
    "医療",
    "環境",
    "AI",
    "デザイン",
    "音楽",
    "文学",
    "旅行",
    "リーダーシップ",
    "経済",
    "法律",
    "哲学",
    "地域活動",
    "ゲーム",
    "プログラミング",
    "データ分析",
]

PERSONALITY_OPTIONS = [
    "慎重",
    "好奇心が強い",
    "粘り強い",
    "社交的",
    "論理的",
    "行動力がある",
    "挑戦的",
    "協調的",
    "計画的",
    "柔軟",
    "責任感が強い",
    "負けず嫌い",
    "面倒見が良い",
    "自立志向",
    "観察力が高い",
    "感受性が高い",
    "冷静",
    "楽観的",
    "集中力が高い",
    "探究心が強い",
    "誠実",
    "発想力がある",
    "聞き上手",
    "芯が強い",
]


def ensure_session_id(request: Request) -> str:
    return request.cookies.get(SESSION_COOKIE_NAME) or uuid.uuid4().hex


def current_state(request: Request) -> tuple[str, dict[str, Any]]:
    session_id = ensure_session_id(request)
    state = SESSION_STORE.get(session_id)
    if not state:
        state = initial_state()
        SESSION_STORE[session_id] = state
    return session_id, state


def save_state(session_id: str, state: dict[str, Any]) -> None:
    SESSION_STORE[session_id] = state


def build_context(request: Request, state: dict[str, Any]) -> dict[str, Any]:
    return {
        "request": request,
        "state": state,
        "stage": state.get("stage", "setup"),
        "panel": state.get("panel", "main"),
        "error": state.get("error", ""),
        "profile": state.get("profile"),
        "branches": state.get("branches", []),
        "current_node": state.get("current_node"),
        "selected_nodes": state.get("selected_nodes", []),
        "tree_nodes": state.get("nodes", []),
        "tree_view": build_tree_view_model(state.get("nodes", [])),
        "story": state.get("story", ""),
        "provider_options": PROVIDER_OPTIONS,
        "interest_options": INTEREST_OPTIONS,
        "personality_options": PERSONALITY_OPTIONS,
    }


def attach_session_cookie(response: HTMLResponse, session_id: str) -> HTMLResponse:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        samesite="lax",
    )
    return response


def render_app(request: Request, session_id: str, state: dict[str, Any], status_code: int = 200) -> HTMLResponse:
    response = templates.TemplateResponse(
        request=request,
        name="partials/app.html",
        context=build_context(request, state),
        status_code=status_code,
    )
    return attach_session_cookie(response, session_id)


def render_index(request: Request, session_id: str, state: dict[str, Any]) -> HTMLResponse:
    response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context=build_context(request, state),
    )
    return attach_session_cookie(response, session_id)
