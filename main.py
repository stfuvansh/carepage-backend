from fastapi import FastAPI, UploadFile, File, Form, Depends, Query
from fastapi.middleware.cors import CORSMiddleware

import os
import cloudinary
import cloudinary.uploader

from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import text

from database import (
    SessionLocal,
    Prescription,
    get_db,
    Base,
    engine
)


# -----------------------------
# Create database tables
# -----------------------------

Base.metadata.create_all(bind=engine)


# -----------------------------
# Cloudinary Configuration
# -----------------------------

cloudinary.config(
    cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
    api_key=os.environ["CLOUDINARY_API_KEY"],
    api_secret=os.environ["CLOUDINARY_API_SECRET"]
)


# -----------------------------
# FastAPI App
# -----------------------------

app = FastAPI(
    title="CarePage API",
    description="Prescription management backend",
    version="1.0.0"
)


# -----------------------------
# CORS Configuration
# -----------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Home Route
# -----------------------------

@app.get("/")
def home():
    return {
        "message": "CarePage backend is running"
    }


# -----------------------------
# Database Test
# -----------------------------

@app.get("/test-db")
def test_db():

    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))

    finally:
        db.close()

    return {
        "message": "Database connection successful"
    }


# -----------------------------
# Get Prescriptions
# -----------------------------

@app.get("/prescriptions")
def get_prescriptions(
    db: Session = Depends(get_db)
):

    prescriptions = db.query(Prescription).all()

    return prescriptions


# -----------------------------
# Search Prescriptions
# -----------------------------

@app.get("/search-prescriptions")
def search_prescriptions(
    name: str = Query(None),
    date: str = Query(None),
    db: Session = Depends(get_db)
):

    query = db.query(Prescription)

    if name:
        query = query.filter(
            Prescription.patient_name.ilike(f"%{name}%")
        )

    if date:
        query = query.filter(
            Prescription.date == date
        )

    return query.all()


# -----------------------------
# Save Prescription
# -----------------------------

@app.post("/save-prescription")
def save_prescription(
    patient_name: str = Form(...),
    date: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    safe_name = (
        patient_name
        .lower()
        .replace(" ", "_")
    )

    clean_date = date.replace("-", "")

    current_time = datetime.now().strftime(
        "%H%M%S"
    )

    filename = (
        f"{safe_name}_"
        f"{clean_date}_"
        f"{current_time}"
    )


    # Upload image to Cloudinary

    upload_result = cloudinary.uploader.upload(
        file.file,
        folder="carepage_prescriptions",
        public_id=filename
    )


    image_url = upload_result["secure_url"]


    # Save database entry

    new_prescription = Prescription(
        patient_name=patient_name,
        date=date,
        image_path=image_url
    )


    db.add(new_prescription)

    db.commit()

    db.refresh(new_prescription)


    return {
        "message": "Prescription saved successfully",
        "file_path": image_url
    }