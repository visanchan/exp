# Cleanup Checklist

> Copy into the experiment folder (or the cleanup PR / task) and complete every
> item **before** deleting anything. Deletion is the last step, not the first.
>
> An AI agent must not delete an experiment on a general cleanup request. It must
> complete this checklist and present a keep/delete proposal for approval.

---

**Experiment:** `exp-NNN-short-description`
**Date:** YYYY-MM-DD
**Performed by:**

---

## 1. Documentation reviewed
- [ ] Experiment `README.md` is complete — no unfilled template placeholders.
- [ ] Results and Problems sections reflect what actually happened.
- [ ] Assumptions and decisions are written down.
- [ ] Repo-wide decisions recorded in `docs/decisions/`.

## 2. Reusable code extracted
- [ ] Reviewed all source for anything reusable, educational, or hard to recreate.
- [ ] Extracted code moved to `knowledge/code-snippets/` or `knowledge/reusable-patterns/`.
- [ ] Each extract is self-contained and has a one-line explanation of what it does.
- [ ] Confirmed nothing worth keeping remains only inside the experiment folder.

## 3. Prompts preserved
- [ ] Effective prompts moved to `knowledge/prompt-library/`.
- [ ] Each prompt records the model/tool used and why it worked.
- [ ] Prompts that failed instructively are recorded too.

## 4. Screenshots or artifacts preserved
- [ ] Useful outputs, screenshots, diagrams, and sample data identified.
- [ ] Kept artifacts moved out of the disposable folder to a permanent location.
- [ ] All artifacts redacted — no keys, tokens, emails, names, or real user data.
- [ ] Large or regenerable binaries dropped rather than committed.

## 5. Lessons-learned document completed
- [ ] Written from `templates/lessons-learned-template.md`.
- [ ] Saved to `knowledge/lessons-learned/exp-NNN-short-description.md`.
- [ ] Stands alone without the code — a reader who never sees the implementation
      still understands what was learned.
- [ ] "What failed" and "Root causes" are filled in honestly, not left blank.

## 6. Experiment index updated
- [ ] Row present in `archive/experiment-index.md`.
- [ ] Status, main lesson, and preserved artifacts are accurate.
- [ ] Artifact links point at files that actually exist.
- [ ] `Original Code Removed` will be set correctly after deletion.

## 7. Credentials checked
- [ ] No `.env` or secret file is tracked by git.
- [ ] No key, token, password, or connection string in source, tests, fixtures,
      comments, docs, or artifacts being kept.
- [ ] `git log -p` / history spot-checked for anything previously committed.
- [ ] Any credential that was exposed has been **rotated** (not just deleted).
- [ ] Required variable names documented in `.env.example` with blank values.

## 8. Sensitive data checked
- [ ] No personal information, customer data, or production data retained.
- [ ] No internal URLs, hostnames, or infrastructure details that should stay private.
- [ ] Test/sample data is synthetic or properly anonymized.
- [ ] Screenshots contain no private information.

## 9. Dependencies reviewed
- [ ] Packages installed for this experiment are not needed elsewhere.
- [ ] Nothing shared will break when this folder is removed.
- [ ] Any dependency worth remembering is noted in `knowledge/tool-notes/`.
- [ ] Local `node_modules/`, `venv/`, caches, and build output cleared.

## 10. Keep/delete proposal prepared
- [ ] Explicit **KEEP** list, with the destination of each item.
- [ ] Explicit **DELETE** list.
- [ ] Statement that no credentials or sensitive data are being preserved.
- [ ] Anything uncertain or unreviewed is flagged rather than silently deleted.

**KEEP**

| Item | Why | Destination |
|---|---|---|
| | | |

**DELETE**

| Item | Why safe to delete |
|---|---|
| | |

**Flagged / uncertain**

- 

## 11. Deletion approved
- [ ] Proposal reviewed by a human.
- [ ] Approval explicit — not assumed from a general "clean this up".
- [ ] Approved by: ____________________ on YYYY-MM-DD
- [ ] Deletion scope is the experiment folder only. `knowledge/`, `archive/`,
      `docs/`, `templates/`, and git history are **out of scope**.
- [ ] Deletion executed on YYYY-MM-DD.
- [ ] `archive/experiment-index.md` updated: status set, `Original Code Removed` = Yes.
