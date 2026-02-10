# Physician Notetaker

Medical Transcription (NLP Based Summarization)

An AI-powered system for medical transcription, NLP-based summarization, and sentiment analysis using Google's Gemini 2.5 Flash API.

## Video 

https://github.com/user-attachments/assets/e0d7a940-443b-4113-ac07-cb72d33f9228


## Features

1. **Medical NLP Summarization**
   - Named Entity Recognition (NER): Extract Symptoms, Treatment, Diagnosis, Prognosis
   - Text Summarization: Convert transcripts into structured medical reports
   - Keyword Extraction: Identify important medical phrases

2. **Sentiment & Intent Analysis**
   - Sentiment Classification: Anxious, Neutral, or Reassured
   - Intent Detection: Seeking reassurance, Reporting symptoms, Expressing concern

3. **SOAP Note Generation (Bonus)**
   - Automated SOAP note generation from transcripts
   - Structured output: Subjective, Objective, Assessment, Plan

## Project Structure

```
PhysicianNotetaker/
├── src/
│   ├── __init__.py
│   ├── gemini_client.py          # Gemini API wrapper
│   ├── medical_ner.py            # NER and medical entity extraction
│   ├── summarization.py           # Text summarization pipeline
│   ├── sentiment_analysis.py      # Sentiment and intent detection
│   ├── soap_generator.py          # SOAP note generation
│   └── pipeline.py               # Main orchestration pipeline
├── notebooks/
│   └── physician_notetaker.ipynb  # Interactive Jupyter notebook
├── tests/
│   └── test_sample_transcript.txt # Sample transcript for testing
├── requirements.txt
└── README.md
└── quickrun.py (use this to run on terminal quickly)
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Google Gemini API key 

### 2. Installation

1. Clone or navigate to the project directory:
```bash
cd PhysicianNotetaker
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configuration

1. Create a `.env` file in the project root:
```bash
cp .env.example .env
```

2. Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

Alternatively, you can set the environment variable directly:
```bash
export GEMINI_API_KEY=your_actual_api_key_here
```

## Usage

### Option 1: Command-Line Interface (Recommended)

The easiest way to process transcripts is using the command-line tool:

```bash
# Basic usage - process a transcript file
python quickrun.py transcript.txt

# Output as JSON format
python quickrun.py transcript.txt --format json

# Save results to a file
python quickrun.py transcript.txt --output results.txt

# Skip SOAP note generation (faster)
python quickrun.py transcript.txt --no-soap

# Process the sample transcript
python quickrun.py tests/test_sample_transcript.txt
```

**Command-line Options:**
- `filename`: Path to transcript file (required)
- `--format {json,text}`: Output format (default: text)
- `--output OUTPUT`: Save results to file (optional)
- `--no-soap`: Skip SOAP note generation for faster processing

### Option 2: Jupyter Notebook (Recommended for Exploration)

1. Start Jupyter Notebook:
```bash
jupyter notebook
```

2. Open `notebooks/physician_notetaker.ipynb`

3. Run all cells to see the complete demonstration with the sample transcript

### Option 3: Python Script

```python
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.pipeline import PhysicianNotetakerPipeline

# Initialize pipeline
pipeline = PhysicianNotetakerPipeline()

# Load transcript
with open('tests/test_sample_transcript.txt', 'r') as f:
    transcript = f.read()

# Process transcript
results = pipeline.process_transcript(transcript, include_soap=True)

# Export results
output = pipeline.export_results(results, format_type="json")
print(output)
```

### Option 4: Individual Modules

```python
from src.medical_ner import MedicalNER
from src.sentiment_analysis import SentimentAnalyzer
from src.soap_generator import SOAPGenerator

# Initialize modules
ner = MedicalNER()
sentiment_analyzer = SentimentAnalyzer()
soap_generator = SOAPGenerator()

# Use individual modules
transcript = "Your transcript here..."

# Extract medical entities
entities = ner.extract_entities(transcript)

# Analyze sentiment
sentiment = sentiment_analyzer.analyze_full_transcript(transcript)

# Generate SOAP note
soap_note = soap_generator.generate_soap_note(transcript)
```

## Sample Output

### Medical NER Output
```json
{
  "Patient_Name": "Janet Jones",
  "Symptoms": ["Neck pain", "Back pain", "Head impact"],
  "Diagnosis": "Whiplash injury",
  "Treatment": ["10 physiotherapy sessions", "Painkillers"],
  "Current_Status": "Occasional backache",
  "Prognosis": "Full recovery expected within six months"
}
```

### Sentiment Analysis Output
```json
{
  "Sentiment": "Reassured",
  "Intent": "Seeking reassurance"
}
```

### SOAP Note Output
```json
{
  "Subjective": {
    "Chief_Complaint": "Neck and back pain",
    "History_of_Present_Illness": "Patient had a car accident, experienced pain for four weeks, now occasional back pain."
  },
  "Objective": {
    "Physical_Exam": "Full range of motion in cervical and lumbar spine, no tenderness.",
    "Observations": "Patient appears in normal health, normal gait."
  },
  "Assessment": {
    "Diagnosis": "Whiplash injury and lower back strain",
    "Severity": "Mild, improving"
  },
  "Plan": {
    "Treatment": "Continue physiotherapy as needed, use analgesics for pain relief.",
    "Follow-Up": "Patient to return if pain worsens or persists beyond six months."
  }
}
```

## API Reference

### PhysicianNotetakerPipeline

Main pipeline class that orchestrates all modules.

**Methods:**
- `process_transcript(transcript: str, include_soap: bool = True) -> Dict[str, Any]`: Process complete transcript
- `process_quick_summary(transcript: str) -> Dict[str, Any]`: Quick processing with essential info only
- `export_results(results: Dict[str, Any], format_type: str = "json") -> str`: Export results in JSON or text format

### MedicalNER

Extract medical entities from transcripts.

**Methods:**
- `extract_entities(transcript: str) -> Dict[str, Any]`: Extract medical entities
- `extract_keywords(transcript: str, top_n: int = 10) -> List[str]`: Extract medical keywords
- `extract_structured_summary(transcript: str) -> Dict[str, Any]`: Complete structured summary

### SentimentAnalyzer

Analyze patient sentiment and intent.

**Methods:**
- `analyze_sentiment(patient_text: str) -> Dict[str, str]`: Analyze single patient statement
- `analyze_full_transcript(transcript: str) -> Dict[str, Any]`: Analyze entire transcript

### SOAPGenerator

Generate SOAP notes from transcripts.

**Methods:**
- `generate_soap_note(transcript: str) -> Dict[str, Any]`: Generate SOAP note
- `format_soap_note(soap_note: Dict[str, Any], format_type: str = "json") -> str`: Format SOAP note (json/text/markdown)

## Handling Ambiguous or Missing Data

The system handles ambiguous or missing medical data by:
- Using `null` for missing string values
- Using empty arrays `[]` for missing list values
- Using "Not documented" or "Not specified" for missing clinical information
- Providing confidence through structured validation

## Pre-trained Models

This system uses **Google Gemini 2.5 Flash** API, which is:
- Pre-trained on large medical and general text corpora
- Fine-tuned for structured output generation
- Optimized for medical domain understanding

## Questions & Answers

### How would you handle ambiguous or missing medical data in the transcript?

The system handles this by:
1. Explicitly requesting null values when data is unavailable
2. Using validation functions to ensure proper data types
3. Providing fallback values ("Not documented", "Not specified")
4. Maintaining structured output even with missing fields

### What pre-trained NLP models would you use for medical summarization?

This implementation uses **Google Gemini 2.5 Flash**, which provides:
- Strong medical domain understanding
- Structured JSON output capabilities
- Efficient processing for medical transcripts
- No need for local model training or fine-tuning

### How would you fine-tune BERT for medical sentiment detection?

While this implementation uses Gemini API, fine-tuning BERT would involve:
1. Using healthcare-specific datasets (e.g., MIMIC-III notes, medical forums)
2. Creating labeled datasets with Anxious/Neutral/Reassured labels
3. Fine-tuning BERT-base or BioBERT on medical sentiment tasks
4. Evaluating on held-out medical dialogue datasets

### What datasets would you use for training a healthcare-specific sentiment model?

Recommended datasets:
- MIMIC-III Clinical Notes (with sentiment annotations)
- Medical dialogue datasets from patient forums
- Healthcare conversation transcripts with labeled sentiment
- Custom labeled dataset from medical consultations

## License

MIT License - See LICENSE file for details

## Author

Shremya Gupta

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
