# Day 04 — Files, Errors & Data Formats

## 🎯 Goal
Read and write real files (CSV, JSON) and handle bad data **without crashing and without silently accepting garbage**.

## 🧠 First Principles

**1. Everything outside your program can fail.** Files go missing, users type nonsense, disks fill up. Your code's job is to decide, for each failure: *recover, skip and report, or stop*.

**2. Exceptions are a second return channel.** A function either returns a valid result **or** raises. That keeps the "happy path" clean:
```python
try:
    inv = clean_row(row)      # happy path reads like a sentence
except ValidationError as err:
    rejected.append(reason)   # the failure path, handled in ONE place
```
- Catch **specific** exceptions (`ValueError`), never bare `except:` — it hides real bugs.
- Define your own (`class ValidationError(ValueError)`) so callers can tell *your* errors from Python's.
- `raise ... from None` hides noisy internal tracebacks; `from err` keeps the cause.

**3. `with` guarantees cleanup.** `with open(...) as f:` closes the file even if an exception happens. Same pattern for DB connections, locks, network sessions.

**4. Formats are contracts.**
| Format | Good for | Watch out |
|---|---|---|
| CSV | tables, Excel exchange | everything is a string; quoted commas |
| JSON | nested data, APIs | no dates/decimals — convert to strings |
| `pathlib.Path` | building paths | works on Windows *and* Linux |

**5. Validate at the boundary.** Clean data once, when it enters. Everything inside your system can then trust it.

## 🌍 Real-World Scenario
Finance exports invoices from three systems into one CSV. Dates come in 4 formats, amounts have `€`, `$`, commas and spaces, one row is duplicated, some are invalid. Build the cleaner that:
- outputs `invoices_clean.csv` (normalised),
- outputs `rejected.csv` with **line number + reason** (so a human can fix them),
- outputs `summary.json` with totals per currency.

## 💻 Code
```bash
python main.py
```

![code](screenshots/code.png)
![output](screenshots/output.png)

> ⚠️ **Real-world trap:** `01/08/2026` is 1 August in Europe and 8 January in the US. The parser here assumes European order. In production, agree the format with the data source — no code can guess it reliably.

## 🏋️ Exercises
1. `INV-010` also has an invalid email but only one reason is reported. Collect **all** reasons per row.
2. Add a `--input` argument using `argparse`.
3. Convert all totals to CHF using a rates dict loaded from `rates.json`.
4. What happens if `invoices_raw.csv` doesn't exist? Handle it with a clear message and exit code 1.

## ✅ Takeaways
- Functions should return valid data or raise — never return "maybe-broken" data.
- Catch narrow, report clearly, keep going when it's safe.
- `with` + `pathlib` + `csv`/`json` modules = 90% of everyday file work.
