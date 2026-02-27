"""Quick diagnostic: check ST CS data in the CSV."""
import pandas as pd
import os

base = r"C:\Users\user\OneDrive\Desktop\Vidyāpatha"
df = pd.read_csv(os.path.join(base, "josaa_cleaned_for_embedding.csv"))
df["Closing_Rank_Num"] = pd.to_numeric(df["Closing_Rank_Num"], errors="coerce")

print("=== All unique Seat Types in dataset ===")
print(df["Seat Type"].unique())

print("\n=== ST rows with CS programs ===")
st_cs = df[
    df["Seat Type"].str.startswith("ST", na=False) &
    df["Academic Program Name"].str.contains("Computer Science", case=False, na=False)
]
print(f"Total ST-CS rows: {len(st_cs)}")
print(st_cs[["Institute","Academic Program Name","Seat Type","Closing_Rank_Num"]].head(20).to_string())

print("\n=== ST CS rows with Closing_Rank_Num >= 15000 ===")
eligible = st_cs[st_cs["Closing_Rank_Num"] >= 15000]
print(f"Eligible count: {len(eligible)}")
print(eligible[["Institute","Seat Type","Closing_Rank_Num"]].head(20).to_string())
