"""Real todayful data - full pipeline test (ALL hinbans)"""
import sys, io, os, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from app import extract_unique_hinban, lookup_official_names, enrich_mapping_with_kde

df = pd.read_excel(r'C:\Users\komed\Downloads\allsites_todayful_20260223_231740.xlsx')
print(f"Total: {len(df)} rows")

unique = extract_unique_hinban(df)
print(f"Unique hinbans: {len(unique)}")

def progress(cur, tot, msg):
    print(f"  {msg}")

start = time.perf_counter()
mapping_df = lookup_official_names(
    df, "todayful",
    max_lookup=9999,  # ALL hinbans
    wear_search=True,
    web_search=False,
    progress_callback=progress,
)
elapsed = time.perf_counter() - start

print(f"\nCompleted in {elapsed:.1f}s")

# Stats
local_count = (mapping_df['ソース'] == 'ローカル').sum()
wear_count = (mapping_df['ソース'] == 'WEAR').sum()
empty_count = (mapping_df['正式名称'] == '').sum()
total = len(mapping_df)
print(f"\nResults: {total} items")
print(f"  Local:  {local_count} ({local_count/total*100:.0f}%)")
print(f"  WEAR:   {wear_count} ({wear_count/total*100:.0f}%)")
print(f"  Empty:  {empty_count} ({empty_count/total*100:.0f}%)")

# KDE
print(f"\n{'='*80}")
print("KDE Price Analysis + Filter (>10000)")
print(f"{'='*80}")
enriched, filtered = enrich_mapping_with_kde(df, mapping_df, min_price=10000)
named = enriched[enriched['正式名称'] != '']
excluded = len(named) - len(filtered[filtered['正式名称'] != ''])
print(f"  Before filter: {len(named)} items with names")
print(f"  KDE excluded:  {excluded} items (<=10000)")
print(f"  After filter:  {len(filtered[filtered['正式名称'] != ''])} items")

# Show WEAR results
print(f"\n{'='*80}")
print(f"WEAR sourced items ({wear_count}):")
print(f"{'='*80}")
wear_items = filtered[filtered['ソース'] == 'WEAR']
for _, row in wear_items.head(30).iterrows():
    kde_str = f"Y{row['KDE代表価格']:,.0f}" if row['KDE代表価格'] > 0 else "---"
    print(f"  {row['品番']:<10} {row['正式名称']:<50} {kde_str}")

# Show all filtered results
print(f"\n{'='*80}")
print(f"Filtered items (KDE > 10000):")
print(f"{'='*80}")
for _, row in filtered.iterrows():
    if row['正式名称']:
        kde_str = f"Y{row['KDE代表価格']:,.0f}" if row['KDE代表価格'] > 0 else "---"
        print(f"  {row['品番']:<10} {row['正式名称']:<50} {row['ソース']:<8} {row['件数']:>3} {kde_str:>8}")
