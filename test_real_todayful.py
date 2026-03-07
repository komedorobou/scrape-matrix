"""Real todayful data - full pipeline test"""
import sys, io, os, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from app import extract_unique_hinban, lookup_official_names, enrich_mapping_with_kde

df = pd.read_excel(r'C:\Users\komed\Downloads\allsites_todayful_20260223_231740.xlsx')
print(f"Total: {len(df)} rows")
print(f"Sites: {dict(df['サイト'].value_counts())}")

# Check RAGTAG data quality
ragtag = df[df['サイト'] == 'RAGTAG']
ragtag_has_name = ragtag['商品名'].notna().sum()
ragtag_has_hinban = ragtag['品番'].notna().sum()
print(f"\nRAGTAG: {len(ragtag)} rows, 商品名あり={ragtag_has_name}, 品番あり={ragtag_has_hinban}")

# Unique hinban
unique = extract_unique_hinban(df)
print(f"\nUnique 品番: {len(unique)}")
print(f"First 20: {unique[:20]}")

# Run full pipeline: local + WEAR (no DDG/Brave)
print(f"\n{'='*80}")
print("Running lookup: Phase 1 (Local) + Phase 2a (WEAR)")
print(f"{'='*80}")

def progress(cur, tot, msg):
    print(f"  {msg}")

start = time.perf_counter()
mapping_df = lookup_official_names(
    df, "todayful",
    max_lookup=100,  # first 100 hinbans
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

# KDE analysis
print(f"\n{'='*80}")
print("KDE Price Analysis + Filter (>10000)")
print(f"{'='*80}")
enriched, filtered = enrich_mapping_with_kde(df, mapping_df, min_price=10000)
excluded = len(enriched) - len(filtered) - empty_count
print(f"  Before filter: {total - empty_count} items with names")
print(f"  KDE excluded:  {excluded} items (<=10000)")
print(f"  After filter:  {len(filtered[filtered['正式名称'] != ''])} items")

# Show filtered results
print(f"\n{'品番':<12} {'正式名称':<50} {'ソース':<8} {'件数':>4} {'KDE':>8} {'価格レンジ'}")
print("-" * 110)
for _, row in filtered.iterrows():
    if row['正式名称']:
        kde_str = f"¥{row['KDE代表価格']:,.0f}" if row['KDE代表価格'] > 0 else "---"
        print(f"  {row['品番']:<10} {row['正式名称']:<48} {row['ソース']:<8} {row['件数']:>4} {kde_str:>8} {row['価格レンジ']}")

# Show some WEAR-sourced items specifically
print(f"\n{'='*80}")
print(f"WEAR sourced items ({wear_count}):")
print(f"{'='*80}")
wear_items = filtered[filtered['ソース'] == 'WEAR']
for _, row in wear_items.iterrows():
    kde_str = f"¥{row['KDE代表価格']:,.0f}" if row['KDE代表価格'] > 0 else "---"
    print(f"  {row['品番']:<10} {row['正式名称']:<50} {kde_str}")
