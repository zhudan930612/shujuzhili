#!/usr/bin/env python
from __future__ import annotations

import re
import sys
from pathlib import Path

from check_common import (
    CheckResult,
    Issue,
    has_any_landing_status,
    has_archive_link,
    has_meaningful_link_or_path,
    iter_markdown_table_rows,
    print_issues,
    read_lines,
)


RUN_CHECKS_ALL_COMMAND = "python 06-工具脚本/run_checks.py --scope all"
RUN_CHECKS_PROTOTYPES_COMMAND = "python 06-工具脚本/run_checks.py --scope prototypes"
DISCUSSION_LANDING_CHECKLIST_TITLE = "拆回正式文档清单"
DISCUSSION_LANDING_CHECKLIST_COLUMNS = ["结论/规则", "主定义文档", "影响资产", "状态", "备注"]
DISCUSSION_LANDING_CHECKLIST_ALLOWED_STATUSES = {
    "待确认",
    "沟通中",
    "已确认",
    "待拆回",
    "已拆回",
    "待归档",
    "已归档",
    "已拒绝",
}
REQUIREMENT_OUTPUT_FRAMEWORK_TITLE = "## 需求沟通输出框架"
REQUIREMENT_COMPLETENESS_CHECKLIST_TITLE = "## 需求完备性检查清单"
PAGE_REQUIREMENT_HEADING_RE = re.compile(r"^#####\s+Q\d+(?:-\d+)?\s+.+")
CONFIRMED_PAGE_ROW_RE = re.compile(r"^\|\s*(Q\d+(?:-\d+)?)\s*\|.*\|\s*已确认\s*\|")
REVIEW_ENTRY_HEADING_RE = re.compile(r"^##\s+\d{4}-\d{2}-\d{2}\s+.+")
PAGE_REQUIREMENT_CORE_HEADING_ALTERNATIVES = [
    ("功能目标",),
    ("使用角色", "业务使用对象/参与角色建议"),
    ("入口与权限", "页面入口"),
    ("页面结构",),
    ("ASCII 草图",),
    ("待确认/待研发项",),
]
REVIEW_RECORD_REQUIRED_HEADINGS = [
    "问题描述",
    "原因分析",
    "评审结论",
    "后续处理",
    "收获",
]
COMPLETION_CLOSURE_GATE_PHRASES = [
    "本轮任务类型",
    "对应协议产物",
    "新增结论是否进入拆回清单",
    "待拆回/已拆回/已归档",
    "WARN",
    "可复发错误",
    "制度化动作",
    "同一页面、同一对象是否存在互斥规则",
]
WORKBENCH_PROTOCOL_RULE_PHRASES = [
    "协议驱动",
    "任务执行协议.md",
    "任务完成检查.md",
    "当前需求沟通文档.md",
    "评审记录.md",
    "错误治理清单.md",
]
PERMISSION_MATRIX_DUPLICATION_TERMS = [
    "角色权限矩阵",
    "页面权限矩阵",
    "操作权限矩阵",
]
PERMISSION_BEHAVIOR_RULE_PHRASES = [
    "权限相关行为",
    "系统管理.md",
]


def run_checks(root: Path) -> CheckResult:
    root = root.resolve()
    result = CheckResult()
    check_completion_check_command(root, result)
    check_discussion_landing_checklist(root, result)
    check_requirement_output_framework(root, result)
    check_review_record_structure(root, result)
    check_workbench_protocol_alignment(root, result)
    check_permission_definition_boundary(root, result)
    return result


def check_completion_check_command(root: Path, result: CheckResult) -> None:
    rel_path = Path("03-工作台/任务完成检查.md")
    path = root / rel_path
    if not path.exists():
        return

    text = path.read_text(encoding="utf-8")
    if RUN_CHECKS_ALL_COMMAND not in text:
        result.add(
            Issue(
                "ERROR",
                rel_path,
                None,
                "任务完成检查.md missing run_checks all command.",
                "The completion checklist should point AI to the unified mechanical check entry.",
                f"Add `{RUN_CHECKS_ALL_COMMAND}` to the task completion checklist.",
            )
        )
    if RUN_CHECKS_PROTOTYPES_COMMAND not in text:
        result.add(
            Issue(
                "WARN",
                rel_path,
                None,
                "任务完成检查.md missing prototype scope command.",
                "Prototype tasks need an explicit scope command so users can run only the prototype sensor when appropriate.",
                f"Add `{RUN_CHECKS_PROTOTYPES_COMMAND}` to the prototype-related completion checks.",
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

    lines = read_lines(path)
    for line_no, row in iter_markdown_table_rows(lines, DISCUSSION_LANDING_CHECKLIST_TITLE):
        status = row.get("状态", "").strip()
        main_doc = row.get("主定义文档", "").strip()
        row_text = " | ".join(row.values())

        if status and status not in DISCUSSION_LANDING_CHECKLIST_ALLOWED_STATUSES:
            result.add(
                Issue(
                    "WARN",
                    rel_path,
                    line_no,
                    f"Row has invalid landing status: {status}",
                    "Unexpected status values make it hard for AI to reason about whether conclusions are pending, landed, or archived.",
                    "Use one of the agreed statuses: 待确认, 沟通中, 已确认, 待拆回, 已拆回, 待归档, 已归档, 已拒绝.",
                )
            )

        if status == "已拆回" and not has_meaningful_link_or_path(main_doc):
            result.add(
                Issue(
                    "WARN",
                    rel_path,
                    line_no,
                    "Landing row marked 已拆回 but has no source-of-truth link.",
                    "A split-back conclusion is not traceable if the checklist row does not point to the source-of-truth file.",
                    "Add the source-of-truth Markdown link or relative path in 主定义文档.",
                )
            )

        if status == "已归档" and not has_archive_link(row_text):
            result.add(
                Issue(
                    "WARN",
                    rel_path,
                    line_no,
                    "Landing row marked 已归档 but has no archive link.",
                    "An archived conclusion is not auditable if the checklist row does not point to the archive record.",
                    "Add a Markdown link or relative path under 90-归档记录 in 主定义文档, 影响资产, or 备注.",
                )
            )

    if has_any_landing_status(lines, DISCUSSION_LANDING_CHECKLIST_TITLE, {"已确认", "待拆回", "已拆回", "已归档"}):
        completion_rel_path = Path("03-工作台/任务完成检查.md")
        completion_path = root / completion_rel_path
        if completion_path.exists():
            completion_text = completion_path.read_text(encoding="utf-8")
            missing_phrases = [
                phrase for phrase in COMPLETION_CLOSURE_GATE_PHRASES if phrase not in completion_text
            ]
            for phrase in missing_phrases:
                result.add(
                    Issue(
                        "WARN",
                        completion_rel_path,
                        None,
                        f"任务完成检查.md missing closure gate: {phrase}",
                        "When conclusions are confirmed or pending split-back, the completion checklist should explicitly ask for closure evidence.",
                        "Add the missing closure gate so task wrap-up can verify protocol artifacts and next actions.",
                    )
                )

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
        if "###### 功能目标" not in section:
            continue

        missing_headings = []
        for heading_group in PAGE_REQUIREMENT_CORE_HEADING_ALTERNATIVES:
            if not any(f"###### {heading}" in section for heading in heading_group):
                missing_headings.append(" / ".join(heading_group))
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


def check_review_record_structure(root: Path, result: CheckResult) -> None:
    rel_path = Path("03-工作台/评审记录.md")
    path = root / rel_path
    if not path.exists():
        return

    lines = read_lines(path)
    entry_start_indexes = [
        index for index, line in enumerate(lines) if REVIEW_ENTRY_HEADING_RE.match(line)
    ]
    for offset, start_index in enumerate(entry_start_indexes):
        end_index = entry_start_indexes[offset + 1] if offset + 1 < len(entry_start_indexes) else len(lines)
        section = "\n".join(lines[start_index:end_index])
        missing_headings = [
            heading for heading in REVIEW_RECORD_REQUIRED_HEADINGS if f"### {heading}" not in section
        ]
        if missing_headings:
            result.add(
                Issue(
                    "WARN",
                    rel_path,
                    start_index + 1,
                    f"review entry missing sections: {', '.join(missing_headings)}.",
                    "Review records should use a consistent skeleton so AI can quickly find the problem, reasoning, decision, and follow-up.",
                    "Add the missing review sections: 问题描述, 原因分析, 评审结论, 后续处理, 收获.",
                )
            )


def check_workbench_protocol_alignment(root: Path, result: CheckResult) -> None:
    rel_path = Path("03-工作台/README.md")
    path = root / rel_path
    if not path.exists():
        return

    text = path.read_text(encoding="utf-8")
    missing_phrases = [phrase for phrase in WORKBENCH_PROTOCOL_RULE_PHRASES if phrase not in text]
    for phrase in missing_phrases:
        result.add(
            Issue(
                "WARN",
                rel_path,
                None,
                f"README missing protocol-driven workbench rule: {phrase}",
                "Workbench navigation should make the protocol-driven workflow obvious before AI starts editing discussion docs.",
                "Add protocol-driven routing for 当前需求沟通文档, 评审记录, 任务执行协议, and 任务完成检查.",
            )
        )


def check_permission_definition_boundary(root: Path, result: CheckResult) -> None:
    protocol_rel_path = Path("03-工作台/任务执行协议.md")
    protocol_path = root / protocol_rel_path
    if protocol_path.exists():
        protocol_text = protocol_path.read_text(encoding="utf-8")
        for phrase in PERMISSION_BEHAVIOR_RULE_PHRASES:
            if phrase not in protocol_text:
                result.add(
                    Issue(
                        "WARN",
                        protocol_rel_path,
                        None,
                        f"任务执行协议.md missing permission-boundary rule: {phrase}",
                        "Without an explicit permission-boundary rule, page requirements may duplicate role-permission source-of-truth content in process docs.",
                        "Add rules that pages keep only 权限相关行为 and reference 系统管理.md for role-permission source of truth.",
                    )
                )

    discussion_rel_path = Path("03-工作台/当前需求沟通文档.md")
    discussion_path = root / discussion_rel_path
    if not discussion_path.exists():
        return

    for line_no, line in enumerate(read_lines(discussion_path), start=1):
        for term in PERMISSION_MATRIX_DUPLICATION_TERMS:
            if term in line:
                result.add(
                    Issue(
                        "WARN",
                        discussion_rel_path,
                        line_no,
                        f"Process doc appears to repeat permission source-of-truth content: {term}",
                        "Process documents should not become the long-term source of truth for role-to-page or role-to-operation permission matrices.",
                        "Move the matrix definition back to 02-PRD文档/后台管理/系统管理.md and keep only 权限相关行为 in the process doc.",
                    )
                )


def main() -> int:
    root = Path.cwd()
    result = run_checks(root)
    print_issues(result)
    return 1 if result.errors else 0


if __name__ == "__main__":
    sys.exit(main())
