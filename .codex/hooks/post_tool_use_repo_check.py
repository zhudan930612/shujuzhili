import json
import subprocess


def main() -> None:
    result = subprocess.run(
        ["python", "06-工具脚本/run_checks.py", "--scope", "repo"],
        capture_output=True,
        text=True,
        check=False,
    )
    output = (result.stdout + result.stderr).strip()
    if not output:
        print("{}")
        return

    payload = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": "[repo check] " + output[:2000],
        }
    }
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
