#!/usr/bin/env python3
"""Validate a watch-the-hands ledger.

Checks, in order: every line is JSON with a record_type and
schema_version; primary IDs are unique; each record type carries its
required fields; references between records resolve. Corrections must
point at a real record.

Usage: python3 src/validate.py path/to/ledger.jsonl
"""
import json
import sys
from pathlib import Path

PRIMARY_ID = {
    "task": "task_id",
    "tool_call": "call_id",
    "flag": "flag_id",
    "snapshot": "snapshot_id",
    "correction": "correction_id",
    "alert": "alert_id",
}

REQUIRED = {
    "task": ["task_id", "class", "run_id"],
    "tool_call": ["call_id", "ts", "run_id", "lane", "tool", "task_id",
                  "authorization", "requested_config", "observed_config"],
    "flag": ["flag_id", "ts", "task_id", "kind", "severity"],
    "snapshot": ["snapshot_id", "observed_at", "scope", "metrics"],
    "correction": ["correction_id", "corrects_record_id", "reason"],
    "alert": ["alert_id", "ts", "run_id", "detail"],
}


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip())
        return 2
    p = Path(sys.argv[1])
    errors = []
    ids = {}
    rows = []
    for n, line in enumerate(p.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError as e:
            errors.append(f"line {n}: invalid JSON: {e}")
            continue
        rows.append((n, r))
        if not r.get("record_type") or not r.get("schema_version"):
            errors.append(f"line {n}: missing record_type/schema_version")
        f = PRIMARY_ID.get(r.get("record_type"))
        if f and r.get(f):
            if r[f] in ids:
                errors.append(f"line {n}: duplicate ID {r[f]} (line {ids[r[f]]})")
            else:
                ids[r[f]] = n

    for n, r in rows:
        t = r.get("record_type")
        for f in REQUIRED.get(t, []):
            if f not in r:
                errors.append(f"line {n}: {t} missing {f}")
        refs = []
        if t == "tool_call":
            refs = [r.get("task_id")]
        elif t == "flag":
            refs = [r.get("task_id"), r.get("call_id")]
        elif t == "correction":
            refs = [r.get("corrects_record_id")]
        for ref in filter(None, refs):
            if ref not in ids:
                errors.append(f"line {n}: dangling reference {ref}")
        if t == "snapshot":
            for name, m in r.get("metrics", {}).items():
                if not isinstance(m, dict) or "value" not in m or "availability" not in m:
                    errors.append(f"line {n}: snapshot metric {name} needs value and availability")

    if errors:
        print("\n".join(errors))
        return 1
    print(f"OK: {len(rows)} records, {len(ids)} unique IDs, references resolved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
