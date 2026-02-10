"""
Main Pipeline Orchestrator
Combines all modules for end-to-end medical transcript processing
"""

from typing import Dict, Any, Optional
from .gemini_client import GeminiClient
from .medical_ner import MedicalNER
from .summarization import MedicalSummarizer
from .sentiment_analysis import SentimentAnalyzer
from .soap_generator import SOAPGenerator


class PhysicianNotetakerPipeline:
    """Main pipeline for processing medical transcripts"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the complete pipeline
        
        Args:
            api_key: Gemini API key. If None, reads from environment variable.
        """
        # Initialize shared Gemini client
        self.client = GeminiClient(api_key=api_key)
        
        # Initialize all modules
        self.ner = MedicalNER(gemini_client=self.client)
        self.summarizer = MedicalSummarizer(gemini_client=self.client)
        self.sentiment_analyzer = SentimentAnalyzer(gemini_client=self.client)
        self.soap_generator = SOAPGenerator(gemini_client=self.client)
    
    def process_transcript(self, transcript: str, include_soap: bool = True) -> Dict[str, Any]:
        """
        Process transcript through complete pipeline
        
        Args:
            transcript: Raw physician-patient conversation transcript
            include_soap: Whether to include SOAP note generation (bonus feature)
        
        Returns:
            Complete analysis with all extracted information
        """
        results = {
            "Medical_NER": {},
            "Summarization": {},
            "Sentiment_Analysis": {},
            "SOAP_Note": {}
        }
        
        # 1. Medical NER Extraction
        try:
            results["Medical_NER"] = self.ner.extract_structured_summary(transcript)
        except Exception as e:
            results["Medical_NER"] = {"error": str(e)}
        
        # 2. Text Summarization
        try:
            results["Summarization"] = self.summarizer.summarize(transcript)
        except Exception as e:
            results["Summarization"] = {"error": str(e)}
        
        # 3. Sentiment & Intent Analysis
        try:
            results["Sentiment_Analysis"] = self.sentiment_analyzer.analyze_full_transcript(transcript)
        except Exception as e:
            results["Sentiment_Analysis"] = {"error": str(e)}
        
        # 4. SOAP Note Generation (Bonus)
        if include_soap:
            try:
                results["SOAP_Note"] = self.soap_generator.generate_soap_note(transcript)
            except Exception as e:
                results["SOAP_Note"] = {"error": str(e)}
        
        return results
    
    def process_quick_summary(self, transcript: str) -> Dict[str, Any]:
        """
        Quick processing with only essential information
        
        Args:
            transcript: Raw transcript
        
        Returns:
            Quick summary with NER and sentiment only
        """
        results = {
            "Medical_Entities": {},
            "Sentiment": {}
        }
        
        try:
            results["Medical_Entities"] = self.ner.extract_entities(transcript)
        except Exception as e:
            results["Medical_Entities"] = {"error": str(e)}
        
        try:
            results["Sentiment"] = self.sentiment_analyzer.analyze_full_transcript(transcript)
        except Exception as e:
            results["Sentiment"] = {"error": str(e)}
        
        return results
    
    def export_results(self, results: Dict[str, Any], format_type: str = "json") -> str:
        """
        Export results in specified format
        
        Args:
            results: Pipeline results dictionary
            format_type: "json" or "text"
        
        Returns:
            Formatted results string
        """
        if format_type == "json":
            import json
            return json.dumps(results, indent=2)
        
        elif format_type == "text":
            text = "=" * 60 + "\n"
            text += "MEDICAL TRANSCRIPT ANALYSIS RESULTS\n"
            text += "=" * 60 + "\n\n"
            
            # Medical NER
            if "Medical_NER" in results:
                text += "MEDICAL ENTITIES:\n"
                text += "-" * 60 + "\n"
                ner = results["Medical_NER"]
                if "error" not in ner:
                    text += f"Patient Name: {ner.get('Patient_Name', 'N/A')}\n"
                    text += f"Symptoms: {', '.join(ner.get('Symptoms', []))}\n"
                    text += f"Diagnosis: {ner.get('Diagnosis', 'N/A')}\n"
                    text += f"Treatment: {', '.join(ner.get('Treatment', []))}\n"
                    text += f"Current Status: {ner.get('Current_Status', 'N/A')}\n"
                    text += f"Prognosis: {ner.get('Prognosis', 'N/A')}\n"
                else:
                    text += f"Error: {ner['error']}\n"
                text += "\n"
            
            # Sentiment Analysis
            if "Sentiment_Analysis" in results:
                text += "SENTIMENT ANALYSIS:\n"
                text += "-" * 60 + "\n"
                sentiment = results["Sentiment_Analysis"]
                if "error" not in sentiment:
                    text += f"Overall Sentiment: {sentiment.get('Overall_Sentiment', 'N/A')}\n"
                    text += f"Overall Intent: {sentiment.get('Overall_Intent', 'N/A')}\n"
                    text += f"Segments Analyzed: {sentiment.get('Segments_Analyzed', 0)}\n"
                else:
                    text += f"Error: {sentiment['error']}\n"
                text += "\n"
            
            # SOAP Note
            if "SOAP_Note" in results:
                text += "SOAP NOTE:\n"
                text += "-" * 60 + "\n"
                soap = results["SOAP_Note"]
                if "error" not in soap:
                    text += self.soap_generator.format_soap_note(soap, format_type="text")
                else:
                    text += f"Error: {soap['error']}\n"
            
            return text
        
        else:
            raise ValueError(f"Unknown format type: {format_type}")

