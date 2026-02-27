import os
import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def build_index():
    print("Loading data...")
    # Load the cleaned JoSAA dataset
    df = pd.read_csv("../../josaa_cleaned_for_embedding.csv")
    
    # We load the dataframe into langchain documents
    # The 'page_content_column' is the pre-formatted explicit text created for embeddings
    loader = DataFrameLoader(df, page_content_column="embedding_text")
    documents = loader.load()
    
    print("Initializing embeddings model...")
    # Free local open-source embeddings (all-MiniLM-L6-v2 is fast and lightweight)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    print("Building FAISS index...")
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    # Save the index to disk
    vectorstore.save_local("faiss_index")
    print("Index saved successfully to 'faiss_index' directory.")

if __name__ == "__main__":
    os.makedirs("faiss_index", exist_ok=True)
    build_index()
