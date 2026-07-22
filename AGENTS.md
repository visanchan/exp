# AGENTS.md — Instructions for AI Agents

This file governs any AI agent (Claude Code, Copilot, Cursor, Codex, or similar)
operating in this repository. Read it before making any change.

This repository is a **temporary experimentation workspace**. Implementations are
disposable. Knowledge is permanent. Every rule below exists to protect the second
category while allowing the first to be freely created and destroyed.

---

## 1. Scope of Work

- Work **only inside this repository**. Do not read, write, move, or delete files
  outside the repository root.
- Do not modify the user's global configuration, shell profile, SSH keys, or any
  system-level settings.
- Do not install global packages. Keep installs local to an experiment folder.

## 2. Inspect Before Changing

- **Inspect existing files before changing them.** List the directory, read the
  file, and understand its current content before editing.
- Do not overwrite an existing file when an edit will do.
- Do not silently replace user-authored documentation. If a file already covers
  the topic, extend it and preserve the original wording where it is still true.
- If an intended change conflicts with existing content, stop and report the
  conflict instead of guessing.

## 3. Experiment Isolation

- **Every experiment lives in its own folder** under `experiments/`.
- **Naming format is mandatory:** `exp-001-short-description`
  - Three-digit zero-padded sequence number.
  - Lowercase kebab-case description.
  - Examples: `exp-001-rag-chunking`, `exp-002-langgraph-router`.
- Never mix two experiments in one folder.
- Never modify a different experiment's files while working on one.
- Recommended internal layout:

  ```text
  experiments/exp-001-short-description/
  ├── README.md      # from templates/experiment-readme-template.md
  ├── src/
  ├── tests/
  ├── notes/
  └── artifacts/
  ```

## 4. Security and Privacy

- **Never commit credentials or personal data.** This includes API keys, tokens,
  passwords, private keys, database URLs with embedded credentials, cookies,
  service-account files, customer data, and production data.
- Never write a real secret into any tracked file, including examples, tests,
  fixtures, comments, and documentation.
- Add required variable **names only** to `.env.example`. Values stay blank.
- Real values go in `.env`, which is git-ignored.
- If a secret is discovered in the working tree or in history, **stop immediately**
  and report it. Do not attempt history rewriting or force-pushing on your own.
- Redact secrets from logs, screenshots, and pasted terminal output before saving
  them as artifacts.

## 5. Dependencies

- **Avoid adding unnecessary dependencies.** Prefer the standard library and what
  is already installed.
- Before adding a package, state in the experiment README: what it does, why a
  built-in was insufficient, and its rough weight.
- Never add a dependency to a shared/root manifest to satisfy a single experiment.
- Never upgrade or remove a dependency another experiment relies on.

## 6. Assumptions and Decisions

- **Record important assumptions and decisions.**
  - Experiment-local decisions → that experiment's `README.md`.
  - Repository-wide or cross-cutting decisions → `docs/decisions/`, one short
    file per decision (context, decision, consequences).
- When a requirement is ambiguous, write down the assumption you proceeded under
  and flag it in your summary rather than silently choosing.

## 7. Testing

- **Test changes before claiming completion.** Run the code, run the tests, or
  otherwise exercise the change.
- Report results honestly. If tests fail, say so and include the output. If a
  step was skipped or could not be run, say that explicitly.
- Never describe untested work as "working", "verified", or "done".
- Record test cases and outcomes in the experiment README.

## 8. Knowledge Preservation

- **Preserve reusable knowledge before deleting temporary code.** Extraction
  comes first; deletion comes last.
- Destinations:

  | Content | Destination |
  |---|---|
  | What was learned, what failed, why | `knowledge/lessons-learned/` |
  | Patterns worth reusing | `knowledge/reusable-patterns/` |
  | Prompts that worked well | `knowledge/prompt-library/` |
  | Small self-contained code | `knowledge/code-snippets/` |
  | Notes on a tool/framework/API | `knowledge/tool-notes/` |
  | One-line historical record | `archive/experiment-index.md` |

- Preserve code only when it is reusable, educational, hard to recreate, useful
  to another project, a good example of a working pattern, or an instructive
  failure. Do not preserve code merely because it exists.

## 9. Deletion and Cleanup

- **Never delete the complete repository or the experiment history** without
  first reviewing what should be retained.
- Never run a broad destructive command (recursive delete of the repo root,
  `git clean -xfd` across the repo, history rewrite, branch force-delete) on your
  own initiative.
- **Produce a keep/delete proposal before any destructive cleanup**, listing:
  - Files and folders proposed for deletion.
  - Files and folders proposed to keep, and where knowledge was moved.
  - Confirmation that no credentials or sensitive data are being preserved.
  - Anything unreviewed or uncertain.
- Work through `templates/cleanup-checklist.md` and only delete after the human
  explicitly approves the proposal.
- Deleting an experiment folder is allowed **after** approval. Deleting
  `knowledge/`, `archive/`, `docs/`, `templates/`, or the git history is not.

## 10. Experiment Index

- **Update `archive/experiment-index.md` after** creating, completing, archiving,
  or removing an experiment.
- Keep one row per experiment. Never delete a row — an experiment's code may be
  removed, but its index entry is permanent history.
- Set `Original Code Removed` to `Yes` when the implementation is deleted, and
  make sure `Preserved Artifacts` points at real files.

## 11. Git and GitHub

- **Check staged files before every commit** (`git status`, `git diff --staged`).
  Confirm no `.env`, no secrets, no large binaries, no unrelated files.
- Commit and push **only when explicitly asked**.
- **Avoid pushing to GitHub unless the work is coherent and safe to share.** Do
  not push broken, half-finished, or sensitive work merely to save progress.
- Prefer a branch per experiment: `experiment/exp-001-short-description`.
- **Commit the define step on its own, before any source file exists.** That
  commit contains only the experiment `README.md` (objective, hypothesis, success
  criteria) and the `Active` index row. This is what makes "define before code"
  checkable rather than an honour-system rule — see
  `knowledge/reusable-patterns/define-before-code-commit.md`.
- Use clear commit messages:

  ```text
  chore: initialize experiment 001
  feat: add prototype workflow
  test: add validation cases
  docs: record experiment findings
  chore: remove temporary implementation
  ```

- Never force-push, never rewrite shared history, never skip hooks
  (`--no-verify`) unless explicitly instructed.

## 12. Do Not

- Do not create a sample or demo application unless explicitly requested.
- Do not scaffold frameworks "just in case".
- Do not reformat or restructure files unrelated to the task.
- Do not commit, push, or open a pull request without being asked.
- Do not claim completion without evidence.

## 13. Portable Class Skills

- Repo-local skills live under `.agents/skills/`, indexed in
  `.agents/skills/README.md`:
  - `ai-class-operating-partner/SKILL.md` — class experiments, prototypes,
    coding, business or data analysis, documents, UI work, and experiment
    preservation. The default for repository work.
  - `local-dev-servers/SKILL.md` — starting or troubleshooting long-running dev
    servers, backend plus frontend, or a localhost URL that will not open.
  - `systematic-debugging/SKILL.md` — finding the actual cause of a bug rather
    than guessing at fixes.
  - `reviewing-ai-written-code/SKILL.md` — reviewing generated code before
    keeping or committing it.
  - `session-handoff/SKILL.md` — carrying work across a context limit, a session
    end, or a change of agent.
  - `business-analysis/SKILL.md` — turning a business question into an analysis
    that changes a decision; unit economics, break-even, sensitivity.
  - `market-sizing/SKILL.md` — TAM, SAM and SOM estimated three ways and
    triangulated.
  - `write-a-repo-skill/SKILL.md` — adding or improving a skill here, including
    the provenance and privacy check.
- The skills complement this file; this file wins if instructions conflict.
- Do not assume a clone has the repository owner's user-level, system, plugin,
  or other project skills installed.
- Keep the portable skills free of credentials, personal paths, private business
  context, production configuration, and unlicensed third-party skill text.
- Record a new skill, or a change to a skill's repository-wide scope, in
  `docs/decisions/`.

---

**Final principle:** temporary code may be deleted; useful knowledge must survive.
