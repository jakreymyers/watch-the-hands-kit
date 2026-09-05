#!/usr/bin/env python3
"""Detect silent downgrades.

Compares each tool call's requested model/effort against what the
provider actually ran. A stripped reasoning budget produces no error
from the vendor, so the check has to live on your side. Mismatches are
printed, and with --write an alert record is appended to the ledger.

Usage:
  python3 src/downgrade.py ledger.jsonl
  python3 src/downgrade.py ledger.jsonl --write
"""
import argparse
import json
import uuid


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ledger")
    ap.add_argument("--write", action="store_true",
                    help="append alert records for each mismatched call")
    args = ap.parse_args()

    mismatches = []
    comparable = 0
    calls = 0
    with open(args.ledger, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("record_type") != "tool_call":
                continue
            calls += 1
            req = r.get("requested_config") or {}
            obs = r.get("observed_config") or {}
            diff = []
            has_overlap = False
            for field in sorted(set(req) | set(obs)):
                rv, ov = req.get(field), obs.get(field)
                if rv is not None and ov is not None:
                    has_overlap = True
                    if rv != ov:
                        diff.append({"field": field, "requested": rv, "observed": ov})
            if has_overlap:
                comparable += 1
            if diff:
                mismatches.append((r, diff))

    if calls and comparable == 0:
        print(f"{calls} tool call(s) checked; none carried observable config "
              f"(observed_config is null everywhere). Downgrade detection is "
              f"blind on this ledger: a mismatched run would produce no alert. "
              f"Record the observed model and effort per call, or this check "
              f"cannot fire.")
        return 1
    if not mismatches:
        blind = f" ({calls - comparable} call(s) carried no observable config)" if calls > comparable else ""
        print(f"No config mismatches found across {comparable} comparable call(s){blind}.")
        return 0

    alerts = []
    for r, diff in mismatches:
        print(f"{r.get('ts')} run {r.get('run_id')} call {r.get('call_id')}: "
              + ", ".join(f"{d['field']}: requested {d['requested']!r}, got {d['observed']!r}"
                          for d in diff))
        alerts.append({
            "record_type": "alert",
            "alert_id": f"alert-{uuid.uuid4().hex[:12]}",
            "ts": r.get("ts"),
            "kind": "config_mismatch",
            "run_id": r.get("run_id"),
            "call_id": r.get("call_id"),
            "detail": diff,
        })

    if args.write:
        with open(args.ledger, "a", encoding="utf-8") as f:
            for a in alerts:
                a.setdefault("schema_version", "1.0")
                f.write(json.dumps(a, sort_keys=True) + "\n")
        print(f"\n{len(alerts)} alert record(s) appended.")
    else:
        print(f"\n{len(mismatches)} mismatched call(s). Re-run with --write to record alerts.")
    return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
