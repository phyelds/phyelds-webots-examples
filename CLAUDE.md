# CLAUDE.md

Examples of [phyelds](https://github.com/phyelds/phyelds) on a swarm of Elisa-3 robots
in Webots R2025a. Every robot runs the same aggregate program through
`phyelds.webots.AggregateController`.

- `src/phyelds_webots_examples/`: the aggregate programs, one module per example
  (`gradient`, `channel`, `flocking`, `formation`), and what the robots need to run them
  (`lights`: the colours of the LED and the light sensors). `phyelds.webots.Body` drives
  the LED and the wheels.
- `controllers/phyelds_swarm/`: the one controller of every robot; its argument names the
  program.
- `protos/SwarmElisa.proto`: an Elisa-3 with a radio of limited range, a GPS, an inertial
  unit and two light sensors looking up.
- `worlds/`: one world per example.
- `tests/`: they mirror `src/`. `tests/test_worlds.py` runs the worlds in Webots, and is
  skipped when `webots` is not on the PATH.

Dependencies:

- The programs depend on `phyelds-webots` from PyPI, and `phyelds-simulator` is a
  development dependency for the fast tests.
- `phyelds.experimental` (flocking, formation) is a study in progress whose API may change
  in any release: pin and update it deliberately.

## Commands

```bash
poetry env use 3.13                # Python 3.12–3.13: the system one may be newer
poetry install                     # set up the environment
poetry run webots worlds/gradient.wbt   # open an example: Webots runs the controllers on the venv's python3
poetry run pytest -m "not webots"  # the fast tests, as the pre-commit hook
poetry run pytest -m webots        # the worlds, in Webots (batch mode, no rendering)
poetry run pytest tests/test_lights.py::test_name   # a single test
poetry run pylint src controllers  # lint, as in CI
poetry run flake8                  # style, max line length 120, as in CI
```

A change is done only when `pytest` (with the worlds, if Webots is installed), `pylint`
and `flake8` all pass: CI runs exactly these, the worlds in the Webots container. When a
change touches what a reader sees (an example, how to run it), also update the README.

## Workflow: test-driven development

Every feature and every bug fix follows red → green → refactor. Do not write
production code that no failing test asks for.

1. **Understand.** Restate the requested behaviour as a short list of observable
   cases (normal case, edge cases, error cases). If a requirement is ambiguous,
   ask before writing code.
2. **Red.** Write *one* test for the next case and run it. It must fail, and fail
   for the expected reason (an assertion or a missing name, not a typo or an
   import error elsewhere). Do not write the implementation in the same step.
3. **Green.** Write the minimum code that makes that test pass. Run the whole
   suite, not only the new test.
4. **Refactor.** With the suite green, remove duplication and improve names and
   structure, in both production and test code. Run the suite after each change.
5. **Commit** (see below), then repeat from step 2 for the next case.

Rules:

- Never change or delete an existing test just to make it pass. If a test is
  wrong, say so, explain why, and fix it in its own commit.
- Never skip, `xfail` or weaken an assertion to get to green.
- For a bug, first write a test that reproduces it; the fix comes after.
- Test behaviour through the public API, not implementation details, so the
  refactor step stays free.
- Tests mirror the source tree: `src/phyelds_webots_examples/gradient.py` →
  `tests/test_gradient.py`. A program is tested twice: on `phyelds-simulator` (fast)
  and in its world (`tests/test_worlds.py`, marked `webots`). Reuse the helpers already
  there instead of building new fixtures.
- In a world, assert robust properties (who lights up, how many end inside a shape),
  never exact positions: the physics and the timing of the controllers are not exact.
- Name tests after the behaviour: `test_<unit>_<does_what>_<when>`, and lay them
  out as Arrange / Act / Assert.
- Keep tests fast and deterministic: fix random seeds, keep simulations small.

## Commits

Commit small and often: one logical change per commit, each one leaving the
suite green. A typical feature is a series of commits, e.g. a failing test plus
its implementation, then a refactor.

- Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):
  `<type>(<optional scope>): <description>`, with the types `feat`, `fix`, `test`,
  `refactor`, `docs`, `style`, `perf`, `build`, `ci`, `chore`. Nothing is released
  from this repository, but the history reads as the one of phyelds.
- Subject: imperative mood, lowercase, no trailing period, ≤ 72 characters.
- Body (when useful): wrap at 72 columns, explain *why* and what the previous
  behaviour was, not a line-by-line list of the diff. Follow the style of the
  existing history (`git log`).
- Stage files explicitly (`git add <path>`), never `git add -A` / `git add .`.
- Never use `--no-verify`; if a pre-commit hook fails, fix the cause.
- Never amend or rewrite commits that are already pushed, and do not push
  unless asked.
- **No AI attribution.** Do not add `Co-Authored-By: Claude …`, "Generated
  with Claude Code", emoji or any other reference to AI tools in commit
  messages, PR titles or PR descriptions. Commits are authored by the git user
  only.

## Python style

Follow [PEP 8](https://peps.python.org/pep-0008/),
[PEP 257](https://peps.python.org/pep-0257/) and the
[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html);
pylint and flake8 enforce the mechanical part. Match the surrounding code first.

### Design and modularity

- One module, one responsibility. An aggregate program says *what* the swarm does and
  knows nothing of Webots; the controller turns sensors into the program's inputs and its
  outputs into motors and lights. Keep that direction: `phyelds_webots_examples` never
  imports `controller`.
- Small, focused functions; a function longer than ~40 lines or with deep
  nesting is a signal to split it. Prefer early returns over nested `if`s.
- Prefer composition and plain functions over class hierarchies; use
  `dataclass` for data carriers.
- Keep side effects at the edges and pure logic in the middle, so it is easy
  to test.
- No mutable module-level state; if it is unavoidable, make it private
  (`_name`) and expose it through functions.
- Do not duplicate: look for an existing helper, here or in phyelds, before writing a
  new one.
- Do not add a dependency without asking.

### Code

- Type-annotate every public function, method and attribute. Use modern
  syntax: `list[int]`, `X | None`, `collections.abc` abstract types for
  parameters (`Sequence`, `Mapping`, `Callable`).
- Naming: `lower_with_under` for modules, functions and variables, `CapWords`
  for classes, `CAPS_WITH_UNDER` for constants, a leading `_` for internals.
  Descriptive names, no type in the name, no single letters outside short
  loops or maths. Do not shadow builtins (`max`, `min`, `id`, `list`, …).
- Physical quantities in SI units (metres, seconds, radians), and say so in the name or
  the docstring.
- Imports: absolute (`from phyelds.calculus import aggregate`), grouped as
  standard library / third party / local, no wildcard imports.
- Never use mutable default arguments; default to `None` and build the value
  inside.
- Exceptions: raise specific built-in ones (`ValueError`, `TypeError`) or a
  custom one ending in `Error`; no bare `except:`, no broad `except Exception`
  unless re-raising; keep `try` blocks small. Do not use `assert` for runtime
  checks in library code (it is fine in tests).
- Comprehensions only when they stay simple; otherwise use a loop.
- Use f-strings, `pathlib`, context managers (`with`) for resources, and
  `logging` instead of `print` in library code (the controller prints what the tests read).
- Executable scripts put their logic in `main()` behind
  `if __name__ == "__main__":`.

### Docstrings and comments

- Every public module, class and function has a docstring in Google style: a
  one-line summary ending with a period, then `Args:`, `Returns:` (or
  `Yields:`) and `Raises:` when relevant. Describe behaviour and contract, not
  implementation.
- Comments explain *why*, not *what*. Do not leave commented-out code, TODOs
  without context, or comments describing the change you just made.
- Update the README or docstrings when what an example shows changes.
