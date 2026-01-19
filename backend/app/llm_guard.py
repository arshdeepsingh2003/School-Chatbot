from .llm import call_llm

def generate_guard_response(reason, role, user_message):
    try:
        prompt = f"""
You are a school safety assistant.
User role: {role}
Violation type: {reason}

User message:
{user_message}

Respond politely, safely, and professionally.
Do NOT provide any harmful, illegal, or sensitive information.
Keep the response short and supportive.
"""
        return call_llm(prompt, role)
    except Exception:
        return (
            "Your message cannot be processed due to safety policies. "
            "Please contact the school office for further assistance."
        )
