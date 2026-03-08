"""Analyze unresolved hinbans"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from app import extract_unique_hinban, extract_names_from_local_data

df = pd.read_excel(r'C:\Users\komed\Downloads\allsites_todayful_20260223_231740.xlsx')
unique = extract_unique_hinban(df)
target = unique[:100]

local = extract_names_from_local_data(df, 'todayful')
unresolved = [h for h in target if not local.get(h, '')]
print(f'Unresolved ({len(unresolved)}):')
for h in unresolved:
    print(f'  {h}')
