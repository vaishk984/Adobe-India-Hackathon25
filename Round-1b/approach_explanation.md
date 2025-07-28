## Problem Statement

The objective is to extract and rank the most relevant sections from a set of PDFs based on a defined persona and job-to-be-done. The system must work offline, within a 1GB model constraint, run on CPU, and complete processing in under 60 seconds per document collection.

---

## Methodology

### 1. **Persona + Job-to-Be-Done Query Formation**

A search query is dynamically constructed from:
- Persona: `"General Analyst"`
- Job: `"Understand key information"`

This yields the semantic intent:  
**`"General Analyst needs to: Understand key information"`**

---

### 2. **PDF Parsing and Section Extraction**

Using PyMuPDF (`fitz`), each PDF is processed:
- All pages are parsed into text blocks.
- Each block is cleaned and stored with its page number and document origin.
- Each block is treated as a candidate section.

---

### 3. **Semantic Similarity Scoring**

We use the lightweight transformer model:  
**`sentence-transformers/all-MiniLM-L6-v2`**, which:
- Is under 100MB
- Is CPU-optimized
- Produces high-quality embeddings

Steps:
- Convert each text block to vector embeddings.
- Convert the persona query into an embedding.
- Compute cosine similarity scores between the query and each section.

---

### 4. **Ranking and Output Generation**

- Top 5 sections with highest similarity scores are selected.
- The `extracted_sections` list includes: document name, title, page number, and rank.
- The `subsection_analysis` list provides refined full-text excerpts for each section.

---

## Output Format

The final output includes:
1. Metadata: Input docs, persona, job, timestamp.
2. Top-ranked extracted sections with rank & location.
3. Full-text refined analysis of those sections.

---

## Dockerfile (Round 1B)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    pymupdf \
    sentence-transformers

COPY . .

CMD ["python", "persona_extractor.py"]

```
---

## Execution Instructions

1. **Build the Docker Image**

```bash
docker build --platform linux/amd64 -t persona-intelligence .
```

2. Prepare Input Folder Structure

project-root/
├── input/
│   ├── Collection-1/
│   │   ├── file1.pdf
│   │   └── file2.pdf
│   ├── Collection-2/
│   └── Collection-3/

3. Run the Container

```bash
docker run --rm -v "${PWD}/input:/app/input" -v "${PWD}/output:/app/output" persona-intelligence
```
4. Output Location
/output/Collection-1/output.json
/output/Collection-2/output.json
/output/Collection-3/output.json

## Constraints Handling

- **CPU-only**: All operations are lightweight and use PyTorch CPU backend.
- **Model Size ≤ 1GB**: Model used is ~90MB.
- **Execution Time ≤ 60s**: Fast embedding and I/O allow fast processing for 3–5 PDFs.
- **No Internet Access**: All models are pre-loaded; no external API or internet use required.

---


