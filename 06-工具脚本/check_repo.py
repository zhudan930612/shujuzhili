#!/usr/bin/env python
from __future__ import annotations

import re
import sys
from pathlib import Path

from check_common import (
    CheckResult,
    Issue,
    MARKDOWN_LINK_RE,
    RELATIVE_TIME_RE,
    iter_markdown_files,
    normalize_link_target,
    print_issues,
    read_lines,
    should_skip_link,
)


AGENTS_MAX_LINES = 120
DISCUSSION_DOC_WARN_BYTES = 30000

REQUIRED_FILES = [
    Path("AGENTS.md"),
    Path("03-工作台/任务执行协议.md"),
    Path("03-工作台/任务完成检查.md"),
]

EXPECTED_ROOT_DIRS = {
    "00-项目总览",
    "01-产品架构",
    "02-PRD文档",
    "03-工作台",
    "04-原型效果图",
    "05-来源资料",
    "06-工具脚本",
    "90-归档记录",
}

README_REQUIRED_HEADINGS = ["## 目录定位", "## 主要内容"]

DEPRECATED_TERMS = {
    "ASCII 原型": "Use PRD ASCII 草图 or ASCII 草图 for PRD low-fi sketches.",
}

AGENTS_FORBIDDEN_DETAILS = {
    "视觉基线": "Move backend visual details to 04-原型效果图/后台管理/README.md.",
    "组件优先原则": "Move backend component details to 04-原型效果图/后台管理/README.md.",
    "Excel 模板规则": "Move template details to 04-原型效果图/后台管理/模板文件/README.md.",
    "后台列表页 ASCII": "Move PRD ASCII sketch rules to 02-PRD文档/README.md.",
    "原型修改前检查清单": "Move backend prototype checks to 04-原型效果图/后台管理/README.md.",
}


def run_checks(root: Path) -> CheckResult:
    root = root.resolve()
    result = CheckResult()
    check_required_files(root, result)
    check_agents_length(root, result)
    check_agents_forbidden_details(root, result)
    check_deprecated_terms(root, result)
    check_markdown_links(root, result)
    check_relative_time(root, result)
    check_large_discussion_doc(root, result)
    check_root_directories(root, result)
    check_readme_headings(root, result)
    check_agents_directory_entries(root, result)
    check_root_readme_references(root, result)
    return result


def check_required_files(root: Path, result: CheckResult) -> None:
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            result.add(
                Issue(
                    "ERROR",
                    rel_path,
                    None,
                    "Missing required file.",
                    "Missing harness files prevent AI from following the project workflow.",
                    "Restore required harness file.",
                )
            )


def check_agents_length(root: Path, result: CheckResult) -> None:
    rel_path = Path("AGENTS.md")
    path = root / rel_path
    if not path.exists():
        return

    line_count = len(read_lines(path))
    if line_count > AGENTS_MAX_LINES:
        result.add(
            Issue(
                "ERROR",
                rel_path,
                None,
                f"AGENTS.md has {line_count} lines, limit {AGENTS_MAX_LINES}.",
                "Large top-level instructions increase context load.",
                "Move topic-specific rules to directory README; keep AGENTS as map.",
            )
        )


def check_agents_forbidden_details(root: Path, result: CheckResult) -> None:
    rel_path = Path("AGENTS.md")
    path = root / rel_path
    if not path.exists():
        return

    for line_no, line in enumerate(read_lines(path), start=1):
        for term, fix in AGENTS_FORBIDDEN_DETAILS.items():
            if term in line:
                result.add(
                    Issue(
                        "ERROR",
                        rel_path,
                        line_no,
                        f"Topic detail found in AGENTS.md: {term}",
                        "Topic details in AGENTS.md make the top-level map harder for AI to scan.",
                        fix,
                    )
                )


def check_deprecated_terms(root: Path, result: CheckResult) -> None:
    for path in iter_markdown_files(root):
        rel_path = path.relative_to(root)
        for line_no, line in enumerate(read_lines(path), start=1):
            for term, fix in DEPRECATED_TERMS.items():
                if term in line:
                    result.add(
                        Issue(
                            "ERROR",
                            rel_path,
                            line_no,
                            f"Deprecated term found: {term}",
                            "Mixed terminology causes inconsistent future edits.",
                            fix,
                        )
                    )


def check_relative_time(root: Path, result: CheckResult) -> None:
    for path in iter_markdown_files(root):
        rel_path = path.relative_to(root)
        for line_no, line in enumerate(read_lines(path), start=1):
            for match in RELATIVE_TIME_RE.finditer(line):
                result.add(
                    Issue(
                        "WARN",
                        rel_path,
                        line_no,
                        f"Relative time expression found: {match.group()}",
                        "Relative time expressions rot over time and become inaccurate.",
                        "Replace with an absolute date (e.g., 2026-04-29) or remove the time reference.",
                    )
                )


def check_markdown_links(root: Path, result: CheckResult) -> None:
    for path in iter_markdown_files(root):
        rel_path = path.relative_to(root)
        for line_no, line in enumerate(read_lines(path), start=1):
            for match in MARKDOWN_LINK_RE.finditer(line):
                target = normalize_link_target(match.group(1))
                if should_skip_link(target):
                    continue

                target_path = (path.parent / target).resolve()
                try:
                    target_path.relative_to(root)
                except ValueError:
                    result.add(
                        Issue(
                            "ERROR",
                            rel_path,
                            line_no,
                            f"Markdown link points outside repository: {match.group(1)}",
                            "AI cannot safely follow context links outside the repository record.",
                            "Keep links inside repository or use an explicit external URL.",
                        )
                    )
                    continue

                if not target_path.exists():
                    result.add(
                        Issue(
                            "ERROR",
                            rel_path,
                            line_no,
                            f"Broken Markdown link: {match.group(1)}",
                            "AI cannot follow stale context links.",
                            "Correct the relative path or remove stale reference.",
                        )
                    )


def check_large_discussion_doc(root: Path, result: CheckResult) -> None:
    rel_path = Path("03-工作台/需求沟通模板.md")
    path = root / rel_path
    if not path.exists():
        return

    size = path.stat().st_size
    if size > DISCUSSION_DOC_WARN_BYTES:
        result.add(
            Issue(
                "WARN",
                rel_path,
                None,
                f"Current discussion doc is large: {size} bytes, warning threshold {DISCUSSION_DOC_WARN_BYTES}.",
                "Large process documents increase context rot risk.",
                "Move stable rules to PRD; keep process, tradeoffs, summary, links.",
            )
        )


def check_root_directories(root: Path, result: CheckResult) -> None:
    ignored_dirs = {".git", ".claude"}
    for path in root.iterdir():
        if not path.is_dir() or path.name in ignored_dirs:
            continue
        if path.name not in EXPECTED_ROOT_DIRS:
            result.add(
                Issue(
                    "WARN",
                    Path(path.name),
                    None,
                    f"Unexpected root directory: {path.name}",
                    "Unexpected root folders make repository navigation less predictable for AI.",
                    "Confirm the directory is needed; otherwise move it under an existing numbered directory.",
                )
            )


def check_readme_headings(root: Path, result: CheckResult) -> None:
    for dirname in EXPECTED_ROOT_DIRS:
        readme = root / dirname / "README.md"
        if not readme.exists():
            continue

        text = readme.read_text(encoding="utf-8")
        for heading in README_REQUIRED_HEADINGS:
            if heading not in text:
                result.add(
                    Issue(
                        "WARN",
                        readme.relative_to(root),
                        None,
                        f"README missing heading: {heading}",
                        "Consistent README sections help AI locate local rules quickly.",
                        "Add the standard README section or explain why this directory needs a different structure.",
                    )
                )


def check_agents_directory_entries(root: Path, result: CheckResult) -> None:
    agents = root / "AGENTS.md"
    if not agents.exists():
        return

    text = agents.read_text(encoding="utf-8")
    for dirname in EXPECTED_ROOT_DIRS:
        if (root / dirname).exists() and f"`{dirname}" not in text:
            result.add(
                Issue(
                    "ERROR",
                    Path("AGENTS.md"),
                    None,
                    f"AGENTS.md missing root directory entry: {dirname}/",
                    "AGENTS.md is the top-level map; missing directories hide context from AI.",
                    "Add the root directory to AGENTS.md key files/directories table.",
                )
            )


def check_root_readme_references(root: Path, result: CheckResult) -> None:
    for path in iter_markdown_files(root):
        rel_path = path.relative_to(root)
        for line_no, line in enumerate(read_lines(path), start=1):
            if "../README.md" in line:
                result.add(
                    Issue(
                        "WARN",
                        rel_path,
                        line_no,
                        "Root README reference found: ../README.md",
                        "A missing root README sends AI to a dead navigation path.",
                        "This repository currently uses AGENTS.md as the top-level map; link to AGENTS.md unless a root README is created.",
                    )
                )


def main() -> int:
    root = Path.cwd()
    result = run_checks(root)
    print_issues(result)
    return 1 if result.errors else 0


if __name__ == "__main__":
    sys.exit(main())

