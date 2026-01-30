from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from app.advisor_intent import is_advisor_query

from fastapi.middleware.cors import CORSMiddleware

from app.admin_routes import router as admin_router
from app.database import SessionLocal, engine
from app import models, schemas
from app.filters import filter_input, apply_tone
from app.llm import call_llm
from app.llm_guard import generate_guard_response
from app.services import (
    fetch_student_data,
    save_chat,
    generate_smart_school_reply
)
from app.intent import detect_time_intent, school_domain_guard
from app.models import ChatHistory
from app.ollama_warmup import start_warmup
from app.advisor_intent import is_advisor_query

# ----------------- WARM UP OLLAMA -----------------
start_warmup()

# ----------------- ENV -----------------
load_dotenv()

# ----------------- DB INIT -----------------
models.Base.metadata.create_all(bind=engine)

# ----------------- APP -----------------
app = FastAPI(
    title="Smart School Chatbot Backend",
    description="Backend API for Smart School Chatbot Application",
    version="3.2.0"
)

# ----------------- CORS -----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- ROUTERS -----------------
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
def health_check():
    return {
        "status": "ok",
        "message": "Smart School Chatbot Backend Running (SQL + AI + Advisor Enabled)"
    }

# ----------------- ADMIN CHECK -----------------
@app.get("/admin/check")
def admin_check(x_admin_token: str = Header(None)):
    admin_token = os.getenv("ADMIN_TOKEN")

    if not admin_token:
        raise HTTPException(
            status_code=500,
            detail="ADMIN_TOKEN not set on server"
        )

    if not x_admin_token:
        raise HTTPException(
            status_code=401,
            detail="Missing admin token"
        )

    if x_admin_token.strip() != admin_token.strip():
        raise HTTPException(
            status_code=401,
            detail="Invalid admin token"
        )

    return {"message": "Admin authenticated"}

# ----------------- CHAT -----------------
@app.post("/chat", response_model=schemas.ChatResponse)
def chat(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    try:
        msg = request.message.lower().strip()

        # ----------------- SAFETY FILTER -----------------
        allowed, reason, guard_reply = filter_input(request.message)

        if not allowed:
            ai_guard_reply = generate_guard_response(
                reason,
                request.role,
                request.message
            )

            final_reply = apply_tone(request.role, ai_guard_reply, reason)

            save_chat(
                db,
                request.role,
                request.message,
                final_reply,
                request.student_id
            )

            return {"reply": final_reply}

        # ----------------- SMART ADVISOR (TOP PRIORITY) -----------------
        print("ADVISOR MATCH:", is_advisor_query(msg), "| MESSAGE:", msg)

        if request.student_id and is_advisor_query(msg):
            smart_reply = generate_smart_school_reply(
                db,
                request.student_id,
                request.role,
                request.message
            )

            if smart_reply:
                final_reply = apply_tone(request.role, smart_reply)

                save_chat(
                    db,
                    request.role,
                    request.message,
                    final_reply,
                    request.student_id
                )

                return {"reply": final_reply}

        # ----------------- DOMAIN GUARD -----------------
        is_valid, guard_reply = school_domain_guard(request.message)

        if not is_valid:
            final_reply = apply_tone(request.role, guard_reply)

            save_chat(
                db,
                request.role,
                request.message,
                final_reply,
                request.student_id
            )

            return {"reply": final_reply}

        # ----------------- DIRECT DB QUERY -----------------
        DB_KEYWORDS = [
            "mark", "marks", "score", "result",
            "attendance", "present", "absent",
            "exam", "test", "subject",
            "math", "science", "english", "history"
        ]

        if any(word in msg for word in DB_KEYWORDS):
            if not request.student_id:
                raise HTTPException(
                    status_code=400,
                    detail="student_id is required for this query."
                )

            db_reply = fetch_student_data(
                db,
                request.message,
                request.student_id
            )

            final_reply = apply_tone(request.role, db_reply)

            save_chat(
                db,
                request.role,
                request.message,
                final_reply,
                request.student_id
            )

            return {"reply": final_reply}

        # ----------------- FALLBACK AI -----------------
        llm_response = call_llm(
            request.message,
            request.role
        )

        final_reply = apply_tone(request.role, llm_response)

        save_chat(
            db,
            request.role,
            request.message,
            final_reply,
            request.student_id
        )

        return {"reply": final_reply}

    except Exception as e:
        print("CHAT ERROR:", str(e))

        fallback = (
            "We are experiencing a technical issue at the moment.\n"
            "Please contact the school office."
        )

        final_reply = apply_tone(request.role, fallback)

        save_chat(
            db,
            request.role,
            request.message,
            final_reply,
            request.student_id
        )

        return {"reply": final_reply}

