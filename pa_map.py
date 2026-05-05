#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  4 19:07:54 2026

@author: josephriley
"""

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# load pennsylvania ZCTA boundary file
geo_pa = gpd.read_file('cb_2020_42_zcta520_500k.gpkg', layer='zip')
geo_pa = geo_pa.rename(columns={'ZCTA5CE20': 'zip'})
geo_pa = geo_pa[['zip', 'geometry']]

# get list of PA zips
pa_zips = set(geo_pa['zip'])

# load by_party files and filter to PA
by_party_20 = pd.read_csv('by_party_20.csv', dtype={'ZIP_CODE': str})
by_party_24 = pd.read_csv('by_party_24.csv', dtype={'ZIP_CODE': str})

# standardize name of zip column
by_party_20 = by_party_20.rename(columns={'ZIP_CODE': 'zip'})
by_party_24 = by_party_24.rename(columns={'ZIP_CODE': 'zip'})

# ensure leading zeros
by_party_20['zip'] = by_party_20['zip'].str.zfill(5)
by_party_24['zip'] = by_party_24['zip'].str.zfill(5)

# filter to just PA
by_party_20_pa = by_party_20[by_party_20['zip'].isin(pa_zips)].copy()
by_party_24_pa = by_party_24[by_party_24['zip'].isin(pa_zips)].copy()

print(f'PA ZIPs in 2020 data: {len(by_party_20_pa)}')
print(f'PA ZIPs in 2024 data: {len(by_party_24_pa)}')

# begin computing the shift metric
import pickle
import zipfile

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

# compute shares using national totals
by_party_20_pa['DEM_share'] = by_party_20_pa['DEM'] / dem_national_20
by_party_20_pa['REP_share'] = by_party_20_pa['REP'] / rep_national_20
by_party_24_pa['DEM_share'] = by_party_24_pa['DEM'] / dem_national_24
by_party_24_pa['REP_share'] = by_party_24_pa['REP'] / rep_national_24

# merge 2020 and 2024
pa_merged = pd.merge(by_party_20_pa[['zip', 'DEM_share', 'REP_share']],
                     by_party_24_pa[['zip', 'DEM_share', 'REP_share']],
                     on='zip', how='outer', suffixes=('_20', '_24')).fillna(0)

# compute shift metric
pa_merged['metric'] = (pa_merged['DEM_share_24'] - pa_merged['DEM_share_20']) - \
                       (pa_merged['REP_share_24'] - pa_merged['REP_share_20'])

# join onto geometry
geo_pa = geo_pa.merge(pa_merged[['zip', 'metric']], on='zip', how='left')

print(geo_pa['metric'].describe())

# load state boundary for outline
geo_state_pa = gpd.read_file('cb_2020_42_zcta520_500k.gpkg', layer='state')

# plot
fig, ax = plt.subplots(figsize=(12, 8))

max_val = geo_pa['metric'].abs().max()

geo_pa.plot(ax=ax, column='metric', cmap='RdBu',
            edgecolor='none',
            vmin=-max_val, vmax=max_val,
            legend=True,
            missing_kwds={'color': 'lightgray'},
            legend_kwds={'label': 'Democratic Shift'})

# overlay state border
geo_state_pa.boundary.plot(ax=ax, color='black', linewidth=1)

ax.set_title('ZIP-Level Shift in Share of Presidential Fundraising\nPennsylvania 2020 to 2024')
ax.set_axis_off()
plt.tight_layout()
plt.savefig('pa_zip_choropleth.png', dpi=150)
plt.show()