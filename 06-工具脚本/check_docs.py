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
CHECK_DOCS_COMMAND = "python 06-工具脚本/check_docs.py"
DISCUSSION_LANDING_CHECKLIST_TITLE = "拆回正式文档清单"
DISCUSSION_LANDING_CHECKLIST_COLUMNS = ["结论/规则", "主定义文档", "影响资产", "状态", "备注"]
REQUIREMENT_OUTPUT_FRAMEWORK_TITLE = "## 需求沟通输出框架"
REQUIREMENT_COMPLETENESS_CHECKLIST_TITLE = "## 需求完备性检查清单"
PAGE_REQUIREMENT_HEADING_RE = re.compile(r"^#####\s+Q\d+(?:-\d+)?\s+.+")
CONFIRMED_PAGE_ROW_RE = re.compile(r"^\|\s*(Q\d+(?:-\d+)?)\s*\|.*\|\s*已确认\s*\|")
PAGE_REQUIREMENT_CORE_HEADINGS = [
    "功能目标",
    "使用角色",
    "入口与权限",
    "页面结构",
    "ASCII 草图",
    "待确认/待研发项",
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
    check_completion_check_command(root, result)
    check_discussion_landing_checklist(root, result)
    check_requirement_output_framework(root, result)

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


def check_completion_check_command(root: Path, result: CheckResult) -> None:
    rel_path = Path("03-工作台/任务完成检查.md")
    path = root / rel_path
    if not path.exists():
        return

    text = path.read_text(encoding="utf-8")
    if CHECK_DOCS_COMMAND not in text:
        result.add(
            Issue(
                "ERROR",
                rel_path,
                None,
                "任务完成检查.md missing check_docs command.",
                "The completion checklist should point AI to the mechanical check command.",
                f"Add `{CHECK_DOCS_COMMAND}` to the task completion checklist.",
            )
        )


def check_discussion_landing_checklist(root: Path, result: CheckResult) -> None:
    rel_path = Path("03-工作台/当前需求沟通文档.md")
    path = root / rel_path
    if not path.exists():
        return

    text = path.read_text(encoding="utf-8")
    if DISCUSSION_LANDING_CHECKLIST_TITLE not in text:
        result.add(
            Issue(
                "WARN",
                rel_path,
                None,
                f"Current discussion doc missing {DISCUSSION_LANDING_CHECKLIST_TITLE}.",
                "Process conclusions can stay in chat or discussion docs without landing in source-of-truth files.",
                "Add a landing checklist with conclusion, source document, affected assets, status, and notes.",
            )
        )
        return

    missing_columns = [column for column in DISCUSSION_LANDING_CHECKLIST_COLUMNS if column not in text]
    if missing_columns:
        result.add(
            Issue(
                "WARN",
                rel_path,
                None,
                f"Landing checklist missing columns: {', '.join(missing_columns)}.",
                "Incomplete landing checklists make it hard for AI to verify whether conclusions reached source-of-truth files.",
                "Use columns: 结论/规则, 主定义文档, 影响资产, 状态, 备注.",
            )
        )


def check_requirement_output_framework(root: Path, result: CheckResult) -> None:
    protocol_rel_path = Path("03-工作台/任务执行协议.md")
    protocol_path = root / protocol_rel_path
    if protocol_path.exists():
        protocol_text = protocol_path.read_text(encoding="utf-8")
        if REQUIREMENT_OUTPUT_FRAMEWORK_TITLE not in protocol_text:
            result.add(
                Issue(
                    "WARN",
                    protocol_rel_path,
                    None,
                    f"任务执行协议.md missing {REQUIREMENT_OUTPUT_FRAMEWORK_TITLE}.",
                    "Without a fixed requirement output framework, complex demand discussions can become fragmented.",
                    "Add a requirement output framework with goal, roles, entry, page structure, sketch, and open questions.",
                )
            )
        if REQUIREMENT_COMPLETENESS_CHECKLIST_TITLE not in protocol_text:
            result.add(
                Issue(
                    "WARN",
                    protocol_rel_path,
                    None,
                    f"任务执行协议.md missing {REQUIREMENT_COMPLETENESS_CHECKLIST_TITLE}.",
                    "Without a fixed completeness checklist, page discussions can miss data model and cross-role issues.",
                    "Add a requirement completeness checklist covering business object, role granularity, status ownership, data ownership, triggers, conflicts, downstream flow, permissions, exceptions, traceability, MVP boundary, and sketch consistency.",
                )
            )

    discussion_rel_path = Path("03-工作台/当前需求沟通文档.md")
    discussion_path = root / discussion_rel_path
    if not discussion_path.exists():
        return

    lines = read_lines(discussion_path)
    confirmed_page_ids = {
        match.group(1)
        for line in lines
        if (match := CONFIRMED_PAGE_ROW_RE.match(line))
    }
    page_start_indexes = [
        index for index, line in enumerate(lines) if PAGE_REQUIREMENT_HEADING_RE.match(line)
    ]

    for offset, start_index in enumerate(page_start_indexes):
        end_index = page_start_indexes[offset + 1] if offset + 1 < len(page_start_indexes) else len(lines)
        section = "\n".join(lines[start_index:end_index])
        has_framework_heading = "###### 功能目标" in section
        if not has_framework_heading:
            continue

        missing_headings = [
            heading for heading in PAGE_REQUIREMENT_CORE_HEADINGS if f"###### {heading}" not in section
        ]
        if missing_headings:
            result.add(
                Issue(
                    "WARN",
                    discussion_rel_path,
                    start_index + 1,
                    f"Page requirement section missing core headings: {', '.join(missing_headings)}.",
                    "Page-level requirement discussions should be complete enough to review without chasing scattered chat context.",
                    "Add the missing headings or mark the section as a lightweight note instead of a page requirement section.",
                )
            )

        page_id = lines[start_index].split(maxsplit=2)[1] if len(lines[start_index].split()) >= 2 else ""
        if page_id in confirmed_page_ids:
            confirmed_required_headings = ["ASCII 草图", "待确认/待研发项"]
            missing_confirmed_headings = [
                heading for heading in confirmed_required_headings if f"###### {heading}" not in section
            ]
            if missing_confirmed_headings:
                result.add(
                    Issue(
                        "WARN",
                        discussion_rel_path,
                        start_index + 1,
                        f"Confirmed page missing required headings: {', '.join(missing_confirmed_headings)}.",
                        "Confirmed page requirements should preserve sketch and open-item boundaries for later PRD split.",
                        "Add ASCII 草图 and 待确认/待研发项 sections before marking the page confirmed.",
                    )
                )

            has_record_requirement = any(
                term in section for term in ["任务记录抽屉", "记录类型", "记录内容"]
            )
            if has_record_requirement and "触发规则" not in section:
                result.add(
                    Issue(
                        "WARN",
                        discussion_rel_path,
                        start_index + 1,
                        "Confirmed page mentions records but has no trigger rules.",
                        "Record requirements are incomplete if the document does not say when records are created.",
                        "Add a 触发规则 section/table for record creation, update, and clearing.",
                    )
                )


def iter_markdown_files(root: Path):
    for path in root.rglob("*.md"):
        parts = path.relative_to(root).parts
        if ".git" in parts or "check_docs_tests_sandbox" in parts:
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
        print(f"  Why: {issue.why}")
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
