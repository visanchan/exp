# experiments/

**Disposable zone.** Everything in this directory is temporary and may be
deleted once its knowledge has been extracted. Nothing here is precious.

## One folder per experiment

Naming format — three-digit zero-padded number, lowercase kebab-case:

```text
exp-001-short-description
exp-002-short-description
```

Recommended internal layout:

```text
exp-001-short-description/
├── README.md      # copy of ../templates/experiment-readme-template.md
├── src/           # implementation
├── tests/         # test cases
├── notes/         # working notes, scratch thinking
└── artifacts/     # screenshots, outputs, sample data (redacted)
```

Create only the subfolders the experiment actually needs.

## Starting an experiment

1. `mkdir experiments/exp-NNN-short-description`
2. Copy [`../templates/experiment-readme-template.md`](../templates/experiment-readme-template.md)
   in as `README.md`.
3. Fill in Objective, Hypothesis, and Success criteria **before** writing code.
4. Add a row to [`../archive/experiment-index.md`](../archive/experiment-index.md)
   with status `Active`.

## Rules

- Keep dependencies and config isolated inside the experiment folder.
- Never place credentials in source. Variable **names** go in
  [`../.env.example`](../.env.example); values go in a git-ignored `.env`.
- Do not modify another experiment's files.
- Before deleting: extract knowledge into `../knowledge/`, complete
  [`../templates/cleanup-checklist.md`](../templates/cleanup-checklist.md), and
  get the keep/delete proposal approved.
