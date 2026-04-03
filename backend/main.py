from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
from pathlib import Path
import os
import random
import csv
import json
from dotenv import load_dotenv

# Add project root to path so we can import src module
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
load_dotenv(dotenv_path=project_root / '.env')

try:
    from src.pipeline import PhysicianNotetakerPipeline
except ImportError as e:
    print(f"Error importing pipeline: {e}")
    sys.exit(1)

app = FastAPI(title="Physician Notetaker API", description="API for NLP-based Medical Summarization")

# Configure CORS for the React frontend (running typically on port 5173 or 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the NLP pipeline once
try:
    pipeline = PhysicianNotetakerPipeline()
except Exception as e:
    print(f"Failed to initialize NLP model. Is GEMINI_API_KEY set? Error: {e}")
    pipeline = None

class TranscriptRequest(BaseModel):
    transcript: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Physician Notetaker API is running."}

@app.post("/api/generate-notes")
async def generate_notes(request: TranscriptRequest):
    if pipeline is None:
        raise HTTPException(status_code=500, detail="NLP model initialization failed on the server. Check server logs.")
    
    if not request.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty.")
    
    try:
        results = pipeline.process_transcript(request.transcript, include_soap=True)
        formatted_text = pipeline.export_results(results, format_type='text')
        
        return {
            "status": "success",
            "results": results,
            "formatted_text": formatted_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating notes: {str(e)}")

@app.post("/api/suggest-medicine")
async def suggest_medicine(request: TranscriptRequest):
    if pipeline is None:
        raise HTTPException(status_code=500, detail="NLP model initialization failed on the server.")
    
    if not request.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty.")
        
    try:
        suggestion = pipeline.suggest_medicine(request.transcript)
        return {
            "status": "success",
            "suggestion": suggestion
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating suggestion: {str(e)}")

@app.post("/api/diet-exercise-plan")
async def diet_exercise_plan(request: TranscriptRequest):
    """Generate a diet and exercise plan using the NLP pipeline"""
    if pipeline is None:
        raise HTTPException(status_code=500, detail="NLP model initialization failed on the server.")

    if not request.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty.")

    # Let the pipeline handle Gemini errors and return a structured result
    result = pipeline.suggest_diet_exercise_plan(request.transcript)

    return {
        "status": "success",
        "suggestion": result.get("plan_text", ""),
        "emergency": bool(result.get("is_emergency", False)),
        "risk_level": result.get("risk_level", "Unknown"),
    }

@app.get("/api/sample-conversation")
async def get_sample_conversation():
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    jsonl_path = os.path.join(data_dir, "doctor_patient_conversations_3000.jsonl")
    csv_path = os.path.join(data_dir, "doctor_patient_conversations_3000.csv")
    
    # Try JSONL first as it is more structured
    if os.path.exists(jsonl_path):
        try:
            with open(jsonl_path, mode='r', encoding='utf-8') as f:
                lines = f.readlines()
                if not lines:
                    raise ValueError("JSONL dataset is empty")

                line = random.choice(lines)
                sample = json.loads(line)

                # Format conversation list into text
                conv_text = ""
                for msg in sample.get("conversation", []):
                    role = msg.get("role", "Unknown").capitalize()
                    message = msg.get("message", "")
                    conv_text += f"{role}: {message}\n"

                return {
                    "conversation_text": conv_text.strip(),
                    "metadata": {
                        "id": sample.get("conversation_id"),
                        "complaint": sample.get("chief_complaint"),
                        "severity": sample.get("severity")
                    }
                }
        except Exception as e:
            print(f"JSONL loading failed: {e}, falling back to CSV")

    # Fallback to CSV
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Dataset not found (Checked both .jsonl and .csv)")
    
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
            if not reader:
                raise HTTPException(status_code=404, detail="Dataset is empty")
            
            sample = random.choice(reader)
            return {
                "conversation_text": sample["conversation_text"],
                "metadata": {
                    "id": sample.get("conversation_id"),
                    "complaint": sample.get("chief_complaint"),
                    "severity": sample.get("severity")
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load sample: {str(e)}")


@app.get("/api/sample-conversation-structured")
async def get_sample_conversation_structured():
    """Return a random conversation with structured doctor/patient turns.

    This is used by the frontend to automatically drive doctor questions
    while the user responds as the patient.
    """
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    jsonl_path = os.path.join(data_dir, "doctor_patient_conversations_3000.jsonl")
    csv_path = os.path.join(data_dir, "doctor_patient_conversations_3000.csv")

    # Prefer structured JSONL file if available
    if os.path.exists(jsonl_path):
        try:
            with open(jsonl_path, mode="r", encoding="utf-8") as f:
                lines = f.readlines()
                if not lines:
                    raise HTTPException(status_code=404, detail="JSONL dataset is empty")

                line = random.choice(lines)
                sample = json.loads(line)
                conversation = sample.get("conversation", [])

                # Normalize roles and extract doctor messages
                normalized_conversation = []
                doctor_questions = []
                for msg in conversation:
                    role = msg.get("role", "unknown").lower()
                    message = msg.get("message", "")
                    normalized_conversation.append({"role": role, "message": message})
                    if role == "doctor":
                        doctor_questions.append(message)

                if not doctor_questions:
                    raise HTTPException(status_code=404, detail="No doctor messages found in sample conversation")

                return {
                    "conversation_id": sample.get("conversation_id"),
                    "doctor_questions": doctor_questions,
                    "conversation": normalized_conversation,
                    "metadata": {
                        "chief_complaint": sample.get("chief_complaint"),
                        "severity": sample.get("severity"),
                        "risk_level": sample.get("risk_level"),
                        "urgency": sample.get("urgency"),
                    },
                }
        except HTTPException:
            # Re-raise known HTTP errors
            raise
        except Exception as e:
            print(f"JSONL structured loading failed: {e}, falling back to CSV")

    # Fallback: derive structure from CSV text transcript
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Dataset not found (Checked both .jsonl and .csv)")

    try:
        with open(csv_path, mode="r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            if not rows:
                raise HTTPException(status_code=404, detail="CSV dataset is empty")

            sample = random.choice(rows)
            raw_text = sample.get("conversation_text", "") or ""
            lines = raw_text.split("\n")

            normalized_conversation = []
            doctor_questions = []
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue

                lower = stripped.lower()
                if lower.startswith("doctor:"):
                    role = "doctor"
                    message = stripped[len("doctor:") :].strip()
                elif lower.startswith("patient:"):
                    role = "patient"
                    message = stripped[len("patient:") :].strip()
                else:
                    # Default to doctor if we cannot infer role
                    role = "doctor"
                    message = stripped

                normalized_conversation.append({"role": role, "message": message})
                if role == "doctor":
                    doctor_questions.append(message)

            if not doctor_questions:
                raise HTTPException(status_code=404, detail="No doctor messages found in CSV sample conversation")

            return {
                "conversation_id": sample.get("conversation_id"),
                "doctor_questions": doctor_questions,
                "conversation": normalized_conversation,
                "metadata": {
                    "chief_complaint": sample.get("chief_complaint"),
                    "severity": sample.get("severity"),
                    "risk_level": sample.get("risk_level"),
                    "urgency": sample.get("urgency"),
                },
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load structured sample: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
