from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os   

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

# Main Chatbot Endpoint
@app.post("/chat", response_model=schemas.ChatResponse)
def chat(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    try:
        # Filter 1 - Input Filtering and restricted content check
        requires_db = filter_input(request.message)

        # Detect intent and ensure it's school domain
        is_valid, quard_reply = school_domain_guard(request.message)
        if not is_valid:
            return {
                "reply": apply_tone(request.role, quard_reply)
            }
        
        # Time intent detection
        time_scope = detect_time_intent(request.message)

        # Database path
        if requires_db:
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
                db_reply += f"\n\nTime Scope Detected: {time_scope.replace('_', ' ').title()}"

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
    
    except Exception:
        # General system fallback
        fallback = (
            "We are experiencing a technical issue at the moment.\n"
            "Please try again later or contact the school office at +9876543210."
        )
        return {"reply": apply_tone(request.role, fallback)}
