"""役割: シミュレーション進行中の状態遷移を担当する。"""

from __future__ import annotations

import asyncio
import copy
import uuid
from typing import Any

from .llm_gateway import call_llm
from .openai_service import parse_json_text
from .prompt_builder import build_branch_prompt, build_result_prompt, build_story_prompt


def _refresh_derived(state: dict[str, Any]) -> dict[str, Any]:
    nodes = state.get("nodes", [])
    current_node = next((node for node in nodes if node["id"] == state.get("current_node_id")), None)
    state["current_node"] = current_node
    state["selected_nodes"] = [node for node in nodes if node.get("selected")]
    return state


def _new_id() -> str:
    return uuid.uuid4().hex[:8]


async def _generate_branches(profile: dict[str, Any], event: str, history: list[str]) -> list[dict[str, Any]]:
    system, message = build_branch_prompt(profile, event, history)
    text = await asyncio.to_thread(call_llm, profile.get("provider", "openai"), system, message, True)
    parsed = parse_json_text(text)
    branches = parsed.get("branches", [])
    if not branches:
        raise ValueError("分岐候補を生成できませんでした。")

    return [
        {
            "id": _new_id(),
            "event": branch.get("event", "新しい分岐"),
            "stability": branch.get("stability", "medium"),
            "challenge": branch.get("challenge", "medium"),
            "selected": False,
        }
        for branch in branches[:2]
    ]


async def start_simulation(state: dict[str, Any], event: str) -> dict[str, Any]:
    new_state = copy.deepcopy(state)
    try:
        root = {
            "id": _new_id(),
            "event": event.strip(),
            "stability": "medium",
            "challenge": "medium",
            "selected": True,
            "parent_id": None,
        }
        new_state["nodes"] = [root]
        new_state["current_node_id"] = root["id"]
        new_state["branches"] = await _generate_branches(new_state["profile"], root["event"], [])
        for branch in new_state["branches"]:
            branch["parent_id"] = root["id"]
        new_state["stage"] = "branches"
        new_state["panel"] = "main"
        new_state["error"] = ""
    except Exception as exc:
        new_state["stage"] = "event"
        new_state["error"] = str(exc)
    return _refresh_derived(new_state)


def get_branch_by_id(state: dict[str, Any], branch_id: str) -> dict[str, Any]:
    branch = next((branch for branch in state.get("branches", []) if branch["id"] == branch_id), None)
    if not branch:
        raise ValueError("分岐候補が見つかりません。")
    return branch


async def select_branch(state: dict[str, Any], branch: dict[str, Any]) -> dict[str, Any]:
    new_state = copy.deepcopy(state)
    try:
        history = [node["event"] for node in new_state.get("nodes", []) if node.get("selected")]
        system, message = build_result_prompt(new_state["profile"], branch["event"], history)
        text = await asyncio.to_thread(call_llm, new_state.get("provider", "openai"), system, message, True)
        parsed = parse_json_text(text)
        selected_branch = {
            **branch,
            "selected": True,
            "result": parsed.get("result_summary", parsed.get("result", "結果を生成できませんでした。")),
            "happiness": parsed.get("happiness", "medium"),
        }
        others = [{**item, "selected": False} for item in new_state["branches"] if item["id"] != branch["id"]]
        new_state["nodes"].append(selected_branch)
        new_state["nodes"].extend(others)
        new_state["branches"] = []
        new_state["current_node_id"] = selected_branch["id"]
        new_state["stage"] = "result"
        new_state["panel"] = "main"
        new_state["error"] = ""
    except Exception as exc:
        new_state["error"] = str(exc)
    return _refresh_derived(new_state)


def add_custom_branch(state: dict[str, Any], event: str) -> dict[str, Any]:
    new_state = copy.deepcopy(state)
    try:
        current_id = new_state.get("current_node_id")
        if not current_id:
            raise ValueError("基準となるノードが見つかりません。")
        new_state["branches"].append(
            {
                "id": _new_id(),
                "event": event.strip(),
                "stability": "medium",
                "challenge": "medium",
                "selected": False,
                "parent_id": current_id,
            }
        )
        new_state["stage"] = "branches"
        new_state["panel"] = "main"
        new_state["error"] = ""
    except Exception as exc:
        new_state["error"] = str(exc)
    return _refresh_derived(new_state)


async def continue_simulation(state: dict[str, Any]) -> dict[str, Any]:
    new_state = copy.deepcopy(state)
    try:
        current = next((node for node in new_state["nodes"] if node["id"] == new_state["current_node_id"]), None)
        if not current:
            raise ValueError("現在のノードが見つかりません。")
        history = [node["event"] for node in new_state["nodes"] if node.get("selected")]
        new_state["branches"] = await _generate_branches(new_state["profile"], current["event"], history)
        for branch in new_state["branches"]:
            branch["parent_id"] = current["id"]
        new_state["stage"] = "branches"
        new_state["panel"] = "main"
        new_state["error"] = ""
    except Exception as exc:
        new_state["error"] = str(exc)
    return _refresh_derived(new_state)


async def generate_story(state: dict[str, Any]) -> dict[str, Any]:
    new_state = copy.deepcopy(state)
    try:
        if not new_state.get("profile"):
            new_state["panel"] = "story"
            new_state["story"] = ""
            new_state["error"] = ""
            return _refresh_derived(new_state)

        selected_nodes = [node for node in new_state["nodes"] if node.get("selected")]
        if not selected_nodes:
            new_state["panel"] = "story"
            new_state["story"] = ""
            new_state["error"] = ""
            return _refresh_derived(new_state)

        system, message = build_story_prompt(new_state["profile"], selected_nodes)
        text = await asyncio.to_thread(call_llm, new_state.get("provider", "openai"), system, message, True)
        parsed = parse_json_text(text)
        new_state["story"] = parsed.get("story_summary", "")
        new_state["panel"] = "story"
        new_state["error"] = ""
    except Exception as exc:
        new_state["error"] = str(exc)
    return _refresh_derived(new_state)
