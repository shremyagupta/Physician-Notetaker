#!/usr/bin/env python3
"""
Command-line interface for Physician Notetaker
Usage: python test.py <filename.txt>
"""

import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
load_dotenv()

from src.pipeline import PhysicianNotetakerPipeline


def main():
    parser = argparse.ArgumentParser(
        description='Process medical transcripts and generate analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test.py transcript.txt
  python test.py transcript.txt --format json
  python test.py transcript.txt --output results.txt
        """
    )
    
    parser.add_argument(
        'filename',
        type=str,
        help='Path to transcript file (.txt)'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        choices=['json', 'text'],
        default='text',
        help='Output format: json or text (default: text)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Save results to file (optional)'
    )
    
    parser.add_argument(
        '--no-soap',
        action='store_true',
        help='Skip SOAP note generation'
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    transcript_path = Path(args.filename)
    if not transcript_path.exists():
        print(f"Error: File '{args.filename}' not found.")
        sys.exit(1)
    
    # Read transcript
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    if not transcript.strip():
        print("Error: Transcript file is empty.")
        sys.exit(1)
    
    # Initialize pipeline
    print("Initializing pipeline...")
    try:
        pipeline = PhysicianNotetakerPipeline()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set GEMINI_API_KEY environment variable or create .env file")
        sys.exit(1)
    
    # Process transcript
    print(f"Processing transcript from: {transcript_path}")
    print(f"Transcript length: {len(transcript)} characters")
    print("Processing... (this may take a few moments)\n")
    
    try:
        results = pipeline.process_transcript(
            transcript, 
            include_soap=not args.no_soap
        )
    except Exception as e:
        print(f"Error during processing: {e}")
        sys.exit(1)
    
    # Generate output
    output = pipeline.export_results(results, format_type=args.format)
    
    # Display results
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(output)
    
    # Save to file if specified
    if args.output:
        output_path = Path(args.output)
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"\nResults saved to: {output_path}")
        except Exception as e:
            print(f"Error saving file: {e}")
    
    print("\nDone!")


if __name__ == "__main__":
    main()

