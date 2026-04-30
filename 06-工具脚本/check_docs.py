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
CHECK_PROTOTYPES_COMMAND = "python 06-工具脚本/check_prototypes.py"
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
MODULE_PRD_PAGE_INDEX_HEADING = "## 页面目录索引"
MODULE_PRD_PAGE_DEMAND_HEADING = "## 页面需求"
MODULE_PRD_PAGE_HEADING_RE = re.compile(r"^###\s+.+")
MODULE_PRD_REQUIRED_PAGE_HEADINGS = [
    "页面基本信息",
    "页面入口",
    "对应原型",
    "页面状态",
    "字段与展示规则",
    "操作规则",
    "异常与边界",
    "页面弹窗 / 抽屉",
    "权限相关行为",
    "模块衔接",
    "暂缓 / 待研发确认项",
    "页面待确认问题",
]
MODULE_PRD_CONFIRM_POPUP_HEADING_RE = re.compile(r"^#####\s+弹窗\s*\d+[：:].*(确认|提示).*")
MODULE_PRD_CONFIRM_POPUP_REQUIRED_PHRASES = [
    "触发入口",
    "触发条件 / 阻断条件",
    "提示文案",
    "按钮",
    "结果反馈",
]
FORMAL_PRD_SKETCH_TERMS = ["ASCII原型", "原型图 1："]
FORMAL_PRD_BOX_DRAWING_RE = re.compile(r"[┌┐└┘│─].*[┌┐└┘│─]")
MODULE_PRD_OPEN_ENDED_TERMS = ["包括但不限于"]
MODULE_PRD_NEGATIVE_REDUNDANCY_TERMS = [
    "无编辑按钮",
    "无新增按钮",
    "无编辑入口",
    "无新增入口",
    "无删除入口",
]
MODULE_PRD_STAGING_FORMAL_RULE_TERMS = ["仅做", "统一在", "必须", "不允许"]

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
    check_review_record_structure(root, result)
    check_workbench_protocol_alignment(root, result)
    check_permission_definition_boundary(root, result)
    check_module_prd_page_rules(root, result)

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
    if CHECK_PROTOTYPES_COMMAND not in text:
        result.add(
            Issue(
                "WARN",
                rel_path,
                None,
                "任务完成检查.md missing check_prototypes command.",
                "Prototype tasks need a dedicated sensor for shared-component reuse and shared-script integration.",
                f"Add `{CHECK_PROTOTYPES_COMMAND}` to the prototype-related completion checks.",
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

    if has_any_landing_status(lines, {"已确认", "待拆回", "已拆回", "已归档"}):
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
        has_framework_heading = "###### 功能目标" in section
        if not has_framework_heading:
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


def check_module_prd_page_rules(root: Path, result: CheckResult) -> None:
    prd_root = root / "02-PRD文档"
    if not prd_root.exists():
        return

    for path in iter_backend_module_prd_files(root):
        rel_path = path.relative_to(root)
        lines = read_lines(path)
        text = "\n".join(lines)

        check_formal_prd_sketch_residue(rel_path, lines, result)

        if MODULE_PRD_PAGE_DEMAND_HEADING not in text:
            continue

        if MODULE_PRD_PAGE_INDEX_HEADING not in text:
            result.add(
                Issue(
                    "WARN",
                    rel_path,
                    None,
                    "module PRD has 页面需求 but missing 页面目录索引.",
                    "When a module PRD contains multiple page sections, AI and reviewers need a quick page index to see how many pages the module includes.",
                    "Add `## 页面目录索引` before `## 页面需求` and list the pages in reading order.",
                )
            )

        page_sections = extract_module_prd_page_sections(lines)
        for page_heading, start_line, section_lines in page_sections:
            check_module_prd_page_skeleton(
                rel_path, page_heading, start_line, section_lines, result
            )
            check_confirm_popup_minimum_structure(
                rel_path, page_heading, start_line, section_lines, result
            )
            check_module_prd_page_wording(
                rel_path, page_heading, start_line, section_lines, result
            )


def check_formal_prd_sketch_residue(
    rel_path: Path, lines: list[str], result: CheckResult
) -> None:
    for line_no, line in enumerate(lines, start=1):
        if any(term in line for term in FORMAL_PRD_SKETCH_TERMS) or FORMAL_PRD_BOX_DRAWING_RE.search(line):
            result.add(
                Issue(
                    "WARN",
                    rel_path,
                    line_no,
                    "formal PRD appears to retain page sketch body.",
                    "Formal PRDs should reference the corresponding prototype file instead of long-lived page ASCII sketch bodies.",
                    "Remove the page sketch正文 from the PRD, keep the page rules, and reference the prototype file in `对应原型`.",
                )
            )
            break


def check_module_prd_page_skeleton(
    rel_path: Path,
    page_heading: str,
    start_line: int,
    section_lines: list[str],
    result: CheckResult,
) -> None:
    page_heading_titles = {
        normalize_heading_title(line)
        for line in section_lines
        if line.strip().startswith("#### ")
    }
    missing_headings = [
        heading for heading in MODULE_PRD_REQUIRED_PAGE_HEADINGS if heading not in page_heading_titles
    ]
    if missing_headings:
        result.add(
            Issue(
                "WARN",
                rel_path,
                start_line,
                f"{page_heading} missing page skeleton headings: {', '.join(missing_headings)}.",
                "Module PRDs should use the agreed page-level skeleton so AI and developers can scan each page with the same reading order.",
                "Add the missing page headings under this page section.",
            )
        )


def check_confirm_popup_minimum_structure(
    rel_path: Path,
    page_heading: str,
    start_line: int,
    section_lines: list[str],
    result: CheckResult,
) -> None:
    popup_sections = extract_heading_blocks(section_lines, "##### ")
    for popup_heading, popup_line_offset, popup_lines in popup_sections:
        if not MODULE_PRD_CONFIRM_POPUP_HEADING_RE.match(popup_heading.strip()):
            continue
        missing_phrases = [
            phrase
            for phrase in MODULE_PRD_CONFIRM_POPUP_REQUIRED_PHRASES
            if not any(phrase in line for line in popup_lines)
        ]
        if missing_phrases:
            result.add(
                Issue(
                    "WARN",
                    rel_path,
                    start_line + popup_line_offset,
                    f"{page_heading} confirm popup missing structure: {', '.join(missing_phrases)}.",
                    "Confirmation popups need a small but stable structure so developers can implement cancel, confirm, and blocked-result branches without guessing.",
                    "For this confirmation popup, add: 触发入口, 触发条件 / 阻断条件, 提示文案, 按钮, 结果反馈.",
                )
            )


def check_module_prd_page_wording(
    rel_path: Path,
    page_heading: str,
    start_line: int,
    section_lines: list[str],
    result: CheckResult,
) -> None:
    for offset, line in enumerate(section_lines):
        line_no = start_line + offset
        if any(term in line for term in MODULE_PRD_OPEN_ENDED_TERMS):
            result.add(
                Issue(
                    "WARN",
                    rel_path,
                    line_no,
                    f"{page_heading} uses open-ended wording: 包括但不限于.",
                    "Page-level PRD field and rule sections should list deterministic content instead of open-ended wording.",
                    "Replace the open-ended wording with a concrete field or rule list.",
                )
            )
        if line.strip() == "##### 扩展字段":
            result.add(
                Issue(
                    "WARN",
                    rel_path,
                    line_no,
                    f"{page_heading} contains 扩展字段 section.",
                    "An 扩展字段 section often reintroduces fields that are not actually shown on the current page.",
                    "Keep only fields that are actually shown on this page; move other fields back to the page or popup where they appear.",
                )
            )
        if any(term in line for term in MODULE_PRD_NEGATIVE_REDUNDANCY_TERMS):
            result.add(
                Issue(
                    "WARN",
                    rel_path,
                    line_no,
                    f"{page_heading} contains negative redundancy wording: {line.strip()}",
                    "Page PRDs should default to writing only what exists on the page instead of negating elements just because other pages have them.",
                    "Delete the negative wording unless it is the only way to block a concrete ambiguity.",
                )
            )

    staging_sections = extract_heading_blocks(section_lines, "#### ")
    for heading, offset, block_lines in staging_sections:
        if normalize_heading_title(heading) != "暂缓 / 待研发确认项":
            continue
        for inner_offset, block_line in enumerate(block_lines[1:], start=1):
            for term in MODULE_PRD_STAGING_FORMAL_RULE_TERMS:
                if term in block_line:
                    result.add(
                        Issue(
                            "WARN",
                            rel_path,
                            start_line + offset + inner_offset,
                            f"{page_heading} staging section may contain a formal rule: {term}",
                            "The 暂缓 / 待研发确认项 section should not become a place to hold already-decided formal rules.",
                            "Move the stable rule back into 字段与展示规则, 操作规则, 异常与边界, or another formal page section.",
                        )
                    )


def iter_backend_module_prd_files(root: Path):
    base = root / "02-PRD文档" / "后台管理"
    if not base.exists():
        return
    for path in base.glob("*.md"):
        yield path


def extract_module_prd_page_sections(lines: list[str]) -> list[tuple[str, int, list[str]]]:
    in_page_demand = False
    section_start = None
    section_heading = None
    sections: list[tuple[str, int, list[str]]] = []

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == MODULE_PRD_PAGE_DEMAND_HEADING:
            in_page_demand = True
            section_start = None
            section_heading = None
            continue
        if in_page_demand and stripped.startswith("## ") and stripped != MODULE_PRD_PAGE_DEMAND_HEADING:
            if section_heading is not None and section_start is not None:
                sections.append((section_heading, section_start + 1, lines[section_start:index]))
            break
        if not in_page_demand:
            continue
        if MODULE_PRD_PAGE_HEADING_RE.match(stripped):
            if section_heading is not None and section_start is not None:
                sections.append((section_heading, section_start + 1, lines[section_start:index]))
            section_heading = stripped[4:].strip()
            section_start = index

    if in_page_demand and section_heading is not None and section_start is not None:
        sections.append((section_heading, section_start + 1, lines[section_start:]))
    return sections


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


def iter_markdown_files(root: Path):
    for path in root.rglob("*.md"):
        parts = path.relative_to(root).parts
        if ".git" in parts or "check_docs_tests_sandbox" in parts:
            continue
        yield path


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
        if not saw_separator and all(set(cell) <= {"-", " "} for cell in cells):
            saw_separator = True
            continue
        if header and saw_separator and len(cells) >= len(header):
            yield index, {header[i]: cells[i] for i in range(len(header))}


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def normalize_heading_title(line: str) -> str:
    stripped = line.strip()
    stripped = re.sub(r"^#+\s*", "", stripped)
    stripped = re.sub(r"^\d+\.\s*", "", stripped)
    return stripped.strip()


def has_meaningful_link_or_path(value: str) -> bool:
    if not value or value in {"-", "—"}:
        return False
    return "[" in value and "](" in value or "/" in value or "\\" in value


def has_archive_link(value: str) -> bool:
    return "90-归档记录/" in value or "90-归档记录\\" in value


def has_any_landing_status(lines: list[str], statuses: set[str]) -> bool:
    for _, row in iter_markdown_table_rows(lines, DISCUSSION_LANDING_CHECKLIST_TITLE):
        if row.get("状态", "").strip() in statuses:
            return True
    return False


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
