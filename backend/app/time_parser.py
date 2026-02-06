import re
from calendar import month_name
from datetime import date

# Valid month names only (January–December)
MONTH_MAP = {
    m.lower(): i for i, m in enumerate(month_name) if m
}

def extract_month_year(msg: str):
    msg = msg.lower()

    month = None
    year = None

    # 1️⃣ Extract month by name (only real months)
    for name, number in MONTH_MAP.items():
        if re.search(rf"\b{name}\b", msg):
            month = number
            break

    # 2️⃣ Extract numeric month (1–12 only)
    if month is None:
        m = re.search(r"\b(1[0-2]|[1-9])\b", msg)
        if m:
            month = int(m.group())

    # 3️⃣ Extract year (2000 → current year only)
    y = re.search(r"\b(20\d{2})\b", msg)
    if y:
        year = int(y.group())
        if year < 2000 or year > date.today().year:
            return "INVALID_YEAR", None

    # 4️⃣ Validate month range
    if month is not None and not (1 <= month <= 12):
        return "INVALID_MONTH", None

    # STRICT: no defaults
    return month, year
