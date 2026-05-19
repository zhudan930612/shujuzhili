#!/usr/bin/env python
"""扫描会话历史中 data-governance-layer-triage 的分诊记录，输出模式统计。

用途：回答「哪些分诊规则最常被命中」「哪些层次最常被推荐」「哪些经验反复出现，该上移了」
不直接改文件，只输出报告。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# 分诊输出字段的正则
TRIAGE_FIELDS = {
    "object": re.compile(r"【分诊对象】\s*(.+)"),
    "keep": re.compile(r"【是否沉淀】\s*(.+)"),
    "rule": re.compile(r"【命中规则】\s*(.+)"),
    "layer": re.compile(r"【推荐层级】\s*(.+)"),
    "location": re.compile(r"【推荐位置】\s*(.+)"),
    "action": re.compile(r"【建议动作】\s*(.+)"),
    "upgrade": re.compile(r"【上移提醒】\s*(.+)"),
}

# 上移关键词：当上移提醒包含这些词时，视为有效上移信号
UPGRADE_POSITIVE = {"上移", "建议", "应", "优先", "迁移", "升级"}
UPGRADE_NEGATIVE = {"不涉及", "不适用", "暂不", "当前不"}

HISTORY_SOURCES = [
    (Path.home() / ".codex" / "history.jsonl", "text"),
    (Path.home() / ".claude" / "history.jsonl", "display"),
]

MIN_REPEAT_FOR_SIGNAL = 3  # 同类经验出现 >= 3 次才触发上移提醒


def parse_triage_entries(text: str) -> list[dict]:
    """从助手回复文本中提取所有分诊输出块。"""
    entries: list[dict] = []
    lines = text.splitlines()
    current: dict[str, str] = {}
    in_block = False

    for line in lines:
        matched = False
        for key, pattern in TRIAGE_FIELDS.items():
            m = pattern.search(line)
            if m:
                current[key] = m.group(1).strip()
                matched = True
                in_block = True
                break

        # 遇到空行或非字段行，且正在收集的块已有足够信息时，提交
        if not matched and in_block:
            if "object" in current:
                entries.append(dict(current))
            current = {}
            in_block = False

    if in_block and "object" in current:
        entries.append(dict(current))
    return entries


def scan_history(path: Path, text_field: str) -> list[dict]:
    """扫描单个 JSONL 历史文件。"""
    entries: list[dict] = []
    if not path.exists():
        return entries
    raw = path.read_text(encoding="utf-8", errors="replace")
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        text = obj.get(text_field, "")
        if isinstance(text, str) and text:
            entries.extend(parse_triage_entries(text))
    return entries


def normalize_object_key(obj: str) -> str:
    """将分诊对象归约为短键，用于发现重复模式。"""
    # 去掉过长的描述，保留前 60 字符做分组
    return obj[:60].strip()


def aggregate(entries: list[dict]) -> dict:
    """汇总统计数据。"""
    rule_hits: Counter[str] = Counter()
    layer_hits: Counter[str] = Counter()
    location_hits: Counter[str] = Counter()
    keep_count: Counter[str] = Counter()
    upgrade_signals: list[str] = []
    object_groups: defaultdict[str, list[str]] = defaultdict(list)

    for entry in entries:
        rule = entry.get("rule", "(未命中)")
        rule_hits[rule] += 1
        layer = entry.get("layer", "(未知)")
        layer_hits[layer] += 1
        location = entry.get("location", "(未知)")
        location_hits[location] += 1
        keep = entry.get("keep", "(未知)")
        keep_count[keep] += 1

        upgrade = entry.get("upgrade", "")
        if _is_upgrade_signal(upgrade):
            upgrade_signals.append(upgrade)

        obj = entry.get("object", "")
        if obj:
            object_groups[normalize_object_key(obj)].append(obj)

    # 找出同类经验 >= MIN_REPEAT_FOR_SIGNAL 的
    repeated = [
        (key, items)
        for key, items in object_groups.items()
        if len(items) >= MIN_REPEAT_FOR_SIGNAL
    ]
    repeated.sort(key=lambda x: len(x[1]), reverse=True)

    return {
        "total": len(entries),
        "rule_hits": rule_hits.most_common(),
        "layer_hits": layer_hits.most_common(),
        "location_hits": location_hits.most_common(),
        "keep_ratio": dict(keep_count),
        "upgrade_count": len(upgrade_signals),
        "upgrade_signals": upgrade_signals,
        "repeated": repeated,
    }


def _is_upgrade_signal(text: str) -> bool:
    if not text:
        return False
    if any(w in text for w in UPGRADE_NEGATIVE):
        return False
    return any(w in text for w in UPGRADE_POSITIVE)


def format_report(stats: dict) -> str:
    lines: list[str] = []
    lines.append("## 分诊模式统计")
    lines.append(f"- 扫描到分诊记录总数：**{stats['total']}**")
    lines.append("")

    if stats["total"] == 0:
        lines.append("暂无分诊记录。")
        return "\n".join(lines)

    # 规则命中分布
    lines.append("### 分诊规则命中次数")
    for rule, count in stats["rule_hits"]:
        lines.append(f"- 命中 {count} 次 — {rule}")
    lines.append("")

    # 推荐层级分布
    lines.append("### 推荐层级分布")
    for layer, count in stats["layer_hits"]:
        lines.append(f"- {count} 次 → {layer}")
    lines.append("")

    # 推荐落点分布
    lines.append("### 推荐落点分布")
    for loc, count in stats["location_hits"]:
        lines.append(f"- {count} 次 → {loc}")
    lines.append("")

    # 沉淀/不沉淀比例
    lines.append("### 沉淀决策")
    for k, v in stats["keep_ratio"].items():
        lines.append(f"- {k}: {v} 次")
    lines.append("")

    # 上移提醒
    if stats["upgrade_signals"]:
        lines.append(f"### 上移信号（共 {stats['upgrade_count']} 次）")
        for s in stats["upgrade_signals"]:
            lines.append(f"- {s}")
        lines.append("")

    # 重复出现的经验
    if stats["repeated"]:
        lines.append(f"### 重复出现的经验模式（≥{MIN_REPEAT_FOR_SIGNAL} 次）")
        for key, items in stats["repeated"]:
            lines.append(f"- **出现 {len(items)} 次** — `{key}...`")
            for item in items:
                lines.append(f"  - {item}")
        lines.append("")
    else:
        lines.append(f"### 重复出现的经验模式（≥{MIN_REPEAT_FOR_SIGNAL} 次）")
        lines.append("暂无满足阈值的重复模式。")
        lines.append("")

    # 上移建议
    if stats["repeated"]:
        lines.append("### 自动上移建议")
        lines.append("以下经验已反复出现，建议考虑上移到更高层级：")
        for key, items in stats["repeated"]:
            count = len(items)
            sample = items[0]
            lines.append(f"- 出现 {count} 次：`{sample}`")
            lines.append(f"  → 建议检查是否需要从当前落点上移到 AGENTS.md 或对应 skill")
        lines.append("")

    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="扫描会话历史中的分诊记录，输出模式统计"
    )
    p.add_argument(
        "--min-repeat",
        type=int,
        default=MIN_REPEAT_FOR_SIGNAL,
        help=f"重复出现的阈值（默认 {MIN_REPEAT_FOR_SIGNAL}）",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出原始统计数据",
    )
    p.add_argument(
        "--history",
        type=Path,
        default=None,
        help="指定历史文件路径（默认自动检测 codex/claude 历史）",
    )
    return p.parse_args(argv or sys.argv[1:])


def main(argv: list[str] | None = None) -> int:
    global MIN_REPEAT_FOR_SIGNAL
    args = parse_args(argv)
    MIN_REPEAT_FOR_SIGNAL = args.min_repeat

    if args.history:
        if str(args.history).endswith(".jsonl"):
            sources = [(args.history, "text")]
        else:
            print("错误：--history 需要指向 .jsonl 文件", file=sys.stderr)
            return 1
    else:
        sources = HISTORY_SOURCES

    all_entries: list[dict] = []
    for path, field in sources:
        entries = scan_history(path, field)
        if entries:
            all_entries.extend(entries)

    stats = aggregate(all_entries)

    if args.json:
        serializable = {
            "total": stats["total"],
            "rule_hits": stats["rule_hits"],
            "layer_hits": stats["layer_hits"],
            "location_hits": stats["location_hits"],
            "keep_ratio": stats["keep_ratio"],
            "upgrade_count": stats["upgrade_count"],
            "repeated": [
                {"key": k, "count": len(v), "samples": v}
                for k, v in stats["repeated"]
            ],
        }
        print(json.dumps(serializable, ensure_ascii=False, indent=2))
    else:
        print(format_report(stats))

    return 0


if __name__ == "__main__":
    sys.exit(main())
