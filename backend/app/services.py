from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import date, datetime
from calendar import monthrange

from app.models import Academics, Attendance, Master, ChatHistory
from app.llm import call_llm


# =====================================================
# 🔐 SECURITY
# =====================================================

def validate_student(db: Session, student_id: int):
    return db.query(Master).filter(Master.id == student_id).first()


# =====================================================
# 📅 DATE-SPECIFIC ATTENDANCE
# =====================================================

def fetch_attendance_by_date(db, student_id: int, date_str: str):
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD."

    record = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.date == target_date
    ).first()

    if not record:
        return f"No attendance record found for {date_str}."

    return f"On {date_str}, you were marked **{record.status}**."


# =====================================================
# 📊 ATTENDANCE SUMMARY
# =====================================================

def fetch_attendance_summary(db, student_id: int, month=None, year=None):
    query = db.query(Attendance).filter(
        Attendance.student_id == student_id
    )

    if year:
        query = query.filter(extract("year", Attendance.date) == year)

    if month:
        query = query.filter(extract("month", Attendance.date) == month)

    records = query.all()

    if not records:
        return "No attendance records found."

    total = len(records)
    present = sum(1 for r in records if r.status.lower() == "present")
    absent = total - present
    percentage = round((present / total) * 100, 2)

    label = f"{month}/{year}" if month else str(year)

    return (
        f"Attendance Summary ({label}):\n"
        f"Total days recorded: {total}\n"
        f"Days present: {present}\n"
        f"Days absent: {absent}\n"
        f"Attendance percentage: {percentage}%"
    )


# =====================================================
# 📈 AVERAGE SCORE
# =====================================================

def fetch_average_score(db, student_id: int):
    records = db.query(Academics).filter(
        Academics.student_id == student_id
    ).all()

    if not records:
        return "No academic records found."

    avg = round(sum(r.score for r in records) / len(records), 2)
    return f"Your average score is **{avg}**."


# =====================================================
# 📚 RAW DATA FETCH (MARKS / ATTENDANCE)
# =====================================================

def fetch_student_data(db: Session, message: str, student_id: int, month=None, year=None):
    if not validate_student(db, student_id):
        return "Student record not found."

    msg = message.lower()

    # ---------- ATTENDANCE ----------
    if "attendance" in msg:
        query = db.query(Attendance).filter(
            Attendance.student_id == student_id
        )

        if month and year:
            start = date(year, month, 1)
            end = date(year, month, monthrange(year, month)[1])
            query = query.filter(
                Attendance.date >= start,
                Attendance.date <= end
            )

        records = query.all()
        if not records:
            return "No attendance records found."

        present = sum(1 for r in records if r.status.lower() == "present")
        percentage = round((present / len(records)) * 100, 2)

        return (
            f"Attendance Summary:\n"
            f"Total days recorded: {len(records)}\n"
            f"Days present: {present}\n"
            f"Days absent: {len(records) - present}\n"
            f"Attendance percentage: {percentage}%"
        )

    # ---------- MARKS ----------
    if any(word in msg for word in [
        "mark", "marks", "score", "result",
        "math", "science", "english", "history"
    ]):
        records = db.query(Academics).filter(
            Academics.student_id == student_id
        ).all()

        if not records:
            return "No academic records found."

        return "\n".join(
            ["Academic Records:"] +
            [f"{r.subject}: {r.score}" for r in records]
        )

    return "No matching academic data found."


# =====================================================
# 🥇 STRONGEST / WEAKEST SUBJECT
# =====================================================

def get_strongest_and_weakest_subject(db, student_id: int):
    records = db.query(Academics).filter(
        Academics.student_id == student_id
    ).all()

    if not records:
        return None, None

    scores = {r.subject: r.score for r in records}
    strongest = max(scores, key=scores.get)
    weakest = min(scores, key=scores.get)

    return strongest, weakest


# =====================================================
# 🧠 AI SCHOOL ADVISOR (FIXED — NO HALLUCINATIONS)
# =====================================================

def generate_smart_school_reply(db, student_id, role, message):
    marks = db.query(Academics).filter(
        Academics.student_id == student_id
    ).all()

    attendance = db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).all()

    if not marks and not attendance:
        return "No academic data available to generate suggestions."

    marks_summary = [f"{m.subject}: {m.score}" for m in marks]

    total_days = len(attendance)
    present_days = sum(1 for a in attendance if a.status.lower() == "present")
    attendance_pct = (
        round((present_days / total_days) * 100, 2)
        if total_days > 0 else "N/A"
    )

    prompt = f"""
You are a SCHOOL ACADEMIC ADVISOR.

Student question:
"{message}"

ACADEMIC DATA (ONLY SOURCE OF TRUTH):

Marks:
{marks_summary}

Attendance:
Total days: {total_days}
Days present: {present_days}
Attendance percentage: {attendance_pct}

STRICT RULES:
- Talk ONLY about academics (marks, subjects, attendance, study habits)
- Do NOT mention politics, voting, news, or unrelated topics
- Do NOT invent ranks, trends, or external examples
- Give practical study improvement suggestions
- Keep response short (5–7 bullet points max)

Now respond.
"""

    return call_llm(prompt, role)


# =====================================================
# 💬 CHAT HISTORY
# =====================================================

def save_chat(db, role, message, reply, student_id=None):
    db.add(ChatHistory(
        role=role,
        user_message=message,
        bot_reply=reply,
        student_id=student_id
    ))
    db.commit()
