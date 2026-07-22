"""Check that the repository contains the directories README.md promises.

The repository README declares a structure and splits it into a disposable zone
(experiments/) and permanent zones (knowledge/, docs/, templates/, archive/).
This module turns that prose contract into a checkable list.

Pure: it reads the filesystem and returns results. It never prints and never
exits — that is the caller's job.
"""

from pathlib import Path

# Paths the README contract promises. Trailing slash means directory.
REQUIRED = [
    "README.md",
    "AGENTS.md",
    ".gitignore",
    ".env.example",
    "experiments/",
    "knowledge/lessons-learned/",
    "knowledge/reusable-patterns/",
    "knowledge/prompt-library/",
    "knowledge/code-snippets/",
    "knowledge/tool-notes/",
    "templates/experiment-readme-template.md",
    "templates/lessons-learned-template.md",
    "templates/cleanup-checklist.md",
    "archive/experiment-index.md",
    "docs/class-notes/",
    "docs/decisions/",
]


def check(root):
    """Return [(path, present)] for every required path, in declared order.

    A path ending in "/" must be a directory; anything else must be a file.
    """
    root = Path(root)
    results = []
    for entry in REQUIRED:
        target = root / entry.rstrip("/")
        present = target.is_dir() if entry.endswith("/") else target.is_file()
        results.append((entry, present))
    return results


def missing(root):
    """Return only the paths that are absent."""
    return [path for path, present in check(root) if not present]
