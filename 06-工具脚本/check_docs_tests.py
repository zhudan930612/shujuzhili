import shutil
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import check_docs


class CheckDocsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_base = Path(__file__).resolve().parent / "check_docs_tests_sandbox"
        if cls.temp_base.exists():
            shutil.rmtree(cls.temp_base)
        cls.temp_base.mkdir()

    @classmethod
    def tearDownClass(cls):
        if cls.temp_base.exists():
            shutil.rmtree(cls.temp_base)

    def make_root(self, name: str) -> Path:
        root = self.temp_base / name
        root.mkdir()
        return root

    def add_required_files(self, root: Path) -> None:
        (root / "AGENTS.md").write_text("ok\n", encoding="utf-8")
        workbench = root / "03-工作台"
        workbench.mkdir(parents=True)
        (workbench / "任务执行协议.md").write_text("ok\n", encoding="utf-8")
        (workbench / "任务完成检查.md").write_text(
            "python 06-工具脚本/check_docs.py\n", encoding="utf-8"
        )

    def test_reports_missing_required_file(self):
        root = self.make_root("missing_required")
        result = check_docs.run_checks(root)

        self.assertTrue(any("Missing required file" in item.message for item in result.errors))

    def test_reports_deprecated_term_with_line_number(self):
        root = self.make_root("deprecated_term")
        self.add_required_files(root)
        (root / "doc.md").write_text("这里有 ASCII 原型\n", encoding="utf-8")

        result = check_docs.run_checks(root)

        self.assertTrue(any(item.path == Path("doc.md") and item.line == 1 for item in result.errors))

    def test_reports_broken_relative_markdown_link(self):
        root = self.make_root("broken_link")
        self.add_required_files(root)
        workbench = root / "03-工作台"
        (workbench / "任务执行协议.md").write_text("[missing](../missing.md)\n", encoding="utf-8")

        result = check_docs.run_checks(root)

        self.assertTrue(any("Broken Markdown link" in item.message for item in result.errors))
        self.assertTrue(any("AI cannot follow stale context links" in item.why for item in result.errors))

    def test_large_discussion_doc_is_warning_only(self):
        root = self.make_root("large_discussion")
        self.add_required_files(root)
        (root / "AGENTS.md").write_text("`03-工作台/`\n", encoding="utf-8")
        workbench = root / "03-工作台"
        (workbench / "当前需求沟通文档.md").write_text("x" * 30001, encoding="utf-8")

        result = check_docs.run_checks(root)

        self.assertEqual([], result.errors)
        self.assertTrue(any("Current discussion doc is large" in item.message for item in result.warnings))

    def test_reports_unexpected_root_directory(self):
        root = self.make_root("unexpected_root_directory")
        self.add_required_files(root)
        (root / "99-临时目录").mkdir()

        result = check_docs.run_checks(root)

        self.assertTrue(any("Unexpected root directory" in item.message for item in result.warnings))

    def test_reports_readme_missing_required_heading(self):
        root = self.make_root("readme_missing_heading")
        self.add_required_files(root)
        overview = root / "00-项目总览"
        overview.mkdir()
        (overview / "README.md").write_text("# 项目总览\n## 目录定位\n", encoding="utf-8")

        result = check_docs.run_checks(root)

        self.assertTrue(any("README missing heading" in item.message for item in result.warnings))

    def test_reports_agents_missing_root_directory_entry(self):
        root = self.make_root("agents_missing_directory")
        (root / "00-项目总览").mkdir()
        self.add_required_files(root)

        result = check_docs.run_checks(root)

        self.assertTrue(any("AGENTS.md missing root directory entry" in item.message for item in result.errors))

    def test_reports_root_readme_reference(self):
        root = self.make_root("root_readme_reference")
        self.add_required_files(root)
        doc_dir = root / "00-项目总览"
        doc_dir.mkdir()
        (doc_dir / "doc.md").write_text("[根 README](../README.md)\n", encoding="utf-8")

        result = check_docs.run_checks(root)

        self.assertTrue(any("Root README reference found" in item.message for item in result.warnings))

    def test_reports_missing_check_docs_command_in_completion_check(self):
        root = self.make_root("missing_completion_command")
        (root / "AGENTS.md").write_text("ok\n", encoding="utf-8")
        workbench = root / "03-工作台"
        workbench.mkdir(parents=True)
        (workbench / "任务执行协议.md").write_text("ok\n", encoding="utf-8")
        (workbench / "任务完成检查.md").write_text("no command\n", encoding="utf-8")

        result = check_docs.run_checks(root)

        self.assertTrue(any("任务完成检查.md missing check_docs command" in item.message for item in result.errors))

    def test_deprecated_term_issue_has_fix(self):
        root = self.make_root("deprecated_term_has_fix")
        self.add_required_files(root)
        (root / "doc.md").write_text("ASCII 原型\n", encoding="utf-8")

        result = check_docs.run_checks(root)

        self.assertTrue(any("PRD ASCII 草图" in item.fix for item in result.errors))

    def test_print_issues_includes_why_and_fix(self):
        root = self.make_root("print_includes_why")
        self.add_required_files(root)
        (root / "doc.md").write_text("ASCII 原型\n", encoding="utf-8")
        result = check_docs.run_checks(root)
        output = StringIO()

        with redirect_stdout(output):
            check_docs.print_issues(result)

        rendered = output.getvalue()
        self.assertIn("Why:", rendered)
        self.assertIn("Fix:", rendered)

    def test_reports_missing_discussion_landing_checklist(self):
        root = self.make_root("missing_landing_checklist")
        self.add_required_files(root)
        workbench = root / "03-工作台"
        (workbench / "当前需求沟通文档.md").write_text("过程讨论\n", encoding="utf-8")

        result = check_docs.run_checks(root)

        self.assertTrue(any("missing 拆回正式文档清单" in item.message for item in result.warnings))

    def test_reports_incomplete_discussion_landing_checklist_columns(self):
        root = self.make_root("incomplete_landing_checklist")
        self.add_required_files(root)
        workbench = root / "03-工作台"
        (workbench / "当前需求沟通文档.md").write_text(
            "### 拆回正式文档清单\n\n| 结论/规则 | 状态 |\n|---|---|\n",
            encoding="utf-8",
        )

        result = check_docs.run_checks(root)

        self.assertTrue(any("Landing checklist missing columns" in item.message for item in result.warnings))

    def test_reports_missing_requirement_output_framework(self):
        root = self.make_root("missing_requirement_output_framework")
        self.add_required_files(root)
        workbench = root / "03-工作台"
        (workbench / "当前需求沟通文档.md").write_text(
            "### 拆回正式文档清单\n\n| 结论/规则 | 主定义文档 | 影响资产 | 状态 | 备注 |\n|---|---|---|---|---|\n",
            encoding="utf-8",
        )

        result = check_docs.run_checks(root)

        self.assertTrue(
            any("missing ## 需求沟通输出框架" in item.message for item in result.warnings)
        )

    def test_reports_missing_requirement_completeness_checklist(self):
        root = self.make_root("missing_requirement_completeness_checklist")
        self.add_required_files(root)
        workbench = root / "03-工作台"
        (workbench / "任务执行协议.md").write_text(
            "## 需求沟通输出框架\npython 06-工具脚本/check_docs.py\n",
            encoding="utf-8",
        )
        (workbench / "当前需求沟通文档.md").write_text(
            "### 拆回正式文档清单\n\n"
            "| 结论/规则 | 主定义文档 | 影响资产 | 状态 | 备注 |\n"
            "|---|---|---|---|---|\n",
            encoding="utf-8",
        )

        result = check_docs.run_checks(root)

        self.assertTrue(
            any("missing ## 需求完备性检查清单" in item.message for item in result.warnings)
        )

    def test_reports_page_requirement_missing_core_headings(self):
        root = self.make_root("page_requirement_missing_core_headings")
        self.add_required_files(root)
        workbench = root / "03-工作台"
        (workbench / "任务执行协议.md").write_text(
            "## 需求沟通输出框架\npython 06-工具脚本/check_docs.py\n",
            encoding="utf-8",
        )
        (workbench / "当前需求沟通文档.md").write_text(
            "### 拆回正式文档清单\n\n"
            "| 结论/规则 | 主定义文档 | 影响资产 | 状态 | 备注 |\n"
            "|---|---|---|---|---|\n\n"
            "##### Q8-1 标注任务列表\n\n"
            "###### 功能目标\n",
            encoding="utf-8",
        )

        result = check_docs.run_checks(root)

        self.assertTrue(
            any("Page requirement section missing core headings" in item.message for item in result.warnings)
        )

    def test_reports_confirmed_page_missing_required_headings(self):
        root = self.make_root("confirmed_page_missing_required_headings")
        self.add_required_files(root)
        workbench = root / "03-工作台"
        (workbench / "任务执行协议.md").write_text(
            "## 需求沟通输出框架\n## 需求完备性检查清单\npython 06-工具脚本/check_docs.py\n",
            encoding="utf-8",
        )
        (workbench / "当前需求沟通文档.md").write_text(
            "### 拆回正式文档清单\n\n"
            "| 结论/规则 | 主定义文档 | 影响资产 | 状态 | 备注 |\n"
            "|---|---|---|---|---|\n\n"
            "| Q8-1 | 标注任务列表 | 标注员 | 网格 | 已确认 | - |\n\n"
            "##### Q8-1 标注任务列表\n\n"
            "###### 功能目标\n",
            encoding="utf-8",
        )

        result = check_docs.run_checks(root)

        self.assertTrue(
            any("Confirmed page missing required headings" in item.message for item in result.warnings)
        )

    def test_reports_confirmed_page_record_missing_trigger_rules(self):
        root = self.make_root("confirmed_page_record_missing_trigger_rules")
        self.add_required_files(root)
        workbench = root / "03-工作台"
        (workbench / "任务执行协议.md").write_text(
            "## 需求沟通输出框架\n## 需求完备性检查清单\npython 06-工具脚本/check_docs.py\n",
            encoding="utf-8",
        )
        (workbench / "当前需求沟通文档.md").write_text(
            "### 拆回正式文档清单\n\n"
            "| 结论/规则 | 主定义文档 | 影响资产 | 状态 | 备注 |\n"
            "|---|---|---|---|---|\n\n"
            "| Q8-1 | 标注任务列表 | 标注员 | 网格 | 已确认 | - |\n\n"
            "##### Q8-1 标注任务列表\n\n"
            "###### 功能目标\n"
            "###### ASCII 草图\n"
            "任务记录抽屉\n"
            "###### 待确认/待研发项\n",
            encoding="utf-8",
        )

        result = check_docs.run_checks(root)

        self.assertTrue(
            any("mentions records but has no trigger rules" in item.message for item in result.warnings)
        )

    def test_reports_invalid_landing_checklist_status(self):
        root = self.make_root("invalid_landing_checklist_status")
        self.add_required_files(root)
        workbench = root / "03-工作台"
        (workbench / "当前需求沟通文档.md").write_text(
            "### 拆回正式文档清单\n\n"
            "| 结论/规则 | 主定义文档 | 影响资产 | 状态 | 备注 |\n"
            "|---|---|---|---|---|\n"
            "| 规则A | [主文档](../02-PRD文档/后台管理/系统管理.md) | - | 已完成 | - |\n",
            encoding="utf-8",
        )

        result = check_docs.run_checks(root)

        self.assertTrue(any("invalid landing status" in item.message for item in result.warnings))

    def test_reports_landing_row_missing_source_doc_for_split_back(self):
        root = self.make_root("landing_split_back_missing_doc")
        self.add_required_files(root)
        workbench = root / "03-工作台"
        (workbench / "当前需求沟通文档.md").write_text(
            "### 拆回正式文档清单\n\n"
            "| 结论/规则 | 主定义文档 | 影响资产 | 状态 | 备注 |\n"
            "|---|---|---|---|---|\n"
            "| 规则A | - | - | 已拆回 | - |\n",
            encoding="utf-8",
        )

        result = check_docs.run_checks(root)

        self.assertTrue(any("已拆回 but has no source-of-truth link" in item.message for item in result.warnings))

    def test_reports_landing_row_missing_archive_link(self):
        root = self.make_root("landing_archive_missing_link")
        self.add_required_files(root)
        workbench = root / "03-工作台"
        (workbench / "当前需求沟通文档.md").write_text(
            "### 拆回正式文档清单\n\n"
            "| 结论/规则 | 主定义文档 | 影响资产 | 状态 | 备注 |\n"
            "|---|---|---|---|---|\n"
            "| 规则A | [主文档](../02-PRD文档/后台管理/系统管理.md) | - | 已归档 | - |\n",
            encoding="utf-8",
        )

        result = check_docs.run_checks(root)

        self.assertTrue(any("已归档 but has no archive link" in item.message for item in result.warnings))

    def test_reports_missing_completion_closure_gates_when_landing_statuses_exist(self):
        root = self.make_root("missing_completion_closure_gates")
        self.add_required_files(root)
        workbench = root / "03-工作台"
        (workbench / "当前需求沟通文档.md").write_text(
            "### 拆回正式文档清单\n\n"
            "| 结论/规则 | 主定义文档 | 影响资产 | 状态 | 备注 |\n"
            "|---|---|---|---|---|\n"
            "| 规则A | [主文档](../02-PRD文档/后台管理/系统管理.md) | - | 待拆回 | - |\n",
            encoding="utf-8",
        )

        result = check_docs.run_checks(root)

        self.assertTrue(any("missing closure gate" in item.message for item in result.warnings))

    def test_reports_review_record_missing_required_sections(self):
        root = self.make_root("review_record_missing_sections")
        self.add_required_files(root)
        workbench = root / "03-工作台"
        (workbench / "评审记录.md").write_text(
            "# 评审记录\n\n## 2026-04-29 示例主题\n\n### 问题描述\n",
            encoding="utf-8",
        )

        result = check_docs.run_checks(root)

        self.assertTrue(any("review entry missing sections" in item.message for item in result.warnings))

    def test_reports_workbench_readme_missing_protocol_driven_rules(self):
        root = self.make_root("workbench_readme_missing_protocol_rules")
        self.add_required_files(root)
        workbench = root / "03-工作台"
        (workbench / "README.md").write_text(
            "# 工作台\n\n## 目录定位\n当前目录用于承接讨论。\n\n## 主要内容\n- 记录\n",
            encoding="utf-8",
        )

        result = check_docs.run_checks(root)

        self.assertTrue(any("README missing protocol-driven workbench rule" in item.message for item in result.warnings))

    def test_reports_missing_prototype_check_command_in_completion_check(self):
        root = self.make_root("missing_prototype_check_command")
        (root / "AGENTS.md").write_text("ok\n", encoding="utf-8")
        workbench = root / "03-工作台"
        workbench.mkdir(parents=True)
        (workbench / "任务执行协议.md").write_text("ok\n", encoding="utf-8")
        (workbench / "任务完成检查.md").write_text("python 06-工具脚本/check_docs.py\n", encoding="utf-8")

        result = check_docs.run_checks(root)

        self.assertTrue(any("missing check_prototypes command" in item.message for item in result.warnings))

    def test_reports_missing_permission_boundary_rules_in_protocol(self):
        root = self.make_root("missing_permission_boundary_rules")
        self.add_required_files(root)
        workbench = root / "03-工作台"
        (workbench / "当前需求沟通文档.md").write_text(
            "### 拆回正式文档清单\n\n"
            "| 结论/规则 | 主定义文档 | 影响资产 | 状态 | 备注 |\n"
            "|---|---|---|---|---|\n",
            encoding="utf-8",
        )

        result = check_docs.run_checks(root)

        self.assertTrue(any("missing permission-boundary rule" in item.message for item in result.warnings))

    def test_reports_permission_matrix_duplication_in_discussion_doc(self):
        root = self.make_root("permission_matrix_duplication")
        self.add_required_files(root)
        workbench = root / "03-工作台"
        (workbench / "任务执行协议.md").write_text(
            "权限相关行为\n系统管理.md\npython 06-工具脚本/check_docs.py\n",
            encoding="utf-8",
        )
        (workbench / "当前需求沟通文档.md").write_text(
            "### 拆回正式文档清单\n\n"
            "| 结论/规则 | 主定义文档 | 影响资产 | 状态 | 备注 |\n"
            "|---|---|---|---|---|\n\n"
            "这里新增一张页面权限矩阵。\n",
            encoding="utf-8",
        )

        result = check_docs.run_checks(root)

        self.assertTrue(any("repeat permission source-of-truth content" in item.message for item in result.warnings))

    def test_reports_missing_error_governance_doc_reference_in_workbench_readme(self):
        root = self.make_root("missing_error_governance_reference")
        self.add_required_files(root)
        workbench = root / "03-工作台"
        (workbench / "README.md").write_text(
            "# 工作台\n\n"
            "## 目录定位\n当前目录用于承接讨论。\n\n"
            "## 主要内容\n"
            "| 文件 | 用途 |\n|---|---|\n| 当前需求沟通文档.md | 过程记录 |\n\n"
            "## 协议驱动区\n"
            "- 查看任务执行协议.md\n"
            "- 查看任务完成检查.md\n"
            "- 当前需求沟通文档.md\n"
            "- 评审记录.md\n",
            encoding="utf-8",
        )

        result = check_docs.run_checks(root)

        self.assertTrue(any("错误治理清单.md" in item.message for item in result.warnings))


if __name__ == "__main__":
    unittest.main()
