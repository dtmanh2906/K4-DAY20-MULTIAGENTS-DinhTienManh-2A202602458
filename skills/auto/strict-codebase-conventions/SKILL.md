---
name: strict-codebase-conventions
description: "WHEN TO USE THIS SKILL: When modifying or refactoring existing packages, writing tests, adding bug fixes, and updating documentation or changelogs."
---
- Never modify existing files in test suites (e.g., `tests/`) unless explicitly permitted; always add new test files (e.g., `tests/test_regressions.py`).
- Add comprehensive regression tests for every bug fixed (at least one test function per bug).
- Ensure every public function (names not starting with `_`) has complete type annotations for all parameters and return values.
- Record all bug fixes in the changelog (e.g., `CHANGELOG.md`) under the required heading (e.g., `## Unreleased`) using the specified bullet format.
- Handle edge cases in numerical parsing and formatting robustly (e.g., currency symbols, parentheses for negative numbers, half-up rounding in decimal arithmetic).
