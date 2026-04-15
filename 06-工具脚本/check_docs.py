#!/usr/bin/env python
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote


AGENTS_MAX_LINES = 120
DISCUSSION_DOC_WARN_BYTES = 30000

REQUIRED_FILES = [
    Path("AGENTS.md"),
    Path("03-工作台/任务执行协议.md"),
    Path("03-工作台/任务完成检查.md"),
]

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

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


@dataclass(frozen=True)
class Issue:
    severity: str
    path: Path
    line: int | None
    message: str
    fix: str


@dataclass
class CheckResult:
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)

    def add(self, issue: Issue) -> None:
        if issue.severity == "ERROR":
            self.errors.append(issue)
        else:
            self.warnings.append(issue)


def run_checks(root: Path) -> CheckResult:
    root = root.resolve()
    result = CheckResult()

    check_required_files(root, result)
    check_agents_length(root, result)
    check_agents_forbidden_details(root, result)
    check_deprecated_terms(root, result)
    check_markdown_links(root, result)
    check_large_discussion_doc(root, result)

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
                            fix,
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
                            "Correct the relative path or remove stale reference.",
                        )
                    )


def check_large_discussion_doc(root: Path, result: CheckResult) -> None:
    rel_path = Path("03-工作台/当前需求沟通文档.md")
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
                "Move stable rules to PRD; keep process, tradeoffs, summary, links.",
            )
        )


def iter_markdown_files(root: Path):
    for path in root.rglob("*.md"):
        if ".git" in path.relative_to(root).parts:
            continue
        yield path


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def normalize_link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if not target:
        return target
    if " " in target:
        target = target.split()[0]
    target = target.split("#", 1)[0]
    return unquote(target)


def should_skip_link(target: str) -> bool:
    if not target:
        return True
    lower = target.lower()
    return (
        lower.startswith("http://")
        or lower.startswith("https://")
        or lower.startswith("mailto:")
        or target.startswith("#")
    )


def print_issues(result: CheckResult) -> None:
    for issue in result.errors + result.warnings:
        location = str(issue.path)
        if issue.line is not None:
            location = f"{location}:{issue.line}"
        print(f"{issue.severity}: {location}: {issue.message}")
        print(f"  Fix: {issue.fix}")

    if not result.errors and not result.warnings:
        print("OK: documentation checks passed.")


def main() -> int:
    root = Path.cwd()
    result = run_checks(root)
    print_issues(result)
    return 1 if result.errors else 0


if __name__ == "__main__":
    sys.exit(main())
