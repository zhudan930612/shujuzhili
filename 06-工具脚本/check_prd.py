#!/usr/bin/env python
from __future__ import annotations

import re
import sys
from pathlib import Path

from check_common import (
    CheckResult,
    Issue,
    extract_heading_blocks,
    normalize_heading_title,
    print_issues,
    read_lines,
)


MODULE_PRD_PAGE_INDEX_HEADING = "## 页面目录索引"
MODULE_PRD_PAGE_DEMAND_HEADING = "## 页面需求"
MODULE_PRD_COMMON_RULES_HEADING = "## 通用规则 / 跨页面共用规则"
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
MODULE_PRD_NEGATIVE_REDUNDANCY_GENERIC_RE = re.compile(r"无(?:按钮|入口|展示)")
MODULE_PRD_REVERSE_DEFINED_NON_DISPLAY_ROW_RE = re.compile(r"^\|\s*(不展示项|不提供项|不支持项|不显示项)\s*\|")
MODULE_PRD_STAGING_FORMAL_RULE_TERMS = ["仅做", "统一在", "必须", "不允许"]
MODULE_PRD_IMAGE_RULE_MIN_RETAIN_RE = re.compile(r"至少保留\s*1\s*张图片")
MODULE_PRD_IMAGE_RULE_DELETE_LAST_BLOCK_RE = re.compile(r"删除到最后\s*1\s*张.*阻断")
MODULE_PRD_IMAGE_RULE_EMPTY_STATE_RE = re.compile(r"无图片时.*空状态")
MODULE_PRD_IMAGE_RULE_DELETE_TO_ZERO_RE = re.compile(r"删除至\s*0\s*张")
MODULE_PRD_OPEN_ENDED_AT_LEAST_RE = re.compile(r"至少(?:展示|显示|列出)")
MODULE_PRD_OPEN_ENDED_ETC_RE = re.compile(r"(?:字段|内容|元素|信息|图片|按钮|入口).{0,20}等")
MODULE_PRD_COMMON_RULES_REDUNDANT_SIGNAL_TERMS = ["扩展字段", "历史字段", "重复导航", "补充说明"]
MODULE_PRD_COMMON_RULES_PAGE_TRIGGER_TERMS = [
    "按钮",
    "点击",
    "弹窗",
    "抽屉",
    "面板",
    "状态入口",
    "筛选查看",
    "查看",
]
MODULE_PRD_COMMON_RULES_PAGE_TRIGGER_RE = re.compile(r"当前图片存在.*不允许")


def run_checks(root: Path) -> CheckResult:
    root = root.resolve()
    result = CheckResult()
    prd_root = root / "02-PRD文档"
    if not prd_root.exists():
        return result

    for path in iter_backend_module_prd_files(root):
        rel_path = path.relative_to(root)
        lines = read_lines(path)
        text = "\n".join(lines)

        check_formal_prd_sketch_residue(rel_path, lines, result)
        check_module_prd_common_rules(rel_path, lines, result)

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
            check_module_prd_page_skeleton(rel_path, page_heading, start_line, section_lines, result)
            check_confirm_popup_minimum_structure(rel_path, page_heading, start_line, section_lines, result)
            check_module_prd_page_wording(rel_path, page_heading, start_line, section_lines, result)

    return result


def iter_backend_module_prd_files(root: Path):
    base = root / "02-PRD文档" / "后台管理"
    if not base.exists():
        return
    for path in base.glob("*.md"):
        yield path


def check_formal_prd_sketch_residue(rel_path: Path, lines: list[str], result: CheckResult) -> None:
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
        if contains_open_ended_wording(line):
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
        if MODULE_PRD_REVERSE_DEFINED_NON_DISPLAY_ROW_RE.match(line.strip()):
            result.add(
                Issue(
                    "WARN",
                    rel_path,
                    line_no,
                    "page field table contains reverse-defined non-display row.",
                    "Page field tables should list only fields, actions, or states that are actually shown on the page, not reverse-defined rows describing what is absent.",
                    "Delete the reverse-defined row and keep only the fields that are actually shown on this page. If you still think the absence needs explanation, move it to a more appropriate rule section and verify it is truly necessary.",
                )
            )
        if any(term in line for term in MODULE_PRD_NEGATIVE_REDUNDANCY_TERMS) or MODULE_PRD_NEGATIVE_REDUNDANCY_GENERIC_RE.search(line):
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

    min_retain_matches: list[tuple[int, str]] = []
    empty_state_matches: list[tuple[int, str]] = []
    for offset, line in enumerate(section_lines):
        line_no = start_line + offset
        stripped = line.strip()
        if (
            MODULE_PRD_IMAGE_RULE_MIN_RETAIN_RE.search(stripped)
            or MODULE_PRD_IMAGE_RULE_DELETE_LAST_BLOCK_RE.search(stripped)
        ):
            min_retain_matches.append((line_no, stripped))
        if (
            MODULE_PRD_IMAGE_RULE_EMPTY_STATE_RE.search(stripped)
            or MODULE_PRD_IMAGE_RULE_DELETE_TO_ZERO_RE.search(stripped)
        ):
            empty_state_matches.append((line_no, stripped))

    if min_retain_matches and empty_state_matches:
        result.add(
            Issue(
                "WARN",
                rel_path,
                min_retain_matches[0][0],
                f"{page_heading} may contain conflicting image-object rules: {min_retain_matches[0][1]} / {empty_state_matches[0][1]}",
                "The same page appears to describe both 'must retain at least one image' and an 'image list can become empty' path for what may be the same image object.",
                "Check whether these lines describe the same image object. If they do, keep one consistent rule; if they describe different objects, split the wording so the object boundary is explicit.",
            )
        )


def check_module_prd_common_rules(rel_path: Path, lines: list[str], result: CheckResult) -> None:
    block = extract_heading_block(lines, MODULE_PRD_COMMON_RULES_HEADING)
    if block is None:
        return

    start_line, block_lines = block
    for offset, line in enumerate(block_lines):
        line_no = start_line + offset
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if contains_common_rules_open_ended_wording(stripped):
            result.add(
                Issue(
                    "WARN",
                    rel_path,
                    line_no,
                    "module common rules use open-ended wording.",
                    "Module-level common rules should also use deterministic wording instead of leaving display or rule scope open-ended.",
                    "Replace the open-ended wording with a concrete field, element, or rule list.",
                )
            )

        if any(term in stripped for term in MODULE_PRD_COMMON_RULES_REDUNDANT_SIGNAL_TERMS):
            result.add(
                Issue(
                    "WARN",
                    rel_path,
                    line_no,
                    "module common rules may retain non-page-effective residue.",
                    "Common rules should not become a place to hold history fields, repeat navigation, or extra explanatory residue that belongs to a specific page.",
                    "Check whether this line should be deleted or moved back to the page where the field, navigation, or explanation actually appears.",
                )
            )

        if any(term in stripped for term in MODULE_PRD_COMMON_RULES_PAGE_TRIGGER_TERMS) or MODULE_PRD_COMMON_RULES_PAGE_TRIGGER_RE.search(stripped):
            result.add(
                Issue(
                    "WARN",
                    rel_path,
                    line_no,
                    "module common rules may mix in page-triggered behavior.",
                    "Rules that depend on buttons, clicks, popups, list actions, page display areas, or page-level blocking conditions should usually live in the specific page section instead of the module-level common rules.",
                    "Check whether this rule should be moved down to the corresponding page section. Keep it at module level only if it is a truly cross-page unique definition.",
                )
            )

        if any(term in stripped for term in MODULE_PRD_NEGATIVE_REDUNDANCY_TERMS) or MODULE_PRD_NEGATIVE_REDUNDANCY_GENERIC_RE.search(stripped):
            result.add(
                Issue(
                    "WARN",
                    rel_path,
                    line_no,
                    "module common rules contain negative redundancy wording.",
                    "Common rules should not describe page structure by negating missing buttons, entrances, or display areas just because other pages have them.",
                    "Delete the negative wording unless it is the only way to block a concrete ambiguity.",
                )
            )


def contains_open_ended_wording(line: str) -> bool:
    return (
        any(term in line for term in MODULE_PRD_OPEN_ENDED_TERMS)
        or MODULE_PRD_OPEN_ENDED_AT_LEAST_RE.search(line) is not None
        or MODULE_PRD_OPEN_ENDED_ETC_RE.search(line) is not None
    )


def contains_common_rules_open_ended_wording(line: str) -> bool:
    return any(term in line for term in MODULE_PRD_OPEN_ENDED_TERMS) or MODULE_PRD_OPEN_ENDED_ETC_RE.search(line) is not None


def extract_heading_block(lines: list[str], heading: str) -> tuple[int, list[str]] | None:
    start_index = None
    for index, line in enumerate(lines):
        if line.strip() == heading:
            start_index = index
            break
    if start_index is None:
        return None

    end_index = len(lines)
    for index in range(start_index + 1, len(lines)):
        if lines[index].strip().startswith("## "):
            end_index = index
            break
    return start_index + 1, lines[start_index:end_index]


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


def main() -> int:
    root = Path.cwd()
    result = run_checks(root)
    print_issues(result)
    return 1 if result.errors else 0


if __name__ == "__main__":
    sys.exit(main())
