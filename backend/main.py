import os
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = FastAPI()

# Allow frontend requests from Vercel & local test
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("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")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

ACTIVE_SLOTS = [
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

@app.get("/")
def home():
    return {"status": "Sahayika backend running"}

@app.get("/api/slots")
def get_slots():
    return ACTIVE_SLOTS

@app.post("/api/voice-to-slot")
async def voice_to_slot(audio: UploadFile = File(...)):
    if not groq_client:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not configured on Render.")

    try:
        # Read the raw audio bytes directly from upload
        audio_bytes = await audio.read()
        
        # Whisper requires a filename with an audio extension
        filename = audio.filename or "recording.webm"
        if not any(filename.endswith(ext) for ext in [".webm", ".mp4", ".m4a", ".mp3", ".wav"]):
            filename = f"{filename}.webm"

        # 1. Transcribe with Whisper-Large-v3
        transcription = groq_client.audio.transcriptions.create(
            file=(filename, audio_bytes),
            model="whisper-large-v3",
            prompt="Bengali or Hindi household services, cooking tiffin, tailoring clothes, cleaning, meal portion"
        )
        raw_text = transcription.text.strip()

        # 2. Extract structured JSON using Llama-3.3
        extraction_prompt = f"""
        Extract the micro-job slot details from this speech transcription: "{raw_text}"
        Return ONLY valid JSON matching this schema:
        {{
          "title": "English short description (max 5 words)",
          "category": "tiffin | tailoring | prep | cleaning",
          "price": 40,
          "slot_time": "approximate time or Today"
        }}
        Do not include markdown tags, code blocks, or explanatory text.
        """

        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": extraction_prompt}],
            temperature=0.1
        )

        response_content = completion.choices[0].message.content.strip()
        cleaned_json = response_content.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(cleaned_json)

        new_slot = {
            "id": str(len(ACTIVE_SLOTS) + 1),
            "title": parsed.get("title", "Fresh Home Service"),
            "category": parsed.get("category", "tiffin"),
            "price": int(parsed.get("price", 40)),
            "slot_time": parsed.get("slot_time", "Today Afternoon"),
            "profiles": {
                "name": "Local Homemaker",
                "zone": "Kalyani A-Block",
                "upi_id": "homemaker@upi"
            }
        }

        # Add new slot to top of the list
        ACTIVE_SLOTS.insert(0, new_slot)

        return {
            "status": "success",
            "transcript": raw_text,
            "slot": new_slot
        }

    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
