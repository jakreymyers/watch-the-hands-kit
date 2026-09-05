# Example 2: the style decision nobody asked for

The launch-week failure: a live on-camera test caught an agent making
"a style decision you never asked for," then explaining itself fluently
afterward. The explanation sounded reasonable. That is the trap. A
fluent account of a decision is not authorization for the decision.

This ledger reproduces the shape. A drafting task, a covered write
call, then an `update_doc_style` call that names the same grant. The
grant covers drafting text in one directory. It says nothing about
style. The flag was raised by a human reviewer, but the reason it was
findable in one grep is structural: every call names the approver or
grant behind it, so "which calls acted without coverage" is a query,
not an investigation.

Run it:

```bash
python3 ../../src/validate.py ledger.jsonl
grep -c '"kind":"grant"' ledger.jsonl   # every call names its cover
```

What to take from it:

- Name grants narrowly. `draft-text-in-drafts-dir` is a scope a
  reviewer can check a call against. `general-assistant-duties` is not.
- A grant and an approval are different records. Approval names the
  person who signed off on this exact action; a grant names the
  standing rule. Both live in the same field so the query is one
  field deep.
- When the agent explains itself afterward, the explanation is output.
  Log it as output. Do not let it upgrade the authorization.
