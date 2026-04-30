import shutil
import unittest
from pathlib import Path

import check_repo


class CheckRepoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_base = Path(__file__).resolve().parent / "check_repo_tests_sandbox"
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
        (root / "AGENTS.md").write_text(
            "`00-项目总览/\n`01-产品架构/\n`02-PRD文档/\n`03-工作台/\n`04-原型效果图/\n`05-来源资料/\n`06-工具脚本/\n`90-归档记录/\n",
            encoding="utf-8",
        )
        workbench = root / "03-工作台"
        workbench.mkdir(parents=True)
        (workbench / "任务执行协议.md").write_text("ok\n", encoding="utf-8")
        (workbench / "任务完成检查.md").write_text("ok\n", encoding="utf-8")

    def test_reports_missing_required_file(self):
        root = self.make_root("missing_required")
        result = check_repo.run_checks(root)
        self.assertTrue(any("Missing required file" in item.message for item in result.errors))

    def test_reports_broken_relative_markdown_link(self):
        root = self.make_root("broken_link")
        self.add_required_files(root)
        (root / "doc.md").write_text("[missing](./missing.md)\n", encoding="utf-8")
        result = check_repo.run_checks(root)
        self.assertTrue(any("Broken Markdown link" in item.message for item in result.errors))

    def test_large_discussion_doc_is_warning_only(self):
        root = self.make_root("large_discussion")
        self.add_required_files(root)
        (root / "03-工作台" / "当前需求沟通文档.md").write_text("x" * 30001, encoding="utf-8")
        result = check_repo.run_checks(root)
        self.assertTrue(any("Current discussion doc is large" in item.message for item in result.warnings))


if __name__ == "__main__":
    unittest.main()
