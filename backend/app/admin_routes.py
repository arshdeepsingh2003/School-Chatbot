from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date as dt_date
from app.database import SessionLocal
from app.models import Master, Academics, Attendance
from app.admin_auth import admin_auth

router = APIRouter(prefix="/admin", tags=["Admin Panel"])


# ---------------- DB DEPENDENCY ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- STUDENTS ----------------

# Get All Students
@router.get("/students", dependencies=[Depends(admin_auth)])
def get_all_students(db: Session = Depends(get_db)):
    return db.query(Master).order_by(Master.id).all()


# Add Student (Prevent Duplicate)
@router.post("/students", dependencies=[Depends(admin_auth)])
def add_student(student_id: int, name: str, db: Session = Depends(get_db)):
    existing = db.query(Master).filter(Master.id == student_id).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Student already exists"
        )

    student = Master(id=student_id, name=name)
    db.add(student)
    db.commit()

    return {"message": "Student added successfully"}


# Update Student
@router.put("/students/{student_id}", dependencies=[Depends(admin_auth)])
def update_student(student_id: int, name: str, db: Session = Depends(get_db)):
    student = db.query(Master).filter(Master.id == student_id).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    student.name = name
    db.commit()

    return {"message": "Student updated successfully"}


# ---------------- MARKS ----------------

# Add / Update Marks (Duplicate Subject = Update)
@router.post("/marks", dependencies=[Depends(admin_auth)])
def add_or_update_marks(
    student_id: int,
    subject: str,
    score: int,
    db: Session = Depends(get_db)
):
    student = db.query(Master).filter(Master.id == student_id).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # Case-insensitive subject match
    record = db.query(Academics).filter(
        Academics.student_id == student_id,
        Academics.subject.ilike(subject)
    ).first()

    if record:
        record.score = score
        db.commit()
        return {"message": f"Marks updated for {record.subject}"}

    db.add(
        Academics(
            student_id=student_id,
            subject=subject,
            score=score
        )
    )
    db.commit()

    return {"message": f"Marks added for {subject}"}


# ---------------- DELETE ----------------

# Delete Student + All Related Records
@router.delete("/students/{student_id}", dependencies=[Depends(admin_auth)])
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Master).filter(Master.id == student_id).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # Delete related data
    db.query(Academics).filter(
        Academics.student_id == student_id
    ).delete()

    db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).delete()

    db.delete(student)
    db.commit()

    return {"message": "Student and all related records deleted"}


# ---------------- REPORT ----------------

# Student Report
@router.get("/report/{student_id}", dependencies=[Depends(admin_auth)])
def student_report(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Master).filter(Master.id == student_id).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

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

# ---------------- ATTENDANCE ----------------

@router.post("/attendance", dependencies=[Depends(admin_auth)])
def add_or_update_attendance(
    student_id: int,
    date: str,    # YYYY-MM-DD
    status: str, # Present / Absent
    db: Session = Depends(get_db)
):
    student = db.query(Master).filter(Master.id == student_id).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    try:
        att_date = dt_date.fromisoformat(date)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    record = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.date == att_date
    ).first()

    if record:
        record.status = status
        db.commit()
        return {"message": f"Attendance updated for {att_date}"}

    db.add(
        Attendance(
            student_id=student_id,
            date=att_date,
            status=status
        )
    )
    db.commit()

    return {"message": f"Attendance added for {att_date}"}
