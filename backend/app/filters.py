import re

ABUSE_WORDS = [
    "abuse", "abusive", "harass", "harassment",
    "hate", "hateful", "racist", "sexist",
    "bully", "bullying",
    "idiot", "stupid", "moron", "dumb"
]

VIOLENCE_WORDS = [
    "kill", "killing", "murder", "attack", "fight",
    "weapon", "gun", "knife", "bomb",
    "terror", "terrorist",
    "suicide", "die", "death"
]

ILLEGAL_WORDS = [
    "hack", "hacking", "crack", "phish", "phishing",
    "steal", "theft", "fraud", "scam",
    "drugs", "alcohol", "smoke", "cigarette", "weed"
]

SYSTEM_WORDS = [
    "ignore rules", "bypass", "jailbreak",
    "system prompt", "developer message",
    "pretend you are admin",
    "password", "otp", "credit card", "bank details"
]


RESTRICTED_WORDS = (
    ABUSE_WORDS +
    VIOLENCE_WORDS +
    ILLEGAL_WORDS +
    SYSTEM_WORDS
)

def filter_input(message: str):
    msg = message.lower()

    for word in RESTRICTED_WORDS:
        pattern = rf"\b{re.escape(word)}\b"
        if re.search(pattern, msg):
            raise ValueError(
                "Your message contains content that is not allowed."
            )

    DB_KEYWORDS = ["marks", "score", "attendance", "present", "absent"]
    requires_db = any(keyword in msg for keyword in DB_KEYWORDS)

    return requires_db
