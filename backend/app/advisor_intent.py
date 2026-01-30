import re

# Strong, school-specific advisor intent patterns
ADVISOR_PATTERNS = [
    r"\bhow am i performing\b",
    r"\bhow is my performance\b",
    r"\bhow am i doing\b",
    r"\bhow is my progress\b",
    r"\banalyze my progress\b",
    r"\banalyze my performance\b",
    r"\bperformance analysis\b",
    r"\bprogress report\b",
    r"\bsuggest improvements\b",
    r"\bhow can i improve\b",
    r"\bstudy advice\b",
    r"\bstudy plan\b",
    r"\bweak subjects\b",
    r"\bstrong subjects\b",
    r"\bfeedback\b",
    r"\bguidance\b",
    r"\bparent advice\b",
    r"\bacademic advice\b"
]

def is_advisor_query(message: str) -> bool:
    """
    Returns True if the message is asking for
    performance analysis, improvement, or academic advice
    instead of raw marks or attendance.
    """
    msg = message.lower().strip()

    for pattern in ADVISOR_PATTERNS:
        if re.search(pattern, msg):
            return True

    return False
