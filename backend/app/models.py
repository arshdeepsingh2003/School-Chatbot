from sqlalchemy import Column, Integer, String, ForeignKey, Date
from .database import Base

class Master(Base):
    __tablename__ = "master"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)


class Academics(Base):
    __tablename__ = "academics"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("master.id"), nullable=False)

    subject = Column(String, nullable=False)
    score = Column(Integer, nullable=False)


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("master.id"), nullable=False)

    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)  # Present / Absent
