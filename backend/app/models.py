from sqlalchemy import Column, Integer, String, ForeignKey, Date
from .database import Base

class Master(Base):
    __tablename__ = "master"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)


class Academics(Base):
    __tablename__ = "academics"
    id = Column(Integer, ForeignKey("master.id"))
    subject = Column(String)
    score = Column(Integer)


class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, ForeignKey("master.id"))
    date = Column(Date)
    status = Column(String)  # Present / Absent
