import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_prototypes


class CheckPrototypesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_base = Path(__file__).resolve().parent / "check_prototypes_tests_sandbox"
        if cls.temp_base.exists():
            shutil.rmtree(cls.temp_base)
        cls.temp_base.mkdir()

    @classmethod
    def tearDownClass(cls):
        if cls.temp_base.exists():
            shutil.rmtree(cls.temp_base)

    def make_root(self, name: str) -> Path:
        root = self.temp_base / name
        (root / "04-原型效果图/后台管理").mkdir(parents=True)
        return root

    def test_reports_missing_prototype_css(self):
        root = self.make_root("missing_css")
        page = root / "04-原型效果图/后台管理/系统管理-角色管理.html"
        page.write_text("<html><body></body></html>", encoding="utf-8")

        result = check_prototypes.run_checks(root)

        self.assertTrue(any("missing prototype.css" in item.message for item in result.errors))

    def test_reports_missing_layout_script_when_frame_present(self):
        root = self.make_root("missing_layout_script")
        page = root / "04-原型效果图/后台管理/系统管理-角色管理.html"
        page.write_text(
            '<link rel="stylesheet" href="./assets/prototype.css" />\n'
            '<div class="frame"><header class="topbar"></header><aside class="sidebar"></aside></div>\n'
            '<script src="./assets/prototype.js"></script>\n',
            encoding="utf-8",
        )

        result = check_prototypes.run_checks(root)

        self.assertTrue(any("missing prototype-layout.js" in item.message for item in result.warnings))

    def test_reports_missing_switcher_script_for_state_bar(self):
        root = self.make_root("missing_switcher_script")
        page = root / "04-原型效果图/后台管理/系统管理-角色管理.html"
        page.write_text(
            '<link rel="stylesheet" href="./assets/prototype.css" />\n'
            '<div class="prototype-state-bar" data-prototype-switch></div>\n'
            '<script src="./assets/prototype.js"></script>\n'
            '<script src="./assets/prototype-layout.js"></script>\n',
            encoding="utf-8",
        )

        result = check_prototypes.run_checks(root)

        self.assertTrue(any("missing prototype-switcher.js" in item.message for item in result.warnings))

    def test_reports_list_page_without_proto_list_shell(self):
        root = self.make_root("list_without_shell")
        page = root / "04-原型效果图/后台管理/巡查管理-巡查记录列表页.html"
        page.write_text(
            '<link rel="stylesheet" href="./assets/prototype.css" />\n'
            '<table><tr><td>列表</td></tr></table>\n'
            '<script src="./assets/prototype.js"></script>\n'
            '<script src="./assets/prototype-layout.js"></script>\n',
            encoding="utf-8",
        )

        result = check_prototypes.run_checks(root)

        self.assertTrue(any("missing proto-list-shell" in item.message for item in result.warnings))

    def test_reports_page_actions_without_has_page_actions(self):
        root = self.make_root("page_actions_without_has_class")
        page = root / "04-原型效果图/后台管理/知识库管理-隐患子页面.html"
        page.write_text(
            '<link rel="stylesheet" href="./assets/prototype.css" />\n'
            '<section class="content-panel"></section>\n'
            '<div class="page-actions"></div>\n'
            '<script src="./assets/prototype.js"></script>\n'
            '<script src="./assets/prototype-layout.js"></script>\n',
            encoding="utf-8",
        )

        result = check_prototypes.run_checks(root)

        self.assertTrue(any("page-actions without has-page-actions" in item.message for item in result.warnings))

    def test_reports_multiple_row_actions_without_proto_row_actions(self):
        root = self.make_root("multi_actions_without_proto_row_actions")
        page = root / "04-原型效果图/后台管理/知识库管理-隐患库列表页.html"
        page.write_text(
            '<link rel="stylesheet" href="./assets/prototype.css" />\n'
            '<section class="proto-list-shell"><table><tbody><tr><td><span class="link">编辑</span> <span class="link">删除</span></td></tr></tbody></table></section>\n'
            '<script src="./assets/prototype.js"></script>\n'
            '<script src="./assets/prototype-layout.js"></script>\n',
            encoding="utf-8",
        )

        result = check_prototypes.run_checks(root)

        self.assertTrue(any("multi-action cell without proto-row-actions" in item.message for item in result.warnings))

    def test_reports_filter_grid_using_flexible_fr_columns(self):
        root = self.make_root("filter_grid_with_fr")
        page = root / "04-原型效果图/后台管理/系统管理-角色管理.html"
        page.write_text(
            '<link rel="stylesheet" href="./assets/prototype.css" />\n'
            '<style>.role-filter { display:grid; grid-template-columns:1.2fr 1fr 1.25fr auto auto; }</style>\n'
            '<div class="role-filter"><input /><select></select><div></div><button>查询</button><button>重置</button></div>\n'
            '<script src="./assets/prototype.js"></script>\n'
            '<script src="./assets/prototype-layout.js"></script>\n',
            encoding="utf-8",
        )

        result = check_prototypes.run_checks(root)

        self.assertTrue(any("custom filter grid" in item.message for item in result.warnings))


if __name__ == "__main__":
    unittest.main()
