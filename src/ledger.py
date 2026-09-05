"""Append and read records in a watch-the-hands ledger.

A ledger is one JSONL file. One record per line, append-only. A mistake
is fixed by appending a correction record that points at the record it
replaces. Nothing is edited in place.

Stdlib only, Python 3.9+.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "1.0"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def append(path, record: dict) -> dict:
    record.setdefault("schema_version", SCHEMA_VERSION)
    line = json.dumps(record, sort_keys=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    return record


def read(path):
    p = Path(path)
    if not p.exists():
        return
    for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError as e:
            raise ValueError(f"line {n}: invalid JSON: {e}")


def log_task(path, *, task_id=None, task_class, run_id, request, decision,
             started_at=None, ended_at=None) -> dict:
    record = {
        "record_type": "task",
        "task_id": task_id or new_id("task"),
        "class": task_class,
        "run_id": run_id,
        "started_at": started_at or utc_now(),
        "ended_at": ended_at,
        "request": request,
        "decision": decision,
    }
    return append(path, record)


def log_tool_call(path, *, call_id=None, run_id, lane, tool, inputs, outputs,
                  task_id, authorization, requested_config, observed_config,
                  status="ok", cost_usd=None, ts=None) -> dict:
    """Record one tool call.

    authorization is {"kind": "approval", "ref": "<who approved this exact
    action>"} or {"kind": "grant", "ref": "<name of the standing grant>"}.
    Config dicts are {"model": ..., "effort": ...}; use null for fields
    your stack cannot observe. Unknown cost stays null, never zero.
    """
    record = {
        "record_type": "tool_call",
        "call_id": call_id or new_id("call"),
        "ts": ts or utc_now(),
        "run_id": run_id,
        "lane": lane,
        "tool": tool,
        "inputs": inputs,
        "outputs": outputs,
        "task_id": task_id,
        "authorization": authorization,
        "requested_config": requested_config,
        "observed_config": observed_config,
        "status": status,
        "cost_usd": cost_usd,
    }
    return append(path, record)


def log_flag(path, *, flag_id=None, task_id, call_id=None, kind, severity,
             summary, source, ts=None) -> dict:
    record = {
        "record_type": "flag",
        "flag_id": flag_id or new_id("flag"),
        "ts": ts or utc_now(),
        "task_id": task_id,
        "call_id": call_id,
        "kind": kind,
        "severity": severity,
        "summary": summary,
        "source": source,
    }
    return append(path, record)


def log_snapshot(path, *, snapshot_id=None, scope, metrics,
                 observed_at=None) -> dict:
    """Cumulative counts for a scope. Each metric is
    {"value": <number or null>, "availability": <str>, "source": <str>}.
    """
    record = {
        "record_type": "snapshot",
        "snapshot_id": snapshot_id or new_id("snap"),
        "observed_at": observed_at or utc_now(),
        "scope": scope,
        "metrics": metrics,
    }
    return append(path, record)


def log_correction(path, *, correction_id=None, corrects_record_id, reason,
                   replacement_values) -> dict:
    record = {
        "record_type": "correction",
        "correction_id": correction_id or new_id("corr"),
        "corrects_record_id": corrects_record_id,
        "reason": reason,
        "replacement_values": replacement_values,
        "ts": utc_now(),
    }
    return append(path, record)
