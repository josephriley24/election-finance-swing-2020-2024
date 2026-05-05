#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  4 17:06:05 2026

@author: josephriley
"""

import pandas as pd
import pickle
import zipfile
import matplotlib.pyplot as plt
import geopandas as gpd

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

# aggregate by state and party for each cycle
state_20 = national_20.groupby(['STATE', 'CAND_PTY_AFFILIATION'])['amt'].sum().reset_index()
state_24 = national_24.groupby(['STATE', 'CAND_PTY_AFFILIATION_x'])['amt'].sum().reset_index()

# rename for consistency
state_24 = state_24.rename(columns={'CAND_PTY_AFFILIATION_x': 'CAND_PTY_AFFILIATION'})

# pivot to wide format
state_20_wide = state_20.pivot_table(index='STATE', columns='CAND_PTY_AFFILIATION', values='amt').reset_index()
state_24_wide = state_24.pivot_table(index='STATE', columns='CAND_PTY_AFFILIATION', values='amt').reset_index()

print(state_20_wide.head())
print(state_24_wide.head())

# compute national totals
dem_national_20 = national_20[national_20['CAND_PTY_AFFILIATION'] == 'DEM']['amt'].sum()
rep_national_20 = national_20[national_20['CAND_PTY_AFFILIATION'] == 'REP']['amt'].sum()
dem_national_24 = national_24[national_24['CAND_PTY_AFFILIATION_x'] == 'DEM']['amt'].sum()
rep_national_24 = national_24[national_24['CAND_PTY_AFFILIATION_x'] == 'REP']['amt'].sum()

# compute shares for each state
state_20_wide['DEM_share'] = state_20_wide['DEM'] / dem_national_20
state_20_wide['REP_share'] = state_20_wide['REP'] / rep_national_20
state_24_wide['DEM_share'] = state_24_wide['DEM'] / dem_national_24
state_24_wide['REP_share'] = state_24_wide['REP'] / rep_national_24

# merge 2020 and 2024 together
state_merged = pd.merge(state_20_wide[['STATE', 'DEM_share', 'REP_share']],
                         state_24_wide[['STATE', 'DEM_share', 'REP_share']],
                         on='STATE', suffixes=('_20', '_24'))

# compute shift metric
state_merged['metric'] = (state_merged['DEM_share_24'] - state_merged['DEM_share_20']) - \
                          (state_merged['REP_share_24'] - state_merged['REP_share_20'])

print(state_merged[['STATE', 'metric']].sort_values('metric', ascending=False))

# load state boundary file
geo_state = gpd.read_file('cb_2020_us_state_500k.zip')
print(geo_state.columns.tolist())

# join metric onto shapefile
geo_state = geo_state.merge(state_merged[['STATE', 'metric']], left_on = 'STUSPS', right_on='STATE', how='left')

# define swing states
swing_states = {'PA', 'MI', 'WI', 'AZ', 'GA', 'NV', 'NC'}

# flag swing states
geo_state['is_swing'] = geo_state['STUSPS'].isin(swing_states)

# check metric values
print(state_merged[state_merged['STATE'].isin(swing_states)][['STATE', 'metric']].sort_values('metric', ascending=False))

# exclude Alaska, Hawaii, and US territories from map
exclude = {'AK', 'HI', 'GU', 'PR', 'VI', 'MP', 'AS'}
geo_state = geo_state[~geo_state['STUSPS'].isin(exclude)]

# plot
fig, ax = plt.subplots(figsize=(12, 8))

# first plot with all states


# set limits based on percentiles rather than min/max
import numpy as np
max_val = np.percentile(geo_state['metric'].abs().dropna(), 95)

geo_state.plot(ax=ax, column='metric', cmap='RdBu',
               vmin=-max_val, vmax=max_val,
               edgecolor='white', linewidth=0.5,
               legend=True)

ax.set_title('Shift in Each States Share of Presidential Fundraising\n2020 to 2024')
ax.set_axis_off()
plt.tight_layout()
plt.savefig('full_us_choropleth.png', dpi=150)
plt.show()

# next plot with just swing states
fig, ax = plt.subplots(figsize=(12, 8))  # new figure

# plot non-swing states in light gray
geo_state[~geo_state['is_swing']].plot(ax=ax, color='lightgray', edgecolor='white')

# find the maximum absolute value to center the colormap
max_val = geo_state[geo_state['is_swing']]['metric'].abs().max()

# plot swing states with centered colormap
geo_state[geo_state['is_swing']].plot(ax=ax, column='metric', cmap='RdBu',
                                       edgecolor='white', linewidth=0.5,
                                       legend=True,
                                       vmin=-max_val, vmax=max_val,
                                       legend_kwds={'label': 'Democratic Shift'})

ax.set_title('Shift in Swing State Share of Presidential Fundraising\n2020 to 2024')
ax.set_axis_off()
plt.tight_layout()
plt.savefig('swing_state_choropleth.png', dpi=150)
plt.show()