import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / ".codex" / "hooks" / "post_tool_use_dispatch.py"
SPEC = importlib.util.spec_from_file_location("post_tool_use_dispatch", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class PostToolUseDispatchTests(unittest.TestCase):
    def collect_scopes(self, tool_name: str, tool_input: dict) -> list[str]:
        return MODULE.collect_scopes({"tool_name": tool_name, "tool_input": tool_input})

    def test_repo_scope_for_agents(self):
        scopes = self.collect_scopes("Edit", {"file_path": "AGENTS.md"})
        self.assertEqual(scopes, ["repo"])

    def test_readme_routes_to_repo_even_under_prd(self):
        scopes = self.collect_scopes("Write", {"path": "02-PRD文档/README.md"})
        self.assertEqual(scopes, ["repo"])

    def test_workbench_scope_for_discussion_doc(self):
        scopes = self.collect_scopes("Edit", {"file_path": "03-工作台/20260510需求文档.md"})
        self.assertEqual(scopes, ["workbench"])

    def test_prd_scope_for_prd_doc(self):
        scopes = self.collect_scopes("Edit", {"file_path": "02-PRD文档/后台管理/项目管理.md"})
        self.assertEqual(scopes, ["prd"])

    def test_prototypes_scope_for_backend_html(self):
        scopes = self.collect_scopes("Write", {"path": "04-原型效果图/后台管理/标注质检-质检工作台.html"})
        self.assertEqual(scopes, ["prototypes"])

    def test_multi_scope_is_deduped_and_ordered(self):
        scopes = self.collect_scopes(
            "Edit",
            {"paths": ["02-PRD文档/后台管理/项目管理.md", "AGENTS.md", "AGENTS.md"]},
        )
        self.assertEqual(scopes, ["repo", "prd"])

    def test_archive_path_is_excluded(self):
        scopes = self.collect_scopes("Edit", {"file_path": "90-归档记录/历史决策.md"})
        self.assertEqual(scopes, [])

    def test_unrelated_path_is_ignored(self):
        scopes = self.collect_scopes("Edit", {"file_path": "tmp/notes.md"})
        self.assertEqual(scopes, [])


if __name__ == "__main__":
    unittest.main()
