from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from app.models import ChatHistory
from fastapi.middleware.cors import CORSMiddleware

from app.database import SessionLocal, engine
from app import models, schemas
from app.filters import filter_input, apply_tone
from app.llm import call_llm
from app.llm_guard import generate_guard_response
from app.services import fetch_student_data, save_chat
from app.intent import detect_time_intent, school_domain_guard

# Load env
load_dotenv()

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="School Chatbot Backend",
    description="Backend API for School Chatbot Application",
    version="2.0.0"
)

# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- DB Dependency ----
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---- Health ----
@app.get("/")
def health_check():
    return {"status": "ok", "message": "School Chatbot Backend Running (SQL Enabled)"}

# ---- Admin Check ----
@app.get("/admin/check")
def admin_check(x_admin_token: str = Header(None)):
    admin_token = os.getenv("ADMIN_TOKEN")

    if x_admin_token != admin_token:
        raise HTTPException(status_code=401, detail="Invalid admin token")

    return {"message": "Admin authenticated"}


# ---- Chat Endpoint ----
@app.post("/chat", response_model=schemas.ChatResponse)
def chat(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    try:
        allowed, reason, guard_reply = filter_input(request.message)

        # BLOCKED
        if not allowed:
            ai_guard_reply = generate_guard_response(
                reason,
                request.role,
                request.message
            )
            final_reply = apply_tone(request.role, ai_guard_reply, reason)

            save_chat(db, request.role, request.message, final_reply, request.student_id)
            return {"reply": final_reply}

        # SCHOOL DOMAIN CHECK
        is_valid, guard_reply = school_domain_guard(request.message)
        if not is_valid:
            final_reply = apply_tone(request.role, guard_reply)
            save_chat(db, request.role, request.message, final_reply, request.student_id)
            return {"reply": final_reply}

        # TIME INTENT
        time_scope = detect_time_intent(request.message)

        # DATABASE QUERY
        if any(word in request.message.lower() for word in [
            "mark", "score", "result", "attendance",
            "present", "absent", "exam", "test", "subject"
        ]):
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

            if time_scope:
                if isinstance(time_scope, dict) and time_scope.get("type") == "month_year":
                    db_reply += f"\n\nTime Scope: {time_scope['month']}/{time_scope['year']}"
                elif isinstance(time_scope, dict):
                    db_reply += f"\n\nTime Scope: {time_scope.get('type').replace('_', ' ').title()}"

            final_reply = apply_tone(request.role, db_reply)

        else:
            llm_response = call_llm(
                request.message,
                request.role
            )
            final_reply = apply_tone(request.role, llm_response)

        # SAVE CHAT TO SQL
        save_chat(db, request.role, request.message, final_reply, request.student_id)

        return {"reply": final_reply}

    except Exception as e:
        print("CHAT ERROR:", str(e))

        fallback = (
            "We are experiencing a technical issue at the moment.\n"
            "Please contact the school office."
        )

        final_reply = apply_tone(request.role, fallback)
        save_chat(db, request.role, request.message, final_reply, request.student_id)

        return {"reply": final_reply}

@app.get("/chat/history/{student_id}")
def get_chat_history(student_id: int, db: Session = Depends(get_db)):
    history = db.query(ChatHistory)\
        .filter(ChatHistory.student_id == student_id)\
        .order_by(ChatHistory.timestamp.desc())\
        .limit(20)\
        .all()

    return history