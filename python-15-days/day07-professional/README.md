# Day 07 — Professional Projects

## 🎯 Goal
Turn scripts into a **package other people can install, trust and change safely**: project layout, virtual envs, tests, logging, linting.

## 🧠 First Principles

**1. Code others can trust = tests + logs + structure.**
- **Tests** prove it works *now* and warn you the moment a change breaks it.
- **Logs** tell you what happened in production, where you can't use a debugger.
- **Structure** tells a newcomer where everything lives in 10 seconds.

**2. A test is an executable example.** `assert slugify("Hello World") == "hello-world"` is both documentation and a guard. Write tests for: normal cases, edge cases (empty, huge, unicode), and error cases.

**3. Pure functions are the easiest to test.** Same input → same output, no side effects. Push I/O (files, network, DB) to the edges; keep the logic pure in the middle.

**4. `print` is for users, `logging` is for operators.** Logging gives levels (`DEBUG < INFO < WARNING < ERROR`), timestamps and module names — and a library should *never* configure logging itself; the app does.

**5. Isolate dependencies.** A virtual environment (`python -m venv .venv`) gives each project its own packages, so project A's `pandas 1.x` never breaks project B's `pandas 2.x`.

## 🗂️ The standard layout
```
day07-professional/
├── pyproject.toml     ← one file: metadata, dependencies, tool config
├── src/textkit/       ← the importable package
│   ├── __init__.py    ← public API (what users import)
│   └── core.py
├── tests/             ← mirrors src/
│   └── test_core.py
└── main.py            ← an "app" using the package
```
The `src/` layout stops you accidentally importing local files instead of the installed package.

## 🌍 Real-World Scenario
A publishing platform needs: URL slugs for article titles (with accents: *Zürich*, *Café*), reading-time estimates, short summaries, and **PII masking** so emails/phones never leak into logs (a GDPR requirement).

## 💻 Code
```bash
pip install -e ".[dev]"     # editable install + dev tools
pytest -v                   # run tests
ruff check .                # lint
python main.py
```

![tests](screenshots/tests.png)
![output](screenshots/output.png)

> 💡 **VS Code:** open the *Testing* panel (flask icon) → it discovers pytest automatically, and you can click to run/debug single tests. Great screenshot material.

## 🏋️ Exercises
1. **TDD:** write a failing test for `truncate(text, n)` that adds `…` without cutting words. Then implement it.
2. Find a bug: does `mask_pii` mask `+41 79 123 45 67` inside a longer number? Write a test that proves it either way.
3. Add a GitHub Actions workflow `.github/workflows/test.yml` that runs pytest on every push.
4. Run `pytest --cov` (install `pytest-cov`) and get coverage to 100%.

## ✅ Takeaways
- If it isn't tested, assume it's broken.
- `pyproject.toml` + `src/` + `tests/` is the modern standard.
- Libraries log; applications configure logging.
