import re
from datetime import datetime

CURRENT_YEAR = datetime.now().year

MONTH_MAP = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12
}

def extract_month_year(msg: str):
    msg = msg.lower().strip()

    # ---------------- YEAR ----------------
    year_match = re.search(r"\b(19\d{2}|20\d{2})\b", msg)
    year = int(year_match.group()) if year_match else None

    if year and year > CURRENT_YEAR:
        return None, "INVALID_YEAR"

    # ---------------- MONTH NAME / ABBR ----------------
    for name, number in MONTH_MAP.items():
        if re.search(rf"\b{name}\b", msg):
            return number, year

    # ---------------- MONTH NUMBER (1–12 ONLY) ----------------
    month_match = re.search(r"\b(1[0-2]|[1-9])\b", msg)
    if month_match:
        return int(month_match.group()), year

    # ---------------- NO MONTH FOUND ----------------
    # Important: DO NOT mark invalid yet
    return None, year
