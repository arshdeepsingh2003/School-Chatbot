import re

ADVISOR_PATTERNS = [
    r"\bperformance\b",
    r"\bprogress\b",
    r"\bimprove\b",
    r"\bimprovement\b",
    r"\bdoing\b",
    r"\bhow am i\b",
    r"\bweak\b",
    r"\bstrong\b",
    r"\banalyze\b",
    r"\badvice\b",
    r"\bfeedback\b",
    r"\bstudy\b",
    r"\bhelp me\b"
]

def is_advisor_query(message: str):
    msg = message.lower()
    return any(re.search(p, msg) for p in ADVISOR_PATTERNS)
