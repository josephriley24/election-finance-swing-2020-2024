#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 19:47:13 2026

@author: josephriley
"""

import pandas as pd
import pickle
import zipfile
import matplotlib.pyplot as plt

# load candidate/committee info
cand20 = pd.read_csv('com_cand_info.csv', dtype=str)
cand24 = pd.read_csv('com_cand_info_2024.csv', dtype=str)

# get presidential committee IDs for each year
pres_cmtes_20 = set(cand20['CMTE_ID'].str.strip())
pres_cmtes_24 = set(cand24['CMTE_ID'].str.strip())

# load national 2020 data
with zipfile.ZipFile('indiv_national_2020.zip', 'r') as z:
    print(z.namelist())
    with z.open(z.namelist()[0]) as f:
        indiv20_full = pickle.load(f)

# load national 2024 data
with zipfile.ZipFile('indiv_national_2024.zip', 'r') as z:
    print(z.namelist())
    with z.open(z.namelist()[0]) as f:
        indiv24_full = pickle.load(f)
        
# filter to presidential committees
national_20 = indiv20_full[indiv20_full['CMTE_ID'].isin(pres_cmtes_20)].copy()
national_24 = indiv24_full[indiv24_full['CMTE_ID'].isin(pres_cmtes_24)].copy()

# join party info
national_20 = pd.merge(national_20, cand20[['CMTE_ID', 'CAND_PTY_AFFILIATION']], 
                        on='CMTE_ID', how='left')
national_24 = pd.merge(national_24, cand24[['CMTE_ID', 'CAND_PTY_AFFILIATION_x']], 
                        on='CMTE_ID', how='left')

# convert amt to numeric
national_20['amt'] = pd.to_numeric(national_20['amt'], errors='coerce')
national_24['amt'] = pd.to_numeric(national_24['amt'], errors='coerce')

# compute national totals
dem_national_20 = national_20[national_20['CAND_PTY_AFFILIATION'] == 'DEM']['amt'].sum()
rep_national_20 = national_20[national_20['CAND_PTY_AFFILIATION'] == 'REP']['amt'].sum()
dem_national_24 = national_24[national_24['CAND_PTY_AFFILIATION_x'] == 'DEM']['amt'].sum()
rep_national_24 = national_24[national_24['CAND_PTY_AFFILIATION_x'] == 'REP']['amt'].sum()

print(f'DEM 2020 national: ${dem_national_20/1e6:.1f}M')
print(f'REP 2020 national: ${rep_national_20/1e6:.1f}M')
print(f'DEM 2024 national: ${dem_national_24/1e6:.1f}M')
print(f'REP 2024 national: ${rep_national_24/1e6:.1f}M')

# swing state totals (from by_party files)
by_party_20 = pd.read_csv('by_party_20.csv')
by_party_24 = pd.read_csv('by_party_24.csv')

by_party_20['DEM'] = pd.to_numeric(by_party_20['DEM'], errors='coerce')
by_party_20['REP'] = pd.to_numeric(by_party_20['REP'], errors='coerce')
by_party_24['DEM'] = pd.to_numeric(by_party_24['DEM'], errors='coerce')
by_party_24['REP'] = pd.to_numeric(by_party_24['REP'], errors='coerce')

dem_swing_20 = by_party_20['DEM'].sum()
rep_swing_20 = by_party_20['REP'].sum()
dem_swing_24 = by_party_24['DEM'].sum()
rep_swing_24 = by_party_24['REP'].sum()

# compute shares
swing_shares = {
    'DEM 2020': dem_swing_20 / dem_national_20 * 100,
    'REP 2020': rep_swing_20 / rep_national_20 * 100,
    'DEM 2024': dem_swing_24 / dem_national_24 * 100,
    'REP 2024': rep_swing_24 / rep_national_24 * 100
}

print('\nSwing state shares:')
for k, v in swing_shares.items():
    print(f'{k}: {v:.2f}%')

# plot
fig, ax = plt.subplots(figsize=(8, 5))
colors = ['blue', 'red', 'blue', 'red']
alphas = [0.5, 0.5, 1.0, 1.0]

bars = ax.bar(swing_shares.keys(), swing_shares.values(), color=colors)
for bar, alpha in zip(bars, alphas):
    bar.set_alpha(alpha)

# add value labels on bars
for bar, val in zip(bars, swing_shares.values()):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
            f'{val:.2f}%', ha='center', va='bottom', fontsize=10)

ax.set_title('Swing State Share of National Presidential Fundraising\n2020 vs 2024')
ax.set_ylabel('% of National Total')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.1f}%'))
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('national_swing_share.png', dpi=150)
plt.show()


