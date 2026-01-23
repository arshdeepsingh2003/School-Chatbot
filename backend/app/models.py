from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text, DateTime
from .database import Base
from datetime import datetime

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

# Chat Memory
class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=True)
    role = Column(String, nullable=False)
    user_message = Column(Text, nullable=False)
    bot_reply = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)