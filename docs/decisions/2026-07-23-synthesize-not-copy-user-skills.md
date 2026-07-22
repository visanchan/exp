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

## Consequences

- A classmate cloning the repository gets six usable skills and no private
  material.
- Coverage is narrower than the owner's environment, deliberately. Business
  analysis, market sizing, financial modelling and similar remain within
  `ai-class-operating-partner`'s scope rather than becoming separate skills.
- The excluded skills stay available to the owner locally; nothing was removed
  from the source environment.
- Future additions follow `write-a-repo-skill`, which encodes the same
  provenance check, so the rule is enforced by a document rather than by memory.
- If a specific excluded method is later wanted here, the route is to rewrite the
  generalizable idea from scratch, not to copy the original text.
