"""Test 3-sheet Excel output"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from app import extract_unique_hinban, lookup_official_names, enrich_mapping_with_kde, _kde_peak_price

df = pd.read_excel(r'C:\Users\komed\Downloads\allsites_todayful_20260223_231740.xlsx')
brand = "todayful"

# Run lookup
mapping_df = lookup_official_names(df, brand, max_lookup=9999, wear_search=True, web_search=False)
enriched_df, filtered_df = enrich_mapping_with_kde(df, mapping_df, min_price=10000)

# Build Excel
from io import BytesIO
output = BytesIO()
name_map = dict(zip(filtered_df["品番"], filtered_df["正式名称"]))

with pd.ExcelWriter(output, engine='openpyxl') as writer:
    # Sheet1
    s1 = df[['品番', '価格']].copy() if '価格' in df.columns else df[['品番']].copy()
    s1.insert(0, 'ブランド', brand.upper())
    s1.to_excel(writer, index=False, sheet_name='元データ')
    print(f"Sheet1 (元データ): {len(s1)} rows, cols={list(s1.columns)}")
    print(s1.head(3).to_string())

    # Sheet2
    s2_cols = ["品番", "正式名称", "ソース", "件数", "KDE代表価格", "価格レンジ"]
    s2 = filtered_df[[c for c in s2_cols if c in filtered_df.columns]].copy()
    s2.to_excel(writer, index=False, sheet_name='品番マッピング')
    print(f"\nSheet2 (品番マッピング): {len(s2)} rows")
    print(s2.head(3).to_string())

    # Sheet3
    merged = df.copy()
    merged["正式名称"] = ""
    if "品番" in merged.columns:
        merged["正式名称"] = merged["品番"].map(
            lambda x: name_map.get(str(x).strip(), "") if pd.notna(x) else ""
        )
    named = merged[merged["正式名称"] != ""].copy()

    groups = []
    for name, grp in named.groupby("正式名称"):
        prices = pd.to_numeric(grp["価格"], errors="coerce").dropna().tolist()
        prices = [p for p in prices if p > 0]
        if not prices:
            continue
        kde_price = _kde_peak_price(prices)
        groups.append({
            "ブランド": brand.upper(),
            "正式名称": name,
            "件数": len(prices),
            "KDE代表価格": kde_price,
            "最安値": int(min(prices)),
            "最高値": int(max(prices)),
        })
    s3 = pd.DataFrame(groups).sort_values("KDE代表価格", ascending=False).reset_index(drop=True)
    s3.to_excel(writer, index=False, sheet_name='正式名称集計')
    print(f"\nSheet3 (正式名称集計): {len(s3)} rows")
    print(s3.head(10).to_string())
    print(f"\n...last 5:")
    print(s3.tail(5).to_string())

# Save test file
with open(r'C:\Users\komed\Downloads\test_3sheet.xlsx', 'wb') as f:
    f.write(output.getvalue())
print(f"\nSaved to test_3sheet.xlsx")
