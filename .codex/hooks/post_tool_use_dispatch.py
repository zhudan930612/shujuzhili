from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT_POSIX = REPO_ROOT.as_posix().lower()
SCOPE_ORDER = ["repo", "workbench", "prd", "prototypes"]
SCOPE_LABELS = {
    "repo": "repo",
    "workbench": "workbench",
    "prd": "prd",
    "prototypes": "prototypes",
}
PATH_KEYS = {
    "path",
    "paths",
    "file",
    "files",
    "file_path",
    "filepath",
    "filename",
    "target",
    "targets",
    "target_file",
    "target_path",
    "output_path",
    "output_file",
    "destination",
    "dest",
    "uri",
    "uris",
}
REPO_PREFIXES = (
    "00-项目总览/",
    "01-产品架构/",
    "05-来源资料/",
    "06-工具脚本/",
    ".codex/",
)
EXCLUDED_PREFIXES = ("90-归档记录/",)
MAX_CONTEXT_LEN = 4000


def load_event() -> dict[str, Any]:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {}

    return payload if isinstance(payload, dict) else {}


def normalize_repo_relative(value: str) -> str | None:
    text = value.strip().strip("'\"")
    if not text:
        return None

    text = text.replace("\\", "/")
    if text.startswith("file://"):
        text = text[7:]
        if text.startswith("/"):
            text = text[1:]

    lower = text.lower()
    if lower.startswith(REPO_ROOT_POSIX + "/"):
        relative = text[len(REPO_ROOT.as_posix()) + 1 :]
    else:
        relative = text.removeprefix("./")

    if not relative or relative.startswith("../"):
        return None

    candidate = (REPO_ROOT / relative).resolve(strict=False)
    try:
        normalized = candidate.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return None

    return normalized


def add_candidate_paths(container: set[str], value: Any) -> None:
    if isinstance(value, str):
        normalized = normalize_repo_relative(value)
        if normalized:
            container.add(normalized)
        return

    if isinstance(value, list):
        for item in value:
            add_candidate_paths(container, item)


def extract_paths(node: Any, *, parent_key: str | None = None) -> set[str]:
    paths: set[str] = set()

    if isinstance(node, dict):
        for key, value in node.items():
            key_lower = key.lower()
            if key_lower in PATH_KEYS:
                add_candidate_paths(paths, value)
            paths.update(extract_paths(value, parent_key=key_lower))
        return paths

    if isinstance(node, list):
        for item in node:
            paths.update(extract_paths(item, parent_key=parent_key))
        return paths

    if parent_key in PATH_KEYS and isinstance(node, str):
        add_candidate_paths(paths, node)

    return paths


def resolve_scope(relative_path: str) -> str | None:
    relative_path = relative_path.replace("\\", "/")
    path_name = PurePosixPath(relative_path).name

    if any(relative_path.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
        return None

    if relative_path == "AGENTS.md" or path_name == "README.md":
        return "repo"

    if any(relative_path.startswith(prefix) for prefix in REPO_PREFIXES):
        return "repo"

    if relative_path.startswith("03-工作台/"):
        return "workbench"

    if relative_path.startswith("02-PRD文档/"):
        return "prd"

    if relative_path.startswith("04-原型效果图/后台管理/"):
        return "prototypes"

    return None


def collect_scopes(event: dict[str, Any]) -> list[str]:
    tool_name = str(event.get("tool_name", "")).strip()
    if tool_name not in {"Edit", "Write"}:
        return []

    paths = extract_paths(event.get("tool_input", {}))
    selected = {scope for path in paths if (scope := resolve_scope(path))}
    return [scope for scope in SCOPE_ORDER if scope in selected]


def run_scope(scope: str) -> str:
    result = subprocess.run(
        ["python", "06-工具脚本/run_checks.py", "--scope", scope],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = (result.stdout + result.stderr).strip()
    if not output:
        return ""
    return f"[{SCOPE_LABELS[scope]} check] {output}"


def truncate_sections(sections: list[str]) -> str:
    if len(sections) == 1:
        return sections[0][:MAX_CONTEXT_LEN]

    max_per_section = max(800, MAX_CONTEXT_LEN // len(sections))
    truncated: list[str] = []
    for section in sections:
        if len(section) > max_per_section:
            truncated.append(section[: max_per_section - 4] + " ...")
        else:
            truncated.append(section)
    return "\n\n".join(truncated)[:MAX_CONTEXT_LEN]


def main() -> None:
    event = load_event()
    scopes = collect_scopes(event)
    if not scopes:
        print("{}")
        return

    sections = [section for scope in scopes if (section := run_scope(scope))]
    if not sections:
        print("{}")
        return

    payload = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": truncate_sections(sections),
        }
    }
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
