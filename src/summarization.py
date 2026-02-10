"""
Medical Text Summarization Module
Converts transcripts into structured medical reports
"""

from typing import Dict, Any, Optional
from .gemini_client import GeminiClient


class MedicalSummarizer:
    """Medical text summarization using Gemini API"""
    
    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        """
        Initialize Medical Summarizer
        
        Args:
            gemini_client: GeminiClient instance. If None, creates a new one.
        """
        self.client = gemini_client or GeminiClient()
    
    def summarize(self, transcript: str) -> Dict[str, Any]:
        """
        Summarize medical transcript into structured report
        
        Args:
            transcript: Raw physician-patient conversation transcript
        
        Returns:
            Structured medical summary in JSON format
        """
        prompt = self.client.get_summarization_prompt(transcript)
        
        # Request structured summary
        enhanced_prompt = f"""{prompt}

Return a JSON object with this structure:
{{
  "Patient_Demographics": {{
    "Name": "string or null",
    "Age": "string or null",
    "Gender": "string or null"
  }},
  "Chief_Complaint": "string",
  "History_of_Present_Illness": "string",
  "Symptoms": {{
    "Primary": ["symptom1", "symptom2"],
    "Secondary": ["symptom1", "symptom2"],
    "Timeline": "string description"
  }},
  "Previous_Treatments": ["treatment1", "treatment2"],
  "Current_Status": "string",
  "Medical_Findings": "string",
  "Clinical_Notes": "string"
}}"""
        
        result = self.client.generate_json(enhanced_prompt, temperature=0.3)
        return self._validate_summary(result)
    
    def _validate_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and structure summary result"""
        validated = {
            "Patient_Demographics": {
                "Name": result.get("Patient_Demographics", {}).get("Name") if isinstance(result.get("Patient_Demographics"), dict) else None,
                "Age": result.get("Patient_Demographics", {}).get("Age") if isinstance(result.get("Patient_Demographics"), dict) else None,
                "Gender": result.get("Patient_Demographics", {}).get("Gender") if isinstance(result.get("Patient_Demographics"), dict) else None,
            },
            "Chief_Complaint": result.get("Chief_Complaint") or "Not specified",
            "History_of_Present_Illness": result.get("History_of_Present_Illness") or "Not documented",
            "Symptoms": {
                "Primary": self._ensure_list(result.get("Symptoms", {}).get("Primary") if isinstance(result.get("Symptoms"), dict) else []),
                "Secondary": self._ensure_list(result.get("Symptoms", {}).get("Secondary") if isinstance(result.get("Symptoms"), dict) else []),
                "Timeline": result.get("Symptoms", {}).get("Timeline") if isinstance(result.get("Symptoms"), dict) else "Not specified"
            },
            "Previous_Treatments": self._ensure_list(result.get("Previous_Treatments", [])),
            "Current_Status": result.get("Current_Status") or "Not specified",
            "Medical_Findings": result.get("Medical_Findings") or "Not documented",
            "Clinical_Notes": result.get("Clinical_Notes") or "Not documented"
        }
        return validated
    
    def _ensure_list(self, value: Any) -> list:
        """Ensure value is a list of strings"""
        if isinstance(value, list):
            return [str(item).strip() for item in value if item]
        elif isinstance(value, str):
            return [value.strip()] if value.strip() else []
        else:
            return []
    
    def generate_executive_summary(self, transcript: str, max_length: int = 200) -> str:
        """
        Generate a concise executive summary of the medical encounter
        
        Args:
            transcript: Raw transcript
            max_length: Maximum length of summary in characters
        
        Returns:
            Concise text summary
        """
        prompt = f"""Summarize the following medical conversation in {max_length} characters or less. 
        Focus on the key medical issue, diagnosis, and outcome.

        Transcript:
        {transcript}

        Provide a concise summary:"""
        
        summary = self.client.generate_text(prompt, temperature=0.4)
        return summary.strip()[:max_length]

