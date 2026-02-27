from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import pandas as pd

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from agent.scoring import calculate_probability, calculate_tier_weight

app = FastAPI(title="Vidyāpatha College Admission AI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

embeddings  = None
vectorstore = None
df_all      = None   # Full JoSAA dataset for exact filtering


@app.on_event("startup")
async def startup_event():
    global embeddings, vectorstore, df_all

    print("Loading Embeddings and FAISS Index...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    try:
        idx_path = r"C:\faiss_index"   # ASCII path — avoids FAISS C++ Unicode bug on Windows
        vectorstore = FAISS.load_local(idx_path, embeddings, allow_dangerous_deserialization=True)
        print("FAISS index loaded.")
    except Exception as e:
        print(f"Warning: FAISS index not loaded — {e}. Run indexer.py first.")

    # Load the full CSV for exact pandas filtering (category / rank)
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path   = os.path.normpath(os.path.join(script_dir, "..", "josaa_cleaned_for_embedding.csv"))
        df_all = pd.read_csv(csv_path)
        df_all["Closing_Rank_Num"]  = pd.to_numeric(df_all["Closing_Rank_Num"],  errors="coerce")
        df_all["Opening_Rank_Num"]  = pd.to_numeric(df_all["Opening_Rank_Num"],  errors="coerce")
        df_all = df_all.dropna(subset=["Closing_Rank_Num"])
        print(f"Dataset loaded: {len(df_all)} rows.")
    except Exception as e:
        print(f"Warning: Could not load CSV — {e}")


class RecommendRequest(BaseModel):
    rank:       int
    category:   str
    branch:     str
    gender:     str
    home_state: str = "Telangana"


@app.post("/recommend")
async def get_recommendations(req: RecommendRequest):
    if not vectorstore:
        return {"error": "Vector store not initialized. Run indexer.py first."}
    if df_all is None:
        return {"error": "Dataset not loaded."}

    # ── Step 1: FAISS semantic search for branch matching ───────────────────
    docs = vectorstore.similarity_search(req.branch, k=500)

    relevant_programs = set()
    for doc in docs:
        prog = doc.metadata.get("Academic Program Name", "")
        if prog:
            relevant_programs.add(prog)

    # ── Step 2: Build keyword filter from branch name ────────────────────────
    # Extract meaningful keywords from the branch (drop generic words)
    STOP_WORDS = {"and", "or", "of", "the", "in", "engineering", "technology", "science"}
    branch_keywords = [
        w.lower() for w in req.branch.split()
        if w.lower() not in STOP_WORDS and len(w) > 2
    ]

    def program_matches_branch(prog_name: str) -> bool:
        """True if at least ONE key branch word appears in the program name."""
        prog_lower = prog_name.lower()
        return any(kw in prog_lower for kw in branch_keywords)

    # ── Step 2b: Gender Filter ──────────────────────────────────────────────
    # Female candidates are eligible for BOTH Female-only AND Gender-Neutral.
    # Others are eligible ONLY for Gender-Neutral.
    if req.gender.lower() == "female":
        gender_mask = df_all["Gender"].notna()  # i.e., True for all rows
    else:
        gender_mask = df_all["Gender"] == "Gender-Neutral"

    # ── Step 3: Exact pandas filtering ──────────────────────────────────────
    # Filters: relevant FAISS programs  AND  keyword-matching program names
    #          AND exact Seat Type startswith category   AND rank eligibility
    df_filtered = df_all[
        df_all["Academic Program Name"].isin(relevant_programs) &
        df_all["Academic Program Name"].apply(program_matches_branch) &
        df_all["Seat Type"].str.startswith(req.category, na=False) &
        gender_mask &
        (df_all["Closing_Rank_Num"] >= req.rank)
    ].copy()

    # Fallback: if keyword filter is too strict, widen to just category + rank + gender
    if df_filtered.empty:
        df_filtered = df_all[
            df_all["Academic Program Name"].apply(program_matches_branch) &
            df_all["Seat Type"].str.startswith(req.category, na=False) &
            gender_mask &
            (df_all["Closing_Rank_Num"] >= req.rank)
        ].copy()

    if df_filtered.empty:
        return {"recommendations": [], "total_found": 0}

    # ── Step 3: Aggregate across rounds (keep worst closing / best opening) ──
    agg = (
        df_filtered
        .groupby(["Institute", "Academic Program Name", "Seat Type"])
        .agg(
            closing_rank=("Closing_Rank_Num", "max"),
            opening_rank=("Opening_Rank_Num", "min"),
        )
        .reset_index()
    )

    # ── Step 4: Score each candidate ────────────────────────────────────────
    results = []
    for _, row in agg.iterrows():
        prob_str, prob_score = calculate_probability(
            req.rank, row["closing_rank"], row["opening_rank"]
        )
        tier  = calculate_tier_weight(row["Institute"])
        score = prob_score + (tier * 5)

        results.append({
            "institute":         row["Institute"],
            "branch":            row["Academic Program Name"],
            "category":          row["Seat Type"],
            "probability":       round(prob_score, 2),
            "probability_label": prob_str,
            "score":             round(score, 2),
            "closing_rank":      int(row["closing_rank"]),
            "reason": (
                f"Your rank ({req.rank:,}) qualifies under the {req.category} closing rank of "
                f"{int(row['closing_rank']):,}. Admission chance: {prob_str} ({prob_score:.1f}%)."
            ),
        })

    top = sorted(results, key=lambda x: x["score"], reverse=True)[:8]
    return {"recommendations": top, "total_found": len(results)}
