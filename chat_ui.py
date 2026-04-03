#!/usr/bin/env python3
"""
Interactive Text UI for Doctor-Patient Conversation
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Setup paths
import os
import sys

os.system("") # Enable ANSI escape sequences on Windows
sys.stdout.reconfigure(encoding='utf-8') # Enable UTF-8 emojis

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
load_dotenv()

try:
    from src.pipeline import PhysicianNotetakerPipeline
except ImportError as e:
    print(f"Error importing pipeline: {e}")
    sys.exit(1)

# ANSI color codes for Text UI
class Colors:
    HEADER = '\033[95m'
    DOCTOR = '\033[94m'   # Blue
    PATIENT = '\033[92m'  # Green
    SYSTEM = '\033[93m'   # Yellow
    FAIL = '\033[91m'     # Red
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 65}")
    print(f"  {text}")
    print(f"{'=' * 65}{Colors.ENDC}\n")

def main():
    print_header("⚕️  Physician Notetaker - Live Text UI ⚕️")
    
    print(f"{Colors.SYSTEM}Instructions:{Colors.ENDC}")
    print(" - The conversation alternates between the Doctor and Patient automatically.")
    print(" - If the same person is speaking multiple times, just hit Enter with empty text to skip the turn.")
    print(" - Type your message and press Enter.")
    print(f" - Type {Colors.FAIL}'END'{Colors.ENDC} or {Colors.FAIL}'QUIT'{Colors.ENDC} to finish and generate medical notes.\n")
    print("-" * 65 + "\n")
    
    transcript_lines = []
    current_speaker = "Doctor"
    
    while True:
        try:
            # Set color based on speaker
            speaker_color = Colors.DOCTOR if current_speaker == "Doctor" else Colors.PATIENT
            prompt = f"{speaker_color}{Colors.BOLD}{current_speaker}:{Colors.ENDC} "
            
            line = input(prompt)
            
            if line.strip().upper() in ['END', 'QUIT']:
                break
                
            if line.strip():
                # Append to transcript
                transcript_lines.append(f"{current_speaker}: {line.strip()}")
                
            # Switch speaker auto-toggling
            current_speaker = "Patient" if current_speaker == "Doctor" else "Doctor"
            
        except KeyboardInterrupt:
            print(f"\n{Colors.FAIL}Conversation interrupted.{Colors.ENDC}")
            break
        except EOFError:
            break

    if not transcript_lines:
        print(f"\n{Colors.SYSTEM}No conversation recorded. Exiting.{Colors.ENDC}")
        return

    transcript = "\n".join(transcript_lines)
    
    print_header("Processing Conversation... (Please wait)")
    
    try:
        pipeline = PhysicianNotetakerPipeline()
        results = pipeline.process_transcript(transcript, include_soap=True)
        output = pipeline.export_results(results, format_type='text')
        
        print_header("📝 GENERATED MEDICAL NOTES 📝")
        print(output)
        
    except ValueError as e:
        print(f"{Colors.FAIL}Error: {e}{Colors.ENDC}")
        print(f"{Colors.SYSTEM}Please make sure GEMINI_API_KEY is set in your .env file.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}An error occurred while processing the transcript: {e}{Colors.ENDC}")

if __name__ == "__main__":
    main()
