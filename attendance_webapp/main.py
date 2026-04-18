from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from datetime import date
from typing import List, Optional

# 1. DATABASE CONFIGURATION
# Replace the URL below with your Neon.tech connection string
DATABASE_URL = "postgresql://neondb_owner:npg_w5n7SxXNgiHo@ep-mute-thunder-anmbcppr.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. DATABASE MODELS
class AttendanceRecord(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String, index=True)
    course_code = Column(String, index=True)
    status = Column(String) # 'P' or 'A'
    type = Column(String)   # 'TH' or 'PR'
    batch = Column(String, nullable=True)
    date = Column(Date, default=date.today)

Base.metadata.create_all(bind=engine)

# 3. FASTAPI SETUP
app = FastAPI()

# Enable CORS so your frontend can talk to your backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic schema for data validation
class AttendanceCreate(BaseModel):
    student_name: str
    course_code: str
    status: str
    type: str
    batch: Optional[str] = None

@app.post("/attendance/")
def mark_attendance(records: List[AttendanceCreate]):
    db = SessionLocal()
    try:
        for item in records:
            db_record = AttendanceRecord(**item.dict())
            db.add(db_record)
        db.commit()
        return {"status": "success", "message": f"{len(records)} records saved"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/report/{course_code}")
def get_report(course_code: str):
    db = SessionLocal()
    results = db.query(AttendanceRecord).filter(AttendanceRecord.course_code == course_code).all()
    db.close()
    return results