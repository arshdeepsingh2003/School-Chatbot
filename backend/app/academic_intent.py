import re

RAW_MARKS_PATTERNS = [
    r"\bmy\s+marks\b",
    r"\bmarks\b",
    r"\bshow\s+my\s+marks\b",
    r"\bwhat\s+are\s+my\s+marks\b",
    r"\btell\s+me\s+my\s+marks\b",
    r"\bcan\s+i\s+see\s+my\s+marks\b",
    r"\bmarks\s+pls\b",
    r"\bmarks\s+please\b",
    r"\bwhat\s+r\s+my\s+marks\b",
    r"\bmarks\s+batao\b",
    r"\bmere\s+marks\b",
    r"\bmarks\s+kya\s+hai\b"
]

def is_raw_marks_query(message: str) -> bool:
    msg = message.lower()
    return any(re.search(p, msg) for p in RAW_MARKS_PATTERNS)
