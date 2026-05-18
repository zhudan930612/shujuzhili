import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_workbench


class CheckWorkbenchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_base = Path(__file__).resolve().parent / "check_workbench_tests_sandbox"
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

    def add_required_workbench_files(self, root: Path) -> None:
        workbench = root / "03-工作台"
        workbench.mkdir(parents=True)
        (workbench / "任务执行协议.md").write_text(
            "## 需求沟通输出框架\n## 需求完备性检查清单\n权限相关行为\n角色权限矩阵.xlsx\n系统管理.md\n",
            encoding="utf-8",
        )
        (workbench / "任务完成检查.md").write_text(
            "python 06-工具脚本/run_checks.py --scope all\npython 06-工具脚本/run_checks.py --scope prototypes\n",
            encoding="utf-8",
        )
        (workbench / "README.md").write_text(
            "协议驱动\n任务执行协议.md\n任务完成检查.md\n需求沟通模板.md\n评审记录.md\n错误治理清单.md\n",
            encoding="utf-8",
        )

    def test_reports_missing_run_checks_command(self):
        root = self.make_root("missing_run_checks")
        workbench = root / "03-工作台"
        workbench.mkdir(parents=True)
        (workbench / "任务完成检查.md").write_text("no command\n", encoding="utf-8")
        result = check_workbench.run_checks(root)
        self.assertTrue(any("missing run_checks all command" in item.message for item in result.errors))

    def test_reports_missing_discussion_landing_checklist(self):
        root = self.make_root("missing_landing_checklist")
        self.add_required_workbench_files(root)
        (root / "03-工作台" / "需求沟通模板.md").write_text("过程讨论\n", encoding="utf-8")
        result = check_workbench.run_checks(root)
        self.assertTrue(any("missing 拆回正式文档清单" in item.message for item in result.warnings))

    def test_reports_permission_matrix_duplication(self):
        root = self.make_root("permission_duplication")
        self.add_required_workbench_files(root)
        (root / "03-工作台" / "需求沟通模板.md").write_text("角色权限矩阵\n", encoding="utf-8")
        result = check_workbench.run_checks(root)
        self.assertTrue(any("repeat permission source-of-truth" in item.message for item in result.warnings))


if __name__ == "__main__":
    unittest.main()

