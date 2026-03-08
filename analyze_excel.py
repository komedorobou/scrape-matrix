"""Analyze the allsites todayful Excel file"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd

df = pd.read_excel(r'C:\Users\komed\Downloads\allsites_todayful_20260223_231740.xlsx')

print(f"Total rows: {len(df)}")
print(f"Columns: {list(df.columns)}")

# Site breakdown
if 'サイト' in df.columns:
    print(f"\nSite breakdown:")
    for site, count in df['サイト'].value_counts().items():
        print(f"  {site}: {count}")

# 品番/型番 stats
for col in ['品番', '型番']:
    if col in df.columns:
        non_null = df[col].notna().sum()
        unique = df[col].dropna().nunique()
        print(f"\n{col}: {non_null} non-null, {unique} unique")

# Sample data per site
if 'サイト' in df.columns:
    for site in df['サイト'].unique():
        site_df = df[df['サイト'] == site]
        print(f"\n{'='*60}")
        print(f"Sample from {site} (first 3):")
        print(f"{'='*60}")
        for i, (_, row) in enumerate(site_df.head(3).iterrows()):
            print(f"  商品名: {row.get('商品名', '')}")
            print(f"  品番: {row.get('品番', '')} / 型番: {row.get('型番', '')}")
            print(f"  通称: {row.get('通称', '')}")
            print(f"  価格: {row.get('価格', '')}")
            print()

# Price stats
if '価格' in df.columns:
    print(f"\nPrice stats:")
    print(f"  Mean: ¥{df['価格'].mean():,.0f}")
    print(f"  Min:  ¥{df['価格'].min():,.0f}")
    print(f"  Max:  ¥{df['価格'].max():,.0f}")
