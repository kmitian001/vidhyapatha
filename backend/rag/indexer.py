import os
import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def build_index():
    print("Loading data...")
    # Resolve all paths absolutely from this file's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # IMPORTANT: FAISS C++ library cannot handle Unicode paths on Windows.
    # The project path contains 'ā' so we save the index to a plain ASCII path.
    csv_path = os.path.normpath(os.path.join(script_dir, "..", "..", "josaa_cleaned_for_embedding.csv"))
    save_path = r"C:\faiss_index"
    
    print(f"  CSV path: {csv_path}")
    print(f"  Save path: {save_path}")
    
    df = pd.read_csv(csv_path)
    
    # We load the dataframe into langchain documents
    loader = DataFrameLoader(df, page_content_column="embedding_text")
    documents = loader.load()
    print(f"  Loaded {len(documents)} documents.")
    
    print("Initializing embeddings model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    print("Building FAISS index...")
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    # Ensure save directory exists before writing
    os.makedirs(save_path, exist_ok=True)
    vectorstore.save_local(save_path)
    print(f"Index saved successfully to '{save_path}'.")

if __name__ == "__main__":
    build_index()
