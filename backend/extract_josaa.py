import os
import pandas as pd
from bs4 import BeautifulSoup
import csv

# We are using BeautifulSoup to parse manually just in case pandas.read_html fails or misses data
# because sometimes large HTML files with slightly malformed tags can crash pandas read_html

files = {
    '1': 'rounnd1.html',
    '2': 'round 2.html',
    '3': 'round 3.html',
    '4': 'round 4.html'
}

base_dir = r'c:\Users\user\OneDrive\Desktop\Vidyāpatha'
output_path = os.path.join(base_dir, 'josaa_all_rounds.csv')

headers = [
    "Institute", 
    "Academic Program Name", 
    "Quota", 
    "Seat Type", 
    "Gender", 
    "Opening Rank", 
    "Closing Rank", 
    "Round"
]

all_data = []

for round_num, filename in files.items():
    filepath = os.path.join(base_dir, filename)
    print(f"Processing {filename}...")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        table = soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_GridView1'})
        if not table:
            print(f"Table not found in {filepath}")
            continue
            
        rows = table.find_all('tr')
        # Skip header row (index 0)
        parsed_rows = 0
        for row in rows[1:]:
            cols = row.find_all(['td', 'th'])
            # Ensure it is a data row (7 columns)
            if len(cols) >= 7:
                row_data = [col.get_text(strip=True) for col in cols[:7]]
                row_data.append(round_num)
                all_data.append(row_data)
                parsed_rows += 1
                
        print(f"Extracted {parsed_rows} rows from {filename}")
        
    except Exception as e:
        print(f"Error reading {filename}: {e}")

# Write to CSV
with open(output_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(all_data)

print(f"Successfully saved {len(all_data)} rows to {output_path}")
