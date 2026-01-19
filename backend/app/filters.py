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

def _contains(words, msg):
    return any(
        re.search(rf"\b{re.escape(word)}\b", msg)
        for word in words
    )

# Function to filter input messages(FILTER 1)
def filter_input(message: str):
    msg = message.lower()

    if _contains(SYSTEM_WORDS, msg):
        return False, "SYSTEM", (
            "This request attempts to access restricted system information. "
            "For security reasons, this action is not permitted."
        )

    if _contains(VIOLENCE_WORDS, msg):
        return False, "VIOLENCE", (
            "Your message contains violent or unsafe content. "
            "If this concerns a real issue, please contact school authorities immediately."
        )

    if _contains(ILLEGAL_WORDS, msg):
        return False, "ILLEGAL", (
            "This request involves activities that are not allowed. "
            "Please follow school policies and legal guidelines."
        )

    if _contains(ABUSE_WORDS, msg):
        return False, "ABUSE", (
            "Let's keep our communication respectful and positive. "
            "I'm here to help with your school-related questions."
        )

    return True, "OK", None


# Function to filter output messages(FILTER 2)
def apply_tone(role: str, text: str, reason: str = "OK"):
    # Safety fallback
    if not text:
        text = "We are unable to process your request at the moment."

    role = role.lower()

    # Unknown role fallback (extra safety)
    if role not in ["student", "parent"]:
        return (
            f"{text}\n\n"
            "— School Support Team"
        )

    # Student tone
    if role == "student":
        if reason == "ABUSE":
            return (
                "😊 Hi!\n\n"
                f"{text}\n\n"
                "Let's treat everyone kindly and focus on learning!"
            )
        if reason == "VIOLENCE":
            return (
                "🚨 Hi!\n\n"
                f"{text}\n\n"
                "If you're feeling unsafe, please reach out to a teacher or counselor right away."
            )
        if reason == "ILLEGAL":
            return (
                "😊 Hi!\n\n"
                f"{text}\n\n"
                "It's always best to follow school rules and stay safe."
            )
        if reason == "SYSTEM":
            return (
                "😊 Hi!\n\n"
                f"{text}\n\n"
                "For privacy and security, some actions are restricted."
            )
        return (
            "😊 Hi!\n\n"
            f"{text}\n\n"
            "Keep learning and doing great!"
        )

    # Parent tone
    if reason == "ABUSE":
        return (
            "Dear Parent,\n\n"
            f"{text}\n\n"
            "We encourage respectful communication at all times.\n\n"
            "Regards,\n"
            "School Administration"
        )

    if reason == "VIOLENCE":
        return (
            "Dear Parent,\n\n"
            f"{text}\n\n"
            "For any safety-related concerns, please contact the school office immediately.\n\n"
            "Regards,\n"
            "School Administration"
        )

    if reason == "ILLEGAL":
        return (
            "Dear Parent,\n\n"
            f"{text}\n\n"
            "The school follows strict legal and ethical guidelines.\n\n"
            "Regards,\n"
            "School Administration"
        )

    if reason == "SYSTEM":
        return (
            "Dear Parent,\n\n"
            f"{text}\n\n"
            "This request involves restricted system-level information.\n\n"
            "Regards,\n"
            "School Administration"
        )

    return (
        "Dear Parent,\n\n"
        f"{text}\n\n"
        "Regards,\n"
        "School Administration"
    )
