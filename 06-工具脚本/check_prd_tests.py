import shutil
import unittest
from pathlib import Path

import check_prd


class CheckPrdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_base = Path(__file__).resolve().parent / "check_prd_tests_sandbox"
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

    def add_prd_file(self, root: Path, content: str) -> None:
        prd_dir = root / "02-PRD文档" / "后台管理"
        prd_dir.mkdir(parents=True)
        (prd_dir / "示例.md").write_text(content, encoding="utf-8")

    def test_reports_missing_page_index(self):
        root = self.make_root("missing_page_index")
        self.add_prd_file(
            root,
            "## 页面需求\n\n### 示例页\n\n#### 页面基本信息\n",
        )
        result = check_prd.run_checks(root)
        self.assertTrue(any("missing 页面目录索引" in item.message for item in result.warnings))

    def test_reports_confirm_popup_missing_structure(self):
        root = self.make_root("popup_missing_structure")
        self.add_prd_file(
            root,
            "## 页面目录索引\n\n## 页面需求\n\n### 示例页\n\n"
            "#### 页面基本信息\n#### 页面入口\n#### 对应原型\n#### 页面状态\n#### 字段与展示规则\n"
            "#### 操作规则\n#### 异常与边界\n#### 页面弹窗 / 抽屉\n##### 弹窗 1：删除确认弹窗\n"
            "#### 权限相关行为\n#### 模块衔接\n#### 暂缓 / 待研发确认项\n#### 页面待确认问题\n",
        )
        result = check_prd.run_checks(root)
        self.assertTrue(any("confirm popup missing structure" in item.message for item in result.warnings))

    def test_reports_formal_prd_sketch_residue(self):
        root = self.make_root("sketch_residue")
        self.add_prd_file(root, "ASCII原型\n")
        result = check_prd.run_checks(root)
        self.assertTrue(any("formal PRD appears to retain page sketch body" in item.message for item in result.warnings))


if __name__ == "__main__":
    unittest.main()
