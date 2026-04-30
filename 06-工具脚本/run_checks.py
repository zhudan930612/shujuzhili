#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import check_prd
import check_prototypes
import check_repo
import check_workbench
from check_common import CheckResult, print_issues


SCOPES = {
    "repo": check_repo.run_checks,
    "workbench": check_workbench.run_checks,
    "prd": check_prd.run_checks,
    "prototypes": check_prototypes.run_checks,
}


def run_scope(root: Path, scope: str) -> CheckResult:
    if scope == "all":
        result = CheckResult()
        for runner in SCOPES.values():
            result.extend(runner(root))
        return result
    return SCOPES[scope](root)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run repository document checks by scope.")
    parser.add_argument(
        "--scope",
        choices=["all", *SCOPES.keys()],
        default="all",
        help="Select which asset-type checks to run.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    result = run_scope(Path.cwd().resolve(), args.scope)
    print_issues(result)
    return 1 if result.errors else 0


if __name__ == "__main__":
    sys.exit(main())
