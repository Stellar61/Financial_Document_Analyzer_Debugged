from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from celery.result import AsyncResult
import os
import uuid
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Import Celery task
from tasks import analyze_document_task
from celery_worker import celery_app

app = FastAPI(title="Financial Document Analyzer")

# -------------------------------
# DATABASE CONFIGURATION (SQLite)
# -------------------------------

DATABASE_URL = "sqlite:///./analysis_results.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(String, primary_key=True, index=True)
    file_name = Column(String)
    query = Column(Text)
    result = Column(Text)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

# -------------------------------
# ROOT
# -------------------------------

@app.get("/")
async def root():
    return {"message": "Financial Document Analyzer API is running with Celery + Redis + DB"}

# -------------------------------
# ANALYZE ENDPOINT (ASYNC)
# -------------------------------

@app.post("/analyze")
async def analyze_financial_document(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):

    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"

    os.makedirs("data", exist_ok=True)

    # Save file
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Send task to Celery
    task = analyze_document_task.delay(query, file_path, file.filename)

    # Save initial DB record
    db = SessionLocal()
    db_record = AnalysisResult(
        id=task.id,
        file_name=file.filename,
        query=query,
        result="PENDING",
        status="PENDING"
    )
    db.add(db_record)
    db.commit()
    db.close()

    return {
        "status": "submitted",
        "task_id": task.id,
        "message": "Analysis started in background"
    }

# -------------------------------
# TASK STATUS ENDPOINT
# -------------------------------

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):

    task_result = AsyncResult(task_id, app=celery_app)

    db = SessionLocal()
    record = db.query(AnalysisResult).filter(AnalysisResult.id == task_id).first()

    if not record:
        db.close()
        raise HTTPException(status_code=404, detail="Task not found")

    if task_result.state == "SUCCESS":
        record.status = "SUCCESS"
        record.result = json.dumps(task_result.result)
        db.commit()

    db.close()

    return {
        "task_id": task_id,
        "status": task_result.state,
        "result": task_result.result if task_result.state == "SUCCESS" else None
    }

# -------------------------------
# GET ALL ANALYSIS HISTORY
# -------------------------------

@app.get("/history")
async def get_history():

    db = SessionLocal()
    records = db.query(AnalysisResult).all()
    db.close()

    return [
        {
            "task_id": r.id,
            "file_name": r.file_name,
            "query": r.query,
            "status": r.status,
            "created_at": r.created_at
        }
        for r in records
    ]