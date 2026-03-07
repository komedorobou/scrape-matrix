"""Compare old vs new hinban sort order"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from collections import Counter

df = pd.read_excel(r'C:\Users\komed\Downloads\allsites_todayful_20260223_231740.xlsx')

# Old: sorted alphabetically
from app import _is_valid_hinban
old_candidates = set()
for val in df["品番"].dropna().unique():
    v = str(val).strip()
    if _is_valid_hinban(v):
        old_candidates.add(v)
old_sorted = sorted(old_candidates)

# New: sorted by frequency
from app import extract_unique_hinban
new_sorted = extract_unique_hinban(df)

print("Old (alphabetical) first 20:")
for h in old_sorted[:20]:
    count = len(df[df['品番'].astype(str).str.strip() == h])
    print(f"  {h:<15} ({count} listings)")

print(f"\nNew (frequency) first 20:")
for h in new_sorted[:20]:
    count = len(df[df['品番'].astype(str).str.strip() == h])
    print(f"  {h:<15} ({count} listings)")

print(f"\nOld first 200: {old_sorted[:3]}...{old_sorted[197:200]}")
print(f"New first 200: {new_sorted[:3]}...{new_sorted[197:200]}")

# Check how many of first 200 are 2020+ items
old_new_count = sum(1 for h in old_sorted[:200] if h.startswith('12'))
new_new_count = sum(1 for h in new_sorted[:200] if h.startswith('12'))
print(f"\nFirst 200 - items from 2020+:")
print(f"  Old sort: {old_new_count}/200")
print(f"  New sort: {new_new_count}/200")
