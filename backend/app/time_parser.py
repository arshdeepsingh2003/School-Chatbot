import re
from datetime import datetime

VALID_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12
}

CURRENT_YEAR = datetime.now().year

def extract_month_year(msg: str):
    msg = msg.lower()

    # --- YEAR ---
    year_match = re.search(r"\b(19\d{2}|20\d{2})\b", msg)
    year = int(year_match.group()) if year_match else None

    if year and year > CURRENT_YEAR:
        return "INVALID_MONTH", "INVALID_YEAR"

    # --- MONTH NAME ---
    for name, number in VALID_MONTHS.items():
        if name in msg:
            return number, year

    # --- MONTH NUMBER (1–12 only) ---
    month_match = re.search(r"\b(1[0-2]|[1-9])\b", msg)
    if month_match:
        return int(month_match.group()), year

    # --- INVALID MONTH WORD (e.g., Mars, 32nd) ---
    if "attendance" in msg:
        return "INVALID_MONTH", year

    return None, year
