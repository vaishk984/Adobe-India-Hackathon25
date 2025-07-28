# Adobe India Hackathon 2025 – Round 1A & 1B Submission

Welcome to our submission for the **“Connecting the Dots” Challenge** hosted by Adobe. This repository contains our solutions for both **Round 1A** and **Round 1B**, focusing on document understanding and persona-driven intelligence.

---

## Challenge Overview

### Round 1A: Understand Your Document

Build a system that intelligently parses a PDF to extract a **structured document outline**, including:
- **Title**
- **Headings** (`H1`, `H2`, `H3`, etc.) with correct **page numbers** and **hierarchy**

#### Features:
- Processes any PDF (up to 50 pages)
- Output format: standardized `JSON`
- Based on font size and text structure, with logic to clean up noise and merge split headings
- Fully **offline**, Dockerized, and optimized for **CPU-only** inference

---

### Round 1B: Persona-Driven Document Intelligence

Design an AI assistant that extracts the **most relevant sections** from multiple PDFs based on:
- A specific **persona** (e.g., HR, Analyst, Researcher)
- A **job-to-be-done** (e.g., summarize, identify, analyze)

#### Features:
- Supports dynamic document collections (3–10 PDFs)
- Semantic relevance using `sentence-transformers` (MiniLM)
- Ranks important **sections** and extracts detailed **sub-section insights**
- Produces standardized output in required JSON format
- Generalizes to multiple domains (education, research, business, etc.)

---

