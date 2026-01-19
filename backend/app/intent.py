import re

# ---- TIME INTENT PATTERNS ----
TIME_PATTERNS = {
    r"\btoday\b": "today",
    r"\byesterday\b": "yesterday",
    r"\bthis\s+week\b": "week",
    r"\blast\s+week\b": "last_week",
    r"\bthis\s+month\b": "month",
    r"\blast\s+month\b": "last_month",
    
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

def detect_time_intent(message:str):
    msg=message.lower()
    for pattern,value in TIME_PATTERNS.items():
        if re.search(pattern,msg):
            return value
    return None

def is_education_query(message:str):
    msg=message.lower()
    return any(
        re.search(pattern, msg) for pattern in EDUCATION_PATTERNS
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

