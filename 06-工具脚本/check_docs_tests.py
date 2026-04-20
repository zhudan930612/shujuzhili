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


if __name__ == "__main__":
    unittest.main()
