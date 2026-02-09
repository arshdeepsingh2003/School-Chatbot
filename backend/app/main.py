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

# ---- SERVICES (SQL FIRST) ----
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

# ----------------- APP -----------------
app = FastAPI(
    title="Smart School Chatbot Backend",
    description="SQL-first Academic Chatbot (STRICT + AUTHORIZED)",
    version="4.5.4"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)


# ----------------- DB DEP -----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------- HEALTH -----------------
@app.get("/")
def health():
    return {"status": "ok", "message": "Smart School Chatbot Running"}


# ----------------- CHAT -----------------
@app.post("/chat", response_model=schemas.ChatResponse)
def chat(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    try:
        msg = request.message.lower().strip()

        # ✅ YEAR ONLY INPUT → FORCE ATTENDANCE MODE
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
        # 🚨 STRONG AUTHORIZATION GUARD
        # ======================================================
        if any(k in msg for k in [
            "student id",
            "student with id",
            "another student",
            "other student",
            "friend",
            "my friend",
            "classmate",
            "someone else"
        ]):
            reply = apply_tone(
                request.role,
                "I can share academic details only for the currently logged-in student."
            )
            save_chat(db, request.role, request.message, reply, request.student_id)
            return {"reply": reply}

        # ======================================================
        # 🚫 BLOCK WRITE / ADMIN ACTIONS
        # ======================================================
        if any(w in msg for w in ["change", "update", "modify", "edit", "delete"]):
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
        # 📘 SUBJECT PERFORMANCE (GENERALIZED)
        # ======================================================
        if (
            request.student_id
            and any(sub in msg for sub in ["english", "math", "science", "history"])
            and any(k in msg for k in ["perform", "performance", "doing", "how", "result"])
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
- Neutral tone (student or parent)
"""

            reply = apply_tone(
                request.role,
                call_llm(prompt, request.role)
            )
            save_chat(db, request.role, request.message, reply, request.student_id)
            return {"reply": reply}

        # ======================================================
        # 📅 ATTENDANCE (STRICT + FIXED)
        # ======================================================
        if request.student_id and is_attendance_query(msg):

            # 📌 Exact date
            date_match = re.search(r"\d{4}-\d{2}-\d{2}", msg)
            if date_match:
                reply = fetch_attendance_by_date(
                    db,
                    request.student_id,
                    date_match.group()
                )

            else:
                month, year = extract_month_year(msg)

                # ✅ YEAR ONLY (CHECK FIRST)
                if year and not month:
                    reply = fetch_attendance_summary(
                        db,
                        request.student_id,
                        month=None,
                        year=year
                    )

                # ❌ INVALID MONTH
                elif month == "INVALID_MONTH":
                    reply = (
                        "Invalid month specified.\n"
                        "Please use a valid month name (January–December) "
                        "or a number between 1 and 12."
                    )

                # ❌ INVALID YEAR
                elif year == "INVALID_YEAR":
                    reply = (
                        "Invalid year specified.\n"
                        "Attendance data is available only up to the current year."
                    )

                # ✅ MONTH + YEAR
                elif month and year:
                    reply = fetch_attendance_summary(
                        db,
                        request.student_id,
                        month=month,
                        year=year
                    )

                # ❌ FALLBACK
                else:
                    reply = (
                        "Please specify attendance like:\n"
                        "- Attendance of October 2025\n"
                        "- Attendance of 2025\n"
                        "- Was I present on 2025-10-08"
                    )

            reply = apply_tone(request.role, reply)
            save_chat(db, request.role, request.message, reply, request.student_id)
            return {"reply": reply}

        # ======================================================
        # 🟢 RAW MARKS
        # ======================================================
        if request.student_id and (
            is_raw_marks_query(msg) or msg in ["marks", "scores", "results", "result"]
        ):
            reply = apply_tone(
                request.role,
                fetch_student_data(db, request.message, request.student_id)
            )
            save_chat(db, request.role, request.message, reply, request.student_id)
            return {"reply": reply}

        # ======================================================
        # 🧠 STRONGEST / WEAKEST SUBJECT
        # ======================================================
        if request.student_id and any(w in msg for w in ["strongest", "weakest"]):
            strongest, weakest = get_strongest_and_weakest_subject(db, request.student_id)

            if not strongest:
                reply = "No academic records found."
            elif "strongest" in msg:
                reply = f"Your strongest subject is **{strongest}**."
            else:
                reply = f"Your weakest subject is **{weakest}**."

            reply = apply_tone(request.role, reply)
            save_chat(db, request.role, request.message, reply, request.student_id)
            return {"reply": reply}

        # ======================================================
        # 🔵 SMART ADVISOR
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
