from __future__ import annotations
import sys, json, re
from pathlib import Path
import pdfplumber

DATA_DIR = Path(__file__).parent / "data"
DEFAULT_PDF = Path(__file__).parent.parent / "18-07-2022_4.2A.pdf"
OUTPUT_JSON = DATA_DIR / "requirements.json"

PRIORITY_ORDER = ["High", "Medium", "Low"]

def load_pdf_text(path: Path) -> str:
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            t = p.extract_text() or ""
            text_parts.append(t)
    return "\n".join(text_parts)

def clean_text(t: str) -> str:
    # normalize whitespace, remove repetitive headers/footers heuristically
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{2,}", "\n\n", t)
    return t.strip()

def split_blocks(t: str) -> list[str]:
    """
    Heuristic:
    - Split by blank lines OR bullets (•, -, –) at line starts.
    - Keep blocks reasonably sized (20–1200 chars).
    """
    lines = [ln.strip() for ln in t.splitlines()]
    blocks, cur = [], []
    bullet = re.compile(r"^([•\-–]|[\d]+\.)\s+")
    for ln in lines:
        if not ln:
            if cur:
                blocks.append(" ".join(cur).strip())
                cur = []
            continue
        if bullet.match(ln) and cur:
            blocks.append(" ".join(cur).strip())
            cur = [bullet.sub("", ln)]
        else:
            cur.append(bullet.sub("", ln))
    if cur:
        blocks.append(" ".join(cur).strip())
    # filter too-short/too-long leftovers
    return [b for b in blocks if 20 <= len(b) <= 2000]

def guess_category(text: str) -> str:
    kw = {
        "בטיחות": ["בטיחות", "כיבוי", "גז", "חירום", "דליקה", "מפוח", "אש"],
        "היגיינה": ["היגיינה", "חיטוי", "סניטרי", "ניקיון", "שטיפה", "טמפרטורה"],
        "רישוי כללי": ["רישוי", "היתר", "אישור", "בעלות", "תפוסה", "תכנית", "שילוט"],
    }
    score = {k:0 for k in kw}
    low = text
    for cat, words in kw.items():
        for w in words:
            if w in low:
                score[cat] += 1
    return max(score, key=score.get) if any(score.values()) else "רישוי כללי"

def summarize_title(text: str, max_words: int = 8) -> str:
    words = text.split()
    return " ".join(words[:max_words])

def block_to_item(idx: int, block: str) -> dict:
    cat = guess_category(block)
    return {
        "id": f"req-{idx:03d}",
        "category": cat,
        "title": summarize_title(block),
        "description": block,
        "priority": "Medium",
        "conditions": {
            "size_any": [],
            "min_seats": None,
            "max_seats": None,
            "features_any": [],
            "features_all": [],
            "features_none": []
        }
    }

def parse_text_to_items(text: str) -> list[dict]:
    blocks = split_blocks(clean_text(text))
    items = [block_to_item(i+1, b) for i, b in enumerate(blocks)]
    return items

def save_json(data, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main(pdf_path: Path | None = None):
    pdf_path = pdf_path or DEFAULT_PDF
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    text = load_pdf_text(pdf_path)
    items = parse_text_to_items(text)
    save_json(items, OUTPUT_JSON)
    print(f"Extracted {len(items)} requirements → {OUTPUT_JSON}")

if __name__ == "__main__":
    arg_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    main(arg_path)
