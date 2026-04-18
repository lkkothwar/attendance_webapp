from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import date
from typing import List, Optional

# --- 1. Database Configuration (Neon.tech / Supabase) ---
DATABASE_URL = "postgresql://neondb_owner:npg_w5n7SxXNgiHo@ep-mute-thunder-anmbcppr.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 2. Database Model ---
class Attendance(Base):
    __tablename__ = "attendance_records"
    id = Column(Integer, primary_key=True, index=True)
    year = Column(String)         # FY, SY, TY
    student_name = Column(String)
    course_code = Column(String)
    course_abbr = Column(String)
    type = Column(String)         # TH or PR
    batch = Column(String, nullable=True) # A, B, C
    status = Column(String)       # P or A
    date = Column(Date, default=date.today)

Base.metadata.create_all(bind=engine)

# --- 3. FastAPI App Setup ---
app = FastAPI(title="EJ Attendance API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas
class AttendanceEntry(BaseModel):
    student_name: str
    status: str

class MarkAttendanceRequest(BaseModel):
    year: str
    course_code: str
    course_abbr: str
    type: str
    batch: Optional[str] = None
    students: List[AttendanceEntry]

# --- 4. API Endpoints ---

@app.post("/submit-attendance")
def submit_attendance(req: MarkAttendanceRequest):
    db = SessionLocal()
    try:
        new_records = [
            Attendance(
                year=req.year,
                course_code=req.course_code,
                course_abbr=req.course_abbr,
                type=req.type,
                batch=req.batch,
                student_name=s.student_name,
                status=s.status
            ) for s in req.students
        ]
        db.add_all(new_records)
        db.commit()
        return {"message": "Attendance saved successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/report/{year}/{course_code}")
def get_report(year: str, course_code: str):
    db = SessionLocal()
    records = db.query(Attendance).filter(
        Attendance.year == year, 
        Attendance.course_code == course_code
    ).all()
    db.close()
    return records
