import os
import json
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer, util
from datetime import datetime, timezone

import warnings
warnings.filterwarnings("ignore", category = FutureWarning)


MODEL_PATH = './models/all-MiniLM-L6-v2'   
INPUT_DIR = './input'            
PDF_DIR = os.path.join(INPUT_DIR, 'PDFs')
OUTPUT_FILE = './output/challenge1b_output.json'  
INPUT_JSON = os.path.join(INPUT_DIR, 'challenge1b_input.json')

model = SentenceTransformer(MODEL_PATH)

def extract_candidate_sections(pdf_path):
    reader = PdfReader(pdf_path)
    candidates = []
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            for i, line in enumerate(lines[:3]):
                candidates.append({
                    'document': os.path.basename(pdf_path),
                    'page': page_num + 1,
                    'section_title': line,
                    'full_text': text})
    return candidates

def rank_sections(candidates, persona, job):
    combined_query = persona + ". " + job
    query_embedding = model.encode(combined_query, convert_to_tensor=True)

    section_embeddings = model.encode(
        [c['section_title'] for c in candidates],
        convert_to_tensor=True
    )

    similarities = util.cos_sim(query_embedding, section_embeddings)[0]

    for i, score in enumerate(similarities):
        candidates[i]['score'] = score.item()

    ranked = sorted(candidates, key=lambda x: x['score'], reverse=True)
    return ranked

def main():
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        input_data = json.load(f)

    persona = input_data.get('persona', {}).get('role', '')
    job = input_data.get('job_to_be_done', {}).get('task', '')
    document_files = input_data.get('documents', [])

    all_candidates = []
    for doc in document_files:
        filename = doc.get('filename')
        pdf_path = os.path.join(PDF_DIR, filename)
        candidates = extract_candidate_sections(pdf_path)
        all_candidates.extend(candidates)

    ranked_sections = rank_sections(all_candidates, persona, job)
    top_sections = ranked_sections[:5]
    output = {
        "metadata": {
            "input_documents": [doc.get('filename') for doc in document_files],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.now(timezone.utc).isoformat()
        },
        "extracted_sections": [],
        "sub_section_analysis": []
    }

    for rank, sec in enumerate(top_sections, 1):
        output["extracted_sections"].append({
            "document": sec['document'],
            "page_number": sec['page'],
            "section_title": sec['section_title'],
            "importance_rank": rank
        })
        refined = sec['full_text'][:200].replace('\n', ' ')
        output["sub_section_analysis"].append({
            "document": sec['document'],
            "page_number": sec['page'],
            "refined_text": refined
        })

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)  
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
