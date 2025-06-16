import json
import pickle
import faiss
import numpy as np
import requests
from sentence_transformers import SentenceTransformer

INDEX_PATH = "karlsruhe_faiss_db/index.faiss"
DOCS_PATH = "karlsruhe_faiss_db/docs.pkl"
RAW_JSON_PATH = "karlsruhe_rag_docs.json"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_ENDPOINT = "http://localhost:1234/v1/chat/completions"
LLM_MODEL = "mistral-7b-instruct"
MAX_CONTEXT_CHARS = 300
MAX_TOKENS = 150
SIMILARITY_THRESHOLD = 0.7

with open(DOCS_PATH, "rb") as f:
    docs = json.load(f) if DOCS_PATH.endswith(".json") else pickle.load(f)

with open(RAW_JSON_PATH, "r", encoding="utf-8") as f:
    docs_raw = json.load(f)

all_intents = sorted(set(d.get("metadata", {}).get("intent") for d in docs_raw if d.get("metadata", {}).get("intent")))

index = faiss.read_index(INDEX_PATH)
embedder = SentenceTransformer(EMBED_MODEL)

def embed(text):
    return embedder.encode([text])[0].astype(np.float32)

def detect_intent(user_input, all_intents):
    prompt = (
        "You are an intent classifier for municipal services in Karlsruhe.\n"
        "Respond with exactly one intent ID (a lowercase keyword) that best matches the user's request.\n"
        "Do not explain. Do not write anything else. Only respond with the intent.\n"
        "If none apply, respond: unknown.\n\n"
        f"User: {user_input}"
    )

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "max_tokens": 10,
        "temperature": 0.0
    }

    try:
        response = requests.post(LLM_ENDPOINT, json=payload)
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"].strip().lower()
        return content if content in all_intents else None
    except Exception as e:
        print(f"[intent-detect error] {e}")
        return None

history = []

print("\u2753 Stelle deine Frage zu Dienstleistungen in Karlsruhe (zum Beenden: 'exit'):")
while True:
    user_input = input("\U0001F9D1 Frage: ").strip()
    if user_input.lower() == "exit":
        break

    try:
        vector = embed(user_input)

        intent = detect_intent(user_input, all_intents)

        matched_chunks = []
        if intent:
            filtered_docs = [d for d in docs_raw if d.get("metadata", {}).get("intent") == intent]
            for d in filtered_docs:
                vec = embed(d["page_content"])
                sim = np.dot(vector, vec) / (np.linalg.norm(vector) * np.linalg.norm(vec))
                if sim > SIMILARITY_THRESHOLD:
                    matched_chunks.append(d["page_content"][:MAX_CONTEXT_CHARS])
        
        if not matched_chunks:
            D, I = index.search(np.array([vector]), k=5)
            for rank, idx in enumerate(I[0]):
                if D[0][rank] > SIMILARITY_THRESHOLD and idx < len(docs):
                    doc = docs[idx]
                    text = doc[:MAX_CONTEXT_CHARS] if isinstance(doc, str) else doc.get("page_content", "")
                    matched_chunks.append(text.strip())

        context = "\n\n".join(matched_chunks[:3])
        prompt_text = (
            "You are an assistant for municipal services in Karlsruhe. Respond only based on the provided context.\n"
            "Do NOT invent names, places or services. If context is missing, say 'Sorry, I couldn't find information about that.'\n"
            "Answer in the same language as the question. Use 1–3 complete sentences."
            f"Question: {user_input}\n"
            f"Context:\n{context}"
        )


        payload = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "user", "content": prompt_text.strip()}
            ],
            "stream": False,
            "max_tokens": MAX_TOKENS,
            "temperature": 0.3
        }

        response = requests.post(LLM_ENDPOINT, json=payload)
        response.raise_for_status()
        result = response.json()

        content = result["choices"][0]["message"]["content"]
        print("\U0001F916 Antwort:", content.strip(), "\n")

        history.append((user_input, content.strip()))
        if len(history) > 3:
            history.pop(0)

    except Exception as e:
        print(f"\n\u274C Fehler: {e}\n")
