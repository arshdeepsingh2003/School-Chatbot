import re

# ----------------------------------------
# ATTENDANCE INTENT DETECTION
# ----------------------------------------

ATTENDANCE_PATTERNS = [
    # General attendance
    r"\battendance\b",
    r"\bmy\s+attendance\b",

    # Present / absent queries
    r"\babsent\b",
    r"\bpresent\b",
    r"\bwas\s+i\s+present\b",
    r"\bwas\s+i\s+absent\b",

    # Count-based queries
    r"\bhow\s+many\s+days\s+absent\b",
    r"\bhow\s+many\s+days\s+present\b",
    r"\bdays\s+absent\b",
    r"\bdays\s+present\b",

    # Percentage
    r"\battendance\s+percentage\b",
    r"\bpercentage\b",

    # Time-based
    r"\bthis\s+month\b",
    r"\blast\s+month\b",
    r"\bthis\s+year\b",
    r"\blast\s+year\b",

    # Month + year (October 2025, Dec 2024, etc.)
    r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\b\s+\d{4}",

    # Date-specific (2025-10-08)
    r"\b\d{4}-\d{2}-\d{2}\b"
]


def is_attendance_query(msg: str) -> bool:
    """
    Detects if a message is related to attendance.
    Covers:
    - summaries
    - month/year queries
    - date-specific queries
    - present/absent counts
    - percentage
    """
    msg = msg.lower().strip()
    return any(re.search(pattern, msg) for pattern in ATTENDANCE_PATTERNS)
