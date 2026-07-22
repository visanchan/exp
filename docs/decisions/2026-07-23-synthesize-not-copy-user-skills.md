# Synthesize Class-Relevant Skills, Do Not Copy the User-Level Collection

## Context

The repository is being prepared to share with a classmate. The request was to
explore the owner's user-level skills and re-create them here so the classmate
benefits from them after cloning.

The owner's environment has 48 user-level skills. Inspecting them for provenance
rather than assuming it:

- **12 contain private or personal context** — a private project board URL, a
  family business, a named company and product line, the owner's CV and academic
  profile, and personal design conventions referencing shipped work. Copying
  these into a shared repository would disclose business and personal material
  to anyone who clones it.
- **3 name a third-party author or product** in their body, and redistribution
  rights for that text are unknown.
- The remainder describe generic professional methods — debugging, testing,
  review, product and analysis practice — whose *ideas* are common knowledge even
  where the specific wording is not.

`docs/decisions/2026-07-22-portable-repo-local-class-skill.md` already answered
the general question: keep repository-local skills, and "do not copy private
project facts or complete external skill bodies into the repository."
`references/provenance-and-scope.md` states the skill "is not a byte-for-byte
backup of every installed skill", requires confirming redistribution rights
first, and requires extracting "the smallest generalizable method".

Bulk re-creation would contradict both.

## Decision

Do not copy or mechanically re-create the user-level collection.

Instead, write **original** skills covering the capability gaps a classmate
actually has when working in this repository with a coding agent. Four were
added:

- `systematic-debugging` — reproduce, shrink, hypothesise, falsify, prove.
  **Superseded the same day — see the second addendum below.**
- `reviewing-ai-written-code` — the failure modes specific to generated code,
  and verifying an agent's claims about its own work.
- `session-handoff` — carrying state, decisions and ruled-out approaches across
  a context limit or a change of agent.
- `write-a-repo-skill` — how to add the next one, including the provenance and
  privacy check.

Plus `.agents/skills/README.md` as an index, stating plainly what is excluded
and why.

Selection favoured methods that are general, stable, and repeatedly needed when
an agent is doing the work — not a proportional sample of the source collection.
Skills whose value is inseparable from private context were excluded entirely
rather than genericised into something vague.

**Addendum, same day.** Two business skills were promoted out of
`ai-class-operating-partner`'s general scope into standalone skills on request:

- `business-analysis` — decision framing, unit economics, break-even,
  sensitivity, and writing up so the recommendation leads.
- `market-sizing` — TAM/SAM/SOM, three independent estimation methods,
  triangulation, and the sanity checks that catch the usual errors.

Both are original text built on standard, widely taught methodology, with
synthetic worked examples. Neither draws on the excluded private or third-party
material. Financial modelling, inventory planning and customer-discovery methods
remain inside `ai-class-operating-partner` for now; promote them the same way if
they prove to be needed often enough to justify separate skills.

**Second addendum, same day — `systematic-debugging` merged into
`debug-mantra`.** The owner identified an existing user-level skill,
`debug-mantra`, as worth keeping here. Checked for provenance: no third-party
attribution, no licence or copyright marker, no private context — owner-authored,
so redistribution is the owner's call and permitted.

It overlapped the newly written `systematic-debugging` by roughly 60%: both
covered reproduce, hypothesise and falsify. `write-a-repo-skill` says to merge
near-duplicates rather than ship both, since an agent choosing between them
chooses badly. So they were merged under the `debug-mantra` name, which the owner
asked for and which is the more memorable trigger, and `systematic-debugging` was
deleted.

The merge was worth doing on the content alone. `debug-mantra` contributed
material the newer skill lacked: the verbatim recitation as a commitment device,
flaky-repro triage (raise the failure rate before debugging — 50% is workable,
1% is not), the fail-path escalation order with uniquely tagged probes for
single-grep cleanup, generating 3–5 ranked hypotheses to defeat anchoring,
running the disproof before the proof, and the ledger requiring a new hypothesis
to hold against every prior run rather than the most recent. `systematic-debugging`
contributed bisection, reading stack traces, cause-versus-symptom, proving the
fix with a regression test, the stuck checklist, and the agent-specific traps.

Net: one skill stronger than either, and one fewer near-duplicate.

**Third addendum, same day — `requirements-workbook`.** Added on request, to
address a failure the other skills do not: an agent guessing at requirements
that only exist in a non-technical person's head, then building the wrong thing
competently.

The skill has an agent generate a self-contained HTML questionnaire, open it,
and wait. Questions are multiple-choice, written in business rather than
engineering language, and every option states its consequence so someone who
cannot price the alternatives can still choose between them. A single button
copies the answers back as structured text, listing skipped questions explicitly
so "didn't get to it" is distinguishable from "no".

A complete working template lives in the skill's `references/`. It is the first
skill here to ship a runnable artifact rather than guidance alone, which is
deliberate: rebuilding clipboard handling per use would produce a different bug
each time.

## Consequences

- A classmate cloning the repository gets nine usable skills and no private
  material.
- Coverage is narrower than the owner's environment, deliberately.
- The excluded skills stay available to the owner locally; nothing was removed
  from the source environment.
- Future additions follow `write-a-repo-skill`, which encodes the same
  provenance check, so the rule is enforced by a document rather than by memory.
- If a specific excluded method is later wanted here, the route is to rewrite the
  generalizable idea from scratch, not to copy the original text.
