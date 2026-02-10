import re

ADVISOR_PATTERNS = [
    # overall performance
    r"\bhow am i doing\b",
    r"\bhow is he doing\b",
    r"\bhow is she doing\b",
    r"\bhow am i doing overall\b",
    r"\bhow is he doing overall\b",
    r"\boverall performance\b",

    # analysis
    r"\banalyze\b",
    r"\banalyze my\b",
    r"\banalyze his\b",
    r"\banalyze academic\b",
    r"\bacademic performance\b",
    r"\bperformance analysis\b",

    # feedback / improvement
    r"\bfeedback\b",
    r"\bgive me feedback\b",
    r"\bhow can i improve\b",
    r"\bimprove my studies\b",
    r"\bstudy advice\b",
    r"\bguidance\b",
    r"\bprogress\b",
]

def is_advisor_query(message: str) -> bool:
    msg = message.lower().strip()
    msg = msg.replace("analyse", "analyze")  # UK spelling fix

    return any(re.search(p, msg) for p in ADVISOR_PATTERNS)
