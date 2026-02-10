"""
SOAP Note Generation Module
Converts medical transcripts into structured SOAP notes
"""

from typing import Dict, Any, Optional
from .gemini_client import GeminiClient


class SOAPGenerator:
    """SOAP note generation from medical transcripts"""
    
    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        """
        Initialize SOAP Generator
        
        Args:
            gemini_client: GeminiClient instance. If None, creates a new one.
        """
        self.client = gemini_client or GeminiClient()
    
    def generate_soap_note(self, transcript: str) -> Dict[str, Any]:
        """
        Generate SOAP note from transcript
        
        Args:
            transcript: Raw physician-patient conversation transcript
        
        Returns:
            Structured SOAP note in JSON format
        """
        prompt = self.client.get_soap_prompt(transcript)
        result = self.client.generate_json(prompt, temperature=0.2)
        
        return self._validate_soap_result(result)
    
    def _validate_soap_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and structure SOAP note result"""
        validated = {
            "Subjective": {
                "Chief_Complaint": result.get("Subjective", {}).get("Chief_Complaint", "Not documented") if isinstance(result.get("Subjective"), dict) else "Not documented",
                "History_of_Present_Illness": result.get("Subjective", {}).get("History_of_Present_Illness", "Not documented") if isinstance(result.get("Subjective"), dict) else "Not documented"
            },
            "Objective": {
                "Physical_Exam": result.get("Objective", {}).get("Physical_Exam", "Not documented") if isinstance(result.get("Objective"), dict) else "Not documented",
                "Observations": result.get("Objective", {}).get("Observations", "Not documented") if isinstance(result.get("Objective"), dict) else "Not documented"
            },
            "Assessment": {
                "Diagnosis": result.get("Assessment", {}).get("Diagnosis", "Not documented") if isinstance(result.get("Assessment"), dict) else "Not documented",
                "Severity": result.get("Assessment", {}).get("Severity", "Not documented") if isinstance(result.get("Assessment"), dict) else "Not documented"
            },
            "Plan": {
                "Treatment": result.get("Plan", {}).get("Treatment", "Not documented") if isinstance(result.get("Plan"), dict) else "Not documented",
                "Follow-Up": result.get("Plan", {}).get("Follow-Up", "Not documented") if isinstance(result.get("Plan"), dict) else "Not documented"
            }
        }
        return validated
    
    def format_soap_note(self, soap_note: Dict[str, Any], format_type: str = "json") -> str:
        """
        Format SOAP note for display
        
        Args:
            soap_note: SOAP note dictionary
            format_type: "json", "text", or "markdown"
        
        Returns:
            Formatted SOAP note string
        """
        if format_type == "json":
            import json
            return json.dumps(soap_note, indent=2)
        
        elif format_type == "text":
            text = "SOAP NOTE\n"
            text += "=" * 50 + "\n\n"
            
            text += "SUBJECTIVE:\n"
            text += f"  Chief Complaint: {soap_note['Subjective']['Chief_Complaint']}\n"
            text += f"  History of Present Illness: {soap_note['Subjective']['History_of_Present_Illness']}\n\n"
            
            text += "OBJECTIVE:\n"
            text += f"  Physical Exam: {soap_note['Objective']['Physical_Exam']}\n"
            text += f"  Observations: {soap_note['Objective']['Observations']}\n\n"
            
            text += "ASSESSMENT:\n"
            text += f"  Diagnosis: {soap_note['Assessment']['Diagnosis']}\n"
            text += f"  Severity: {soap_note['Assessment']['Severity']}\n\n"
            
            text += "PLAN:\n"
            text += f"  Treatment: {soap_note['Plan']['Treatment']}\n"
            text += f"  Follow-Up: {soap_note['Plan']['Follow-Up']}\n"
            
            return text
        
        elif format_type == "markdown":
            md = "# SOAP Note\n\n"
            md += "## Subjective\n\n"
            md += f"**Chief Complaint:** {soap_note['Subjective']['Chief_Complaint']}\n\n"
            md += f"**History of Present Illness:** {soap_note['Subjective']['History_of_Present_Illness']}\n\n"
            md += "## Objective\n\n"
            md += f"**Physical Exam:** {soap_note['Objective']['Physical_Exam']}\n\n"
            md += f"**Observations:** {soap_note['Objective']['Observations']}\n\n"
            md += "## Assessment\n\n"
            md += f"**Diagnosis:** {soap_note['Assessment']['Diagnosis']}\n\n"
            md += f"**Severity:** {soap_note['Assessment']['Severity']}\n\n"
            md += "## Plan\n\n"
            md += f"**Treatment:** {soap_note['Plan']['Treatment']}\n\n"
            md += f"**Follow-Up:** {soap_note['Plan']['Follow-Up']}\n"
            
            return md
        
        else:
            raise ValueError(f"Unknown format type: {format_type}")

