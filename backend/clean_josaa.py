import pandas as pd
import os

input_file = r'c:\Users\user\OneDrive\Desktop\Vidyāpatha\josaa_all_rounds.csv'
output_file = r'c:\Users\user\OneDrive\Desktop\Vidyāpatha\josaa_cleaned_for_embedding.csv'

# Load the data
print("Loading data...")
df = pd.read_csv(input_file)

# 1. Inspect and Handle Nulls
initial_count = len(df)
df = df.dropna()
print(f"Removed {initial_count - len(df)} rows with null values.")

# 2. Handle irrelevant issues like 'P' suffix in ranks
# 'P' indicates Preparatory Rank List
print("Handling 'P' (Preparatory Rank) suffixes...")
df['Is_Preparatory_Opening'] = df['Opening Rank'].astype(str).str.endswith('P')
df['Is_Preparatory_Closing'] = df['Closing Rank'].astype(str).str.endswith('P')

df['Opening_Rank_Num'] = df['Opening Rank'].astype(str).str.replace('P', '', regex=False).astype(float)
df['Closing_Rank_Num'] = df['Closing Rank'].astype(str).str.replace('P', '', regex=False).astype(float)

# Function to build comprehensive embedded text
def build_embedding_text(row):
    open_rank = f"{int(row['Opening_Rank_Num'])} (Preparatory Rank)" if row['Is_Preparatory_Opening'] else str(int(row['Opening_Rank_Num']))
    close_rank = f"{int(row['Closing_Rank_Num'])} (Preparatory Rank)" if row['Is_Preparatory_Closing'] else str(int(row['Closing_Rank_Num']))
    
    # A clear, declarative sentence structure works well for embeddings and retrieval
    text = (f"In Round {row['Round']} of JoSAA counseling, the cutoff for the {row['Academic Program Name']} "
            f"program at {row['Institute']} under the {row['Quota']} quota, {row['Seat Type']} category, "
            f"and {row['Gender']} gender had an Opening Rank of {open_rank} and a Closing Rank of {close_rank}.")
    return text

# 3. Create 'embedding_text' column
print("Generating explicit text for embeddings...")
df['embedding_text'] = df.apply(build_embedding_text, axis=1)

# Drop intermediate boolean columns to keep it clean, though they might be useful
df = df.drop(columns=['Is_Preparatory_Opening', 'Is_Preparatory_Closing'])

# Save cleaned output
df.to_csv(output_file, index=False)
print(f"Successfully processed and saved {len(df)} rows.")

print("\nSample embedding text generated:")
print(df['embedding_text'].iloc[0])
print(df['embedding_text'].iloc[150]) # Let's print another record just in case
