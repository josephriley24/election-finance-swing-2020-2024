#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 12:59:51 2026

@author: josephriley
"""

import pandas as pd
import zipfile

import pickle
with zipfile.ZipFile('indiv_swing_2024.zip', 'r') as z:
    print(z.namelist())
    
# read file for 2024
with zipfile.ZipFile('indiv_swing_2024.zip', 'r') as z:
    with z.open('indiv_swing_2024') as f:
        indiv24 = pickle.load(f)

print(indiv24.shape)
print(indiv24.columns.tolist())

# read file for 2020
with zipfile.ZipFile('indiv_swing_2020.zip', 'r') as z:
    with z.open('indiv_swing_2020') as f:
        indiv20 = pickle.load(f)

print(indiv20.shape)
print(indiv20.columns.tolist())
print(indiv24['PGI'].value_counts())
# recreate cand24 and cand20
cand24 = pd.read_csv('com_cand_info_2024.csv', dtype=str)
cand20 = pd.read_csv('com_cand_info.csv', dtype=str)
# filter out donations to non-presidential committees
pres_cmtes_24 = set(cand24['CMTE_ID'].str.strip())
indiv24_pres = indiv24[indiv24['CMTE_ID'].str.strip().isin(pres_cmtes_24)].copy()
print(indiv24_pres.shape)
