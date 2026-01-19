import re
from datetime import date

# ---- MONTH MAPPING ----
MONTHS = {
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

# ---- BASIC TIME INTENT PATTERNS ----
TIME_PATTERNS = {
    r"\btoday\b": "today",
    r"\byesterday\b": "yesterday",
    r"\bthis\s+week\b": "week",
    r"\blast\s+week\b": "last_week",
    r"\bthis\s+month\b": "month",
    r"\blast\s+month\b": "last_month"
}

# ---- EDUCATION DOMAIN PATTERNS ----
EDUCATION_PATTERNS = [
    r"\bmark(s)?\b",
    r"\bscore(s|d)?\b",
    r"\battendance\b",
    r"\battend(ed|ance|ing)?\b",
    r"\bpresent\b",
    r"\babsent\b",
    r"\bresult(s)?\b",
    r"\bsubject(s)?\b",
    r"\bexam(s)?\b",
    r"\btest(s)?\b",
    r"\bgrade(s|d)?\b"
]

# ---- TIME PARSER ----
def detect_time_intent(message: str):
    msg = message.lower()

    # 1. Check month + year like "March 2023"
    month_match = None
    for name, num in MONTHS.items():
        if re.search(rf"\b{name}\b", msg):
            month_match = num
            break

    year_match = re.search(r"\b(19|20)\d{2}\b", msg)

    if month_match and year_match:
        return {
            "type": "month_year",
            "month": month_match,
            "year": int(year_match.group())
        }

    # 2. Fallback to simple patterns
    for pattern, value in TIME_PATTERNS.items():
        if re.search(pattern, msg):
            return {
                "type": value
            }

    return None


def is_education_query(message: str):
    msg = message.lower()
    return any(
        re.search(pattern, msg)
        for pattern in EDUCATION_PATTERNS
    )


# ---- SCHOOL DOMAIN GUARDRAIL ----
def school_domain_guard(message: str):
    if not is_education_query(message):
        return (
            False,
            "I can help only with school-related topics such as academics, "
            "attendance, exams, and results.\n"
            "For other matters, please contact the school office at +9876543210."
        )
    return True, None
