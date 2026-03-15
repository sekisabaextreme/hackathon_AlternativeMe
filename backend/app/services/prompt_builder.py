"""役割: txt テンプレートを読み込み、各用途のプロンプトを組み立てる。"""

from __future__ import annotations

from pathlib import Path


LVL_LABEL = {"high": "高", "medium": "中", "low": "低"}
REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_prompt_file(filename: str) -> str:
    path = REPO_ROOT / filename
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"{filename} が見つかりません。") from exc


def _fill_prompt(template: str, values: dict[str, str]) -> str:
    text = template
    for key, value in values.items():
        text = text.replace(f"{{{key}}}", value)
    return text


def build_branch_prompt(profile: dict[str, str], event: str, history: list[str]) -> tuple[str, str]:
    system = "以下の指示に厳密に従い、JSONのみで返答してください。"
    story_summary = " -> ".join(history) if history else "まだストーリー要約はありません。"
    message = _fill_prompt(
        _load_prompt_file("bunki_prompt.txt"),
        {
            "age": str(profile["current_age"]),
            "values": profile.get("values", ""),
            "interests": profile.get("interests", profile.get("values", "")),
            "personality": profile.get("personality", ""),
            "current_event": event,
            "story_summary": story_summary,
        },
    )
    return system, message


def build_result_prompt(profile: dict[str, str], event: str, history: list[str]) -> tuple[str, str]:
    system = "以下の指示に厳密に従い、JSONのみで返答してください。"
    story_summary = " -> ".join(history[-4:]) if history else "まだストーリー要約はありません。"
    message = _fill_prompt(
        _load_prompt_file("out_prompt.txt"),
        {
            "age": str(profile["current_age"]),
            "values": profile.get("values", ""),
            "interests": profile.get("interests", profile.get("values", "")),
            "personality": profile.get("personality", ""),
            "story_summary": story_summary,
            "selected_branch": event,
        },
    )
    return system, message


def build_story_prompt(profile: dict[str, str], nodes: list[dict[str, str]]) -> tuple[str, str]:
    system = "以下の指示に厳密に従い、JSONのみで返答してください。"
    route_history = " -> ".join(node["event"] for node in nodes)
    result_history = "\n".join(
        f"- {node['event']}: {node.get('result', '結果なし')} / 幸福度: {LVL_LABEL.get(node.get('happiness', 'medium'), '中')}"
        for node in nodes
    )
    message = _fill_prompt(
        _load_prompt_file("sum_prompt.txt"),
        {
            "age": str(profile["current_age"]),
            "values": profile.get("values", ""),
            "interests": profile.get("interests", profile.get("values", "")),
            "personality": profile.get("personality", ""),
            "route_history": route_history,
            "result_history": result_history,
        },
    )
    return system, message
