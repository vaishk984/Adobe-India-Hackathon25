# PDF Outline Extractor

This project extracts structured outlines (headings and subheadings) from PDF documents and generates a JSON file with the document's title and a list of headings with their hierarchy (H1–H4) and corresponding page numbers.

---

## Approach

We use **PyMuPDF** (also known as `fitz`) to analyze each PDF page and extract text blocks with font size, position, and style information. Based on relative font sizes, text patterns (like numbered headings), and heuristics (e.g., filtering noise), we determine the heading levels (H1–H4) and construct an outline.

The **title** is derived by collecting prominent H1-level headings from early pages (usually page 2), combining them with double spaces and preserving the trailing space as per specification.

All files from `/app/input` are processed, and structured outlines are written as `filename.json` to `/app/output`.

---

## Libraries / Tools Used

- [`PyMuPDF`](https://pymupdf.readthedocs.io/en/latest/) - to extract font, position, and text information from PDFs
- `re` - for regex-based pattern matching and heading level identification
- `json` - for structured output generation
- `os` / `glob` - to handle all PDFs from the input directory
- `Docker` - to containerize the solution for a reproducible, isolated environment

No external models or internet access are required.

---

## How to Build & Run

### 1️⃣ Build the Docker Image

```bash
docker build --platform linux/amd64 -t pdf-outliner:round1a .
```

### 2️⃣ Run the Container

Assuming you have a local `input/` folder with PDFs and an `output/` folder for JSON files:

```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  pdf-outliner:round1a
```

This will process all `*.pdf` files in `input/` and generate corresponding `*.json` files in `output/`.

---

## Output Format

Each JSON file will look like:

```json
{
  "title": "Overview  Foundation Level Extensions  ",
  "outline": [
    {
      "level": "H1",
      "text": "1. Introduction to the Foundation Level Extensions ",
      "page": 2
    },
    {
      "level": "H2",
      "text": "2.1 Intended Audience ",
      "page": 3
    }
    ...
  ]
}
```

---

## Compliance

| Constraint                         | Status |
|------------------------------------|-----|
| Execution Time ≤ 10s for 50-page PDF | Passed |
| Model Size ≤ 200MB model size      | N/A |
| Network No internet access         | Yes |
| Runtime CPU-only (amd64)           | Yes |
| Reads from `/app/input`           | Yes |
| Outputs to `/app/output`         | Yes |

