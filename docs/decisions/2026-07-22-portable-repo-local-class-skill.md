# Portable Repo-Local Class Skill

## Context

The repository owner has useful capabilities at several scopes: platform and
plugin skills, user-level skills, and project-local skills. Classmates who clone
this repository do not inherit those installations. Copying every source skill
would also risk exposing private project rules, personal paths, credentials, or
third-party material that is not safe to redistribute.

## Decision

Keep one canonical, repository-local skill at
`.agents/skills/ai-class-operating-partner/`.

The skill synthesizes reusable working methods for coding, debugging, testing,
business and data analysis, UI work, spreadsheets, documents, presentations,
and knowledge preservation. It depends only on files committed in this
repository.

Do not copy private project facts or complete external skill bodies into the
repository. Preserve scope provenance in the skill's
`references/provenance-and-scope.md` file. Treat `AGENTS.md` as authoritative.

## Consequences

- A friend can clone the repository and use the shared workflow without the
  owner's computer-level setup.
- The portable skill provides functional coverage, not identical copies of all
  upstream skills or their tools.
- Plugin-only or system-only capabilities remain optional and may be unavailable
  in another environment.
- Future skill additions require a redistribution and privacy check plus skill
  validation.
- Project-specific truth remains in the project that owns it.
