from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

print("Loading embeddings model...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

print("Loading FAISS index...")
vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

test_scenarios = [
    {
        "description": "Top Scorer targeting CS",
        "query": "My rank is 500 in the OPEN category for Gender-Neutral. I want to study Computer Science and Engineering. Which colleges can I get into?"
    },
    {
        "description": "Mid-tier rank targeting Mechanical in NITs",
        "query": "I have a rank of 25000 in the OBC-NCL category. I am looking for Mechanical Engineering. What are my options?"
    },
    {
        "description": "Lower rank targeting any decent branch",
        "query": "My rank is 55000 in the OPEN category. What B.Tech programs can I get into with this rank?"
    }
]

print("\n--------------------------------------------------")
print("TESTING VECTOR SEARCH WITH ASSUMED STUDENT PROFILES")
print("--------------------------------------------------\n")

for scenario in test_scenarios:
    print(f"--- Scenario: {scenario['description']} ---")
    print(f"Query: '{scenario['query']}'")
    
    # Retrieve top 4 most relevant matches
    docs = vectorstore.similarity_search(scenario['query'], k=4)
    
    print("\nResults found in Vector DB:")
    for i, doc in enumerate(docs):
        print(f"  {i+1}. {doc.page_content}")
    print("\n" + "="*80 + "\n")
