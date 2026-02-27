import os
import warnings
import math
import logging
import pandas as pd
import logging
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

warnings.filterwarnings('ignore')
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_choice(options, prompt="Select an option (Press Enter for Default/Any): ", default_val="ANY"):
    """ Prompts the user to select from a list or hit Enter for a default wildcard. """
    print(f"0. ANY (Default)")
    for idx, opt in enumerate(options, 1):
        print(f"{idx}. {opt}")
    
    while True:
        choice_str = input(f"\n{prompt}").strip()
        
        # User pressed enter -> wildcard behavior
        if not choice_str or choice_str == '0':
            return default_val
            
        try:
            choice = int(choice_str)
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print("Invalid choice. Please select a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number or press Enter.")

def calculate_probability(user_rank, closing_rank, opening_rank=1):
    """
    Standard algorithm to calculate probability.
    """
    try:
        ur = float(user_rank)
        cr = float(closing_rank)
        op = float(opening_rank)
        
        if ur > (1.05 * cr): # Out of bounds
            return "Highly Unlikely", 5.0
            
        if ur <= op: # Better than opening rank
            return "Guaranteed", 99.0
            
        if ur <= cr:
            # Scale probability between 75% and 95% based on how far from closing
            fraction = (cr - ur) / (cr - op) if (cr - op) > 0 else 0
            prob = 75.0 + (fraction * 20.0) 
            
            if prob >= 90.0:
                return "Very Safe", round(prob, 2)
            else:
                return "Likely", round(prob, 2)
        else:
            # Between closing and 1.05x closing - risky (spot rounds)
            fraction = (1.05 * cr - ur) / (0.05 * cr) if (0.05 * cr) > 0 else 0
            prob = 20.0 + (fraction * 50.0) # Scale between 20% and 70%
            return "Borderline/Risky", round(prob, 2)
    except:
        return "Unknown", 0.0

def calculate_tier_weight(institute_name):
    """
    Priority sorting for colleges 
    """
    name = institute_name.lower()
    if 'indian institute  of technology' in name:
        return 5
    elif 'national institute of technology' in name:
        return 4
    elif 'indian institute of information technology' in name:
        return 3
    else:
        return 1

def main():
    clear_screen()
    print("=========================================================")
    print("  Vidyapatha College Recommender | RAG VECTOR DB ENGINE  ")
    print("=========================================================\n")
    
    # LOAD VECTOR DATABASE (RAG)
    print("Initializing HuggingFace Embedding Model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Resolve relative path to avoid FAISS C++ absolute path unicode bugs on Windows
    script_dir = os.path.dirname(os.path.abspath(__file__))
    faiss_abs = os.path.join(os.path.dirname(script_dir), "rag", "faiss_index")
    faiss_path = os.path.relpath(faiss_abs, start=os.getcwd())
    
    if not os.path.exists(faiss_path):
        print(f"Error: FAISS Vector DB not found at the expected path.")
        return

    print("Loading FAISS Knowledge Base Memory...")
    vectorstore = FAISS.load_local(faiss_path, embeddings, allow_dangerous_deserialization=True)
    
    # 1. Get User Rank
    while True:
        try:
            user_rank = int(input("\nEnter your Rank (e.g., 5000): "))
            if user_rank > 0:
                break
            print("Rank must be positive.")
        except ValueError:
            print("Please enter a valid numeric rank.")

    # Distinct categories logic can still be mapped but hardcoding the standard lists for efficiency in RAG flow
    quotas = ["AI", "HS", "OS"]
    categories = ["OPEN", "OBC-NCL", "EWS", "SC", "ST"]
    genders = ["Gender-Neutral", "Female-only (including Supernumerary)"]

    print("\n--------------------------------------------------------------")
    print("Optional Parameters (Press ENTER on any of these to skip/allow ANY)")
    print("--------------------------------------------------------------")

    # 2. Get Quota
    print("\n--- Select Quota ---")
    selected_quota = get_choice(quotas)

    # 3. Get Category
    print("\n--- Select Category ---")
    print("    Note: Default is 'OPEN' for Category if left blank.")
    selected_category = get_choice(categories, default_val="OPEN")

    # 4. Get Gender
    print("\n--- Select Gender ---")
    print("    Note: Default is 'Gender-Neutral' if left blank.")
    selected_gender = get_choice(genders, default_val="Gender-Neutral")

    # 5. Program search
    preferred_program = input("\nEnter keywords for preferred program (1 keyword max, or press Enter to skip): ").strip()

    # == DYNAMIC SEMANTIC QUERY GENERATION ==
    query_parts = []
    
    if preferred_program:
        query_parts.append(preferred_program)
    else:
        query_parts.append("B.Tech") # generic fallback if no program specified
        
    if selected_quota != "ANY":
        query_parts.append(f"{selected_quota} quota")
        
    if selected_category != "ANY":
        query_parts.append(f"{selected_category} category")
        
    if selected_gender != "ANY":
        query_parts.append(f"{selected_gender}")

    semantic_query = " ".join(query_parts)
    print(f"\n[RAG] Shooting Semantic Lookup Query: '{semantic_query}' ...\n")

    # Extrapolate Top 100 closest documents from Vector DB to give us a large enough mathematical pool
    retrieved_docs = vectorstore.similarity_search(semantic_query, k=150)
    
    if not retrieved_docs:
        print("Error: The Vector search returned zero documents.")
        return

    print(f"[RAG] Successfully retrieved {len(retrieved_docs)} nearest semantic vectors. Calculating statistical probability...")
    
    results = {}
    
    # Iterate through RAG outputs and do pure math on the payloads
    for doc in retrieved_docs:
        meta = doc.metadata
        
        # Hard extract payload variables mapped from original DataFrame serialization
        inst = str(meta.get('Institute', 'Unknown'))
        prog = str(meta.get('Academic Program Name', 'Unknown'))
        
        # FAISS extracted metrics
        closing = meta.get('Closing_Rank_Num')
        opening = meta.get('Opening_Rank_Num')
        doc_category = str(meta.get('Seat Type', ''))
        doc_quota = str(meta.get('Quota', ''))
        doc_gender = str(meta.get('Gender', ''))
        
        # We retrieved nearest matches, but we still apply absolute boundaries
        # Vector Similarity might fetch an 'OBC' document when we asked for 'OPEN' if it was highly similar textually.
        # We hard-reject documents that explicitly violate our criteria
        if selected_category != "ANY" and selected_category not in doc_category:
            continue
        if selected_quota != "ANY" and selected_quota not in doc_quota:
            continue
        if selected_gender != "ANY" and selected_gender not in doc_gender:
            continue

        if pd.isna(closing) or pd.isna(opening):
            continue
            
        closing = float(closing)
        opening = float(opening)
        
        # Aggregate max boundaries for duplicate/multi-round document overlaps
        key = f"{inst} | {prog}"
        if key not in results:
            results[key] = {
                'Institute': inst,
                'Program': prog,
                'Closing': closing,
                'Opening': opening
            }
        else:
            if closing > results[key]['Closing']:
                results[key]['Closing'] = closing
            if opening < results[key]['Opening']:
                results[key]['Opening'] = opening

    # Calculate actual probabilities
    scored_results = []
    for payload in results.values():
        prob_str, prob_score = calculate_probability(user_rank, payload['Closing'], payload['Opening'])
        
        if prob_score >= 65.0:  # Adjusting to only Safe/Likely
            tier_weight = calculate_tier_weight(payload['Institute'])
            
            scored_results.append({
                'Institute': payload['Institute'],
                'Program': payload['Program'],
                'Historical_Closing': int(payload['Closing']),
                'Probability_Str': prob_str,
                'Score': prob_score,
                'Tier_Weight': tier_weight
            })

    # Sort Results intelligently
    scored_results = sorted(scored_results, key=lambda x: (-x['Score'], -x['Tier_Weight'], x['Historical_Closing']))

    if not scored_results:
        print(f"\n[RAG] After filtering the Top 150 Semantic Matches for {selected_category} category (Rank {user_rank}), there are no highly probable admissions.")
        return

    # Cap Output
    top_results = scored_results[:15] 

    print("\n" + "="*125)
    print(f"{'Safe Chance %':<15} | {'Closing Rank':<12} | {'Institute':<35} | {'Program'}")
    print("="*125)
    
    for r in top_results:
        inst = r['Institute'][:32] + ".." if len(r['Institute']) > 35 else r['Institute']
        prog_split = r['Program'].split(' (')
        prog = prog_split[0][:40] + ".." if len(prog_split[0]) > 42 else prog_split[0]
        
        # Format percentage nicely
        color_tag = "[SAFE] " if r['Score'] >= 90 else "[LIKE] "
        percent_str = f"{color_tag}{r['Score']}%"
        
        print(f"{percent_str:<15} | {r['Historical_Closing']:<12} | {inst:<35} | {prog}")
    
    print("\n=============================================================================================================================")
    print(" These are the mathematically SAFEST options explicitly derived from HuggingFace Vector RAG Knowledge Base Payloads ")
    print("=============================================================================================================================\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting Engine...")
