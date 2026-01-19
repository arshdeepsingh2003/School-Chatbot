from sqlalchemy.orm import Session
from datetime import date,timedelta

from .models import Academics,Attendance,Master
from .intent import detect_time_intent

def validate_student(db:Session,student_id:int):

    ''' 
    ensures the student exists before any data is returned.
    this prevents to unauthorized access to student data.
    
    '''
    student=db.query(Master).filter(Master.id==student_id).first()
    return student is not None