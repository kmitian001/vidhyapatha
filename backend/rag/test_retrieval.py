from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

print("Loading embeddings model...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

print("Loading FAISS index...")
vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

query = "What is the cutoff for Computer Science at IIT Bombay?"
print(f"\nQuerying: '{query}'")

docs = vectorstore.similarity_search(query, k=3)

for i, doc in enumerate(docs):
    print(f"\n--- Result {i+1} ---")
    print(doc.page_content)
