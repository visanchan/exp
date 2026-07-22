# README — AI Class Experiments

Save this section as `exp/README.md`.

---

# AI Class Experiments

This repository is a temporary experimentation workspace for my AI class.

It is designed for short assignments, prototypes, technical experiments, and practice projects that may later be removed. The main goal is not to preserve every implementation permanently. The goal is to preserve useful knowledge, reusable patterns, lessons learned, and transferable artifacts.

## Purpose

This repository may be used to:

* Build temporary applications during class.
* Test AI coding tools, frameworks, APIs, and workflows.
* Explore ideas without affecting production projects.
* Record successful and unsuccessful approaches.
* Extract reusable knowledge for future projects.
* Practice GitHub, version control, documentation, testing, and deployment.

## Experiment Lifecycle

Each experiment should follow this lifecycle:

1. **Define**

   * Record the objective.
   * Record the assignment or problem.
   * Record the success criteria.

2. **Build**

   * Create the experiment in its own folder.
   * Keep dependencies and configuration isolated.
   * Avoid placing credentials in source code.

3. **Test**

   * Record what was tested.
   * Record what worked and what failed.
   * Save useful screenshots, outputs, or examples when appropriate.

4. **Extract Knowledge**

   * Write a short lessons-learned document.
   * Identify reusable code patterns, prompts, workflows, or design decisions.
   * Move reusable artifacts into the shared knowledge folders.

5. **Clean Up**

   * Remove temporary code when it is no longer useful.
   * Preserve documentation and transferable artifacts.
   * Confirm that no important knowledge will be lost before deletion.

## Recommended Repository Structure

```text
ai-class-experiments/
├── README.md
├── AGENTS.md
├── .gitignore
├── .env.example
├── experiments/
│   ├── README.md
│   └── exp-001-example/
│       ├── README.md
│       ├── src/
│       ├── tests/
│       ├── notes/
│       └── artifacts/
├── knowledge/
│   ├── lessons-learned/
│   ├── reusable-patterns/
│   ├── prompt-library/
│   ├── code-snippets/
│   └── tool-notes/
├── templates/
│   ├── experiment-readme-template.md
│   ├── lessons-learned-template.md
│   └── cleanup-checklist.md
├── archive/
│   └── experiment-index.md
└── docs/
    ├── class-notes/
    └── decisions/
```

## Experiment Naming Convention

Use this format:

```text
exp-001-short-description
exp-002-short-description
exp-003-short-description
```

Each experiment should have its own `README.md` containing:

* Experiment name
* Date
* Class topic
* Objective
* Technologies used
* Setup instructions
* What was built
* Test results
* Problems encountered
* Lessons learned
* Reusable outputs
* Cleanup status

## Knowledge Preservation Rules

Before deleting an experiment, preserve anything useful in one or more of these locations:

```text
knowledge/lessons-learned/
knowledge/reusable-patterns/
knowledge/prompt-library/
knowledge/code-snippets/
knowledge/tool-notes/
archive/experiment-index.md
```

Do not preserve code only because it exists. Preserve it when it is:

* Reusable
* Educational
* Difficult to recreate
* Helpful to another project
* A good example of a successful pattern
* A useful example of a failure or mistake

## Cleanup Safety Rules

An AI agent must not delete an experiment immediately after receiving a general cleanup request.

Before deletion, the agent must:

1. Review the experiment.
2. Identify reusable knowledge and artifacts.
3. Create or update the lessons-learned document.
4. Update `archive/experiment-index.md`.
5. Show the proposed keep/delete list.
6. Confirm that credentials and sensitive files are not being preserved.
7. Delete only the approved temporary implementation.

Git history may still contain previously committed content. Sensitive information must never be committed, even if the plan is to delete it later.

## Security Rules

Never commit:

* `.env`
* API keys
* Access tokens
* Passwords
* Private keys
* Database credentials
* Personal information
* Production data
* Private customer information
* Authentication cookies
* Service-account files

Use `.env.example` to document required environment-variable names without including real values.

Example:

```env
OPENAI_API_KEY=
DATABASE_URL=
NEXT_PUBLIC_APP_URL=
```

## Git Workflow

Each experiment should normally use its own branch:

```text
experiment/exp-001-description
```

Commit messages should be clear:

```text
chore: initialize experiment 001
feat: add prototype workflow
test: add validation cases
docs: record experiment findings
chore: remove temporary implementation
```

Do not push broken or sensitive work merely to preserve progress. Check the staged files before every commit.

## Final Principle

Temporary code may be deleted.

Useful knowledge should survive.

---
