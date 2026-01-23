from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Master, Academics, Attendance
from app.admin_auth import admin_auth

router = APIRouter(prefix="/admin", tags=["Admin Panel"])



# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# Get All Students
@router.get("/students", dependencies=[Depends(admin_auth)])
def get_all_students(db: Session = Depends(get_db)):
    return db.query(Master).all()



# Add Student
@router.post("/students", dependencies=[Depends(admin_auth)])
def add_student(student_id: int, name: str, db: Session = Depends(get_db)):
    if db.query(Master).filter(Master.id == student_id).first():
        raise HTTPException(status_code=400, detail="Student already exists")

    student = Master(id=student_id, name=name)
    db.add(student)
    db.commit()

    return {"message": "Student added successfully"}


# Update Student-
@router.put("/students/{student_id}", dependencies=[Depends(admin_auth)])
def update_student(student_id: int, name: str, db: Session = Depends(get_db)):
    student = db.query(Master).filter(Master.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.name = name
    db.commit()

    return {"message": "Student updated successfully"}



# Add / Update Marks
@router.post("/marks", dependencies=[Depends(admin_auth)])
def add_or_update_marks(
    student_id: int,
    subject: str,
    score: int,
    db: Session = Depends(get_db)
):
    if not db.query(Master).filter(Master.id == student_id).first():
        raise HTTPException(status_code=404, detail="Student not found")

    record = db.query(Academics).filter(
        Academics.student_id == student_id,
        Academics.subject == subject
    ).first()

    if record:
        record.score = score
    else:
        db.add(Academics(
            student_id=student_id,
            subject=subject,
            score=score
        ))

    db.commit()
    return {"message": "Marks saved successfully"}


# Delete Student
@router.delete("/students/{student_id}", dependencies=[Depends(admin_auth)])
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Master).filter(Master.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    db.query(Academics).filter(Academics.student_id == student_id).delete()
    db.query(Attendance).filter(Attendance.student_id == student_id).delete()

    db.delete(student)
    db.commit()

    return {"message": "Student deleted successfully"}


# Student Report
@router.get("/report/{student_id}", dependencies=[Depends(admin_auth)])
def student_report(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Master).filter(Master.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    academics = db.query(Academics).filter(
        Academics.student_id == student_id
    ).all()

    attendance = db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).all()

    return {
        "student": student,
        "academics": academics,
        "attendance": attendance
    }
