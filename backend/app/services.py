from sqlalchemy.orm import Session
from datetime import date, timedelta
from calendar import monthrange
from app.models import Academics, Attendance, Master
from .intent import detect_time_intent
from app.models import Attendance
from app.models import ChatHistory

def validate_student(db: Session, student_id: int):

    ''' 
    ensures the student exists before any data is returned.
    this prevents to unauthorized access to student data.
    
    '''
    return db.query(Master).filter(Master.id == student_id).first()



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


def fetch_student_data(db: Session, message: str, student_id: int):
    # --- Security checks ---
    if not isinstance(student_id, int) or student_id <= 0:
        return "Invalid student ID."

    if not validate_student(db, student_id):
        return "Student record not found."

    msg = message.lower()
    time_scope = detect_time_intent(message)

    # ---- Fetch Attendance Data ----
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

    # ---- Fetch Academic Data ----
    if any(word in msg for word in ["mark", "score", "result", "grade", "exam", "test", "subject"]):
        records = db.query(Academics).filter(
            Academics.student_id == student_id
        ).all()

        if not records:
            return "No academic records found."

        lines = ["Academic Records:"]
        for r in records:
            lines.append(f"{r.subject}: {r.score}")

        return "\n".join(lines)

    return "I can assist only with academic or attendance information."

def save_chat(db, role, message, reply, student_id=None):
    chat = ChatHistory(
        role=role,
        user_message=message,
        bot_reply=reply,
        student_id=student_id
    )
    db.add(chat)
    db.commit()