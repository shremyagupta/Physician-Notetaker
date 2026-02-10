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
        temperature: float = 0.3
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
        return f"""You are a medical documentation expert. Convert the following physician-patient conversation into a structured SOAP note.

SOAP stands for:
- Subjective: Patient's reported symptoms and history
- Objective: Observable findings, physical exam results
- Assessment: Diagnosis and clinical assessment
- Plan: Treatment plan and follow-up

Transcript:
{transcript}

Return a JSON object with this exact structure:
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
}}

If information is not available in the transcript, use "Not documented" for that field."""

