"""Quick debug script to inspect FAISS metadata fields."""
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import json

print("Loading embeddings model...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

print("Loading FAISS index...")
vectorstore = FAISS.load_local(r"C:\faiss_index", embeddings, allow_dangerous_deserialization=True)

query = "Computer Science OPEN category"
print(f"\nQuerying: '{query}'")
docs = vectorstore.similarity_search(query, k=5)

print("\n=== FIRST 5 DOCUMENTS METADATA ===")
for i, doc in enumerate(docs):
    print(f"\n--- Doc {i+1} ---")
    print(json.dumps(doc.metadata, indent=2, default=str))
