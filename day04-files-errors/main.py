"""Day 04 — Messy invoice CSV cleaner: files, formats and failing gracefully."""
import csv
import json
import re
from dataclasses import asdict, dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

HERE = Path(__file__).parent
DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d.%m.%Y", "%b %d %Y"]
ALLOWED_CURRENCIES = {"CHF", "EUR", "USD"}
EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")


class ValidationError(ValueError):
    """Raised when a row can't be trusted. Carries a human-readable reason."""


@dataclass
class Invoice:
    invoice_id: str
    customer: str
    date: date
    amount: Decimal
    currency: str
    email: str


# ── Small, single-purpose parsers. Each one either returns clean data or raises. ──
def parse_date(raw: str) -> date:
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw.strip(), fmt).date()
        except ValueError:
            continue                    # try the next format
    raise ValidationError(f"unrecognised date {raw!r}")


def parse_amount(raw: str) -> Decimal:
    cleaned = re.sub(r"[^\d.\-]", "", raw)     # strip €, $, commas, spaces
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        raise ValidationError(f"amount is not a number: {raw!r}") from None
    if value <= 0:
        raise ValidationError(f"amount must be positive: {value}")
    return value


def clean_row(row: dict) -> Invoice:
    customer = row["customer"].strip()
    if not customer:
        raise ValidationError("missing customer")
    currency = row["currency"].strip().upper()
    if currency not in ALLOWED_CURRENCIES:
        raise ValidationError(f"unsupported currency {currency}")
    email = row["email"].strip().lower()
    if not EMAIL_RE.match(email):
        raise ValidationError(f"invalid email {email!r}")
    return Invoice(
        invoice_id=row["invoice_id"].strip(),
        customer=customer,
        date=parse_date(row["date"]),
        amount=parse_amount(row["amount"]),
        currency=currency,
        email=email,
    )


def process(src: Path, out_dir: Path) -> dict:
    clean, rejected, seen = [], [], set()

    with src.open(newline="", encoding="utf-8") as f:          # always close files
        for line_no, row in enumerate(csv.DictReader(f), start=2):
            try:
                inv = clean_row(row)
                if inv.invoice_id in seen:
                    raise ValidationError("duplicate invoice_id")
                seen.add(inv.invoice_id)
                clean.append(inv)
            except ValidationError as err:
                rejected.append({"line": line_no, **row, "reason": str(err)})

    out_dir.mkdir(exist_ok=True)
    with (out_dir / "invoices_clean.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(Invoice.__dataclass_fields__))
        writer.writeheader()
        writer.writerows(asdict(i) for i in clean)

    with (out_dir / "rejected.csv").open("w", newline="", encoding="utf-8") as f:
        if rejected:
            writer = csv.DictWriter(f, fieldnames=list(rejected[0]))
            writer.writeheader()
            writer.writerows(rejected)

    totals: dict[str, Decimal] = {}
    for inv in clean:
        totals[inv.currency] = totals.get(inv.currency, Decimal(0)) + inv.amount
    summary = {
        "clean_rows": len(clean),
        "rejected_rows": len(rejected),
        "totals_by_currency": {k: str(v) for k, v in sorted(totals.items())},
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    return {"summary": summary, "rejected": rejected}


if __name__ == "__main__":
    result = process(HERE / "invoices_raw.csv", HERE / "output")
    print(json.dumps(result["summary"], indent=2))
    print("\nRejected rows:")
    for r in result["rejected"]:
        print(f"  line {r['line']:>2} {r['invoice_id']:<8} → {r['reason']}")
    print("\nFiles written to ./output/")
