"""Run the structure check against this repository and report pass/fail.

Usage:
    python experiments/exp-001-scaffold-check/tests/test_structure.py

Exits 0 if every contract path is present, 1 otherwise.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import check_structure  # noqa: E402

# tests/ -> exp-001-scaffold-check/ -> experiments/ -> repo root
REPO_ROOT = Path(__file__).resolve().parents[3]


def case_1_all_present():
    """Every contract path exists at the repository root."""
    results = check_structure.check(REPO_ROOT)
    for path, present in results:
        print(f"  {'OK     ' if present else 'MISSING'}  {path}")
    absent = [p for p, ok in results if not ok]
    return not absent, f"{len(results) - len(absent)}/{len(results)} present"


def case_2_missing_detected():
    """A non-existent root reports every path as missing (the check can fail)."""
    absent = check_structure.missing(REPO_ROOT / "no-such-directory")
    expected = len(check_structure.REQUIRED)
    return len(absent) == expected, f"{len(absent)}/{expected} reported missing"


def case_3_experiments_populated():
    """experiments/ contains at least one exp-NNN folder."""
    found = sorted(p.name for p in (REPO_ROOT / "experiments").glob("exp-*") if p.is_dir())
    return bool(found), f"found: {', '.join(found) or 'none'}"


CASES = [
    ("1  all contract paths present", case_1_all_present),
    ("2  missing path detected", case_2_missing_detected),
    ("3  experiments/ populated", case_3_experiments_populated),
]


def main():
    print(f"repo root: {REPO_ROOT}\n")
    failures = 0
    for name, fn in CASES:
        print(f"case {name}")
        passed, detail = fn()
        print(f"  -> {'PASS' if passed else 'FAIL'}  ({detail})\n")
        if not passed:
            failures += 1
    print(f"{len(CASES) - failures}/{len(CASES)} cases passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
