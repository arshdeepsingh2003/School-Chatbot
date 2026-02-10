import re

RAW_MARKS_PATTERNS = [
    r"\bmarks?\b",
    r"\bscore(s)?\b",
    r"\bgrade(s)?\b",
    r"\bresult(s)?\b",
    r"\bexam\s+(result|score)(s)?\b",
    r"\btest\s+(result|score)(s)?\b",
    r"\bacademic\s+record(s)?\b",
    r"\bmere\s+marks\b",
    r"\bmarks\s+batao\b",
    r"\bmarks\s+kya\s+hai\b"
]

def is_raw_marks_query(message: str) -> bool:
    msg = message.lower().strip()
    return any(re.search(p, msg) for p in RAW_MARKS_PATTERNS)
