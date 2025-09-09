from __future__ import annotations
import sys, json, re
from pathlib import Path
from typing import List, Dict, Any, Optional

# Import PDF processing libraries
try:
    from pdfminer.high_level import extract_text as pdfminer_extract
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from bidi.algorithm import get_display
    BIDI_AVAILABLE = True
except ImportError:
    BIDI_AVAILABLE = False

DATA_DIR = Path(__file__).parent / "data"
DEFAULT_PDF = DATA_DIR / "18-07-2022_4.2A.pdf"
DEFAULT_DOCX = DATA_DIR / "18-07-2022_4.2A.docx"
OUTPUT_JSON = DATA_DIR / "requirements.json"

# Feature keyword mapping for auto-extraction
FEATURE_KEYWORDS = {
    'gas': ['גז', 'מ"פג', 'בלוני גז'],
    'hood_vent': ['מנדף', 'יניקה', 'אוורור'],
    'meat': ['בשר'],
    'dairy': ['חלבי'],
    'fish': ['דגים'],
    'alcohol': ['אלכוהול', 'משקאות משכרים'],
    'night': ['לאחר חצות', 'בלילה'],
    'outdoor': ['ישיבה חיצונית', 'חוץ'],
    'smoking': ['אזור עישון'],
    'music': ['מוסיקה', 'בידור', 'הגברה']
}

def load_pdf_text_pdfminer(path: Path) -> str:
    """Extract text using pdfminer.six"""
    try:
        return pdfminer_extract(str(path))
    except Exception as e:
        print(f"pdfminer failed: {e}")
        return ""

def load_pdf_text_pdfplumber(path: Path) -> str:
    """Extract text using pdfplumber"""
    try:
        text_parts = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                text_parts.append(text)
        return "\n".join(text_parts)
    except Exception as e:
        print(f"pdfplumber failed: {e}")
        return ""

def load_docx_text(path: Path) -> str:
    """Extract text from DOCX file"""
    try:
        doc = Document(path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        print(f"docx extraction failed: {e}")
        return ""

def load_text(path: Path) -> str:
    """Load text with fallback chain: pdfminer -> pdfplumber -> docx"""
    text = ""
    
    if path.suffix.lower() == '.pdf':
        if PDFMINER_AVAILABLE:
            text = load_pdf_text_pdfminer(path)
        if not text and PDFPLUMBER_AVAILABLE:
            text = load_pdf_text_pdfplumber(path)
    elif path.suffix.lower() == '.docx':
        if DOCX_AVAILABLE:
            text = load_docx_text(path)
    
    return text

def normalize_spaces(text: str) -> str:
    """Normalize whitespace"""
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{2,}', '\n\n', text)
    return text.strip()

def fix_rtl_line(line: str) -> str:
    """Fix RTL display for Hebrew text"""
    if not BIDI_AVAILABLE or len(line) < 12:
        return line
    
    # Check if line contains Hebrew characters
    if re.search(r'[\u0590-\u05FF]', line):
        return get_display(line)
    return line

def split_blocks(text: str) -> List[str]:
    """Split text into blocks using multiple strategies"""
    lines = text.splitlines()
    blocks = []
    current_block = []
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_block:
                block_text = " ".join(current_block).strip()
                if 40 <= len(block_text) <= 2000:
                    blocks.append(block_text)
                current_block = []
            continue
        
        # Check for numbered headings (e.g., "3.1.2", "4.5.6.7")
        if re.match(r'^\s*(\d+(?:\.\d+){1,3})\s+', line):
            if current_block:
                block_text = " ".join(current_block).strip()
                if 40 <= len(block_text) <= 2000:
                    blocks.append(block_text)
            current_block = [line]
            continue
        
        # Check for bullets
        if re.match(r'^\s*[•\-–]\s+', line):
            if current_block:
                block_text = " ".join(current_block).strip()
                if 40 <= len(block_text) <= 2000:
                    blocks.append(block_text)
            current_block = [line]
            continue
        
        current_block.append(line)
    
    # Add final block
    if current_block:
        block_text = " ".join(current_block).strip()
        if 40 <= len(block_text) <= 2000:
            blocks.append(block_text)
    
    return blocks

def guess_category(text: str) -> str:
    """Guess category based on keywords"""
    keywords = {
        "בטיחות": ["בטיחות", "כיבוי", "גז", "חירום", "דליקה", "מפוח", "אש", "מנדף", "יניקה"],
        "היגיינה": ["היגיינה", "חיטוי", "סניטרי", "ניקיון", "שטיפה", "טמפרטורה", "מלכודת שומן"],
        "רישוי כללי": ["רישוי", "היתר", "אישור", "בעלות", "תפוסה", "תכנית", "שילוט", "נגישות"]
    }
    
    score = {k: 0 for k in keywords}
    text_lower = text.lower()
    
    for category, words in keywords.items():
        for word in words:
            if word in text_lower:
                score[category] += 1
    
    return max(score, key=score.get) if any(score.values()) else "רישוי כללי"

def extract_title(text: str, max_words: int = 12) -> str:
    """Extract title from first sentence"""
    # Fix RTL for title extraction
    fixed_text = fix_rtl_line(text)
    sentences = re.split(r'[.!?]', fixed_text)
    first_sentence = sentences[0].strip()
    words = first_sentence.split()
    return " ".join(words[:max_words])

def infer_priority(text: str) -> str:
    """Infer priority based on strong words"""
    strong_words = ["חובה", "נדרש", "אסור", "חייב", "מחויב"]
    medium_words = ["מומלץ", "רצוי", "יש", "צריך"]
    
    text_lower = text.lower()
    
    for word in strong_words:
        if word in text_lower:
            return "High"
    
    for word in medium_words:
        if word in text_lower:
            return "Medium"
    
    return "Low"

def extract_conditions(text: str) -> Dict[str, Any]:
    """Extract conditions from text using regex patterns"""
    conditions = {}
    
    # Seats patterns
    seats_patterns = [
        (r'עד\s*(\d+)\s*מקומות', 'max_seats'),
        (r'מעל\s*(\d+)\s*מקומות', 'min_seats'),
        (r'תפוסה\s*עד\s*(\d+)', 'max_seats')
    ]
    
    for pattern, key in seats_patterns:
        match = re.search(pattern, text)
        if match:
            conditions[key] = int(match.group(1))
    
    # Area patterns
    area_patterns = [
        (r'עד\s*(\d+)\s*מ"?ר', 'max_area_sqm'),
        (r'מעל\s*(\d+)\s*מ"?ר', 'min_area_sqm')
    ]
    
    for pattern, key in area_patterns:
        match = re.search(pattern, text)
        if match:
            conditions[key] = int(match.group(1))
    
    # Staff patterns
    staff_match = re.search(r'(\d+)\s*עובדים', text)
    if staff_match and 'נדרשים' in text:
        conditions['min_staff'] = int(staff_match.group(1))
    
    # Feature patterns
    features_any = []
    for feature, keywords in FEATURE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                features_any.append(feature)
                break
    
    if features_any:
        conditions['features_any'] = features_any
    
    return conditions

def deduplicate_blocks(blocks: List[str]) -> List[str]:
    """Remove near-duplicate blocks based on title similarity"""
    if not blocks:
        return blocks
    
    unique_blocks = []
    seen_titles = set()
    
    for block in blocks:
        title = extract_title(block, 8)  # Use shorter title for comparison
        if title not in seen_titles:
            seen_titles.add(title)
            unique_blocks.append(block)
    
    return unique_blocks

def block_to_item(idx: int, block: str) -> Dict[str, Any]:
    """Convert text block to requirement item"""
    # Fix RTL for the entire block
    fixed_block = fix_rtl_line(block)
    
    category = guess_category(fixed_block)
    title = extract_title(fixed_block)
    priority = infer_priority(fixed_block)
    conditions = extract_conditions(fixed_block)
    
    return {
        "id": f"req-{idx:03d}",
        "category": category,
        "title": title,
        "description": fixed_block,
        "priority": priority,
        "conditions": conditions
    }

def parse_text_to_items(text: str) -> List[Dict[str, Any]]:
    """Parse text into requirement items"""
    normalized_text = normalize_spaces(text)
    blocks = split_blocks(normalized_text)
    blocks = deduplicate_blocks(blocks)
    
    items = []
    for i, block in enumerate(blocks, 1):
        item = block_to_item(i, block)
        items.append(item)
    
    return items

def save_json(data: List[Dict[str, Any]], path: Path) -> None:
    """Save data to JSON file"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main(input_path: Optional[Path] = None):
    """Main processing function"""
    if input_path is None:
        # Try PDF first, then DOCX
        if DEFAULT_PDF.exists():
            input_path = DEFAULT_PDF
        elif DEFAULT_DOCX.exists():
            input_path = DEFAULT_DOCX
        else:
            raise FileNotFoundError(f"Neither {DEFAULT_PDF} nor {DEFAULT_DOCX} found")
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    print(f"Processing: {input_path}")
    print(f"Available libraries: pdfminer={PDFMINER_AVAILABLE}, pdfplumber={PDFPLUMBER_AVAILABLE}, docx={DOCX_AVAILABLE}, bidi={BIDI_AVAILABLE}")
    
    text = load_text(input_path)
    if not text:
        raise RuntimeError("Failed to extract text from input file")
    
    print(f"Extracted {len(text)} characters")
    
    items = parse_text_to_items(text)
    save_json(items, OUTPUT_JSON)
    
    print(f"Extracted {len(items)} requirements → {OUTPUT_JSON}")

if __name__ == "__main__":
    arg_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    main(arg_path)