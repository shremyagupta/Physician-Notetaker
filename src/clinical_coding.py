"""
Clinical Coding Module
Handles extraction and suggestion of ICD-10-CM codes from medical transcripts
"""

from typing import Dict, Any, List, Optional
from .gemini_client import GeminiClient

class ICD10Coder:
    """Module for generating ICD-10 codes from transcripts"""
    
    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        """
        Initialize the coder
        
        Args:
            gemini_client: GeminiClient instance. If None, creates a new one.
        """
        self.client = gemini_client or GeminiClient()
        
    def suggest_codes(self, transcript: str, diagnosis: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Suggest ICD-10 codes based on transcript content
        
        Args:
            transcript: Raw clinical transcript
            diagnosis: Pre-extracted diagnosis (optional)
            
        Returns:
            List of ICD-10 code dictionaries
        """
        prompt = self.client.get_icd10_prompt(transcript, diagnosis)
        try:
            results = self.client.generate_json(prompt)
            return results.get("ICD10_Codes", [])
        except Exception as e:
            print(f"Error generating ICD-10 codes: {e}")
            return []
