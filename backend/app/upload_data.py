import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Header
from sqlalchemy.orm import Session
import os

from app.database import SessionLocal
from app import models

router = APIRouter(prefix="/admin", tags=["Admin Upload"])

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# Admin Auth
def admin_auth(x_admin_token: str = Header(None)):
    """
    Simple token-based protection.
    Send header:
    X-Admin-Token: your_secret_token
    """
    admin_token = os.getenv("ADMIN_TOKEN")

    if not admin_token:
        raise HTTPException(
            status_code=500,
            detail="Server misconfiguration: ADMIN_TOKEN not set"
        )

    if x_admin_token != admin_token:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid admin token"
        )


# File Reader
def read_file(file: UploadFile):
    filename = file.filename.lower()

    if filename.endswith(".csv"):
        return pd.read_csv(file.file)

    if filename.endswith(".xlsx"):
        return pd.read_excel(file.file)

    raise HTTPException(
        status_code=400,
        detail="Only CSV and Excel (.xlsx) files are supported"
    )



# Upload Endpoint
@router.post("/upload")
def upload_students(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: None = Depends(admin_auth)  # Protect endpoint
):
    try:
        df = read_file(file)

        # ---- Required Columns ----
        required_columns = {
            "student_id",
            "name",
            "subject",
            "score",
            "date",
            "status"
        }

        if not required_columns.issubset(df.columns):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Missing required columns. "
                    "Required: student_id, name, subject, "
                    "score, date, status"
                )
            )

        inserted = 0
        updated_students = set()

        for _, row in df.iterrows():
            student_id = int(row["student_id"])

            # --------------------
            # Student (Master)
            # --------------------
            student = db.query(models.Master).filter(
                models.Master.id == student_id
            ).first()

            if not student:
                student = models.Master(
                    id=student_id,
                    name=str(row["name"])
                )
                db.add(student)
            else:
                # Update name if changed
                student.name = str(row["name"])
                updated_students.add(student_id)

           
            # Academics
            db.add(
                models.Academics(
                    student_id=student_id,
                    subject=str(row["subject"]),
                    score=int(row["score"])
                )
            )

         
            # Attendance
        
            db.add(
                models.Attendance(
                    student_id=student_id,
                    date=pd.to_datetime(row["date"]).date(),
                    status=str(row["status"])
                )
            )

            inserted += 1

        db.commit()

        return {
            "message": "Upload completed successfully",
            "records_processed": inserted,
            "students_updated": list(updated_students)
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )
