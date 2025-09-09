#!/usr/bin/env python3
"""
Simple script to run the PDF parser and show results.
Usage: python run_parser.py [path_to_pdf]
"""

import sys
from pathlib import Path
from process_pdf import main, load_pdf_text, parse_text_to_items

def show_sample_results():
    """Show a sample of the parsed results"""
    data_path = Path(__file__).parent / "data" / "requirements.json"
    
    if not data_path.exists():
        print("No parsed requirements found. Run process_pdf.py first.")
        return
    
    import json
    with open(data_path, "r", encoding="utf-8") as f:
        requirements = json.load(f)
    
    print(f"\n=== Parsed {len(requirements)} Requirements ===")
    for i, req in enumerate(requirements[:3], 1):  # Show first 3
        print(f"\n{i}. {req['title']}")
        print(f"   Category: {req['category']}")
        print(f"   Priority: {req['priority']}")
        print(f"   Description: {req['description'][:100]}...")
    
    if len(requirements) > 3:
        print(f"\n... and {len(requirements) - 3} more requirements")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Process specific PDF
        pdf_path = Path(sys.argv[1])
        main(pdf_path)
    else:
        # Process default PDF
        main()
    
    # Show results
    show_sample_results()
