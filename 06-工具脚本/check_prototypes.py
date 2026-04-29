#!/usr/bin/env python
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


BACKEND_PROTO_DIR = Path("04-原型效果图/后台管理")
PREVIEW_PAGE = "后台管理-组件预览.html"
REQUIRED_CSS = './assets/prototype.css'
REQUIRED_BASE_SCRIPT = './assets/prototype.js'
REQUIRED_LAYOUT_SCRIPT = './assets/prototype-layout.js'
REQUIRED_SWITCHER_SCRIPT = './assets/prototype-switcher.js'
LIST_PAGE_KEYWORDS = ("列表", "字典")
MULTI_ACTION_RE = re.compile(r"<td[^>]*>.*?(编辑|删除).*?(编辑|删除|复制|停用|启用|详情).*?</td>", re.S)
CUSTOM_FILTER_GRID_RE = re.compile(
    r"\.(?P<class_name>[\w-]*filter[\w-]*)\s*\{[^}]*grid-template-columns\s*:\s*(?P<columns>[^;}]*\b\d+(?:\.\d+)?fr\b[^;}]*)",
    re.S,
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
    for path in iter_backend_html_files(root):
        check_prototype_css(root, path, result)
        check_layout_script(root, path, result)
        check_switcher_script(root, path, result)
        check_list_shell(root, path, result)
        check_filter_width_layout(root, path, result)
        check_page_actions(root, path, result)
        check_multi_row_actions(root, path, result)
    return result


def iter_backend_html_files(root: Path):
    target_dir = root / BACKEND_PROTO_DIR
    if not target_dir.exists():
        return
    for path in target_dir.glob("*.html"):
        if path.name == PREVIEW_PAGE:
            continue
        yield path


def check_prototype_css(root: Path, path: Path, result: CheckResult) -> None:
    text = path.read_text(encoding="utf-8")
    if REQUIRED_CSS not in text:
        result.add(
            Issue(
                "ERROR",
                path.relative_to(root),
                None,
                "Prototype page missing prototype.css.",
                "Backend prototype pages should share the same visual baseline instead of re-inventing local styles from scratch.",
                'Add `<link rel="stylesheet" href="./assets/prototype.css" />` to the page head.',
            )
        )


def check_layout_script(root: Path, path: Path, result: CheckResult) -> None:
    text = path.read_text(encoding="utf-8")
    uses_layout_placeholders = '<header class="topbar"></header>' in text or '<aside class="sidebar"></aside>' in text or 'class="frame"' in text
    if uses_layout_placeholders and REQUIRED_LAYOUT_SCRIPT not in text:
        result.add(
            Issue(
                "WARN",
                path.relative_to(root),
                None,
                "Prototype page uses frame/topbar/sidebar but is missing prototype-layout.js.",
                "The shared layout script is the golden path for backend navigation and avoids page-level duplicated menu DOM.",
                'Add `<script src="./assets/prototype-layout.js"></script>` and keep the topbar/sidebar placeholders for injection.',
            )
        )
    if REQUIRED_BASE_SCRIPT not in text:
        result.add(
            Issue(
                "WARN",
                path.relative_to(root),
                None,
                "Prototype page missing prototype.js.",
                "Shared prototype behaviors such as pagination, row actions, cascader, and toast helpers should come from the common runtime.",
                'Add `<script src="./assets/prototype.js"></script>` before layout or switcher scripts.',
            )
        )


def check_switcher_script(root: Path, path: Path, result: CheckResult) -> None:
    text = path.read_text(encoding="utf-8")
    uses_switcher = 'data-prototype-switch' in text or 'prototype-state-bar' in text
    if uses_switcher and REQUIRED_SWITCHER_SCRIPT not in text:
        result.add(
            Issue(
                "WARN",
                path.relative_to(root),
                None,
                "Prototype page uses prototype-state-bar/data-prototype-switch but is missing prototype-switcher.js.",
                "State switching should reuse the shared behavior instead of relying on page-local scripts or a dead static bar.",
                'Add `<script src="./assets/prototype-switcher.js"></script>` when the page uses shared state-switch markup.',
            )
        )


def check_list_shell(root: Path, path: Path, result: CheckResult) -> None:
    text = path.read_text(encoding="utf-8")
    if any(keyword in path.stem for keyword in LIST_PAGE_KEYWORDS) and "<table" in text and "proto-list-shell" not in text:
        result.add(
            Issue(
                "WARN",
                path.relative_to(root),
                None,
                "List-like prototype page missing proto-list-shell.",
                "List and dictionary pages should start from the shared list shell so filters, tools, tables, and pagination stay structurally consistent.",
                "Wrap the page's list area with `proto-list-shell`, and place the title/tools/table/pagination inside the shared shell.",
            )
        )


def check_filter_width_layout(root: Path, path: Path, result: CheckResult) -> None:
    text = path.read_text(encoding="utf-8")
    for match in CUSTOM_FILTER_GRID_RE.finditer(text):
        class_name = match.group("class_name")
        columns = match.group("columns").strip()
        if "role-form-grid" in class_name:
            continue
        if "assignment" in class_name or "dictionary" in class_name:
            continue
        if f'class="{class_name}"' not in text and f'class="{class_name} ' not in text and f" {class_name}\"" not in text:
            continue
        result.add(
            Issue(
                "WARN",
                path.relative_to(root),
                None,
                f"Prototype page uses flexible fr columns in custom filter grid: .{class_name}",
                "Small filter sets should prefer fixed-width fields; fr-based stretching often makes filters visually too wide and inconsistent across pages.",
                f"Replace `{columns}` with fixed widths such as `220px 180px 220px auto auto`, or fall back to `proto-filter-bar` natural layout.",
            )
        )


def check_page_actions(root: Path, path: Path, result: CheckResult) -> None:
    text = path.read_text(encoding="utf-8")
    if "page-actions" not in text:
        return

    if "has-page-actions" not in text:
        result.add(
            Issue(
                "WARN",
                path.relative_to(root),
                None,
                "Prototype page uses page-actions without has-page-actions.",
                "Shared bottom actions need reserved content space; otherwise page content can be visually covered.",
                "Add `has-page-actions` to the surrounding content panel when using `page-actions`.",
            )
        )

    if re.search(r"\.page-actions\s*\{[^}]*position\s*:\s*(fixed|sticky)", text, re.S):
        result.add(
            Issue(
                "WARN",
                path.relative_to(root),
                None,
                "Prototype page overrides page-actions positioning with page-local sticky/fixed styles.",
                "The shared page-actions component already defines the positioning contract; page-local overrides recreate the same bug class.",
                "Remove the page-local `page-actions` positioning patch and use the shared component contract instead.",
            )
        )


def check_multi_row_actions(root: Path, path: Path, result: CheckResult) -> None:
    text = path.read_text(encoding="utf-8")
    if "proto-row-actions" in text:
        return
    if MULTI_ACTION_RE.search(text):
        result.add(
            Issue(
                "WARN",
                path.relative_to(root),
                None,
                "Prototype page has multi-action cell without proto-row-actions.",
                "Repeated row-action patterns should converge on the shared action component instead of ad-hoc text links.",
                "Replace multi-action table cells with `proto-row-actions` + `proto-action`.",
            )
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
        print("OK: prototype checks passed.")


def main() -> int:
    root = Path.cwd()
    result = run_checks(root)
    print_issues(result)
    return 1 if result.errors else 0


if __name__ == "__main__":
    sys.exit(main())
