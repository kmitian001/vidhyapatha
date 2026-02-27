from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import faiss

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from agent.scoring import ScoringEngine

app = FastAPI(title="Vidyāpatha College Admission AI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for embeddings and vector store
embeddings = None
vectorstore = None

@app.on_event("startup")
async def startup_event():
    global embeddings, vectorstore
    print("Loading Embeddings and FAISS Index...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    try:
        # Load local FAISS index
        idx_path = os.path.join(os.path.dirname(__file__), "rag", "faiss_index")
        vectorstore = FAISS.load_local(idx_path, embeddings, allow_dangerous_deserialization=True)
        print("Index loaded successfully.")
    except Exception as e:
        print(f"Warning: FAISS index could not be loaded: {e}. Make sure to run indexer.py first.")

class RecommendRequest(BaseModel):
    rank: int
    category: str
    branch: str
    budget: int
    home_state: str = "Telangana"

@app.post("/recommend")
async def get_recommendations(req: RecommendRequest):
    if not vectorstore:
        return {"error": "Vector store not initialized. Run the indexer script first."}

    # 1. RAG Retrieve matching colleges based strictly on branch & category
    query = f"{req.branch} {req.category} category"
    docs = vectorstore.similarity_search(query, k=15)
    
    # 2. Extract and Filter data
    scored_candidates = []
    
    for doc in docs:
        row = doc.metadata
        # Check quota (simplified logic)
        quota = "Home State" if row.get("location") == req.home_state else "Other State"
        if row.get("quota") != "All India" and row.get("quota") != quota:
            continue
            
        # Hard Filter
        c_rank = float(row.get("closing_rank", 0))
        fee = float(row.get("tuition_fee", 0))
        
        if ScoringEngine.check_eligibility(req.rank, c_rank, req.budget, fee):
            # 3. Score Valid Candidates
            score = ScoringEngine.score_college(row, req.rank, req.budget)
            prob = ScoringEngine.calculate_probability(req.rank, c_rank)
            
            # Format recommendation
            scored_candidates.append({
                "institute": row.get("institute"),
                "branch": row.get("branch"),
                "category": row.get("category"),
                "probability": prob,
                "fee": fee,
                "score": score,
                "closing_rank": c_rank,
                "reason": f"Rank {req.rank} is below the {req.category} cutoff of {c_rank}. Admission is highly probable ({prob}%)."
            })
            
    # 4. Rank by our computed score and take top 5
    top_recommendations = sorted(scored_candidates, key=lambda x: x["score"], reverse=True)[:5]
    
    return {"recommendations": top_recommendations}
