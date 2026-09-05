#!/usr/bin/env python3
"""Resolve the effort budget for a task class.

The rule: set the budget per task class, and never inherit a vendor
default. A class with no entry is an error. Nothing falls back
to whatever the provider ships. The only permitted fallback is one you
wrote yourself in the config, on purpose.

Usage:
  python3 src/budgets.py config/budgets.json research
"""
import argparse
import json
import sys


def load_budgets(path):
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg.get("classes", {}), cfg.get("fallback")


def resolve(cfg_path, task_class):
    classes, fallback = load_budgets(cfg_path)
    if task_class in classes:
        return classes[task_class], "class"
    if fallback is not None:
        return fallback, "fallback"
    raise KeyError(
        f"no budget for task class {task_class!r} and no fallback set. "
        f"Add the class to the config. Inheriting a provider default is "
        f"how routine work ends up running with no readable reasoning, "
        f"or at a price you did not choose."
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("task_class", nargs="?")
    args = ap.parse_args()
    if not args.task_class:
        classes, fallback = load_budgets(args.config)
        print("classes:", ", ".join(sorted(classes)) or "(none)")
        print("fallback:", json.dumps(fallback))
        return 0
    try:
        budget, origin = resolve(args.config, args.task_class)
    except KeyError as e:
        print(e.args[0])
        return 1
    print(json.dumps({"task_class": args.task_class, "origin": origin,
                      "budget": budget}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
