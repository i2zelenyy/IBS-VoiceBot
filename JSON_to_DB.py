from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import pickle
import json

with open("karlsruhe_rag_docs.json", "r", encoding="utf-8") as f:
    data = json.load(f)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

documents = [
    Document(page_content=item["page_content"], metadata=item["metadata"])
    for item in data
]

vectorstore = FAISS.from_documents(documents, embeddings)

vectorstore.save_local("karlsruhe_faiss_db")

with open("karlsruhe_faiss_db/docs.pkl", "wb") as f:
    pickle.dump([doc.page_content for doc in documents], f)
