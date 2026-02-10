"""
Medical Named Entity Recognition (NER) Module
Extracts Symptoms, Treatment, Diagnosis, Prognosis from medical transcripts
"""

import re
from typing import Dict, Any, List, Optional
from .gemini_client import GeminiClient


class MedicalNER:
    """Medical NER extraction using Gemini API"""
    
    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        """
        Initialize Medical NER
        
        Args:
            gemini_client: GeminiClient instance. If None, creates a new one.
        """
        self.client = gemini_client or GeminiClient()
    
    def extract_entities(self, transcript: str) -> Dict[str, Any]:
        """
        Extract medical entities from transcript
        
        Args:
            transcript: Raw physician-patient conversation transcript
        
        Returns:
            Dictionary with extracted medical entities
        """
        prompt = self.client.get_medical_ner_prompt(transcript)
        result = self.client.generate_json(prompt, temperature=0.2)
        
        # Validate and clean the result
        return self._validate_result(result)
    
    def _validate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean NER extraction result"""
        validated = {
            "Patient_Name": result.get("Patient_Name") or None,
            "Symptoms": self._ensure_list(result.get("Symptoms", [])),
            "Diagnosis": result.get("Diagnosis") or None,
            "Treatment": self._ensure_list(result.get("Treatment", [])),
            "Current_Status": result.get("Current_Status") or "Not specified",
            "Prognosis": result.get("Prognosis") or None
        }
        return validated
    
    def _ensure_list(self, value: Any) -> List[str]:
        """Ensure value is a list of strings"""
        if isinstance(value, list):
            return [str(item).strip() for item in value if item]
        elif isinstance(value, str):
            return [value.strip()] if value.strip() else []
        else:
            return []
    
    def extract_keywords(self, transcript: str, top_n: int = 10) -> List[str]:
        """
        Extract important medical keywords/phrases from transcript
        
        Args:
            transcript: Raw transcript
            top_n: Number of top keywords to return
        
        Returns:
            List of important medical keywords/phrases
        """
        # Medical keyword patterns
        medical_patterns = [
            r'\b(whiplash|injury|pain|ache|discomfort|stiffness)\b',
            r'\b(physiotherapy|therapy|treatment|medication|painkiller)\b',
            r'\b(diagnosis|condition|symptom|sign)\b',
            r'\b(recovery|prognosis|healing|improvement)\b',
            r'\b(accident|trauma|impact|collision)\b',
            r'\b(range of motion|mobility|movement|tenderness)\b',
            r'\b(follow-up|appointment|examination|check-up)\b',
        ]
        
        keywords = set()
        transcript_lower = transcript.lower()
        
        for pattern in medical_patterns:
            matches = re.findall(pattern, transcript_lower, re.IGNORECASE)
            keywords.update(matches)
        
        # Also extract multi-word medical phrases using Gemini
        keyword_prompt = f"""Extract the {top_n} most important medical keywords or phrases from this medical transcript. 
        Focus on medical terms, symptoms, treatments, and clinical findings.

        Transcript:
        {transcript}

        Return a JSON array of strings:
        ["keyword1", "keyword2", ...]"""
        
        try:
            gemini_keywords = self.client.generate_json(keyword_prompt, temperature=0.3)
            if isinstance(gemini_keywords, list):
                keywords.update([str(kw).strip() for kw in gemini_keywords])
            elif isinstance(gemini_keywords, dict) and "keywords" in gemini_keywords:
                keywords.update([str(kw).strip() for kw in gemini_keywords["keywords"]])
        except Exception:
            # Fallback to pattern-based extraction if Gemini fails
            pass
        
        return list(keywords)[:top_n]
    
    def extract_structured_summary(self, transcript: str) -> Dict[str, Any]:
        """
        Extract structured medical summary (combines NER + summarization)
        
        Args:
            transcript: Raw transcript
        
        Returns:
            Complete structured summary with all medical details
        """
        # Get NER entities
        entities = self.extract_entities(transcript)
        
        # Get keywords
        keywords = self.extract_keywords(transcript)
        
        # Combine into structured summary
        summary = {
            **entities,
            "Keywords": keywords
        }
        
        return summary

