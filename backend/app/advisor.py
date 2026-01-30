from app.services import get_student_snapshot

def build_advisor_prompt(db, student_id, user_message):
    snapshot = get_student_snapshot(db, student_id)

    marks_text = "\n".join(
        f"- {m['subject']}: {m['score']}"
        for m in snapshot["marks"]
    ) or "No marks available"

    attendance_text = "\n".join(
        f"- {a['date']}: {a['status']}"
        for a in snapshot["attendance"]
    ) or "No attendance data"

    return f"""
You are a Smart School Academic Advisor.

Student Performance Data:
Marks:
{marks_text}

Attendance Records:
{attendance_text}

User Question:
{user_message}

Your job:
- Analyze strengths and weak areas
- Give friendly, encouraging advice
- Keep the tone respectful and motivating
- Do NOT list raw data
- Do NOT mention you are an AI

Respond like a real teacher or counselor.
"""
