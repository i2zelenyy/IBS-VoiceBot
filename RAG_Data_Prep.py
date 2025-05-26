import pandas as pd
import json
import re

df = pd.read_csv("Crawler/karlsruhe_rag_full.csv")

required_columns = ["title", "short_description", "full_text"]
if not all(col in df.columns for col in required_columns):
    raise ValueError("CSV must have columns: title, short_description, full_text")

def split_by_sections(text):
    pattern = r"(##\s+.+)"
    parts = re.split(pattern, text)
    
    sections = []
    current_section = "Einleitung"
    buffer = parts[0].strip()

    if buffer:
        sections.append((current_section, buffer))

    for i in range(1, len(parts), 2):
        header = parts[i].strip(" #")
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""
        sections.append((header, body))

    return sections

documents = []
for _, row in df.iterrows():
    title = row['title']
    intent = title.lower().replace(" ", "_")
    short = row['short_description'].strip()
    full = row['full_text'].strip()

    full_text = f"{short}\n\n{full}"
    sections = split_by_sections(full_text)

    for i, (section_title, content) in enumerate(sections):
        if not content.strip():
            continue
        documents.append({
            "page_content": f"{section_title}\n\n{content}",
            "metadata": {
                "title": title,
                "intent": title.lower().replace(" ", "_"),
                "section": section_title,
                "chunk_id": i
            }
        })

with open("karlsruhe_rag_docs.json", "w", encoding="utf-8") as f:
    json.dump(documents, f, ensure_ascii=False, indent=2)

print(f"✅ Saved {len(documents)} structured RAG-ready docs into karlsruhe_rag_docs.json")
