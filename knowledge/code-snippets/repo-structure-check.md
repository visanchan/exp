# Snippet — Repository Structure Contract Check

**Source:** `exp-001-scaffold-check` (2026-07-22)
**Language:** Python 3.8+, standard library only

## What it does

Turns a documented directory structure into a checkable list. Declares the paths
a README promises, reports which are present, and exits non-zero if any are
missing. Useful in CI, or as a first check after cloning or after a cleanup that
deleted folders.

## The shape that matters

Two pieces, deliberately separated:

- A **pure function** that returns results — no printing, no `sys.exit`.
- A **thin runner** that formats output and owns the exit code.

The pure half survives reuse without edits. A single script that prints and exits
inline has to be rewritten the first time something wants to import it.

## Checker

```python
from pathlib import Path

# Trailing slash means directory; anything else must be a file.
REQUIRED = [
    "README.md",
    "AGENTS.md",
    ".gitignore",
    ".env.example",
    "experiments/",
    "knowledge/lessons-learned/",
    "templates/experiment-readme-template.md",
    "archive/experiment-index.md",
    "docs/decisions/",
]


def check(root):
    """Return [(path, present)] for every required path, in declared order."""
    root = Path(root)
    results = []
    for entry in REQUIRED:
        target = root / entry.rstrip("/")
        present = target.is_dir() if entry.endswith("/") else target.is_file()
        results.append((entry, present))
    return results


def missing(root):
    return [path for path, present in check(root) if not present]
```

## Runner

```python
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]  # adjust depth to your layout


def main():
    results = check(REPO_ROOT)
    for path, present in results:
        print(f"  {'OK     ' if present else 'MISSING'}  {path}")
    absent = [p for p, ok in results if not ok]
    print(f"{len(results) - len(absent)}/{len(results)} present")
    return 1 if absent else 0


if __name__ == "__main__":
    sys.exit(main())
```

## Prove it can fail

A structure check that always returns green is decoration. Always include the
negative case:

```python
def case_missing_detected():
    absent = missing(REPO_ROOT / "no-such-directory")
    assert len(absent) == len(REQUIRED), "checker cannot detect missing paths"
```

If this case does not fail against a bogus root, the passing case means nothing.

## Gotchas

- `parents[3]` is layout-specific. Count directory levels from the file to the
  repo root and adjust, or resolve the root with
  `git rev-parse --show-toplevel`.
- `is_dir()` follows symlinks. Use `Path.is_symlink()` first if that matters.
- Directory entries need the trailing slash, or a directory named `docs` will be
  checked with `is_file()` and reported missing.

## Related

- [[exp-001-scaffold-check]] — where this came from
- [[define-before-code-commit]]
