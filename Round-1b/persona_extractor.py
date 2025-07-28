import os
import json
import fitz
from sentence_transformers import SentenceTransformer, util
from datetime import datetime

model = SentenceTransformer("all-MiniLM-L6-v2")

INPUT_ROOT = "input"
OUTPUT_ROOT = "output"


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    sections = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("blocks")
        for block in blocks:
            text = block[4].strip()
            if text:
                sections.append({
                    "text": text,
                    "page": page_num + 1
                })
    return sections


def get_similarity_scores(texts, query):
    text_embeddings = model.encode([t["text"] for t in texts], convert_to_tensor=True)
    query_embedding = model.encode(query, convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(query_embedding, text_embeddings)[0]
    return [(texts[i], float(similarities[i])) for i in range(len(texts))]


def process_collection(collection_path):
    persona = "General Analyst"
    job = "Understand key information"
    query = f"{persona} needs to: {job}"

    pdf_dir = collection_path
    output_data = {
        "metadata": {
            "input_documents": [],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": [],
        "subsection_analysis": []
    }

    all_texts = []
    file_map = {}

    for filename in os.listdir(pdf_dir):
        if not filename.lower().endswith(".pdf"):
            continue

        pdf_file = filename
        pdf_path = os.path.join(pdf_dir, pdf_file)

        output_data["metadata"]["input_documents"].append(pdf_file)
        text_chunks = extract_text_from_pdf(pdf_path)
        for chunk in text_chunks:
            all_texts.append({
                "document": pdf_file,
                "section_title": chunk["text"].split("\n")[0],
                "text": chunk["text"],
                "page_number": chunk["page"]
            })
            file_map[pdf_file] = True

    top_sections = get_similarity_scores(all_texts, query)
    top_sections.sort(key=lambda x: x[1], reverse=True)
    top_n = top_sections[:5]

    for i, (section, score) in enumerate(top_n):
        output_data["extracted_sections"].append({
            "document": section["document"],
            "section_title": section["section_title"],
            "importance_rank": i + 1,
            "page_number": section["page_number"]
        })
        output_data["subsection_analysis"].append({
            "document": section["document"],
            "refined_text": section["text"],
            "page_number": section["page_number"]
        })

    output_path = os.path.join(collection_path.replace(INPUT_ROOT, OUTPUT_ROOT), "output.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=4)


if __name__ == "__main__":
    for collection_name in os.listdir(INPUT_ROOT):
        collection_path = os.path.join(INPUT_ROOT, collection_name)
        if os.path.isdir(collection_path):
            process_collection(collection_path)