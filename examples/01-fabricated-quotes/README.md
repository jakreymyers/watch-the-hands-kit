# Example 1: fabricated quotes

The launch-week failure: a publication testing a new model on writing
work asked for 8 to 12 quotes and got 43. Of the 27 quotes the editors
checked against the sources, 5 were not there.

The reasoning text would not have caught this. A model that invents a
quote can narrate a clean account of finding it. What catches it is
on your side of the boundary: the fetch calls stored the actual source
text, the write call stored the quotes, and a check compared the two.

This ledger reproduces the shape of that failure. One research task,
three `web_fetch` calls that store the sources, one `write_file` call
that stores 12 quotes, and five `flag` records from a checker script
that found five quotes matching no fetched source.

Run it:

```bash
python3 ../../src/validate.py ledger.jsonl
python3 ../../src/flags.py ledger.jsonl
```

What to take from it:

- The check only works because `outputs` recorded where the sources
  and the quotes landed. Log the pointer (`stored_at`) when the
  payload is big; log the payload when it is small.
- The flags point at the exact call responsible (`call_id`), so the
  postmortem starts at the write, not at a week of archaeology.
- `severity: block` is a choice this kit leaves to you. Define per
  flag kind what stops the line and what just gets counted.
