# Example 3: the silent downgrade

The launch-week failure: a stack downgraded the model mid-task and the
reasoning text disappeared with no error attached. The run kept
returning `status: ok`. The record of the run got thinner, and the
operators found out from the output.

This ledger reproduces it. One research task requested `frontier` at
`high` effort. The first call ran as asked. The second ran at `low`
effort and wrote zero reasoning tokens. The third ran on a cheaper
model entirely. Every call returned ok. Nothing in the provider
responses says anything changed; only the per-call observed config
shows it.

Run it:

```bash
python3 ../../src/validate.py ledger.jsonl
python3 ../../src/downgrade.py ledger.jsonl
python3 ../../src/downgrade.py ledger.jsonl --write   # appends alert records
python3 ../../src/validate.py ledger.jsonl            # still valid with alerts
```

What to take from it:

- The detector is a field-by-field comparison between
  `requested_config` and `observed_config`. It only works if your
  wrapper records both. Requested alone tells you what you hoped for.
- A null in `observed_config` means your provider does not expose that
  field. The detector skips nulls rather than guessing, which means
  unobservable fields are a known blind spot. Say so in your own
  docs when that applies to you.
- Where you send alerts is your call: the kit appends `alert` records
  to the ledger, and a ten-line cron or CI step can page on them.
