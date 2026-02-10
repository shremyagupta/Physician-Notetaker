"""
Sentiment and Intent Analysis Module
Analyzes patient sentiment and intent from medical dialogue
"""

import re
from typing import Dict, Any, List, Optional
from .gemini_client import GeminiClient


class SentimentAnalyzer:
    """Sentiment and intent analysis for patient dialogue"""
    
    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        """
        Initialize Sentiment Analyzer
        
        Args:
            gemini_client: GeminiClient instance. If None, creates a new one.
        """
        self.client = gemini_client or GeminiClient()
    
    def analyze_sentiment(self, patient_text: str) -> Dict[str, str]:
        """
        Analyze sentiment and intent from patient dialogue
        
        Args:
            patient_text: Patient's statement or dialogue segment
        
        Returns:
            Dictionary with Sentiment and Intent classifications
        """
        prompt = self.client.get_sentiment_prompt(patient_text)
        result = self.client.generate_json(prompt, temperature=0.2)
        
        return self._validate_sentiment_result(result)
    
    def _validate_sentiment_result(self, result: Dict[str, Any]) -> Dict[str, str]:
        """Validate sentiment analysis result"""
        valid_sentiments = ["Anxious", "Neutral", "Reassured"]
        valid_intents = ["Seeking reassurance", "Reporting symptoms", "Expressing concern", "Other"]
        
        sentiment = result.get("Sentiment", "Neutral")
        intent = result.get("Intent", "Other")
        
        # Validate sentiment
        if sentiment not in valid_sentiments:
            # Try to match similar sentiment
            sentiment_lower = sentiment.lower()
            if "anxious" in sentiment_lower or "worried" in sentiment_lower or "concerned" in sentiment_lower:
                sentiment = "Anxious"
            elif "reassured" in sentiment_lower or "relieved" in sentiment_lower or "better" in sentiment_lower:
                sentiment = "Reassured"
            else:
                sentiment = "Neutral"
        
        # Validate intent
        if intent not in valid_intents:
            intent_lower = intent.lower()
            if "reassurance" in intent_lower:
                intent = "Seeking reassurance"
            elif "symptom" in intent_lower or "reporting" in intent_lower:
                intent = "Reporting symptoms"
            elif "concern" in intent_lower or "worried" in intent_lower:
                intent = "Expressing concern"
            else:
                intent = "Other"
        
        return {
            "Sentiment": sentiment,
            "Intent": intent
        }
    
    def extract_patient_segments(self, transcript: str) -> List[str]:
        """
        Extract patient dialogue segments from transcript
        
        Args:
            transcript: Full conversation transcript
        
        Returns:
            List of patient dialogue segments
        """
        patient_segments = []
        
        # Pattern to match patient statements
        patterns = [
            r'Patient[:\s]+["\']?([^"]+)["\']?',
            r'Patient:\s*(.+?)(?=\n(?:Physician|Doctor|\[))',
            r'\*\*Patient:\*\*\s*(.+?)(?=\n\*\*Physician|\n\*\*Doctor|\Z)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE | re.DOTALL)
            patient_segments.extend([match.strip() for match in matches if match.strip()])
        
        # If no pattern matches, try line-by-line extraction
        if not patient_segments:
            lines = transcript.split('\n')
            for line in lines:
                line_lower = line.lower()
                if 'patient:' in line_lower or 'patient ' in line_lower:
                    # Extract text after "Patient:"
                    parts = re.split(r'patient[:\s]+', line, flags=re.IGNORECASE)
                    if len(parts) > 1:
                        patient_segments.append(parts[1].strip())
        
        return patient_segments
    
    def analyze_full_transcript(self, transcript: str) -> Dict[str, Any]:
        """
        Analyze sentiment and intent for entire transcript
        
        Args:
            transcript: Full conversation transcript
        
        Returns:
            Dictionary with overall sentiment analysis and per-segment analysis
        """
        patient_segments = self.extract_patient_segments(transcript)
        
        if not patient_segments:
            # If we can't extract segments, analyze the whole transcript
            combined_text = " ".join(transcript.split('\n')[:5])  # First few lines
            overall = self.analyze_sentiment(combined_text)
            return {
                "Overall_Sentiment": overall["Sentiment"],
                "Overall_Intent": overall["Intent"],
                "Segments_Analyzed": 0,
                "Segment_Details": []
            }
        
        segment_analyses = []
        sentiments = []
        intents = []
        
        for segment in patient_segments:
            if len(segment) > 10:  # Only analyze substantial segments
                analysis = self.analyze_sentiment(segment)
                segment_analyses.append({
                    "Text": segment[:100] + "..." if len(segment) > 100 else segment,
                    "Sentiment": analysis["Sentiment"],
                    "Intent": analysis["Intent"]
                })
                sentiments.append(analysis["Sentiment"])
                intents.append(analysis["Intent"])
        
        # Determine overall sentiment (most common)
        overall_sentiment = max(set(sentiments), key=sentiments.count) if sentiments else "Neutral"
        overall_intent = max(set(intents), key=intents.count) if intents else "Other"
        
        return {
            "Overall_Sentiment": overall_sentiment,
            "Overall_Intent": overall_intent,
            "Segments_Analyzed": len(segment_analyses),
            "Segment_Details": segment_analyses
        }

