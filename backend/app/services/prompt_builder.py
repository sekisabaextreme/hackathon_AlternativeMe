from __future__ import annotations

from pathlib import Path


LVL_LABEL = {"high": "高", "medium": "中", "low": "低"}
REPO_ROOT = Path(__file__).resolve().parents[3]
BRANCH_OUTPUT_RULES = """
Return JSON only.
Use this schema:
{
  "branches": [
    {
      "event": "string",
      "stability": "high|medium|low",
      "challenge": "high|medium|low",
      "event_type": "instant_event|progression_event",
      "duration_years": 0
    }
  ]
}
Rules:
- instant_event must use duration_years = 0
- progression_event must use duration_years >= 1
- Do not include year or age in the output
""".strip()

BRANCH_PROMPT_FILES = {
    "short": "bunki_prompt_short.txt",
    "normal": "bunki_prompt.txt",
    "long": "bunki_prompt_long.txt",
}


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
    system = "人生分岐シミュレーションの分岐候補を JSON だけで返してください。"
    story_summary = " -> ".join(history) if history else "まだ履歴はありません。"
    prompt_filename = BRANCH_PROMPT_FILES.get(profile.get("branch_timing", "normal"), "bunki_prompt.txt")
    message = _fill_prompt(
        _load_prompt_file(prompt_filename),
        {
            "age": str(profile["current_age"]),
            "values": profile.get("values", ""),
            "interests": profile.get("interests", profile.get("values", "")),
            "personality": profile.get("personality", ""),
            "mbti": profile.get("mbti", ""),
            "current_event": event,
            "story_summary": story_summary,
        },
    )
    return system, f"{message}\n\n{BRANCH_OUTPUT_RULES}"


def build_result_prompt(profile: dict[str, str], event: str, history: list[str]) -> tuple[str, str]:
    system = "人生分岐シミュレーションの結果を JSON だけで返してください。"
    story_summary = " -> ".join(history[-4:]) if history else "まだストーリー履歴はありません。"
    message = _fill_prompt(
        _load_prompt_file("out_prompt.txt"),
        {
            "age": str(profile["current_age"]),
            "values": profile.get("values", ""),
            "interests": profile.get("interests", profile.get("values", "")),
            "personality": profile.get("personality", ""),
            "mbti": profile.get("mbti", ""),
            "story_summary": story_summary,
            "selected_branch": event,
        },
    )
    return system, message


def build_story_prompt(profile: dict[str, str], nodes: list[dict[str, str]]) -> tuple[str, str]:
    system = "人生分岐シミュレーションの要約を JSON だけで返してください。"
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
            "mbti": profile.get("mbti", ""),
            "route_history": route_history,
            "result_history": result_history,
        },
    )
    return system, message
