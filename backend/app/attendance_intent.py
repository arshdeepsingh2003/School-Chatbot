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

    # Month + year (FULL + SHORT)
    r"\b("
    r"jan|january|"
    r"feb|february|"
    r"mar|march|"
    r"apr|april|"
    r"may|"
    r"jun|june|"
    r"jul|july|"
    r"aug|august|"
    r"sep|sept|september|"
    r"oct|october|"
    r"nov|november|"
    r"dec|december"
    r")\b\s+\d{4}",

    # Month-year only follow-up (nov 2025)
    r"^(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\s+\d{4}$",

    # Date-specific (2025-10-08)
    r"\b\d{4}-\d{2}-\d{2}\b"
]


def is_attendance_query(msg: str) -> bool:
    msg = msg.lower().strip()
    return any(re.search(pattern, msg) for pattern in ATTENDANCE_PATTERNS)
