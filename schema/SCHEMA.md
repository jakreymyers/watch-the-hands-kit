# Ledger schema

The kit stores everything in one append-only JSONL file. One record per
line. Nothing is edited or deleted after it lands; a mistake is fixed by
appending a `correction` record that points at the record it replaces.
These rules come from a production agent ledger, simplified for general
use.

## Rules

- Append-only. Never rewrite history.
- Missing values are null, never zero. A zero is a measurement; a null
  is an honest gap.
- Timestamps are ISO 8601 UTC.
- Corrections append, they do not overwrite.
- Every metric records its availability and source, so a missing number
  can never pass for a real one.
- Counts in snapshots are cumulative. Never sum snapshots together.

The first line of any ledger is a `schema` record stating the version
and rules, so a reader of the raw file can tell what they are looking
at without this document.

## Record types

### schema

First line of the ledger. Declares the version and the house rules.

```json
{"record_type": "schema", "schema_version": "1.0", "created": "2026-09-05", "rules": ["append_only", "missing_is_null_not_zero", "timestamps_iso8601_utc", "corrections_append_not_overwrite"]}
```

### task

One unit of work you asked an agent to do. The task record exists so
every tool call can name the decision it served, and so "zero flags"
has a denominator.

| field | meaning |
| --- | --- |
| task_id | primary key |
| class | task class, used for effort budgets and flag rates (research, drafting, publishing, ...) |
| run_id | groups every record produced by one run |
| started_at / ended_at | ISO 8601 UTC, ended_at null while running |
| request | what was asked, in plain text |
| decision | what the work was for, in plain text |

### tool_call

One record per tool call. This is the core record. If an action can
spend money, send a message, or change stored state, its record names
who allowed it.

| field | meaning |
| --- | --- |
| call_id | primary key |
| ts | when the call fired, ISO 8601 UTC |
| run_id | the run this call belongs to |
| lane | which agent, worker, or sub-process made the call |
| tool | the tool name as your stack calls it |
| inputs | arguments as sent |
| outputs | what came back, or a pointer to where it is stored |
| task_id | the task (and therefore the decision) this call served |
| authorization | `{kind, ref}`: `approval` names the person who approved this exact action; `grant` names the standing grant that covers it |
| requested_config | `{model, effort}` as requested for this run |
| observed_config | `{model, effort}` the provider actually ran, if your stack can observe it; null fields when it cannot |
| status | ok or error |
| cost_usd | null when unknown |

### flag

Something worth a human's attention. A flag is not necessarily a
failure; it is a marker that a check fired.

| field | meaning |
| --- | --- |
| flag_id | primary key |
| ts | when the flag was raised |
| task_id | the task under review |
| call_id | the specific call, when one is responsible; null for task-level flags |
| kind | fabrication, unapproved_action, config_mismatch, cost_overrun, or your own |
| severity | info, warn, or block |
| summary | one sentence, plain words |
| source | the check that raised it (a script name, a person, a review) |

### snapshot

Cumulative counts at a point in time, per scope (a day, a task class, a
lane). Snapshots are how "zero incidents" earns a denominator. Each
metric carries value, availability, and source. A metric you could not
observe is null with availability explaining why, never a zero.

| field | meaning |
| --- | --- |
| snapshot_id | primary key |
| observed_at | when the counts were read |
| scope | what the counts cover, e.g. `{class: "research", day: "2026-09-05"}` |
| metrics | map of metric name to `{value, availability, source}` |

### correction

Fixes a record without touching it. `replacement_values` holds the
fields that change; everything else on the original stands. Readers
apply corrections to get current truth, and can always
reconstruct what was believed at any point in time.

| field | meaning |
| --- | --- |
| correction_id | primary key |
| corrects_record_id | the record being corrected |
| reason | why, in plain words |
| replacement_values | the fields that change |

### alert

Written by the downgrade detector when a run's observed configuration
differs from what was requested. Stripped reasoning produces no error
from the provider; the alert is the error.

| field | meaning |
| --- | --- |
| alert_id | primary key |
| ts | when the detector fired |
| kind | config_mismatch |
| run_id | the affected run |
| detail | `{field, requested, observed}` per differing field |
