from sqlalchemy.orm import Session
from datetime import date,timedelta

from .models import Academics,Attendance,Master
from .intent import detect_time_intent

def validate_student(db:Session,student_id:int):

    ''' 
    ensures the student exists before any data is returned.
    this prevents to unauthorized access to student data.
    
    '''
    return db.query(Master).filter(Master.id==student_id).first()

def _apply_time_filter(query,time_scope):
    
    """
    Applies date filtering to attendance queries based on time intent.
    """

    today=date.today()

    if time_scope=="today":
        return query.filter(Attendance.data==today)
    
    elif time_scope=="yesterday":
        return query.filter(Attendance.date==today-timedelta(days=1))
    
    elif time_scope=="week":
        start_of_week=today-timedelta(days=7)
        return query.filter(Attendance.date>=start_of_week)
    
    elif time_scope=="last_week":
        start_of_last_week=today-timedelta(days=14)
        end_of_last_week=today-timedelta(days=7)
        return query.filter(
            Attendance.date>=start_of_last_week,
            Attendance.date<end_of_last_week
        )
    
    elif time_scope=="month":
        start_of_month=today.replace(day=1)
        return query.filter(Attendance.date>=start_of_month)
    
    elif time_scope=="last_month":
        if today.month==1:
            start_of_last_month=today.replace(year=today.year-1,month=12,day=1)
        else:
            start_of_last_month=today.replace(month=today.month-1,day=1)
        end_of_last_month=today.replace(day=1)
        return query.filter(
            Attendance.date>=start_of_last_month,
            Attendance.date<end_of_last_month
        )
    return query



def fetch_student_data(db:Session,message:str,student_id:int):

    if not isinstance(student_id,int) or student_id<=0:
        return "Invalid student ID."
    
    if not validate_student(db,student_id):
        return "Student record not found"
    
    msg=message.lower()
    time_scope=detect_time_intent(msg)

    #---- Fetch Attendance Data ----
    if "attendance" in msg or "attend" or "present" or "absent" in msg:
        query=db.query(Attendance).filter(Attendance.id==student_id)
        query=_apply_time_filter(query,time_scope)
        records=query.all()

        if not records:
            return "No attendance records found for the specified period."
        
        present_days=sum(
            1 for r in records if r.status.lower()=="present" or "p" in r.status.lower()
        )

        return(
            f"Attendance Summary:\n"
            f"Total days recorded: {len(records)}\n"
            f"Days present: {present_days}\n"
            f"Days absent: {len(records)-present_days}"
        )

#---- Fetch Academic Data ----
if any(word in msg for word in ["mark","score","result","grade","exam","test","subject"]):
    records=db.query(Academics).filter(Academics.id==student_id).all()
    records=query.all()

    if not records:
        return "No academic records found."

    lines=["Academic Records:"]
    for r in records:
        lines.append(f"{r.subject}: {r.score}")

        return "\n".join(lines)

    return "I can assist only with academic or attendance information."
