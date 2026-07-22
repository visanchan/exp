# Experiment Index

Permanent historical record of every experiment in this repository.

**Rows are never deleted.** An experiment's code may be removed, but its row
stays — the row is the proof that the work happened and the pointer to what
survived it.

Update this file after **creating, completing, archiving, or removing** an
experiment.

## Status values

| Status | Meaning |
|---|---|
| `Planned` | Defined, not started |
| `Active` | In progress |
| `Complete` | Finished, code still present |
| `Abandoned` | Stopped before completion, code still present |
| `Archived` | Knowledge extracted, code kept for reference |
| `Removed` | Knowledge extracted, code deleted |

## Index

| ID | Experiment | Date | Status | Main Lesson | Preserved Artifacts | Original Code Removed |
|---|---|---|---|---|---|---|
| exp-001 | scaffold-check | 2026-07-22 | Removed | A process rule with no artifact boundary is unenforced; make the define step its own commit | [lessons](../knowledge/lessons-learned/exp-001-scaffold-check.md) + [pattern](../knowledge/reusable-patterns/define-before-code-commit.md) + [snippet](../knowledge/code-snippets/repo-structure-check.md) | Yes |
| exp-002 | insight-observer | 2026-07-22 | Removed | Scaffolding before defining leaves tooling with nothing to apply it to — and a folder with no index row is invisible to the project that contains it | [lessons](../knowledge/lessons-learned/exp-002-insight-observer.md) — no code, notes, or commits existed to preserve | Yes |
| exp-003 | meowseum-reel-studio | 2026-07-22 | Removed | A reference image holds a visual identity across generations; a text description of the same thing does not — and a model asked to check its own work reports intent, not outcome | [lessons](../knowledge/lessons-learned/exp-003-meowseum-reel-studio.md) + patterns [quarantine](../knowledge/reusable-patterns/structural-data-quarantine.md), [audit](../knowledge/reusable-patterns/deterministic-audit-over-critic.md), [binary](../knowledge/reusable-patterns/discovered-optional-binary.md) + [snippet](../knowledge/code-snippets/stills-plus-audio-to-mp4.md) + [tool notes](../knowledge/tool-notes/openai-model-api-surface.md) + [prompt](../knowledge/prompt-library/character-sheet-for-visual-consistency.md) | Yes |

<!--
Row format — copy, fill in, keep newest at the bottom:

| exp-001 | short-description | 2026-07-22 | Active | — | — | No |
| exp-002 | short-description | 2026-07-22 | Removed | One-line transferable takeaway | [lessons] + [pattern] links to ../knowledge/... | Yes |

Rules:
- ID uses the exp-NNN prefix; Experiment column holds the kebab-case description.
- Date = start date; note completion in the experiment README.
- Main Lesson = one line, transferable, no implementation detail.
- Preserved Artifacts = relative links to files that actually exist. Use "—" if
  genuinely nothing was worth keeping, and say why in the lessons-learned doc.
- Original Code Removed = Yes / No.
-->
