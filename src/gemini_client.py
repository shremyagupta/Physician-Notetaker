"""
Gemini API Client Wrapper for Medical NLP Tasks
Handles API key management, prompt templates, and error handling
"""

import os
import json
import time
from typing import Dict, Any, Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold


class GeminiClient:
    """Wrapper class for Google Gemini 2.5 Flash API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client
        
        Args:
            api_key: Google Gemini API key. If None, reads from GEMINI_API_KEY env var
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. Please set GEMINI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        genai.configure(api_key=self.api_key)
        # Use gemini-2.5-flash as originally requested (user specified gemini-2.5-flash)
        # This is the latest stable flash model available
        try:
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        except Exception:
            # Fallback to gemini-2.0-flash-exp if 2.5 not available
            try:
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            except Exception:
                # Final fallback to gemini-2.0-flash
                self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Configure safety settings for medical content
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
    
    def generate_text(
        self,
        prompt: str,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        temperature: float = 0.3 #for acurate medical extraction, lower temperature is better to reduce hallucinations
    ) -> str:
        """
        Generate text using Gemini API with retry logic
        
        Args:
            prompt: Input prompt for the model
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            temperature: Sampling temperature (0.0-1.0)
        
        Returns:
            Generated text response
        """
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    safety_settings=self.safety_settings,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=8192,
                    )
                )
                return response.text
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise Exception(f"Failed to generate text after {max_retries} attempts: {str(e)}")
    
    def generate_json(
        self,
        prompt: str,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """
        Generate JSON response using Gemini API
        
        Args:
            prompt: Input prompt with JSON format instructions
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            temperature: Sampling temperature (lower for more deterministic JSON)
        
        Returns:
            Parsed JSON dictionary
        """
        json_prompt = f"{prompt}\n\nIMPORTANT: Respond ONLY with valid JSON. Do not include any markdown formatting, code blocks, or explanatory text."
        
        for attempt in range(max_retries):
            try:
                response_text = self.generate_text(json_prompt, max_retries=1, temperature=temperature)
                
                # Clean response - remove markdown code blocks if present
                response_text = response_text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                elif response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise Exception(f"Failed to parse JSON response after {max_retries} attempts: {str(e)}")
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise
    
    def get_medical_ner_prompt(self, transcript: str) -> str:
        """Generate prompt for medical NER extraction"""
        return f"""You are a medical NLP expert. Extract medical entities from the following physician-patient conversation transcript.

Extract the following information:
1. Patient Name (if mentioned)
2. Symptoms (list all symptoms mentioned)
3. Diagnosis (medical diagnosis if stated)
4. Treatment (treatments, medications, procedures mentioned)
5. Prognosis (expected outcome or recovery timeline)
6. Current Status (patient's current condition)

Transcript:
{transcript}

Return a JSON object with the following structure:
{{
  "Patient_Name": "string or null",
  "Symptoms": ["symptom1", "symptom2"],
  "Diagnosis": "string or null",
  "Treatment": ["treatment1", "treatment2"],
  "Current_Status": "string",
  "Prognosis": "string or null"
}}

If information is not available or ambiguous, use null for strings or empty arrays for lists."""

    def get_summarization_prompt(self, transcript: str) -> str:
        """Generate prompt for medical text summarization"""
        return f"""You are a medical transcription expert. Summarize the following physician-patient conversation into a structured medical report.

Transcript:
{transcript}

Create a comprehensive summary that includes:
- Patient demographics (if mentioned)
- Chief complaint
- History of present illness
- Key symptoms and timeline
- Previous treatments
- Current status
- Medical findings

Return a JSON object with structured medical information."""

    def get_sentiment_prompt(self, patient_text: str) -> str:
        """Generate prompt for sentiment and intent analysis"""
        return f"""You are analyzing patient sentiment and intent from medical dialogue. Analyze the following patient statement:

Patient Statement: "{patient_text}"

Classify:
1. Sentiment: One of "Anxious", "Neutral", or "Reassured"
2. Intent: One of "Seeking reassurance", "Reporting symptoms", "Expressing concern", or "Other"

Return a JSON object:
{{
  "Sentiment": "Anxious|Neutral|Reassured",
  "Intent": "Seeking reassurance|Reporting symptoms|Expressing concern|Other"
}}"""

    def get_soap_prompt(self, transcript: str) -> str:
        """Generate prompt for SOAP note generation"""
        return f"""You are a careful medical documentation assistant.
Convert the following physician–patient conversation into a **detailed** structured SOAP note.

SOAP sections:
- Subjective: Patient's own words, complaints, symptom description, onset, duration, aggravating/relieving factors, relevant history.
- Objective: Clinician's observations and exam findings that would reasonably accompany this presentation (vital signs, focused physical exam, notable negatives/positives).
- Assessment: Most likely working diagnosis (or differential if appropriate) and a brief clinical reasoning summary including severity.
- Plan: Concrete treatment plan and follow‑up instructions.

VERY IMPORTANT REQUIREMENTS:
- Use clear, complete sentences in every field (2–5 sentences each, not just short phrases).
- In the Plan section, explicitly describe medicines and non‑drug advice the doctor might reasonably consider based on the transcript.
- For any medicine you mention, include: name (generic if possible), typical adult dose, route, frequency, and duration in days, plus any key cautions.
- If something is not explicitly stated in the transcript but is standard to infer (e.g., basic exam findings), you may state it as a reasonable clinical assumption.
- If you truly cannot infer something, explain that briefly instead of just writing "Not documented".

Transcript:
{transcript}

Return ONLY a JSON object with this exact structure (no extra keys):
{{
    "Subjective": {{
        "Chief_Complaint": "string",
        "History_of_Present_Illness": "string"
    }},
    "Objective": {{
        "Physical_Exam": "string",
        "Observations": "string"
    }},
    "Assessment": {{
        "Diagnosis": "string",
        "Severity": "string"
    }},
    "Plan": {{
        "Treatment": "string",
        "Follow-Up": "string"
    }}
}}"""

    def get_medicine_suggestion_prompt(self, transcript: str) -> str:
        """Generate prompt for AI medicine suggestion"""
        return f"""You are an advanced AI medical assistant analyzing a doctor–patient conversation.
    Based on the patient's reported symptoms and the context of the conversation so far, suggest a **clear, concrete treatment plan** that a licensed clinician could consider.

    Transcript:
    {transcript}

    Your response MUST be plain text (no bullets or markdown) and should include:
    - 2–3 possible diagnoses or explanations, in plain language.
    - A proposed medicine plan (if appropriate) with for each medicine: name, typical adult dose, route, frequency, and duration in days (for example: "paracetamol 500 mg orally every 6 hours as needed for pain, for up to 5 days").
    - Any important cautions, red‑flag symptoms, or when the patient should seek urgent in‑person care.
    - A brief summary of non‑medication advice (rest, hydration, lifestyle measures).

    This is educational content only and does not replace real medical care."""

        def get_diet_exercise_plan_prompt(self, transcript: str) -> str:
                """Generate JSON prompt for AI diet and exercise plan suggestion.

                The model must decide whether the case appears critical/emergent
                based on symptoms (e.g. chest pain, severe shortness of breath,
                stroke signs, uncontrolled bleeding, severe abdominal pain, etc.).
                """
                return f"""You are an experienced clinical nutrition and lifestyle medicine assistant.
Analyze the following doctor–patient conversation and design a safe, practical
diet and exercise plan that could support the patient's recovery and overall
health, based primarily on the reported symptoms.

Transcript:
{transcript}

VERY IMPORTANT:
- First, judge whether this case appears to require urgent in‑person
    medical assessment or emergency care based on red‑flag symptoms
    (for example: chest pain, trouble breathing, signs of stroke,
    severe trauma, uncontrolled bleeding, very high fever with confusion,
    severe abdominal pain, pregnancy emergencies, etc.).
- If such red‑flag patterns are present, mark the case as emergency.

Return ONLY a single JSON object with exactly these fields:
{{
    "plan_text": "Full diet and exercise plan as one plain‑text string with no markdown.",
    "risk_level": "Low" | "Medium" | "High" | "Emergency",
    "is_emergency": true or false
}}

Guidance for the plan_text field:
- Briefly summarise the main health concerns and symptoms in simple language.
- Give specific diet recommendations (what to increase, what to reduce or
    avoid) with clear examples of meals or foods for breakfast, lunch, dinner,
    and snacks.
- Include hydration advice (how much and what kind of fluids).
- Provide a step‑by‑step exercise or physical‑activity plan that is realistic
    for a general adult (frequency per week, duration per session, and
    approximate intensity), including clear cautions for people with pain,
    dizziness, breathlessness, heart disease, or other limitations.
- Add lifestyle tips such as sleep, stress management, posture, and daily
    habits that are relevant to the symptoms.
- Clearly describe any red‑flag warning signs when the patient should stop
    exercise immediately and seek urgent in‑person care.

Do NOT prescribe or adjust medicines. Emphasize near the end that this plan is
educational only and does not replace personalised advice from a licensed
clinician or dietitian."""

    def get_icd10_prompt(self, transcript: str, diagnosis: Optional[str] = None) -> str:
        """Generate prompt for ICD-10 clinical coding"""
        context = f"Diagnosis: {diagnosis}" if diagnosis else "Extract possible diagnoses from the transcript."
        return f"""You are a medical coding expert. Based on the following physician-patient transcript and the identified diagnosis, suggest appropriate ICD-10-CM codes.

Transcript:
{transcript}

{context}

Return a JSON object with this structure:
{{
  "ICD10_Codes": [
    {{
      "code": "CODE123",
      "description": "Description of the code",
      "confidence": "High|Medium|Low"
    }}
  ]
}}

If no specific codes can be identified, return an empty array for ICD10_Codes."""


