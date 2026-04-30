#!/usr/bin/env python
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote


MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
RELATIVE_TIME_RE = re.compile(
    r"今天|昨天|明天|前天|后天|刚刚|最近|近日|上周|本周|下周|上月|本月|下月|去年|今年|明年|月初|月底|年末|年初|星期[一二三四五六日]|周[一二三四五六日]"
)


@dataclass(frozen=True)
class Issue:
    severity: str
    path: Path
    line: int | None
    message: str
    why: str
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

    def extend(self, other: "CheckResult") -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)


def iter_markdown_files(root: Path):
    for path in root.rglob("*.md"):
        parts = path.relative_to(root).parts
        if ".git" in parts or "check_docs_tests_sandbox" in parts:
            continue
        yield path


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def print_issues(result: CheckResult) -> None:
    for issue in result.errors + result.warnings:
        location = str(issue.path)
        if issue.line is not None:
            location = f"{location}:{issue.line}"
        print(f"{issue.severity}: {location}: {issue.message}")
        print(f"  Why: {issue.why}")
        print(f"  Fix: {issue.fix}")


def normalize_link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    target = target.split("#", 1)[0]
    target = target.split("?", 1)[0]
    return unquote(target)


def should_skip_link(target: str) -> bool:
    if not target:
        return True
    lowered = target.lower()
    return (
        lowered.startswith("http://")
        or lowered.startswith("https://")
        or lowered.startswith("mailto:")
        or lowered.startswith("tel:")
    )


def iter_markdown_table_rows(lines: list[str], section_title: str):
    in_section = False
    header = None
    saw_separator = False
    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("#") and section_title in stripped:
            in_section = True
            header = None
            saw_separator = False
            continue
        if not in_section:
            continue
        if stripped.startswith("#") and section_title not in stripped:
            break
        if not stripped.startswith("|"):
            continue

        cells = split_markdown_row(stripped)
        if not header:
            header = cells
            continue
        if not saw_separator:
            saw_separator = True
            continue
        if header and len(cells) == len(header):
            yield index, dict(zip(header, cells))


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def normalize_heading_title(line: str) -> str:
    title = line.lstrip("#").strip()
    return re.sub(r"^\d+\.\s*", "", title)


def has_meaningful_link_or_path(value: str) -> bool:
    if not value:
        return False
    return "](" in value or "/" in value or "\\" in value or value.endswith(".md")


def has_archive_link(value: str) -> bool:
    return "90-归档记录" in value and has_meaningful_link_or_path(value)


def has_any_landing_status(lines: list[str], section_title: str, statuses: set[str]) -> bool:
    for _, row in iter_markdown_table_rows(lines, section_title):
        if row.get("状态", "").strip() in statuses:
            return True
    return False


def extract_heading_blocks(
    lines: list[str], heading_prefix: str
) -> list[tuple[str, int, list[str]]]:
    blocks: list[tuple[str, int, list[str]]] = []
    block_start = None
    block_heading = None
    prefix_level = len(heading_prefix.split()[0])

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(heading_prefix):
            if block_heading is not None and block_start is not None:
                blocks.append((block_heading, block_start, lines[block_start:index]))
            block_heading = stripped
            block_start = index
            continue
        if block_heading is not None and stripped.startswith("#"):
            current_level = len(stripped) - len(stripped.lstrip("#"))
            if current_level <= prefix_level:
                blocks.append((block_heading, block_start, lines[block_start:index]))
                block_heading = None
                block_start = None
    if block_heading is not None and block_start is not None:
        blocks.append((block_heading, block_start, lines[block_start:]))
    return blocks
