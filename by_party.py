#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 10:36:17 2026

@author: josephriley
"""

import zipfile
import pandas as pd
import pickle

# read indiv_swing files for 2020 and 24
# read file for 2020
with zipfile.ZipFile('indiv_swing_2020.zip', 'r') as z:
    with z.open('indiv_swing_2020') as f:
        indiv20 = pickle.load(f)
# read file for 2020
with zipfile.ZipFile('indiv_swing_2024_pres.zip', 'r') as z:
    with z.open('indiv_swing_2024_pres') as f:
        indiv24 = pickle.load(f)
# recreate cand24 and cand20
cand24 = pd.read_csv('com_cand_info_2024.csv', dtype=str)
cand20 = pd.read_csv('com_cand_info.csv', dtype=str)



# create by_party dataframe for 2024
# join party info onto contributions
indiv24_pres = pd.merge(indiv24, cand24[['CMTE_ID', 'CAND_PTY_AFFILIATION_x']], 
                         on='CMTE_ID', how='left')

#trim ZIP to 5 digits
indiv24_pres['ZIP_CODE'] = indiv24_pres['ZIP_CODE'].str[:5]

# groupby ZIP and party, then sum
by_party_24 = indiv24_pres.groupby(['ZIP_CODE', 'CAND_PTY_AFFILIATION_x'])['amt'].sum().reset_index()

# pivot party affiliation into columns
by_party_24 = by_party_24.pivot_table(index='ZIP_CODE', 
                                       columns='CAND_PTY_AFFILIATION_x', 
                                       values='amt', 
                                       aggfunc='sum').reset_index()
by_party_24.columns.name = None

by_party_24.rename(columns={'CAND_PTY_AFFILIATION_x': 'CAND_PTY_AFFILIATION'})

# create by_party dataframe for 2020
# join party info onto contributions
indiv20_pres = pd.merge(indiv20, cand20[['CMTE_ID', 'CAND_PTY_AFFILIATION']], 
                         on='CMTE_ID', how='left')

#trim ZIP to 5 digits
indiv20_pres['ZIP_CODE'] = indiv20_pres['ZIP_CODE'].str[:5]

# groupby ZIP and party, then sum
by_party_20 = indiv20_pres.groupby(['ZIP_CODE', 'CAND_PTY_AFFILIATION'])['amt'].sum().reset_index()

# pivot party affiliation into columns
by_party_20 = by_party_20.pivot_table(index='ZIP_CODE', 
                                       columns='CAND_PTY_AFFILIATION', 
                                       values='amt', 
                                       aggfunc='sum').reset_index()
by_party_20.columns.name = None
by_party_24.to_csv('by_party_24.csv')
by_party_20.to_csv('by_party_20.csv')





