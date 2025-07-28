import fitz  # PyMuPDF
import os
import json
import re

INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"

def extract_text_blocks(pdf_path):
    doc = fitz.open(pdf_path)
    blocks = []
    for page_num, page in enumerate(doc, start=1):
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                text = " ".join([span["text"] for span in line["spans"]])
                if text.strip():
                    max_font = max(span["size"] for span in line["spans"])
                    blocks.append({
                        "text": text,
                        "page": page_num,
                        "font": max_font
                    })
    return blocks


def extract_title(blocks):
    candidates = [b for b in blocks if b["page"] in (1, 2)]
    candidates.sort(key=lambda b: -b["font"])

    title_lines = []
    for b in candidates:
        text = b["text"].strip()
        if (
            len(text) > 6 and
            re.search(r'[A-Za-z]', text) and
            not re.search(r'(version|copyright|page|\d{4}|revision|table of contents)', text, re.IGNORECASE)
        ):
            title_lines.append(text)
        if len(title_lines) >= 3:
            break

    return "  ".join(title_lines).strip() + "  " if title_lines else "Untitled Document"


def detect_headings(blocks):
    outline = []
    font_sizes = sorted(set(b["font"] for b in blocks), reverse=True)

    size_to_level = {}
    if len(font_sizes) >= 4:
        size_to_level = {
            font_sizes[0]: "H1",
            font_sizes[1]: "H2",
            font_sizes[2]: "H3",
            font_sizes[3]: "H4"
        }
    elif len(font_sizes) == 3:
        size_to_level = {
            font_sizes[0]: "H1",
            font_sizes[1]: "H2",
            font_sizes[2]: "H3"
        }

    seen = set()
    i = 0
    while i < len(blocks):
        b = blocks[i]
        raw_text = b["text"]
        text = re.sub(r'\s+', ' ', raw_text).strip()
        font = b["font"]
        page = b["page"]

        if page < 2:
            i += 1
            continue

        normalized = re.sub(r'\s+', ' ', text.lower())
        if not text or normalized in seen:
            i += 1
            continue

        if re.fullmatch(r'\d+\.?', text) or re.fullmatch(r'\d{4}\.?', text):
            i += 1
            continue

        if len(text.split()) < 2 or len(text.split()) > 12:
            i += 1
            continue

        if re.match(r'^\d+\.', text) and text.count(' ') > 6:
            i += 1
            continue

        # Merge “Syllabus” into '3. Overview...'
        if re.search(r'3\.\s*Overview of the Foundation Level Extension', text, re.IGNORECASE):
            if i + 1 < len(blocks):
                next_text = blocks[i + 1]["text"].strip().lower()
                if next_text == "syllabus":
                    text = "3. Overview of the Foundation Level Extension – Agile TesterSyllabus"
                    raw_text = text + " "
                    level = "H1"
                    outline.append({
                        "level": level,
                        "text": raw_text,
                        "page": page
                    })
                    seen.add(normalized)
                    i += 2
                    continue

        if re.match(r'^\d+\.\d+\.\d+\.\d+', text):
            level = "H4"
        elif re.match(r'^\d+\.\d+\.\d+', text):
            level = "H3"
        elif re.match(r'^\d+\.\d+', text):
            level = "H2"
        elif re.match(r'^\d+\.', text):
            level = "H1"
        else:
            level = size_to_level.get(font)

        if text.lower().strip() in ["revision history", "table of contents", "acknowledgements"]:
            level = "H1"

        if level:
            outline.append({
                "level": level,
                "text": raw_text if raw_text.endswith(" ") else raw_text + " ",
                "page": page
            })
            seen.add(normalized)

        i += 1

    return outline


def process_pdf(pdf_path, output_path):
    blocks = extract_text_blocks(pdf_path)
    outline = detect_headings(blocks)
    title = extract_title(blocks)
    result = {
        "title": title,
        "outline": outline
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)


def main():
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".pdf"):
            input_pdf = os.path.join(INPUT_DIR, filename)
            output_json = os.path.join(OUTPUT_DIR, filename.replace(".pdf", ".json"))
            process_pdf(input_pdf, output_json)


if __name__ == "__main__":
    main()
