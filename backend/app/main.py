from fastapi import FastAPI, Depends, HTTPException , Header
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os   
from app.llm_guard import generate_guard_response
from fastapi.middleware.cors import CORSMiddleware

from app.database import SessionLocal, engine
from app import models, schemas
from app.filters import filter_input, apply_tone
from app.llm import call_llm
from app.services import fetch_student_data
from app.intent import detect_time_intent, school_domain_guard
from app.upload_data import router as upload_router

#load environment variables
load_dotenv()

#create db tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="School Chatbot Backend",
    description="Backend API for School Chatbot Application",
    version="1.0.0"
)

# ---- CORS CONFIG ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(upload_router)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Health Check Endpoint
@app.get("/")
def health_check():
    return {"status": "ok", "message": "School Chatbot Backend is running."}

# Admin Token Test Endpoint
@app.get("/admin/check")
def admin_check(x_admin_token: str = Header(None)):
    admin_token = os.getenv("ADMIN_TOKEN")

    if x_admin_token != admin_token:
        raise HTTPException(status_code=401, detail="Invalid admin token")

    return {"message": "Admin authenticated"}

# Main Chatbot Endpoint
@app.post("/chat", response_model=schemas.ChatResponse)
def chat(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    try:
        # Filter 1 - Input Filtering and restricted content check
        allowed, reason, guard_reply = filter_input(request.message)

        if not allowed:
            ai_guard_reply = generate_guard_response(
                reason,
                request.role,
                request.message
            )
            return {
                "reply": apply_tone(request.role, ai_guard_reply, reason)
            }

        # Detect intent and ensure it's school domain
        is_valid, quard_reply = school_domain_guard(request.message)
        if not is_valid:
            return {
                "reply": apply_tone(request.role, quard_reply)
            }
        
        # Time intent detection
        time_scope = detect_time_intent(request.message)

        # Database path
        if any(word in request.message.lower() for word in ["mark", "score", "result", "attendance", "present", "absent", "exam", "test", "subject"]):
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
                    db_reply += (
                        f"\n\nTime Scope Detected: "
                        f"{time_scope['month']}/{time_scope['year']}"
                    )
                elif isinstance(time_scope, dict):
                    db_reply += (
                        f"\n\nTime Scope Detected: "
                        f"{time_scope.get('type', '').replace('_', ' ').title()}"
                    )

            final_reply = apply_tone(request.role, db_reply)

        else:
            # Call LLM for general queries
            llm_response = call_llm(
                request.message,
                request.role
            )
            final_reply = apply_tone(request.role, llm_response)

        return {"reply": final_reply}
    
    except ValueError:
        #Restricted or invalid input fallback
        fallback = (
            "Your message could not be processed.\n"
            "Please contact the school administration for assistance."
        )
        return {"reply": apply_tone(request.role, fallback)}
    
    except Exception as e:
        print("CHAT ERROR:", str(e))

        fallback = (
            "We are experiencing a technical issue at the moment.\n"
            "Please try again later or contact the school office at +9876543210."
        )
        return {"reply": apply_tone(request.role, fallback)}
