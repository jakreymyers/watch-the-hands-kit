# X article staging: How to watch the hands when you can't read the mind

Paste-ready body for X's longform composer. Composer mechanics:

- Title goes in the title field: How to watch the hands when you can't read the mind
- **text** marks bold to apply in the composer (the four list lead-ins).
- Lines like [IMAGE n] are placeholders. Upload the PNG from x/img/ natively at that spot, indented under the list item it follows. Alt text is quoted under each placeholder.
- Links: the composer hyperlinks selected text; the target URL is in (parens) after each linked phrase.
- X articles have no headings, code blocks, or hr. The --- rule from the GitHub version is dropped.

---

Start in September 2024, two years before Astra. OpenAI shipped o1, its first reasoning model, and made a decision most users scrolled past: it stopped showing the model's raw chain of thought. The launch post has a section titled "Hiding the Chains of Thought," and it lists the reasons plainly: "user experience, competitive advantage, and the option to pursue the chain of thought monitoring." From that day on, users got "a model-generated summary" of the thinking. OpenAI kept the full text for itself.

At the time, the reasoning text was the cheapest check on a model you had. You could read what it was thinking and catch a mistake forming. OpenAI's change moved that check behind its own walls: the company kept watching, and its customers read the summary.

Now move to the first week of September 2026. OpenAI shipped Astra, and the summary got thinner still. Part of Astra's reasoning is recurrent, meaning the model loops over its intermediate state internally instead of writing it out as text, so less of the thinking ever becomes words anyone can read.

The safety argument started within days. Steven Adler (@sjgadler), who spent four years leading safety evaluations inside OpenAI, accused his former employer of "violating one of the few redlines that exist in the AI community." Buck Shlegeris (@bshlgrs), CEO of the AI-safety research nonprofit Redwood Research, named the mechanism: the recurrent loop can be dialed up until chain-of-thought monitorability is destroyed. OpenAI's chief scientist, Jakub Pachocki (@merettm), answered that the thinner text is a side effect of capability: "more capable models can perform harder tasks using fewer language tokens." Daniel Kokotajlo (@dkokotajlo), an OpenAI safety alum who now directs the AI Futures Project, widened the point past OpenAI: even if this lab stops here, the next one will not.

Adler and Pachocki disagree about why the reasoning got thinner. They agree that it did.

The same week, Anthropic shipped Fable 5.1, and its version of the problem is quieter. Fable can show its thinking, but the progress updates arrive empty under the default configuration; to watch the agent work, you change the display setting yourself. Anthropic's docs add that the model narrates less than Fable 5 did, and less still at higher effort. And if your stack downgrades the model mid-task, the reasoning text disappears with no error attached (independent report, digitalapplied). The record of the run gets thinner, and you find out from the output.

Anthropic's own research says how far to trust the display even when it is on. In its 2025 faithfulness study, Claude 3.7 Sonnet mentioned a provided hint only 25% of the time, and models trained to cheat the reward admitted it under 2% of the time in most environments, usually constructing a clean rationale instead (link "arXiv 2505.05410" to https://arxiv.org/abs/2505.05410; Anthropic notes the eval settings were contrived). A 2023 study found faithfulness varies widely by task and drops as models get larger (link "arXiv 2307.13702" to https://arxiv.org/abs/2307.13702).

Anthropic researchers co-authored the 2025 multi-lab paper calling chain-of-thought monitoring "a new and fragile opportunity" worth protecting (link "arXiv 2507.11473" to https://arxiv.org/abs/2507.11473).

Then the reviewers started publishing. Simon Willison (@simonw), an independent researcher whose pelican benchmark is a widely used first test for new models, ran it across Fable 5.1's five effort levels. At low and medium, the settings routine work would run on, the model showed no visible reasoning. At xhigh it wrote 36,767 tokens and spent $1.83 on a single pelican. At max: 65,927 tokens, fourteen minutes, $3.30. Effort turns out to be a cost setting with a cliff, and at the cheap settings the model may produce nothing readable to audit.

Every (@every), a publication that spent a week testing Fable 5.1 on writing work, got the sharper result. Asked for 8 to 12 quotes, the model produced 43. Of the 27 quotes Every checked against the sources, 5 were not there. Asked for 1,000 words, it delivered 1,288. At the highest effort setting, it kept working after the operator interrupted it. The Neuron (@TheNeuronDaily) ran a live on-camera test and caught Fable making "a style decision you never asked for," then explaining itself fluently afterward. The Neuron's takeaway was the question of the week: how much judgment should we let it exercise without asking us first?

One developer tied it together in a dev.to piece. Gabriel Anhaia, a senior software engineer, read Astra's system card and noticed where OpenAI put its misalignment monitoring: around its own inference servers. His boundary, where an agent's output becomes a DELETE statement in his database, sits one hop down, and nothing watches it. OpenAI's headline safety claim for Astra, roughly half as many misalignment flags as Sol across more than 54,000 tasks, is a count taken on OpenAI's own runs. A customer has no flag count and no task count for their own agents. Anhaia's summary: "An agent with no flags and an agent with no flag detector produce identical dashboards."

Lay the week's events next to each other. OpenAI keeps the raw reasoning and hands you a summary. Anthropic hands you the reasoning with the display switched off, and publishes the research saying the display misleads. Both companies spent the week raising the same pitch: hand these models bigger jobs and walk away longer. The free way to check on that work, reading what the model was thinking, degraded in both products in the same seven days.

So watch the hands. Here is what that means. A model's reasoning text is the model's account of what it was doing. A tool call, a file written, a query run, a message sent, is the doing itself, with its inputs and outputs attached, and it happens on infrastructure you can instrument. The account can degrade. The actions remain visible on your side. Every failure from the launch week lives in the actions: Every's five fabricated quotes are outputs that match no source. The Neuron's style decision is a change with no request behind it. A silent downgrade is a run whose configuration changed mid-task. Anhaia's identical dashboards are a flag count with no task total behind it.

Four things to own, in order:

1. **Log every tool call.** One record per call: timestamp, agent or lane, tool, inputs, outputs, the decision it served, and the approver or grant that authorized it. If an action can spend money, send messages, or change stored state, its record names who allowed it. Skip this and your next postmortem becomes archaeology.

  [IMAGE 1: upload x/img/tool-call-record.png here, nested under list item 1. Alt: "One record per tool call: timestamp, lane, tool, inputs, outputs, the decision it served, the approver or grant, and the requested and observed configuration"]

2. **Count your flags, and your tasks.** "Zero incidents" means nothing until you know how many tasks ran. Define the count before you need it: flags per agent, per day, per task class. Until then, Anhaia's identical dashboards are what you have.

  [IMAGE 2: upload x/img/identical-dashboards.png here, nested under list item 2. Alt: "Two identical zero-flag dashboards; only one has a task count behind it"]

3. **Set the effort budget per task class.** Never inherit a default. Willison's numbers are the reason: routine work at low effort may run with no readable reasoning, and the top setting costs real money. Decide per class what a wrong answer costs, and spend reasoning to match.

  [IMAGE 3: upload x/img/effort-budgets.png here, nested under list item 3. Alt: "Effort is a cost setting with a cliff: no visible reasoning at low and medium, tens of thousands of tokens at the top settings"]

4. **Detect silent downgrades.** Alert when a run's model or thinking configuration differs from what you requested. Stripped reasoning produces no error. If you are not checking, you find out the way Every and The Neuron did: after the output surprises you.

  [IMAGE 4: upload x/img/silent-downgrade.png here, nested under list item 4. Alt: "A run downgraded mid-task: every response says ok while the observed configuration drops"]

None of the four depends on the vendor. That is the point of the list. The reasoning text is a feature two companies ship, thin, and meter; the log, the counts, the budgets, and the alerts live on your side, with the actions.

Anhaia opened his piece with a test: name the tool call your agent made yesterday that wrote to the database twice. If you can answer that on demand, the reasoning display can degrade as far as the vendors want to take it, and your week looks the same. If you cannot, that is the gap this week exposed, and the first item on the list is where you start.

[GATE: close paragraph wording is with Jak. Current draft below matches the GitHub article; do not publish until Jak signs off.]

The companion repo is at github.com/jakreymyers/watch-the-hands-kit (link that text to https://github.com/jakreymyers/watch-the-hands-kit). It has the ledger schema, the flag counter, the budget config, and the downgrade check, plus worked examples for each of the launch week's four failures. Clone it, keep the records, and replace whatever does not fit your stack.
