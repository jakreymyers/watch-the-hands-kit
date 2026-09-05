# 5. Adapting the kit to your stack

The records are the product; the scripts are reference
implementations. Keep the record shapes and the rules in
`schema/SCHEMA.md`, and replace everything else without guilt.

## Keep these whatever you do

- Append-only, corrections never overwrite.
- Missing is null, never zero.
- Every metric carries availability and source.
- Every tool call names its task, and tasks name the decision served.
- Every action that spends money, sends messages, or changes stored
  state names its approver or grant.

These five are what make the difference between a log and an audit
trail. Everything else is negotiable.

## Storage

JSONL is the starting point because it is append-only by construction,
diffable, and greppable. When volume outgrows it:

- SQLite or Postgres: one table per record type, or one table with a
  `record_type` column and a JSONB body. The validator's checks
  (unique IDs, resolving references, corrections pointing at real
  records) become constraints and queries.
- An existing observability stack: map each record type to an event
  type. Keep the field names; the value is in the schema, not the
  container.

## Logging from your framework

Wrap tool dispatch, wherever your framework puts it:

- Frameworks with tool-call hooks or middleware: translate the hook's
  event into a `tool_call` record at the hook point.
- Frameworks that emit OpenTelemetry spans: a span processor can emit
  the record from span attributes. Inputs and outputs usually need an
  explicit attribute; do not let the default span set decide what you
  record.
- No hooks: give the agent a `call_tool()` function that logs and then
  dispatches, and route everything through it.

Whichever path, test the wrapper the way you would test payment code:
a call that throws still gets a record, with `status: error`.

## Authorization in your org

`approval` and `grant` map onto however your org already delegates:

- A grant is any standing rule: a playbook entry, an IAM policy, a
  signed-off runbook section. `ref` should name something a reviewer
  can open.
- An approval is a person saying yes to this exact action. Tie `ref`
  to wherever that yes lives: a ticket, a message thread, a signed
  commit.

If your agents act under standing grants most of the time, the
discipline that matters is naming grants narrowly enough that a
reviewer can check a call against them. Example 2 is the failure to
aim at.

## Flags, budgets, downgrades

- Point `flags.py` at your store, or rewrite its thirty lines against
  your query layer. Keep the refusal to print a bare zero.
- Keep budgets in a file humans review, in whatever format your org
  reviews well. The mechanism that matters is the error on a missing
  class, not JSON.
- Run `downgrade.py` (or its equivalent) on a schedule and after any
  provider incident. Where your stack does its own routing, the
  observed config is already in your hands, which makes the check
  cheap and exact.
