# AI Class Experiments

A temporary experimentation workspace for my AI class.

Short assignments, prototypes, framework tests, AI coding exercises, and
disposable applications live here. **The goal is not to preserve every
implementation.** The goal is to preserve useful knowledge, reusable patterns,
lessons learned, and transferable artifacts.

---

## The Core Distinction

This repository holds two kinds of content, and they are treated differently.

| | **Disposable implementation** | **Permanent knowledge** |
|---|---|---|
| Where | `experiments/exp-NNN-*/` | `knowledge/`, `docs/`, `templates/`, `archive/` |
| Lifespan | Deleted once it has served its purpose | Kept indefinitely |
| Contains | Source, tests, configs, scaffolding, dependencies | Lessons, patterns, prompts, snippets, tool notes, decisions, index rows |
| Rewriting it | Cheap — that is the point | Expensive — it came from experience |
| Deletion | Allowed, after a reviewed keep/delete proposal | Not allowed |

Nothing in `experiments/` is precious. Everything outside it is.

---

## Purpose

Use this repository to:

- Build temporary applications during class.
- Test AI coding tools, frameworks, APIs, and workflows.
- Explore ideas without touching production projects.
- Record successful and unsuccessful approaches.
- Extract reusable knowledge for future projects.
- Practice GitHub, version control, documentation, testing, and deployment.

---

## Repository Structure

```text
.
├── README.md                 # this file
├── AGENTS.md                 # rules for AI agents working here
├── .gitignore
├── .env.example              # variable NAMES only, never values
├── .agents/
│   └── skills/                         # portable skills — see skills/README.md
│       ├── ai-class-operating-partner/ # class workflow, the default
│       ├── local-dev-servers/          # running dev servers with an agent
│       ├── systematic-debugging/       # finding causes, not guessing fixes
│       ├── reviewing-ai-written-code/  # checking generated code before keeping it
│       ├── session-handoff/            # carrying work across sessions
│       └── write-a-repo-skill/         # adding a skill here safely
├── experiments/              # DISPOSABLE — one folder per experiment
│   └── README.md
├── knowledge/                # PERMANENT — extracted, transferable output
│   ├── lessons-learned/
│   ├── reusable-patterns/
│   ├── prompt-library/
│   ├── code-snippets/
│   └── tool-notes/
├── templates/                # PERMANENT — start-here documents
│   ├── experiment-readme-template.md
│   ├── lessons-learned-template.md
│   └── cleanup-checklist.md
├── archive/                  # PERMANENT — historical record
│   └── experiment-index.md
└── docs/                     # PERMANENT — class + repo documentation
    ├── class-notes/
    └── decisions/
```

---

## Experiment Lifecycle

### 1. Define
Create `experiments/exp-NNN-short-description/`. Copy
[`templates/experiment-readme-template.md`](templates/experiment-readme-template.md)
into it as `README.md`. Fill in objective, hypothesis, and success criteria
**before** writing code. Add a row to
[`archive/experiment-index.md`](archive/experiment-index.md) with status `Active`.

### 2. Build
Keep everything inside the experiment folder — source, tests, dependencies,
config. No credentials in source. Add any required variable names to
[`.env.example`](.env.example).

### 3. Test
Run it. Record test cases, what worked, what failed. Save useful outputs,
screenshots, and examples under the experiment's `artifacts/`.

### 4. Record Results
Complete the Results, Problems, and Lessons sections of the experiment README
while the details are still fresh.

### 5. Extract Knowledge
Write a lessons-learned document from
[`templates/lessons-learned-template.md`](templates/lessons-learned-template.md)
into `knowledge/lessons-learned/`. Move reusable patterns, prompts, snippets,
and tool notes into their `knowledge/` folders.

### 6. Clean Up
Work through [`templates/cleanup-checklist.md`](templates/cleanup-checklist.md).
Produce a keep/delete proposal. Delete the disposable implementation only after
approval.

### 7. Preserve
Update the index: status `Archived` or `Removed`, main lesson, preserved
artifacts, and whether the original code was removed. **The index row is never
deleted.**

---

## Naming Convention

```text
exp-001-short-description
exp-002-short-description
exp-003-short-description
```

Three-digit zero-padded number, lowercase kebab-case description. Branch name,
if used: `experiment/exp-001-short-description`.

---

## Knowledge Preservation Rules

Before deleting an experiment, move anything useful into:

```text
knowledge/lessons-learned/     # what happened and why
knowledge/reusable-patterns/   # approaches worth repeating
knowledge/prompt-library/      # prompts that worked
knowledge/code-snippets/       # small self-contained code
knowledge/tool-notes/          # notes on a tool, framework, or API
archive/experiment-index.md    # one permanent row per experiment
docs/decisions/                # repo-wide decisions and their reasoning
```

Do not preserve code only because it exists. Preserve it when it is:

- Reusable
- Educational
- Difficult to recreate
- Helpful to another project
- A good example of a successful pattern
- A useful example of a failure or mistake

---

## Cleanup Safety Rules

An AI agent must not delete an experiment immediately on a general cleanup
request. Before deletion:

1. Review the experiment.
2. Identify reusable knowledge and artifacts.
3. Create or update the lessons-learned document.
4. Update `archive/experiment-index.md`.
5. Show a proposed keep/delete list.
6. Confirm no credentials or sensitive files are being preserved.
7. Delete only the approved temporary implementation.

Git history may still contain previously committed content. **Sensitive
information must never be committed, even if the plan is to delete it later.**

---

## Security Rules

Never commit: `.env`, API keys, access tokens, passwords, private keys, database
credentials, personal information, production data, private customer
information, authentication cookies, or service-account files.

Document required environment variables by **name only** in `.env.example`:

```env
ANTHROPIC_API_KEY=
DATABASE_URL=
NEXT_PUBLIC_APP_URL=
```

Check staged files before every commit.

---

## Git Workflow

One branch per experiment:

```text
experiment/exp-001-description
```

Clear commit messages:

```text
chore: initialize experiment 001
feat: add prototype workflow
test: add validation cases
docs: record experiment findings
chore: remove temporary implementation
```

Do not push broken or sensitive work merely to preserve progress.

---

## Working With AI Agents

Agent rules live in [`AGENTS.md`](AGENTS.md). Point any AI coding tool at that
file before it starts. It covers scope, inspection-before-change, experiment
isolation, secrets, dependencies, testing, knowledge preservation, and the
keep/delete proposal required before any destructive cleanup.

The repository also carries a portable class skill at
[`.agents/skills/ai-class-operating-partner/SKILL.md`](.agents/skills/ai-class-operating-partner/SKILL.md).
It combines the reusable coding, analytics, business, UI, artifact, testing, and
knowledge-preservation methods needed for typical class work. It has no private
machine or project dependency, so it travels with the clone.

Use it explicitly with a prompt such as:

```text
Use $ai-class-operating-partner to turn this assignment into a tested experiment.
```

Five situational skills sit alongside it, indexed in
[`.agents/skills/README.md`](.agents/skills/README.md):

| Skill | Reach for it when |
|---|---|
| [`local-dev-servers`](.agents/skills/local-dev-servers/SKILL.md) | A project needs a backend and a frontend running at once, a dev server will not stay up under an agent, or a `localhost` URL will not open |
| [`systematic-debugging`](.agents/skills/systematic-debugging/SKILL.md) | Something throws or returns the wrong value — especially after a couple of attempted fixes have already missed |
| [`reviewing-ai-written-code`](.agents/skills/reviewing-ai-written-code/SKILL.md) | Before keeping or committing code an agent wrote |
| [`session-handoff`](.agents/skills/session-handoff/SKILL.md) | A session is ending or straining, or work passes to another agent or person |
| [`write-a-repo-skill`](.agents/skills/write-a-repo-skill/SKILL.md) | A method has proven itself often enough to be worth capturing here |

```text
Use $systematic-debugging — the login test passes locally and fails in CI.
```

These are **synthesized, not copied**. They deliberately exclude private
context, third-party skill text, and anything tied to one machine — see
[`.agents/skills/README.md`](.agents/skills/README.md) for what is left out and
why.

If an AI tool does not automatically discover `.agents/skills/`, point it to the
skill file directly. Repository rules in `AGENTS.md` remain authoritative.

---

## Final Principle

Temporary code may be deleted.

Useful knowledge should survive.
