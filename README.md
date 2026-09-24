# 🐍 Python in 15 Days — From First Principles to AI in Production

> Six months of Python compressed into 15 focused days.
> Every day answers three questions: **Why does this exist? How does it actually work? Where is it used in the real world?**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Days](https://img.shields.io/badge/Progress-0%2F15-orange)
![License](https://img.shields.io/badge/license-MIT-green)
<!-- After your first push, replace <your-username> to get a live CI badge: -->
<!-- ![tests](https://github.com/<your-username>/python-15-days/actions/workflows/tests.yml/badge.svg) -->

> Update the progress badge as you go: change `0%2F15` to `3%2F15`, and so on.

---

## 🧭 The Method

Most tutorials teach *syntax*. This repo teaches *models* — the small set of ideas everything else is built on.

| Principle | What it means here |
|---|---|
| **First principles** | Every topic starts with the one idea that explains the rest (e.g. *"names are labels on objects"* explains copying, mutability and default-argument bugs). |
| **Build it, then use the library** | Write gradient descent by hand *before* calling scikit-learn. Build retrieval by hand *before* using an AI framework. |
| **Real scenarios only** | No `foo`/`bar`. Every day ships a small tool a company would actually use. |
| **Short & dense** | Each lesson is readable in 10 minutes. The rest of the day is code. |

---

## 🗺️ Roadmap

| Day | Topic | First principle | Real-world project |
|---|---|---|---|
| 01 | [How Python Thinks](day01-how-python-thinks) | Names are labels; objects have identity, type, value | Trip expense splitter |
| 02 | [Functions & Control Flow](day02-functions) | Functions are objects you can pass around | Password policy engine + retry helper |
| 03 | [Data Structures](day03-data-structures) | Pick the structure by the question you'll ask of it | Server log analyzer |
| 04 | [Files, Errors & Data Formats](day04-files-errors) | Everything outside your program can fail — plan for it | Messy invoice CSV cleaner |
| 05 | [Object-Oriented Design](day05-oop) | A class bundles data with the rules that protect it | Shopping cart with pricing rules |
| 06 | [Pythonic Power Tools](day06-pythonic) | Laziness: compute only what you need, when you need it | Streaming log pipeline + decorators |
| 07 | [Professional Projects](day07-professional) | Code others can trust = tests + logs + structure | Tested text-utility library |
| 08 | [Concurrency](day08-concurrency) | Waiting ≠ working: I/O-bound vs CPU-bound | Website uptime checker |
| 09 | [HTTP & APIs](day09-apis) | The web is just text requests and text responses | GitHub profile analyzer |
| 10 | [Web Backends](day10-web-backend) | An API is a function exposed over the network | URL shortener (FastAPI + SQLite) |
| 11 | [Data Analysis](day11-data-analysis) | Vectorize: operate on whole columns, not rows | E-commerce sales report |
| 12 | [ML From Scratch](day12-ml-from-scratch) | Learning = minimizing error by following the slope | House price predictor |
| 13 | [Real ML Workflow](day13-ml-workflow) | A model is only as good as how you evaluate it | Customer churn predictor |
| 14 | [AI: Neural Nets & LLM Apps](day14-ai) | Neurons are tiny linear models + a bend; RAG = search + prompt | NN from scratch + mini RAG chatbot |
| 15 | [Capstone: Ship It](day15-capstone) | Software isn't done until someone else can run it | Churn prediction API in Docker |

---

## ⏱️ Daily Routine (~4–6 h)

1. **Read** the day's `README.md` (15 min) — focus on the *First Principles* section.
2. **Run** the code, then **break it** on purpose — change things and predict the output first.
3. **Do the exercises** without looking anything up for 20 minutes. Then search.
4. **Screenshot** your best output (see below) and add it to the day's `screenshots/` folder.
5. **Log** what you learned in [PROGRESS.md](PROGRESS.md) and **commit**.

---

## 🚀 Setup

**First time: publish this folder to your GitHub**
1. On github.com → **New repository** → name it `python-15-days` → leave it empty (no README).
2. In VS Code, open this folder → Terminal:
```bash
git init
git add .
git commit -m "day00: course structure"
git branch -M main
git remote add origin https://github.com/<your-username>/python-15-days.git
git push -u origin main
```

**Environment**
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Days 1–8 need **only the standard library** (Day 7 adds `pytest`). Extra packages start on Day 9.
Every script was run and every test passes (Python 3.11+). The ✅ badge from GitHub Actions confirms it on each push.

---

## 📸 Screenshots from VS Code

1. Install the VS Code extension **CodeSnap** (by adpyke).
2. Select code → `Ctrl/Cmd + Shift + P` → **CodeSnap** → save as `dayXX/screenshots/code.png`.
3. For terminal output, use your OS screenshot tool → `dayXX/screenshots/output.png`.
4. Each day's README already contains the image links. They'll appear as soon as the files exist (every day has an empty `screenshots/` folder ready).
5. Days 11, 12 and 14 also generate charts in `output/`. Those are linked too and look great on GitHub.

Best screenshots per day: the code of the core idea (e.g. the gradient-descent loop on Day 12) + the terminal output proving it works. For Days 7, 10 and 15, also capture the VS Code **Testing** panel with green ticks and the FastAPI `/docs` page.

---

## 🧾 Commit Convention

```bash
git add day03-data-structures
git commit -m "day03: log analyzer with Counter + defaultdict"
git push
```
One commit per milestone shows steady progress on your GitHub graph.

---

## ⚠️ Honest note

15 days gives you a **strong, correct foundation** across the whole Python landscape. Mastery comes from what you build *after*. Day 15 ends with a list of next projects for exactly that.
