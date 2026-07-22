# Provenance and Scope

## What this skill is

This is a repository-local synthesis of reusable working methods known across the owner's skill environment: system capabilities, plugin-provided capabilities, user-level skills, and lessons generalized from project-local skills.

It is designed to work after cloning this repository without access to the owner's computer.

## What this skill is not

- It is not a byte-for-byte backup of every installed skill.
- It does not make uninstalled system or plugin tools available.
- It does not contain private company, customer, production, account, or credential context.
- It does not reproduce third-party skill text whose redistribution rights are unknown.
- It does not replace `AGENTS.md` or project-specific source files.

## Scope boundaries

| Source level | Treatment in this repository |
|---|---|
| System skills | Capability names and general methods may inform routing; implementation stays with the platform |
| Plugin skills | Treated as optional; this skill must remain useful without the plugin |
| User-level skills | Reusable behavior is synthesized, not required as a runtime dependency |
| Other project skills | Only portable lessons are generalized; project-specific truth remains in its owning project |
| This repository | `.agents/skills/ai-class-operating-partner/` is the canonical portable skill |

## Capability families considered

- Repository mapping, software engineering, debugging, testing, review, architecture, accessibility, and web quality.
- Business operations, product management, customer discovery, KPI design, inventory planning, market sizing, financial modeling, and data storytelling.
- UI and interface design, frontend implementation, prototypes, static sites, and Thai-market usability.
- Spreadsheets, documents, PDFs, presentations, visualizations, and standalone HTML workbooks.
- Structured thinking, discovery, handoffs, post-mortems, PRDs, issue decomposition, skill creation, and knowledge preservation.

This list describes functional coverage, not bundled ownership of the original skills.

## Rules for future updates

1. Confirm that the source material is safe and permitted to redistribute.
2. Extract the smallest generalizable method; do not copy private facts or entire skill bodies.
3. Keep absolute computer paths and live service details out of the skill.
4. Update the capability router only when the new method changes what an agent should do.
5. Validate the skill and test at least one realistic class prompt after a material change.
6. Record repository-wide scope changes in `docs/decisions/`.
