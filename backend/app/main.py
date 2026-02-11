from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import re

from fastapi.middleware.cors import CORSMiddleware

from app.academic_intent import is_raw_marks_query
from app.attendance_intent import is_attendance_query
from app.advisor_intent import is_advisor_query
from app.time_parser import extract_month_year

from app.admin_routes import router as admin_router
from app.database import SessionLocal, engine
from app import models, schemas
from app.filters import filter_input, apply_tone
from app.llm_guard import generate_guard_response
from app.llm import call_llm

from app.services import (
    fetch_student_data,
    fetch_attendance_summary,
    fetch_attendance_by_date,
    fetch_average_score,
    get_strongest_and_weakest_subject,
    generate_smart_school_reply,
    save_chat,
)

from app.models import ChatHistory
from app.ollama_warmup import start_warmup


# ----------------- STARTUP -----------------
start_warmup()
load_dotenv()
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart School Chatbot Backend",
    description="SQL-first Academic Chatbot (STRICT + AUTHORIZED)",
    version="4.6.2"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)


# ----------------- DB -----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def health():
    return {"status": "ok", "message": "Smart School Chatbot Running"}


# ----------------- CHAT -----------------
@app.post("/chat", response_model=schemas.ChatResponse)
def chat(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    try:
        msg = request.message.lower().strip()
        msg = msg.replace("analyse", "analyze")

        if re.fullmatch(r"\d{4}", msg):
            msg = f"attendance {msg}"

        # ======================================================
        # 1️⃣ SAFETY FILTER
        # ======================================================
        allowed, reason, _ = filter_input(request.message)
        if not allowed:
            reply = apply_tone(
                request.role,
                generate_guard_response(reason, request.role, request.message),
                reason
            )
            save_chat(db, request.role, request.message, reply, request.student_id)
            return {"reply": reply}

        # ======================================================
        # 🚨 BLOCK OTHER STUDENTS
        # ======================================================
        if any(k in msg for k in [
            "student id", "student with id", "another student",
            "other student", "friend", "friend's",
            "classmate", "someone else"
        ]):
            reply = apply_tone(
                request.role,
                "I can share academic details only for the currently logged-in student."
            )
            save_chat(db, request.role, request.message, reply, request.student_id)
            return {"reply": reply}

        # ======================================================
        # 🚫 HARD BLOCK — WRITE / MODIFY REQUESTS
        # ======================================================
        if any(w in msg for w in [
            "update", "delete", "change", "edit", "modify",
            "remove", "erase", "correct", "alter"
        ]):
            reply = apply_tone(
                request.role,
                "You are not authorized to modify academic records."
            )
            save_chat(db, request.role, request.message, reply, request.student_id)
            return {"reply": reply}

        # ======================================================
        # 📊 AVERAGE SCORE
        # ======================================================
        if request.student_id and "average" in msg:
            reply = apply_tone(
                request.role,
                fetch_average_score(db, request.student_id)
            )
            save_chat(db, request.role, request.message, reply, request.student_id)
            return {"reply": reply}

        # ======================================================
        # 📅 ATTENDANCE
        # ======================================================
        if request.student_id and is_attendance_query(msg):

            natural_date = re.search(
                r"\b(\d{1,2})\s+"
                r"(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|"
                r"january|february|march|april|june|july|august|september|"
                r"october|november|december)\s+"
                r"(19\d{2}|20\d{2})\b",
                msg
            )

            if natural_date:
                day = int(natural_date.group(1))
                month_word = natural_date.group(2)
                year = int(natural_date.group(3))

                month_map = {
                    "jan": 1, "january": 1,
                    "feb": 2, "february": 2,
                    "mar": 3, "march": 3,
                    "apr": 4, "april": 4,
                    "may": 5,
                    "jun": 6, "june": 6,
                    "jul": 7, "july": 7,
                    "aug": 8, "august": 8,
                    "sep": 9, "sept": 9, "september": 9,
                    "oct": 10, "october": 10,
                    "nov": 11, "november": 11,
                    "dec": 12, "december": 12,
                }

                month = month_map[month_word]
                date_str = f"{year}-{month:02d}-{day:02d}"
                reply = fetch_attendance_by_date(db, request.student_id, date_str)

            else:
                month, year = extract_month_year(msg)

                if year and not month:
                    reply = fetch_attendance_summary(db, request.student_id, None, year)
                elif month == "INVALID_MONTH":
                    reply = "Invalid month specified. Please use January–December or 1–12."
                elif year == "INVALID_YEAR":
                    reply = "Invalid year specified. Attendance data is available only up to the current year."
                elif month and year:
                    reply = fetch_attendance_summary(db, request.student_id, month, year)
                else:
                    reply = (
                        "Please specify attendance like:\n"
                        "- Was I present on 17 September 2025\n"
                        "- Attendance of October 2025\n"
                        "- Attendance percentage for 2025"
                    )

            reply = apply_tone(request.role, reply)
            save_chat(db, request.role, request.message, reply, request.student_id)
            return {"reply": reply}

        # ======================================================
        # 📘 SUBJECT PERFORMANCE
        # ======================================================
        if request.student_id and re.search(
            r"\b(how|did|am|is)\b.*\b(i|he|she|my\s+child|my\s+son|my\s+daughter)\b.*\b(perform|performance|doing)\b.*\b(english|math|science|history)\b",
            msg
        ):
            db_data = fetch_student_data(db, request.message, request.student_id)

            prompt = f"""
Question:
"{request.message}"

Academic records:
{db_data}

RULES:
- Answer ONLY for the subject asked
- Use ONLY the marks shown
- No advice
- No bullet points
- 2 short sentences
- Neutral tone
"""

            reply = apply_tone(request.role, call_llm(prompt, request.role))
            save_chat(db, request.role, request.message, reply, request.student_id)
            return {"reply": reply}

        # ======================================================
        # 🟢 RAW MARKS
        # ======================================================
        if request.student_id and is_raw_marks_query(msg):
            reply = apply_tone(
                request.role,
                fetch_student_data(db, request.message, request.student_id)
            )
            save_chat(db, request.role, request.message, reply, request.student_id)
            return {"reply": reply}

        # ======================================================
        # 🧠 STRONGEST / WEAKEST
        # ======================================================
        if request.student_id and any(w in msg for w in [
            "strongest", "weakest",
            "strong", "weak",
            "best", "worst",
            "highest", "lowest"
        ]):
            strongest, weakest = get_strongest_and_weakest_subject(
                db, request.student_id
            )

            if not strongest:
                reply = "No academic records found."
            elif any(w in msg for w in [
                "strongest", "strong", "best", "highest"
            ]):
                reply = f"Your strongest subject is **{strongest}**."
            elif any(w in msg for w in [
                "weakest", "weak", "worst", "lowest"
            ]):
                reply = f"Your weakest subject is **{weakest}**."
            else:
                reply = "Please specify whether you want strongest or weakest subject."

            reply = apply_tone(request.role, reply)
            save_chat(db, request.role, request.message, reply, request.student_id)
            return {"reply": reply}

        # ======================================================
        # 🔵 ADVISOR
        # ======================================================
        if request.student_id and is_advisor_query(msg):
            reply = apply_tone(
                request.role,
                generate_smart_school_reply(
                    db, request.student_id, request.role, request.message
                )
            )
            save_chat(db, request.role, request.message, reply, request.student_id)
            return {"reply": reply}

        # ======================================================
        # ❌ HARD BLOCK
        # ======================================================
        reply = apply_tone(
            request.role,
            "I can help only with school-related topics like attendance, marks, exams, and performance."
        )
        save_chat(db, request.role, request.message, reply, request.student_id)
        return {"reply": reply}

    except Exception as e:
        print("CHAT ERROR:", e)
        reply = apply_tone(
            request.role,
            "We are experiencing a technical issue. Please contact the school office."
        )
        save_chat(db, request.role, request.message, reply, request.student_id)
        return {"reply": reply}


# ----------------- CHAT HISTORY -----------------
@app.get("/chat/history/{student_id}")
def chat_history(student_id: int, db: Session = Depends(get_db)):
    return (
        db.query(ChatHistory)
        .filter(ChatHistory.student_id == student_id)
        .order_by(ChatHistory.timestamp.desc())
        .limit(20)
        .all()
    )
