# watch-the-hands-kit

A starter kit for auditing AI agents by their actions instead of their
reasoning text. Companion to the article "How to watch the hands when
you can't read the mind."

The article's argument in one paragraph: a model's reasoning text is
the model's account of what it was doing, and vendors keep thinning
it, hiding it, or switching the display off. A tool call, a file
written, a query run, a message sent, is the doing itself, and it
happens on infrastructure you can instrument. The account can degrade.
The actions remain visible on your side. This kit is a starting point
for instrumenting them.

Clone it, run the
examples, then keep the records and throw away whatever does not fit
your stack. Python 3.9+, standard library only, no dependencies.

## The four things

1. **Log every tool call.** One record per call: timestamp, lane,
   tool, inputs, outputs, the decision it served, and the approver or
   grant that authorized it. See `schema/SCHEMA.md` and `src/ledger.py`.
   If an action can spend money, send a message, or change stored
   state, its record names who allowed it.
2. **Count flags and tasks.** "Zero incidents" means nothing until you
   know how many tasks ran. `src/flags.py` never prints a bare zero;
   every count carries its denominator.
3. **Set the effort budget per task class.** Never inherit a default.
   `config/budgets.json` plus `src/budgets.py` make a missing class an
   error instead of a silent fallback to whatever the provider ships.
4. **Detect silent downgrades.** `src/downgrade.py` compares the
   model and effort you requested against what the provider actually
   ran, per tool call, and raises an alert when they differ. Stripped
   reasoning produces no error from the vendor; the alert is the error.

![Anatomy of a tool-call record](diagrams/tool-call-record.svg)

## Quickstart

```bash
# run the worked examples
python3 src/validate.py examples/01-fabricated-quotes/ledger.jsonl
python3 src/flags.py examples/04-identical-dashboards/ledger-tasks.jsonl
python3 src/flags.py examples/04-identical-dashboards/ledger-empty.jsonl   # exits 1 on purpose: no tasks recorded, so no flag count means anything
python3 src/downgrade.py examples/03-silent-downgrade/ledger.jsonl --write  # appends 2 alert records to the example ledger, exits 1: that is the detection working
python3 src/budgets.py config/budgets.json research
```

Some commands write to the example ledgers (`--write`) or exit
nonzero on purpose. `git checkout -- examples/` restores the shipped
state.

Each example directory has its own README explaining the failure it
reproduces and what the kit catches.

## Layout

```
schema/SCHEMA.md     record shapes, field by field, with the rules that make them auditable
ledger/schema.jsonl  seed first line for a new ledger
src/ledger.py        append and read records; logging helpers
src/validate.py      structural checks: IDs unique, references resolve, corrections point at real records
src/flags.py         flag and task counts, per class, with denominators
src/budgets.py       per-class effort budget resolution; missing class is an error
src/downgrade.py     requested vs observed config comparison; writes alert records
config/budgets.json  example budget config; edit this first
examples/            the article's four launch-week failures, reproduced as ledgers
diagrams/            the concept images, as SVG
docs/                the longer write-ups, including how to adapt the kit to your stack
```

## Where the schema comes from

The record shapes are a simplified, generalized version of the ledger a
real autonomous operation runs on. The production ledger appends every
signal, decision, snapshot, and correction to one JSONL file and
validates it before every commit. The kit keeps these ideas
(append-only, corrections never overwrite, missing is null not zero,
every metric carries availability and source) and drops everything
specific to that operation.

## Adapting it to your stack

Read `docs/05-adapting-to-your-stack.md`. Short version: keep the
`tool_call` record and the four rules in `schema/SCHEMA.md`, replace
the logging helpers with a wrapper around whatever your agents already
call, and point `flags.py` and `downgrade.py` at the result. The
records are the product; the scripts are reference implementations.

## License

MIT. See `LICENSE`.
