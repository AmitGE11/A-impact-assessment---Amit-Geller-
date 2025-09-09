from __future__ import annotations
import sys, json, re
from pathlib import Path
from typing import List, Dict, Any, Optional

# Hebrew normalization utilities
import re
from bidi.algorithm import get_display

HEB = re.compile(r'[\u0590-\u05FF]')
DOT_RULE = re.compile(r'[.\-_]{6,}')
SPACE_RULE = re.compile(r'[ \t]+')
PAREN_SWAP = str.maketrans({'(':')', ')':'('})

def looks_hebrew(s: str) -> bool:
    return bool(HEB.search(s))

def rtl_fix_line(s: str) -> str:
    """
    Fix a single line:
    - strip dotted rules and extra whitespace
    - if it contains Hebrew, run BiDi get_display
    - avoid double-application by only doing it on raw extracted lines
    - normalize mismatched parentheses after BiDi by swapping ( )
    """
    s = DOT_RULE.sub(' ', s)
    s = SPACE_RULE.sub(' ', s).strip()
    if not s:
        return s
    if looks_hebrew(s):
        s = get_display(s)  # Remove base_dir parameter
        # after BiDi, parentheses are visually flipped; normalize
        s = s.translate(PAREN_SWAP)
    return s

def rtl_fix_block(text: str) -> str:
    """Apply rtl_fix_line on each line and rejoin; collapse multiple blank lines."""
    lines = [rtl_fix_line(ln) for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]  # drop empties
    out = "\n".join(lines)
    out = re.sub(r'\n{3,}', '\n\n', out)
    return out.strip()

def make_title(block: str, max_words: int = 12) -> str:
    cand = block.split('\n', 1)[0]              # first line
    if len(cand) < 10:
        cand = re.split(r'[.:\-–;]\s+', block, maxsplit=1)[0]
    words = cand.split()
    t = " ".join(words[:max_words]).strip()
    # if still empty, use first Hebrew word sequence
    if not t and looks_hebrew(block):
        m = re.search(r'([\u0590-\u05FF][\u0590-\u05FF\s]{6,})', block)
        if m: t = m.group(1).strip()
    return t

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
    
    # Don't apply RTL fix here - do it later in the pipeline
    
    return text

def normalize_spaces(text: str) -> str:
    """Normalize whitespace"""
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{2,}', '\n\n', text)
    return text.strip()


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
                if _is_valid_block(block_text):
                    blocks.append(block_text)
                current_block = []
            continue
        
        # Check for numbered headings (e.g., "3.1.2", "4.5.6.7")
        if re.match(r'^\s*(\d+(?:\.\d+){1,3})\s+', line):
            if current_block:
                block_text = " ".join(current_block).strip()
                if _is_valid_block(block_text):
                    blocks.append(block_text)
            current_block = [line]
            continue
        
        # Check for bullets
        if re.match(r'^\s*[•\-–]\s+', line):
            if current_block:
                block_text = " ".join(current_block).strip()
                if _is_valid_block(block_text):
                    blocks.append(block_text)
            current_block = [line]
            continue
        
        current_block.append(line)
    
    # Add final block
    if current_block:
        block_text = " ".join(current_block).strip()
        if _is_valid_block(block_text):
            blocks.append(block_text)
    
    return blocks

def _is_valid_block(block: str) -> bool:
    """Check if block is valid (length and Hebrew content)"""
    if len(block) < 40 or len(block) > 2200:
        return False
    
    # Check Hebrew content percentage
    hebrew_chars = len(re.findall(r'[\u0590-\u05FF]', block))
    total_chars = len(block)
    hebrew_ratio = hebrew_chars / total_chars if total_chars > 0 else 0
    
    return hebrew_ratio >= 0.1  # At least 10% Hebrew content

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
        title = make_title(block, 8)  # Use shorter title for comparison
        if title not in seen_titles:
            seen_titles.add(title)
            unique_blocks.append(block)
    
    return unique_blocks

def block_to_item(idx: int, block: str) -> Dict[str, Any]:
    """Convert text block to requirement item"""
    # Apply RTL fix to the entire block
    fixed_block = rtl_fix_block(block)
    
    # Generate title with fallback
    title = make_title(fixed_block)
    if not title:
        return None  # Skip blocks without valid titles
    
    category = guess_category(fixed_block)
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

def parse_text_to_items(text: str) -> tuple[List[Dict[str, Any]], Dict[str, int]]:
    """Parse text into requirement items with statistics"""
    normalized_text = normalize_spaces(text)
    blocks = split_blocks(normalized_text)
    blocks = deduplicate_blocks(blocks)
    
    items = []
    dropped_short = 0
    dropped_nonhe = 0
    
    for i, block in enumerate(blocks, 1):
        item = block_to_item(i, block)
        if item is not None:
            items.append(item)
        else:
            # Count why it was dropped
            if len(block) < 40:
                dropped_short += 1
            elif len(re.findall(r'[\u0590-\u05FF]', block)) / len(block) < 0.2:
                dropped_nonhe += 1
    
    stats = {
        "items": len(items),
        "dropped_short": dropped_short,
        "dropped_nonhe": dropped_nonhe
    }
    
    return items, stats

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
    
    items, stats = parse_text_to_items(text)
    save_json(items, OUTPUT_JSON)
    
    print(f"Extracted {stats['items']} requirements → {OUTPUT_JSON}")
    print(f"Summary: {stats}")

if __name__ == "__main__":
    arg_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    main(arg_path)