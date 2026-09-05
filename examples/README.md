# Examples

Each directory reproduces one launch-week failure from the article as a
ledger you can run the kit against. The failures are the four the
article closes on: fabricated quotes, a style decision nobody asked
for, a silent downgrade, and a zero-flag dashboard with no task count
behind it.

| example | failure | what the kit catches |
| --- | --- | --- |
| 01-fabricated-quotes | 5 of 27 checked quotes were not in the sources | outputs are logged, so quotes can be checked against fetched sources; flags point at the exact call |
| 02-unapproved-style-change | an agent made a style decision it was never asked for | every call names its approver or grant, so uncovered actions are a query |
| 03-silent-downgrade | model and effort dropped mid-run, no error | requested vs observed config comparison raises the alert the vendor never sends |
| 04-identical-dashboards | zero flags, and no way to know what ran | flag counts refuse to print without a task denominator |

Run everything from the repo root:

```bash
for d in examples/0*; do python3 src/validate.py "$d"/ledger*.jsonl; done
python3 src/flags.py examples/01-fabricated-quotes/ledger.jsonl
python3 src/downgrade.py examples/03-silent-downgrade/ledger.jsonl --write
```
