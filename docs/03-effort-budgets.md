# 3. Set the effort budget per task class

Effort is a cost setting with a cliff. In the launch-week benchmarks,
the same model wrote zero reasoning tokens at the low and medium
settings routine work runs on, and tens of thousands of tokens at the
top settings, at real prices. Both ends are a problem. At the cheap
end, there may be nothing readable to audit, so the tool-call log is
the only trail. At the expensive end, one task can cost what a day of
tasks should.

A provider default picks a point on that cliff for you, per its own
incentives. Never inherit it.

## The config

`config/budgets.json` maps each task class to a budget:

```json
"research": {
  "model": "frontier",
  "effort": "high",
  "max_cost_usd_per_task": 2.00,
  "why": "A wrong fact here ships in the piece. Spend reasoning to match."
}
```

Three decisions per class:

- **model and effort**: decide per class what a wrong answer costs,
  and spend reasoning to match. Research that feeds published claims
  is not the same class as rescheduling a meeting.
- **max_cost_usd_per_task**: the tripwire. When a run crosses it, that
  is a `cost_overrun` flag, not a surprise on the invoice.
- **why**: one sentence. Six months from now, the person auditing the
  config is you, and the sentence is the difference between a budget
  and a number.

`src/budgets.py` resolves a class to its budget. A class with no entry
is an error, and the `fallback` field ships as null on purpose. If you
want a fallback, write one deliberately, with its own `why`. The
failure mode this refuses is quiet: a new task class appears, nobody
sets a budget, and the provider default decides what the work costs
and how readable its reasoning is.

## Wiring it in

Resolve the budget when a task starts, put the result in every tool
call's `requested_config`, and the downgrade detector (doc 4) gets its
baseline for free. When a budget changes, the change is a config edit
with a reason, not a code change, and the ledger shows the new
`requested_config` from the next task onward.
