import os
import json
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Sahayika backend running"}

@app.get("/api/slots")
def get_slots():
    # Sample fallback slots for testing
    return [
        {
            "id": "1",
            "title": "4 Roti + Seasonal Sabzi",
            "category": "tiffin",
            "price": 40,
            "slot_time": "12:30 PM - 1:30 PM",
            "profiles": {"name": "Mita Das", "zone": "Kalyani B-Block", "upi_id": "test@upi"}
        },
        {
            "id": "2",
            "title": "Kurti & Blouse Alteration",
            "category": "tailoring",
            "price": 50,
            "slot_time": "3:00 PM - 5:00 PM",
            "profiles": {"name": "Anjali Roy", "zone": "Ghoshpara, Kalyani", "upi_id": "test@upi"}
        }
    ]