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
        """Validate and normalize SOAP note result to a flat structure.

        The frontend expects `SOAP_Note` to contain flat fields like
        "Chief_Complaint", "History_of_Present_Illness", "Physical_Exam",
        etc., so we extract from the nested JSON returned by the model.
        """

        subjective = result.get("Subjective") if isinstance(result.get("Subjective"), dict) else {}
        objective = result.get("Objective") if isinstance(result.get("Objective"), dict) else {}
        assessment = result.get("Assessment") if isinstance(result.get("Assessment"), dict) else {}
        plan = result.get("Plan") if isinstance(result.get("Plan"), dict) else {}

        def _clean(value: Any) -> str:
            if not isinstance(value, str):
                return "Not documented"
            text = value.strip()
            return text if text else "Not documented"

        validated = {
            "Chief_Complaint": _clean(subjective.get("Chief_Complaint")),
            "History_of_Present_Illness": _clean(subjective.get("History_of_Present_Illness")),
            "Physical_Exam": _clean(objective.get("Physical_Exam")),
            "Observations": _clean(objective.get("Observations")),
            "Diagnosis": _clean(assessment.get("Diagnosis")),
            "Severity": _clean(assessment.get("Severity")),
            "Treatment": _clean(plan.get("Treatment")),
            "Follow-Up": _clean(plan.get("Follow-Up")),
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
        # Support both flat (current normalized) and nested structures gracefully
        is_nested = "Subjective" in soap_note and isinstance(soap_note.get("Subjective"), dict)

        def _get(field_path_flat, field_path_nested):
            if not is_nested:
                return soap_note.get(field_path_flat, "Not documented")
            section, key = field_path_nested
            section_dict = soap_note.get(section, {}) or {}
            return section_dict.get(key, "Not documented")

        if format_type == "json":
            import json
            return json.dumps(soap_note, indent=2)

        elif format_type == "text":
            text = "SOAP NOTE\n"
            text += "=" * 50 + "\n\n"

            text += "SUBJECTIVE:\n"
            text += f"  Chief Complaint: {_get('Chief_Complaint', ('Subjective', 'Chief_Complaint'))}\n"
            text += f"  History of Present Illness: {_get('History_of_Present_Illness', ('Subjective', 'History_of_Present_Illness'))}\n\n"

            text += "OBJECTIVE:\n"
            text += f"  Physical Exam: {_get('Physical_Exam', ('Objective', 'Physical_Exam'))}\n"
            text += f"  Observations: {_get('Observations', ('Objective', 'Observations'))}\n\n"

            text += "ASSESSMENT:\n"
            text += f"  Diagnosis: {_get('Diagnosis', ('Assessment', 'Diagnosis'))}\n"
            text += f"  Severity: {_get('Severity', ('Assessment', 'Severity'))}\n\n"

            text += "PLAN:\n"
            text += f"  Treatment: {_get('Treatment', ('Plan', 'Treatment'))}\n"
            text += f"  Follow-Up: {_get('Follow-Up', ('Plan', 'Follow-Up'))}\n"
            
            return text
        
        elif format_type == "markdown":
            md = "# SOAP Note\n\n"
            md += "## Subjective\n\n"
            md += f"**Chief Complaint:** {_get('Chief_Complaint', ('Subjective', 'Chief_Complaint'))}\n\n"
            md += f"**History of Present Illness:** {_get('History_of_Present_Illness', ('Subjective', 'History_of_Present_Illness'))}\n\n"
            md += "## Objective\n\n"
            md += f"**Physical Exam:** {_get('Physical_Exam', ('Objective', 'Physical_Exam'))}\n\n"
            md += f"**Observations:** {_get('Observations', ('Objective', 'Observations'))}\n\n"
            md += "## Assessment\n\n"
            md += f"**Diagnosis:** {_get('Diagnosis', ('Assessment', 'Diagnosis'))}\n\n"
            md += f"**Severity:** {_get('Severity', ('Assessment', 'Severity'))}\n\n"
            md += "## Plan\n\n"
            md += f"**Treatment:** {_get('Treatment', ('Plan', 'Treatment'))}\n\n"
            md += f"**Follow-Up:** {_get('Follow-Up', ('Plan', 'Follow-Up'))}\n"
            
            return md
        
        else:
            raise ValueError(f"Unknown format type: {format_type}")

