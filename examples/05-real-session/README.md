# Example 5: a real session, converted

The ledgers in examples 1 to 4 are synthetic. This one is not. It is
converted from one real day (2026-09-04) of a production autonomous
operation's append-only ledger, plus the session records behind it:
one listening pass, one review batch, 21 published items, four failed
publish attempts that became a real platform-friction flag, one
correction, and one account snapshot.

Scrubbing: platform IDs, URLs, handles, account names, and the text of
queries and drafts are removed or replaced with neutral placeholders.
Shapes, counts, timestamps, approval states, and failure modes are
exactly what the real ledger recorded.

Run it:

```bash
python3 ../../src/validate.py ledger.jsonl
python3 ../../src/flags.py ledger.jsonl
python3 ../../src/downgrade.py ledger.jsonl
python3 ../../src/budgets.py ../../config/budgets.json publishing
```

## What running the kit against real data surfaced

Three things, two of which changed the kit:

1. **The downgrade detector was silently blind, and said so nowhere.**
   The real harness records what each run did, but not the model or
   effort configuration behind each call, so `observed_config` is null
   on every record. The old `downgrade.py` compared what it could and
   printed "No config mismatches found," the same message a healthy,
   fully comparable ledger gets. That is the identical-dashboards
   failure one level down: a detector that cannot see, reporting as if
   it saw nothing wrong. `downgrade.py` now counts comparable calls.
   When none exist it says the check is blind and exits 1; when some
   calls lack observable config it says how many. The exit code on a
   found mismatch is now 1 as well, so a pipeline can gate on it.
2. **The exit code was being swallowed.** `downgrade.py` returned a
   status from `main()` but never passed it to `sys.exit`. Real
   pipelines gate on exit codes; this is exactly the kind of bug a
   synthetic ledger never catches, because a human reading the output
   sees the right words either way.
3. **Real class taxonomies outgrow the example config.** The
   operation's task classes include kinds the shipped `budgets.json`
   does not name. `budgets.py` errored on them, which is the designed
   behavior: a missing class is an error, never an inherited default.
   The friction is real though: adopting the kit means mapping your
   own classes into the config on day one, and the error message is
   the reminder to do it.

The authorization field earned its keep on real data. The 21
published items split into two groups without any tagging work:
sixteen approved verbatim by the owner in review batches and six
published under a standing auto-send grant. "Which public actions ran
under a grant versus an explicit approval" is one query over the
ledger, which is the point of the field.

The platform-friction flag is the record the synthetic examples
imitate: four failed submit attempts, each logged, the queue
preserved, and the decision handed to the owner instead of silent
retries. The postmortem for that evening started from the ledger and
needed nothing else.
