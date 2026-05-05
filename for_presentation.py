#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 14:20:41 2026

@author: josephriley
"""

import pandas as pd
import matplotlib.pyplot as plt

# load in data

natl_parties = pd.read_csv("com_cand_info_2024.csv", dtype=str)
natl_parties['TTL_RECEIPTS'] = pd.to_numeric(natl_parties['TTL_RECEIPTS'], errors='coerce')

# separate major parties, group small parties into "other"
major_parties = {'DEM', 'REP', 'LIB'} 
natl_parties['party'] = natl_parties["CAND_PTY_AFFILIATION_x"].where(natl_parties["CAND_PTY_AFFILIATION_x"].isin(major_parties), 'OTHER')

# Trump's total manually sourced from FEC due to committee conversion
trump_total = 495853270.30  

# check Biden's total
print(natl_parties[natl_parties['CAND_NAME_x'].str.contains('BIDEN', na=False)][['CAND_NAME_x', 'TTL_RECEIPTS', 'CMTE_NM']])

# check current DEM and REP totals
natl_parties['TTL_RECEIPTS'] = pd.to_numeric(natl_parties['TTL_RECEIPTS'], errors='coerce')
print(natl_parties.groupby('CAND_PTY_AFFILIATION_x')['TTL_RECEIPTS'].sum())

biden_total = natl_parties[natl_parties['CAND_NAME_x'].str.contains('BIDEN', na=False)]['TTL_RECEIPTS'].sum()


# get base totals by party
party_totals = natl_parties.groupby('CAND_PTY_AFFILIATION_x')['TTL_RECEIPTS'].sum()

# apply corrections
party_totals['DEM'] -= biden_total
party_totals['REP'] += trump_total

print(party_totals)

# create chart for national totals by party

color_map = {
    'DEM': 'blue',
    'REP': 'red',
    'LIB': 'gold',
    'IND': 'gray',
    'OTH': 'gray'
}

colors = [color_map.get(party, 'gray') for party in party_totals.index]
fig, ax = fig, ax = plt.subplots(figsize=(8, 5))
party_totals.plot(kind='bar', ax=ax, color=colors)
ax.set_title('2024 Presidential Campaign Receipts by Party')
ax.set_xlabel('Party')
ax.set_ylabel('Total Receipts ($)')
ax.yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: f'${x/1e6:.0f}M'))
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('national_2024.png', dpi=150)
plt.show()

# create function for R/D lean by state
import pickle
import zipfile

# load indiv 24
with zipfile.ZipFile('indiv_swing_2024_pres.zip', 'r') as z:
    with z.open('indiv_swing_2024_pres') as f:
        indiv24 = pickle.load(f)
        
# bring in party from natl_parties
indiv24 = pd.merge(indiv24, 
                   natl_parties[['CMTE_ID', 'party']], 
                   on='CMTE_ID', how='left')
indiv24['amt'] = pd.to_numeric(indiv24['amt'], errors='coerce')

def state_lean(state):
    df = indiv24[indiv24['STATE'] == state].copy()
    totals = df.groupby('party')['amt'].sum()
    total = totals.sum()
    dem = totals.get('DEM', 0)
    rep = totals.get('REP', 0)
    lean = (rep - dem) / total
    color_map = {
        'DEM': 'blue',
        'REP': 'red',
        'OTH': 'gray'
    }
    colors = [color_map.get(party, 'gray') for party in totals.index]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    totals.plot(kind='bar', ax=ax, color=colors)
    ax.set_title(f'{state} 2024 Contributions — R-D Lean: {lean:.2%}')
    ax.set_xlabel('Party')
    ax.set_ylabel('Total Contributions ($)')
    ax.yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: f'${x/1e6:.1f}M'))
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(f'{state}_2024.png', dpi=150)
    plt.show()
    
    return lean

for state in ['PA', 'MI', 'WI', 'AZ', 'GA', 'NV', 'NC']:
    lean = state_lean(state)
    print(f'{state}: {lean:.2%}')
# see what committees are in the indiv data
print(indiv24['CMTE_ID'].value_counts().head(10))
print(indiv24[indiv24['CMTE_ID'] == 'C00828541'].shape)
print(natl_parties[natl_parties['CMTE_ID'] == 'C00828541'][['CMTE_ID', 'CMTE_NM', 'CAND_PTY_AFFILIATION_x']])
trump_contribs = indiv24[indiv24['CMTE_ID'] == 'C00828541']
print(trump_contribs['party'].value_counts())


names_to_check = ['STEIN', 'OLIVER', 'DE LA CRUZ']
for name in names_to_check:
    matches = natl_parties[natl_parties['CAND_NAME_x'].str.contains(name, na=False)][['CAND_NAME_x', 'CAND_PTY_AFFILIATION_x']]
    print(matches)
print(natl_parties[natl_parties['CAND_PTY_AFFILIATION_x'] == 'DEM']['CAND_NAME_x'].tolist())
print(natl_parties[natl_parties['CAND_PTY_AFFILIATION_x'] == 'REP']['CAND_NAME_x'].tolist())
    
nominees = [
    'HARRIS, KAMALA','KENNEDY, ROBERT, F. JR., SHANAHAN, NICOLE', 'STEIN, JILL',
    'OLIVER, CHASE RUSSELL', 'DE LA CRUZ, CLAUDIA', 'TRUMP, DONALD J.'
    
]

cand24_filtered = natl_parties[natl_parties['CAND_NAME_x'].isin(nominees)].copy()

# recode parties
major_parties = {'DEM', 'REP'}
cand24_filtered['party'] = cand24_filtered['CAND_PTY_AFFILIATION_x'].where(
    cand24_filtered['CAND_PTY_AFFILIATION_x'].isin(major_parties), 'OTH')

party_totals = cand24_filtered.groupby('party')['TTL_RECEIPTS'].sum()
party_totals['REP'] += trump_total

print(party_totals)

color_map = {
    'DEM': 'blue',
    'REP': 'red',
    'LIB': 'gold',
    'IND': 'gray',
    'OTH': 'gray'
}

colors = [color_map.get(party, 'gray') for party in party_totals.index]
fig, ax = fig, ax = plt.subplots(figsize=(8, 5))
party_totals.plot(kind='bar', ax=ax, color=colors)
ax.set_title('2024 Presidential Campaign Receipts by Party')
ax.set_xlabel('Party')
ax.set_ylabel('Total Receipts ($)')
ax.yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: f'${x/1e6:.0f}M'))
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('national_2024.png', dpi=150)
plt.show()