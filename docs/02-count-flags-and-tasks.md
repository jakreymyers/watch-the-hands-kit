# 2. Count flags and tasks

"Zero incidents" means nothing until you know how many tasks ran. Gabriel
Anhaia's summary: "An agent with no flags and an agent with no flag
detector produce identical dashboards." The denominator is what separates
them.

## Define the count before you need it

Pick the axes now, while nothing is on fire: flags per agent, per day,
per task class. The kit's defaults are class and day, because class is
where the risk differs and day is where people report. Add lane,
severity, or kind if your operation needs them. The point is that the
definition exists before the incident review asks for it.

`src/flags.py` is the reference report. Two behaviors matter more than
the numbers:

1. Every flag count prints with its task count and a rate per 100
   tasks. A rate is comparable across weeks; a bare count is not.
2. When no tasks are recorded, the report refuses to print a zero and
   says why, and exits nonzero so a pipeline can catch it.

![Identical dashboards](../diagrams/identical-dashboards.svg)

## What counts as a flag

A flag is a marker that a check fired, not proof of failure. The kit
ships four kinds (fabrication, unapproved_action, config_mismatch,
cost_overrun) and expects you to add your own. Two rules of thumb:

- A check you can run mechanically should raise flags mechanically.
  The quote checker in example 1 and the downgrade detector in
  example 3 both write flag or alert records without a human in the
  loop.
- A human reviewer's call is also a flag, with `source` naming the
  review. Example 2 works this way.

Severity is your policy. The kit uses info, warn, and block, and
leaves which kind maps to which severity, and what block stops, to
you.

## Snapshots

For anything you want to trend, write a `snapshot` record: cumulative
counts for a scope, with each metric's availability and source
attached. Snapshots are never summed together; each is a fresh read of
cumulative state. A metric you could not observe is null with the
reason in `availability`. That one rule is what keeps a missing
number from impersonating a good one.
