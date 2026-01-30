from sqlalchemy.orm import Session
from datetime import date, timedelta
from calendar import monthrange

from app.models import Academics, Attendance, Master, ChatHistory
from .intent import detect_time_intent
from app.llm import call_llm


# ---------------- SECURITY ----------------

def validate_student(db: Session, student_id: int):
    """
    Ensures the student exists before any data is returned.
    This prevents unauthorized access to student data.
    """
    return db.query(Master).filter(Master.id == student_id).first()


# ---------------- TIME FILTER ----------------

def _apply_time_filter(query, time_scope):
    """
    Applies date filtering to attendance queries based on time intent.
    Supports:
    - today, yesterday, week, last_week, month, last_month
    - specific month and year (e.g. March 2023)
    """

    if not time_scope:
        return query

    today = date.today()

    # Specific month & year
    if time_scope.get("type") == "month_year":
        year = time_scope["year"]
        month = time_scope["month"]

        start_date = date(year, month, 1)
        last_day = monthrange(year, month)[1]
        end_date = date(year, month, last_day)

        return query.filter(
            Attendance.date >= start_date,
            Attendance.date <= end_date
        )

    scope = time_scope.get("type")

    if scope == "today":
        return query.filter(Attendance.date == today)

    if scope == "yesterday":
        return query.filter(Attendance.date == today - timedelta(days=1))

    if scope == "week":
        return query.filter(Attendance.date >= today - timedelta(days=7))

    if scope == "last_week":
        start = today - timedelta(days=14)
        end = today - timedelta(days=7)
        return query.filter(
            Attendance.date >= start,
            Attendance.date < end
        )

    if scope == "month":
        start = today.replace(day=1)
        return query.filter(Attendance.date >= start)

    if scope == "last_month":
        if today.month == 1:
            start = today.replace(year=today.year - 1, month=12, day=1)
        else:
            start = today.replace(month=today.month - 1, day=1)

        end = today.replace(day=1)

        return query.filter(
            Attendance.date >= start,
            Attendance.date < end
        )

    return query


# ---------------- RULE-BASED BOT ----------------

def fetch_student_data(db: Session, message: str, student_id: int):
    # --- Security checks ---
    if not isinstance(student_id, int) or student_id <= 0:
        return "Invalid student ID."

    if not validate_student(db, student_id):
        return "Student record not found."

    msg = message.lower()
    time_scope = detect_time_intent(message)

    # ---- Attendance Queries ----
    if any(word in msg for word in ["attendance", "attend", "present", "absent"]):
        query = db.query(Attendance).filter(
            Attendance.student_id == student_id
        )

        query = _apply_time_filter(query, time_scope)
        records = query.all()

        if not records:
            return "No attendance records found for the specified period."

        present_days = sum(
            1 for r in records
            if r.status.lower().startswith("p")
        )

        return (
            f"Attendance Summary:\n"
            f"Total days recorded: {len(records)}\n"
            f"Days present: {present_days}\n"
            f"Days absent: {len(records) - present_days}"
        )

    # ---- Academic Queries ----
    if any(word in msg for word in ["mark", "score", "result", "grade", "exam", "test", "subject", "math", "science", "english", "history"]):
        records = db.query(Academics).filter(
            Academics.student_id == student_id
        ).all()

        if not records:
            return "No academic records found."

        lines = ["Academic Records:"]
        for r in records:
            lines.append(f"{r.subject}: {r.score}")

        return "\n".join(lines)

    return None  # Let AI handle this


# ---------------- FULL PROFILE FETCH ----------------

def fetch_full_student_profile(db: Session, student_id: int):
    student = db.query(Master).filter(
        Master.id == student_id
    ).first()

    if not student:
        return None

    academics = db.query(Academics).filter(
        Academics.student_id == student_id
    ).all()

    attendance = db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).all()

    return {
        "student": {
            "id": student.id,
            "name": student.name
        },
        "academics": [
            {"subject": a.subject, "score": a.score}
            for a in academics
        ],
        "attendance": [
            {"date": str(a.date), "status": a.status}
            for a in attendance
        ]
    }


# ---------------- AI SCHOOL ADVISOR ----------------

def generate_smart_school_reply(db, student_id, role, user_question):
    profile = fetch_full_student_profile(db, student_id)

    if not profile:
        return "No student record found for this ID."

    academics_text = "\n".join(
        [f"{a['subject']}: {a['score']}" for a in profile["academics"]]
    ) or "No academic records available."

    attendance_text = "\n".join(
        [f"{a['date']}: {a['status']}" for a in profile["attendance"][:10]]
    ) or "No attendance records available."

    prompt = f"""
You are a professional school academic advisor AI.

User role: {role}

Student Profile:
Name: {profile['student']['name']}
ID: {profile['student']['id']}

Academic Records:
{academics_text}

Attendance Records (recent):
{attendance_text}

The user asked:
"{user_question}"

Rules:
- Answer ONLY using the data above
- If data is missing, say you do not have that information
- Be polite and supportive
- If performance is asked, give a summary and 2–3 improvement tips
- If a specific subject is asked, answer only for that subject
"""

    return call_llm(prompt, role)


# ---------------- CHAT HISTORY ----------------

def save_chat(db, role, message, reply, student_id=None):
    chat = ChatHistory(
        role=role,
        user_message=message,
        bot_reply=reply,
        student_id=student_id
    )
    db.add(chat)
    db.commit()


# ---------------- SNAPSHOT API ----------------

def get_student_snapshot(db, student_id: int):
    marks = db.query(Academics).filter(
        Academics.student_id == student_id
    ).all()

    attendance = db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).all()

    return {
        "marks": [
            {"subject": m.subject, "score": m.score}
            for m in marks
        ],
        "attendance": [
            {"date": str(a.date), "status": a.status}
            for a in attendance
        ]
    }
