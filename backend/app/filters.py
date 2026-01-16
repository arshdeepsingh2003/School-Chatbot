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

# Function to filter input messages(FILTER 1)
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

# Function to filter output messages(FILTER 2)
def apply_tone(role: str, text: str) -> str:
    if not text or not text.strip():
        text = "We are unable to process your request at the moment. Please try again later."

    role = (role or "").lower()

    # Parent: formal & professional
    if role == "parent":
        return (
            "Dear Parent,\n\n"
            f"{text}\n\n"
            "If you require further assistance, please feel free to contact the school office.\n\n"
            "Regards,\n"
            "School Administration"
        )

    # Student: friendly & encouraging
    if role == "student":
        return (
            "Hello!\n\n"
            f"{text}\n\n"
            "Keep learning, stay curious, and do your best! 🌟"
        )

    # Unknown role fallback (extra safety)
    return (
        f"{text}\n\n"
        "— School Support Team"
    )
