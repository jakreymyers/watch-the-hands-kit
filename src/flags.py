#!/usr/bin/env python3
"""Count flags and tasks, so "zero incidents" means something.

A flag count without a task count is a dashboard with no denominator.
This report never prints a bare zero: every line carries the number of
tasks behind it, and a flag count with no recorded tasks is called out
as meaningless instead of looking clean.

Usage: python3 src/flags.py ledger.jsonl [--class CLASS] [--day YYYY-MM-DD]
"""
import argparse
import json
import sys
from collections import defaultdict


def load(path):
    tasks, flags = {}, []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("record_type") == "task":
                tasks[r["task_id"]] = r
            elif r.get("record_type") == "flag":
                flags.append(r)
    return tasks, flags


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ledger")
    ap.add_argument("--class", dest="klass")
    ap.add_argument("--day")
    args = ap.parse_args()

    tasks, flags = load(args.ledger)
    if args.klass:
        tasks = {k: v for k, v in tasks.items() if v.get("class") == args.klass}
    task_ids = set(tasks)
    flags = [f for f in flags if f.get("task_id") in task_ids]
    if args.day:
        flags = [f for f in flags if str(f.get("ts", "")).startswith(args.day)]

    by_class = defaultdict(lambda: {"tasks": 0, "flags": 0, "kinds": defaultdict(int)})
    for t in tasks.values():
        by_class[t.get("class", "unclassed")]["tasks"] += 1
    for f in flags:
        klass = tasks.get(f.get("task_id"), {}).get("class", "unclassed")
        by_class[klass]["flags"] += 1
        by_class[klass]["kinds"][f.get("kind", "unknown")] += 1

    if not by_class:
        print("No tasks recorded. Any flag count here is meaningless: "
              "an agent with no flags and an agent with no flag detector "
              "produce identical dashboards.")
        return 1

    print(f"{'class':<20} {'tasks':>6} {'flags':>6} {'flags per 100 tasks':>20}")
    total_t = total_f = 0
    for klass in sorted(by_class):
        row = by_class[klass]
        t, fl = row["tasks"], row["flags"]
        total_t += t
        total_f += fl
        rate = f"{100.0 * fl / t:.1f}" if t else "n/a"
        print(f"{klass:<20} {t:>6} {fl:>6} {rate:>20}")
        for kind, c in sorted(row["kinds"].items()):
            print(f"  - {kind}: {c}")
    rate = f"{100.0 * total_f / total_t:.1f}" if total_t else "n/a"
    print(f"{'TOTAL':<20} {total_t:>6} {total_f:>6} {rate:>20}")
    if total_f == 0:
        print(f"\n0 flags across {total_t} recorded tasks. The zero has a denominator.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
